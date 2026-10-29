"""Free media generation: scene images, narration audio, and file storage.

Images:  Cloudflare Workers AI FLUX (CLOUDFLARE_*) -> Hugging Face FLUX (HF_TOKEN)
         -> Pollinations (POLLINATIONS_API_KEY or anonymous, ~1 image/45s per IP)
         -> locally rendered gradient title card (always works).
Voice:   Microsoft Edge neural TTS via edge-tts (free, no key, word timings)
         -> Google Translate TTS via gTTS (free, no key) -> silent track.
Storage: Cloudinary (CLOUDINARY_URL or CLOUDINARY_*) else the local MEDIA_DIR served at /media.
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import logging
import os
import random
import re
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Optional
from urllib.parse import quote, unquote, urlparse

import httpx

logger = logging.getLogger("storyforge.media")

MEDIA_DIR = Path(os.getenv("MEDIA_DIR", "./media")).resolve()

# A small, curated set of natural-sounding Edge neural voices.
VOICES: Dict[str, str] = {
    "en-US-AndrewNeural": "Andrew (US, warm male)",
    "en-US-AvaNeural": "Ava (US, expressive female)",
    "en-US-BrianNeural": "Brian (US, casual male)",
    "en-US-EmmaNeural": "Emma (US, cheerful female)",
    "en-GB-RyanNeural": "Ryan (UK, male)",
    "en-GB-SoniaNeural": "Sonia (UK, female)",
    "en-IN-PrabhatNeural": "Prabhat (India, male)",
    "en-IN-NeerjaNeural": "Neerja (India, female)",
    "hi-IN-MadhurNeural": "Madhur (Hindi, male)",
    "hi-IN-SwaraNeural": "Swara (Hindi, female)",
}
DEFAULT_VOICE = "en-US-AndrewNeural"


def ffmpeg_path() -> str:
    """Locate an ffmpeg binary: system PATH first, then the one bundled with imageio-ffmpeg."""
    found = shutil.which("ffmpeg")
    if found:
        return found
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception as exc:  # pragma: no cover - depends on environment
        raise RuntimeError("ffmpeg not found. Install ffmpeg or `pip install imageio-ffmpeg`.") from exc


def run_ffmpeg(args: List[str], cwd: Optional[Path] = None, timeout: int = 900) -> None:
    cmd = [ffmpeg_path(), "-hide_banner", "-loglevel", "error", "-y", *args]
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {proc.stderr.strip()[-600:]}")


def dimensions(aspect_ratio: str) -> tuple[int, int]:
    """Output video size. A small RENDER_SHORT_SIDE keeps renders fast on free instances."""
    short_side = int(os.getenv("RENDER_SHORT_SIDE", "576"))
    long_side = short_side * 16 // 9
    long_side -= long_side % 2
    if aspect_ratio == "16:9":
        return long_side, short_side
    if aspect_ratio == "1:1":
        return short_side, short_side
    return short_side, long_side


# ---------------------------------------------------------------------------
# Images
# ---------------------------------------------------------------------------


@dataclass
class ImageResult:
    path: Path
    provider: str


# Called with a short status line while a provider waits on a free-tier quota.
StatusFn = Callable[[str], Awaitable[None]]


async def _no_status(_: str) -> None:
    return None


def _check_image(resp: httpx.Response) -> bytes:
    resp.raise_for_status()
    if not resp.headers.get("content-type", "").startswith("image/") or len(resp.content) < 2000:
        raise RuntimeError(f"unexpected response ({resp.headers.get('content-type')}, {len(resp.content)} bytes)")
    return resp.content


async def _cloudflare_image(prompt: str, width: int, height: int, seed: int, dest: Path, status: StatusFn) -> ImageResult:
    """Cloudflare Workers AI - FLUX.1 [schnell], free daily allowance (10k neurons/day)."""
    account = os.getenv("CLOUDFLARE_ACCOUNT_ID", "").strip()
    token = os.getenv("CLOUDFLARE_API_TOKEN", "").strip()
    if not (account and token):
        raise RuntimeError("Cloudflare Workers AI not configured")
    model = os.getenv("CLOUDFLARE_IMAGE_MODEL", "@cf/black-forest-labs/flux-1-schnell")
    url = f"https://api.cloudflare.com/client/v4/accounts/{account}/ai/run/{model}"
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            url, json={"prompt": prompt, "steps": 6, "seed": seed}, headers={"Authorization": f"Bearer {token}"}
        )
        resp.raise_for_status()
        data = resp.json()
    image_b64 = (data.get("result") or {}).get("image")
    if not image_b64:
        raise RuntimeError(f"cloudflare: no image in response {str(data)[:200]}")
    dest.write_bytes(base64.b64decode(image_b64))
    return ImageResult(path=dest, provider="cloudflare-flux")


async def _huggingface_image(prompt: str, width: int, height: int, seed: int, dest: Path, status: StatusFn) -> ImageResult:
    token = os.getenv("HF_TOKEN", "").strip()
    if not token:
        raise RuntimeError("HF_TOKEN not set")
    model = os.getenv("HF_IMAGE_MODEL", "black-forest-labs/FLUX.1-schnell")
    url = f"https://router.huggingface.co/hf-inference/models/{model}"
    payload = {"inputs": prompt, "parameters": {"width": width, "height": height, "seed": seed}}
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(url, json=payload, headers={"Authorization": f"Bearer {token}", "Accept": "image/png"})
        dest.write_bytes(_check_image(resp))
    return ImageResult(path=dest, provider="huggingface-flux")


async def _pollinations_image(prompt: str, width: int, height: int, seed: int, dest: Path, status: StatusFn) -> ImageResult:
    key = os.getenv("POLLINATIONS_API_KEY", "").strip()
    model = os.getenv("POLLINATIONS_IMAGE_MODEL", "flux")
    params = {"width": width, "height": height, "seed": seed, "model": model, "nologo": "true", "safe": "true"}
    if key:
        url, headers = f"https://gen.pollinations.ai/image/{quote(prompt)}", {"Authorization": f"Bearer {key}"}
    else:
        url, headers = f"https://image.pollinations.ai/prompt/{quote(prompt)}", {}
    # The anonymous tier allows ~1 image per 45s per IP and answers 402/429 with
    # "Retry after Ns". Waiting is slow but keeps zero-key setups fully working.
    max_wait = float(os.getenv("POLLINATIONS_MAX_WAIT", "75"))
    last_error = "unknown error"
    async with httpx.AsyncClient(timeout=150.0) as client:
        for _ in range(4):
            try:
                resp = await client.get(url, params=params, headers=headers, follow_redirects=True)
                if resp.status_code in (402, 429, 502, 503, 504):
                    hint = re.search(r"[Rr]etry after (\d+)", resp.text)
                    wait = float(hint.group(1)) + 2 if hint else 20.0
                    last_error = f"HTTP {resp.status_code}: {resp.text[:160]}"
                    if wait > max_wait:
                        break
                    await status(f"waiting {int(wait)}s for free image quota")
                    await asyncio.sleep(wait)
                    continue
                dest.write_bytes(_check_image(resp))
                return ImageResult(path=dest, provider="pollinations")
            except (httpx.HTTPError, RuntimeError) as exc:
                last_error = str(exc)
                await asyncio.sleep(5)
    raise RuntimeError(f"pollinations: {last_error}")


def _title_card(text: str, width: int, height: int, seed: int, dest: Path) -> ImageResult:
    """Last-resort visual: a gradient card rendered locally by ffmpeg."""
    rng = random.Random(seed)
    palette = ["0x1e1b4b", "0x312e81", "0x0f172a", "0x134e4a", "0x4c0519", "0x1c1917", "0x172554"]
    c0, c1 = rng.sample(palette, 2)
    run_ffmpeg(
        [
            "-f", "lavfi", "-i", f"gradients=s={width}x{height}:c0={c0}:c1={c1}:x0=0:y0=0:x1={width}:y1={height}:nb_colors=2",
            "-frames:v", "1", str(dest),
        ]
    )
    return ImageResult(path=dest, provider="local_title_card")


async def generate_image(
    prompt: str, aspect_ratio: str, seed: int, dest: Path, status: StatusFn = _no_status
) -> ImageResult:
    """Generate a scene image, falling through free providers until one works."""
    # Slightly larger than the video frame so the Ken Burns zoom stays sharp,
    # capped at 1024 on the long side (the most free endpoints will return).
    vw, vh = dimensions(aspect_ratio)
    scale = min(1.4, 1024 / max(vw, vh))
    width, height = int(vw * scale) // 16 * 16, int(vh * scale) // 16 * 16
    dest.parent.mkdir(parents=True, exist_ok=True)
    errors: List[str] = []
    for fn in (_cloudflare_image, _huggingface_image, _pollinations_image):
        try:
            return await fn(prompt, width, height, seed, dest, status)
        except Exception as exc:
            errors.append(str(exc))
            logger.info("Image provider skipped/failed: %s", exc)
    logger.warning("All image providers failed (%s); using local title card", "; ".join(errors))
    return await asyncio.to_thread(_title_card, prompt, width, height, seed, dest.with_suffix(".png"))


# ---------------------------------------------------------------------------
# Voice
# ---------------------------------------------------------------------------


@dataclass
class WordTiming:
    word: str
    start: float
    end: float


@dataclass
class VoiceResult:
    path: Path
    duration: float
    provider: str
    words: List[WordTiming] = field(default_factory=list)


def probe_duration(path: Path) -> float:
    """Read a media file's duration by decoding it with ffmpeg (no ffprobe needed)."""
    proc = subprocess.run(
        [ffmpeg_path(), "-hide_banner", "-i", str(path), "-f", "null", "-"],
        capture_output=True, text=True, timeout=120,
    )
    last = 0.0
    for line in proc.stderr.splitlines():
        if "time=" in line:
            stamp = line.split("time=")[-1].split()[0]
            try:
                h, m, s = stamp.split(":")
                last = int(h) * 3600 + int(m) * 60 + float(s)
            except ValueError:
                continue
    return last


def _estimate_word_timings(text: str, duration: float) -> List[WordTiming]:
    words = text.split()
    if not words:
        return []
    weights = [len(w) + 2 for w in words]  # longer words take longer to say
    total = sum(weights)
    t, out = 0.0, []
    for word, weight in zip(words, weights):
        span = duration * weight / total
        out.append(WordTiming(word, round(t, 3), round(t + span, 3)))
        t += span
    return out


async def _edge_tts(text: str, voice: str, dest: Path) -> VoiceResult:
    import edge_tts

    try:
        communicate = edge_tts.Communicate(text, voice, rate=os.getenv("TTS_RATE", "+5%"), boundary="WordBoundary")
    except TypeError:  # edge-tts < 7 has no boundary argument and emits WordBoundary by default
        communicate = edge_tts.Communicate(text, voice, rate=os.getenv("TTS_RATE", "+5%"))
    words: List[WordTiming] = []
    with dest.open("wb") as fh:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                fh.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                start = chunk["offset"] / 10_000_000
                words.append(WordTiming(chunk["text"], round(start, 3), round(start + chunk["duration"] / 10_000_000, 3)))
    if dest.stat().st_size < 1000:
        raise RuntimeError("edge-tts returned no audio")
    duration = await asyncio.to_thread(probe_duration, dest)
    return VoiceResult(path=dest, duration=duration, provider="edge-tts", words=words or _estimate_word_timings(text, duration))


def _gtts(text: str, voice: str, dest: Path) -> VoiceResult:
    from gtts import gTTS

    lang = voice.split("-")[0] if voice else "en"
    tld = {"en-GB": "co.uk", "en-IN": "co.in", "en-US": "com"}.get("-".join(voice.split("-")[:2]), "com")
    gTTS(text=text, lang=lang, tld=tld).save(str(dest))
    duration = probe_duration(dest)
    return VoiceResult(path=dest, duration=duration, provider="gtts", words=_estimate_word_timings(text, duration))


def _silence(text: str, dest: Path) -> VoiceResult:
    duration = max(3.0, len(text.split()) / 2.6)
    run_ffmpeg(["-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", f"{duration:.2f}", "-c:a", "libmp3lame", str(dest)])
    return VoiceResult(path=dest, duration=duration, provider="silent", words=_estimate_word_timings(text, duration))


async def synthesize_voice(text: str, voice: str, dest: Path) -> VoiceResult:
    dest.parent.mkdir(parents=True, exist_ok=True)
    voice = voice if voice in VOICES else DEFAULT_VOICE
    try:
        return await _edge_tts(text, voice, dest)
    except Exception as exc:
        logger.warning("edge-tts failed: %s", exc)
    try:
        return await asyncio.to_thread(_gtts, text, voice, dest)
    except Exception as exc:
        logger.warning("gTTS failed: %s", exc)
    return await asyncio.to_thread(_silence, text, dest)


# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------


def cloudinary_credentials() -> Optional[tuple[str, str, str]]:
    """(cloud_name, api_key, api_secret) from the three CLOUDINARY_* vars, or from
    CLOUDINARY_URL=cloudinary://<api_key>:<api_secret>@<cloud_name> as shown in the Cloudinary console."""
    parts = tuple(os.getenv(k, "").strip() for k in ("CLOUDINARY_CLOUD_NAME", "CLOUDINARY_API_KEY", "CLOUDINARY_API_SECRET"))
    if all(parts):
        return parts  # type: ignore[return-value]
    raw = os.getenv("CLOUDINARY_URL", "").strip()
    if raw.startswith("CLOUDINARY_URL="):  # tolerate pasting the whole "KEY=value" line
        raw = raw.split("=", 1)[1]
    parsed = urlparse(raw)
    if parsed.scheme == "cloudinary" and parsed.username and parsed.password and parsed.hostname:
        return parsed.hostname, unquote(parsed.username), unquote(parsed.password)
    return None


def cloudinary_configured() -> bool:
    return cloudinary_credentials() is not None


async def upload_to_cloudinary(path: Path, resource_type: str, folder: str = "storyforge") -> Dict[str, Any]:
    creds = cloudinary_credentials()
    if not creds:
        raise RuntimeError("Cloudinary is not configured")
    cloud, api_key, secret = creds
    timestamp = str(int(time.time()))
    # Signature covers all signed params in alphabetical order.
    signature = hashlib.sha1(f"folder={folder}&timestamp={timestamp}{secret}".encode()).hexdigest()
    url = f"https://api.cloudinary.com/v1_1/{cloud}/{resource_type}/upload"
    async with httpx.AsyncClient(timeout=300.0) as client:
        with path.open("rb") as fh:
            resp = await client.post(
                url,
                data={"api_key": api_key, "timestamp": timestamp, "folder": folder, "signature": signature},
                files={"file": (path.name, fh)},
            )
    resp.raise_for_status()
    data = resp.json()
    return {"url": data["secure_url"], "bytes": data.get("bytes", path.stat().st_size), "provider": "cloudinary"}


async def publish_file(path: Path, resource_type: str) -> Dict[str, Any]:
    """Make a generated file publicly reachable and return its URL.

    Local URLs are relative (/media/...) - the API prefixes them with its own origin.
    """
    if cloudinary_configured():
        try:
            return await upload_to_cloudinary(path, resource_type)
        except Exception as exc:
            logger.warning("Cloudinary upload failed, serving locally: %s", exc)
    rel = path.resolve().relative_to(MEDIA_DIR).as_posix()
    return {"url": f"/media/{rel}", "bytes": path.stat().st_size, "provider": "local"}
