"""End-to-end story video pipeline.

research -> script -> images -> voice -> render -> publish

Each step reports progress through an async callback so the API can persist it
and the UI can poll it. Every external dependency has a free fallback, so a run
always finishes with a playable MP4 even when no API keys are configured.
"""

from __future__ import annotations

import asyncio
import logging
import os
import random
import re
import shutil
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Optional

import httpx

from . import llm, media

logger = logging.getLogger("storyforge.pipeline")

STEPS = [
    ("research", "Research"),
    ("script", "Script"),
    ("images", "Scene images"),
    ("voice", "Narration"),
    ("render", "Video render"),
    ("publish", "Publish"),
]

Reporter = Callable[..., Awaitable[None]]

PACK_STYLES: Dict[str, Dict[str, str]] = {
    "history": {
        "label": "History & Culture",
        "style": "cinematic historical documentary, painterly realism, warm sepia tones, dramatic lighting",
        "voice": "authoritative documentary narrator",
    },
    "technology": {
        "label": "Technology & AI",
        "style": "sleek futuristic visuals, neon accents, volumetric light, clean product-shot composition",
        "voice": "energetic tech explainer",
    },
    "science": {
        "label": "Science & Space",
        "style": "awe-inspiring scientific illustration, cosmic scale, crisp detail, deep blues and purples",
        "voice": "curious science communicator",
    },
    "cricket": {
        "label": "Cricket & Sports",
        "style": "high-energy stadium photography, floodlights, motion blur, vivid crowd atmosphere",
        "voice": "passionate sports storyteller",
    },
    "travel": {
        "label": "Travel & Places",
        "style": "golden-hour travel photography, sweeping drone vistas, vibrant local colour",
        "voice": "warm travel host",
    },
    "chess": {
        "label": "Chess & Strategy",
        "style": "moody macro photography of carved chess pieces, dramatic shadows, shallow depth of field",
        "voice": "thoughtful strategist",
    },
    "documentary": {
        "label": "Dark Documentary",
        "style": "gritty true-crime documentary still, desaturated, high contrast, film grain",
        "voice": "suspenseful investigative narrator",
    },
}


def pack_info(name: str) -> Dict[str, str]:
    return PACK_STYLES.get((name or "").lower(), PACK_STYLES["history"])


# ---------------------------------------------------------------------------
# Research
# ---------------------------------------------------------------------------


_STOPWORDS = {
    "about", "after", "before", "their", "there", "these", "those", "which", "while", "would", "could", "should",
    "story", "history", "video", "short", "world", "really", "things", "where", "what", "when", "with", "from",
    "surprising", "amazing", "incredible", "secret", "secrets", "truth", "explained", "smart", "behind", "changed",
}


def _stems(text: str) -> set[str]:
    """Crude stems (first 5 letters of longer words) for fuzzy topic matching: octopus ~ octopuses."""
    return {w[:5] for w in re.findall(r"[a-z0-9]+", text.lower()) if len(w) > 3 and w not in _STOPWORDS}


async def wikipedia_context(title: str, topic: str = "", limit: int = 3) -> List[Dict[str, str]]:
    """Grounding snippets from Wikipedia (free and keyless, but rate limited per IP).

    One request does search + intro extracts. Results are re-ranked so pages whose
    titles share words with the title/brief win - full-text search alone returns
    loose matches (e.g. "Doctor Octopus" pages for an octopus documentary).
    """
    # Wikimedia rejects requests without a descriptive User-Agent that includes a contact URL.
    headers = {"User-Agent": os.getenv("WIKIPEDIA_USER_AGENT", "StoryForgeAI/1.0 (https://github.com/; educational project)")}
    query_stems = _stems(f"{title} {topic}")
    # Search on the meaningful words only; filler like "why ... so" drowns the topic.
    words = [w for w in re.findall(r"[\w'-]+", f"{title} {topic}") if len(w) > 3 and w.lower() not in _STOPWORDS]
    query = " ".join(dict.fromkeys(words[:10])) or title
    params = {
        "action": "query", "format": "json", "generator": "search", "gsrsearch": query[:300],
        "gsrlimit": 8, "prop": "extracts", "exintro": 1, "explaintext": 1, "exlimit": 8, "exchars": 1200,
    }
    try:
        async with httpx.AsyncClient(timeout=15.0, headers=headers) as client:
            for attempt in range(2):
                resp = await client.get("https://en.wikipedia.org/w/api.php", params=params)
                if resp.status_code == 429 and attempt == 0:
                    await asyncio.sleep(min(15.0, float(resp.headers.get("retry-after", "5"))))
                    continue
                resp.raise_for_status()
                break
            pages = [p for p in resp.json().get("query", {}).get("pages", {}).values() if p.get("extract")]
    except Exception as exc:
        logger.warning("Wikipedia lookup failed: %s", exc)
        return []

    pages.sort(key=lambda p: (-len(_stems(p["title"]) & query_stems), p.get("index", 99)))
    # No sources beats off-topic sources: the script prompt would trust them.
    relevant = [p for p in pages if _stems(p["title"]) & query_stems][:limit]
    return [
        {"title": p["title"], "extract": p["extract"].strip(), "url": f"https://en.wikipedia.org/wiki/{quote_title(p['title'])}"}
        for p in relevant
    ]


def quote_title(title: str) -> str:
    from urllib.parse import quote

    return quote(title.replace(" ", "_"))


# ---------------------------------------------------------------------------
# Script
# ---------------------------------------------------------------------------

SCRIPT_SYSTEM = (
    "You are an award-winning short-form documentary writer and director. "
    "You write tight, factual, emotionally engaging narration for vertical and landscape videos, "
    "and you design striking visuals for each scene. Never invent statistics or quotes. "
    "Always answer with JSON only."
)


def _scene_count(target_seconds: int) -> int:
    return max(3, min(10, round(target_seconds / 9)))


def build_script_prompt(
    *, title: str, topic: str, pack: str, notes: str, target_seconds: int, sources: List[Dict[str, str]], language: str
) -> str:
    info = pack_info(pack)
    n = _scene_count(target_seconds)
    words = int(target_seconds * 2.4)
    source_block = "\n\n".join(f"[{s['title']}] {s['extract']}" for s in sources) or "(none found)"
    notes_block = notes.strip() or "(none)"
    return f"""Write a {target_seconds}-second short video script.

TITLE: {title}
TOPIC / BRIEF: {topic}
GENRE: {info['label']} - narrated by a {info['voice']}.
NARRATION LANGUAGE: {language}

CREATOR NOTES (follow these closely):
{notes_block}

REFERENCE FACTS (prefer these over memory; do not contradict them):
{source_block}

Requirements:
- Exactly {n} scenes. Total narration about {words} words.
- Scene 1 is a hook that creates curiosity in the first sentence. The last scene lands a memorable payoff.
- Narration is spoken text only: no stage directions, emojis, hashtags or scene labels.
- visual_prompt: a vivid, concrete English description of ONE still image for an AI image model
  (subject, setting, composition, lighting, era). No text, captions or logos in the image.
- on_screen_text: 2-5 punchy words for a caption, or "".

Return JSON:
{{"title": str, "logline": str, "facts": [str, ...up to 5 key facts used],
  "scenes": [{{"heading": str, "narration": str, "visual_prompt": str, "on_screen_text": str}}]}}"""


def template_script(title: str, topic: str, pack: str, target_seconds: int, sources: List[Dict[str, str]]) -> Dict[str, Any]:
    """Offline script used only when every LLM provider is unavailable."""
    sentences: List[str] = []
    for src in sources:
        sentences += [s.strip() for s in re.split(r"(?<=[.!?])\s+", src["extract"]) if len(s.split()) > 5]
    if not sentences:
        sentences = [
            f"This is the story of {topic}.",
            f"To understand {title}, we have to go back to where it began.",
            "What happened next changed everything.",
            f"And that is why {title} still matters today.",
        ]
    n = min(_scene_count(target_seconds), len(sentences))
    style = pack_info(pack)["style"]
    scenes = [
        {
            "heading": f"Scene {i + 1}",
            "narration": " ".join(sentences[i * 2 : i * 2 + 2]) or sentences[i],
            "visual_prompt": f"{title}, {topic}, scene {i + 1}, {style}",
            "on_screen_text": "",
        }
        for i in range(n)
    ]
    return {"title": title, "logline": topic, "facts": sentences[:5], "scenes": scenes}


def normalize_scenes(raw: Any) -> List[Dict[str, str]]:
    scenes = raw.get("scenes", []) if isinstance(raw, dict) else raw
    if not isinstance(scenes, list):
        raise ValueError("script has no scene list")
    out = []
    for i, sc in enumerate(scenes):
        if not isinstance(sc, dict):
            continue
        narration = str(sc.get("narration") or sc.get("narration_text") or "").strip()
        if not narration:
            continue
        out.append(
            {
                "heading": str(sc.get("heading") or f"Scene {i + 1}").strip(),
                "narration": narration,
                "visual_prompt": str(sc.get("visual_prompt") or narration).strip(),
                "on_screen_text": str(sc.get("on_screen_text") or "").strip(),
            }
        )
    if not out:
        raise ValueError("script contained no usable scenes")
    return out


async def write_script(
    *, title: str, topic: str, pack: str, notes: str, target_seconds: int, sources: List[Dict[str, str]], language: str
) -> Dict[str, Any]:
    prompt = build_script_prompt(
        title=title, topic=topic, pack=pack, notes=notes, target_seconds=target_seconds, sources=sources, language=language
    )
    try:
        data, result = await llm.complete_json(prompt, system=SCRIPT_SYSTEM, temperature=0.8)
        scenes = normalize_scenes(data)
        return {
            "title": str(data.get("title") or title) if isinstance(data, dict) else title,
            "logline": str(data.get("logline", "")) if isinstance(data, dict) else "",
            "facts": [str(f) for f in (data.get("facts") or [])][:5] if isinstance(data, dict) else [],
            "scenes": scenes,
            "provider": result.provider,
            "model": result.model,
        }
    except (llm.LLMUnavailableError, ValueError) as exc:
        logger.warning("Falling back to template script: %s", exc)
        script = template_script(title, topic, pack, target_seconds, sources)
        script.update(provider="template", model="offline", warning=str(exc)[:300])
        return script


REVISE_SYSTEM = (
    "You are a video script editor. You apply the creator's instruction to an existing scene list "
    "and return the full updated scene list as JSON only."
)


async def revise_script(scenes: List[Dict[str, Any]], instruction: str, title: str) -> Dict[str, Any]:
    """Apply a natural-language edit to the scene list (used by the studio chat)."""
    import json

    slim = [{k: s.get(k, "") for k in ("heading", "narration", "visual_prompt", "on_screen_text")} for s in scenes]
    prompt = (
        f"Video title: {title}\n\nCurrent scenes JSON:\n{json.dumps(slim, ensure_ascii=False)}\n\n"
        f"Creator instruction: {instruction}\n\n"
        "Apply the instruction. Keep scenes that should not change identical. "
        'Return JSON: {"reply": "one or two sentences describing what you changed", '
        '"scenes": [{"heading", "narration", "visual_prompt", "on_screen_text"}]}'
    )
    data, result = await llm.complete_json(prompt, system=REVISE_SYSTEM, temperature=0.6)
    new_scenes = normalize_scenes(data)
    reply = str(data.get("reply", "Updated the script.")) if isinstance(data, dict) else "Updated the script."
    return {"scenes": new_scenes, "reply": reply, "provider": result.provider}


# ---------------------------------------------------------------------------
# Subtitles
# ---------------------------------------------------------------------------


def _ass_time(t: float) -> str:
    t = max(0.0, t)
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def _ass_escape(text: str) -> str:
    return text.replace("\\", "").replace("{", "(").replace("}", ")").replace("\n", " ")


def caption_chunks(words: List[media.WordTiming], max_words: int = 4, max_span: float = 1.8) -> List[media.WordTiming]:
    """Group word timings into short, readable caption phrases."""
    chunks: List[media.WordTiming] = []
    current: List[media.WordTiming] = []
    for w in words:
        if current and (len(current) >= max_words or w.end - current[0].start > max_span):
            chunks.append(media.WordTiming(" ".join(x.word for x in current), current[0].start, current[-1].end))
            current = []
        current.append(w)
        if re.search(r"[.!?,;:]$", w.word):
            chunks.append(media.WordTiming(" ".join(x.word for x in current), current[0].start, current[-1].end))
            current = []
    if current:
        chunks.append(media.WordTiming(" ".join(x.word for x in current), current[0].start, current[-1].end))
    # Close the gaps so captions don't flicker between phrases.
    for a, b in zip(chunks, chunks[1:]):
        if 0 < b.start - a.end < 0.4:
            a.end = b.start
    return chunks


def build_ass(words: List[media.WordTiming], width: int, height: int, heading: str = "") -> str:
    font_size = int(height * (0.052 if height > width else 0.065))
    margin_v = int(height * 0.16)
    lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        f"PlayResX: {width}",
        f"PlayResY: {height}",
        "WrapStyle: 0",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
        "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: Caption,DejaVu Sans,{font_size},&H00FFFFFF,&H0000FFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,"
        f"{max(2, font_size // 14)},2,2,40,40,{margin_v},1",
        f"Style: Heading,DejaVu Sans,{int(font_size * 0.6)},&H0000D7FF,&H0000D7FF,&H00000000,&H64000000,-1,0,0,0,100,100,2,0,1,"
        f"2,1,8,40,40,{int(height * 0.06)},1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    if heading and words:
        lines.append(f"Dialogue: 1,{_ass_time(0)},{_ass_time(min(2.5, words[-1].end))},Heading,,0,0,0,,{_ass_escape(heading.upper())}")
    for chunk in caption_chunks(words):
        lines.append(
            f"Dialogue: 0,{_ass_time(chunk.start)},{_ass_time(chunk.end)},Caption,,0,0,0,,{{\\fad(80,60)}}{_ass_escape(chunk.word)}"
        )
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

FPS = 25


def render_scene_clip(
    *, image: Path, audio: Path, duration: float, words: List[media.WordTiming], aspect_ratio: str,
    index: int, out: Path, heading: str = "", burn_captions: bool = True,
) -> None:
    """Ken Burns pan/zoom over the still image, narration audio and burned-in captions."""
    width, height = media.dimensions(aspect_ratio)
    frames = max(1, int(round(duration * FPS)))
    big_w, big_h = int(width * 1.5) // 2 * 2, int(height * 1.5) // 2 * 2
    zoom_in = index % 2 == 0
    z = f"1+0.18*on/{frames}" if zoom_in else f"1.18-0.18*on/{frames}"
    # Drift horizontally on alternating scenes for variety.
    x = "iw/2-(iw/zoom/2)" if index % 3 else f"(iw-iw/zoom)*on/{frames}"
    fade_out = max(0.0, duration - 0.35)
    vf = (
        f"scale={big_w}:{big_h}:force_original_aspect_ratio=increase,crop={big_w}:{big_h},"
        f"zoompan=z='{z}':x='{x}':y='ih/2-(ih/zoom/2)':d=1:s={width}x{height}:fps={FPS},"
        f"fade=t=in:st=0:d=0.35,fade=t=out:st={fade_out:.2f}:d=0.35"
    )
    workdir = out.parent
    if burn_captions and words:
        (workdir / f"captions_{index}.ass").write_text(build_ass(words, width, height, heading), encoding="utf-8")
        # Relative path + cwd avoids ffmpeg filter escaping issues with drive letters.
        vf += f",subtitles=captions_{index}.ass"
    vf += ",format=yuv420p"
    args = [
        "-loop", "1", "-framerate", str(FPS), "-i", str(image.resolve()),
        "-i", str(audio.resolve()),
        "-filter_complex", f"[0:v]{vf}[v];[1:a]aresample=44100,apad[a]",
        "-map", "[v]", "-map", "[a]",
        "-t", f"{duration:.2f}",
        "-c:v", "libx264", "-preset", os.getenv("X264_PRESET", "veryfast"), "-crf", "23", "-r", str(FPS),
        "-threads", os.getenv("FFMPEG_THREADS", "2"),
        "-c:a", "aac", "-b:a", "128k", "-ac", "2", "-ar", "44100",
        out.name,
    ]
    try:
        media.run_ffmpeg(args, cwd=workdir)
    except RuntimeError as exc:
        if burn_captions and "subtitles" in vf:
            logger.warning("Caption burn-in failed (%s); rendering scene without captions", exc)
            render_scene_clip(
                image=image, audio=audio, duration=duration, words=words, aspect_ratio=aspect_ratio,
                index=index, out=out, heading=heading, burn_captions=False,
            )
        else:
            raise


def concat_clips(clips: List[Path], out: Path) -> None:
    listing = out.parent / "concat.txt"
    listing.write_text("".join(f"file '{c.name}'\n" for c in clips), encoding="utf-8")
    media.run_ffmpeg(
        ["-f", "concat", "-safe", "0", "-i", listing.name, "-c", "copy", "-movflags", "+faststart", out.name],
        cwd=out.parent,
    )


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


async def _noop(*_: Any, **__: Any) -> None:
    return None


async def run_pipeline(
    *,
    project_id: str,
    title: str,
    topic: str,
    pack: str,
    aspect_ratio: str,
    notes: str = "",
    target_seconds: int = 45,
    voice: str = media.DEFAULT_VOICE,
    language: str = "English",
    existing_script: Optional[Dict[str, Any]] = None,
    regenerate_images: Optional[set[int]] = None,
    previous_scenes: Optional[List[Dict[str, Any]]] = None,
    report: Reporter = _noop,
) -> Dict[str, Any]:
    """Run the pipeline and return the final project payload.

    If existing_script is given, research and script steps are skipped (re-render after edits).
    Images for scenes whose visual_prompt is unchanged are reused unless listed in regenerate_images.
    """
    workdir = media.MEDIA_DIR / project_id
    workdir.mkdir(parents=True, exist_ok=True)
    regenerate_images = regenerate_images or set()
    previous_by_prompt = {
        (s.get("visual_prompt"), i): s for i, s in enumerate(previous_scenes or [])
    }

    # 1. Research ---------------------------------------------------------
    if existing_script is None:
        await report("research", status="running")
        sources = await wikipedia_context(title, topic)
        await report("research", status="completed", provider="wikipedia", detail=f"{len(sources)} sources")

        # 2. Script --------------------------------------------------------
        await report("script", status="running", detail="Writing narration and shot list")
        script = await write_script(
            title=title, topic=topic, pack=pack, notes=notes, target_seconds=target_seconds,
            sources=sources, language=language,
        )
        script["sources"] = [{"title": s["title"], "url": s["url"]} for s in sources]
        await report(
            "script", status="completed", provider=script["provider"], model=script.get("model"),
            detail=f"{len(script['scenes'])} scenes" + (" (offline template - add an LLM key)" if script["provider"] == "template" else ""),
            script=script,
        )
    else:
        script = existing_script
        await report("research", status="skipped", detail="Using edited script")
        await report("script", status="skipped", detail="Using edited script")

    scenes: List[Dict[str, Any]] = [dict(s) for s in script["scenes"]]
    style = pack_info(pack)["style"]

    # 3. Images ----------------------------------------------------------
    await report("images", status="running", detail=f"0/{len(scenes)}")
    image_paths: List[Path] = []
    providers_used: set[str] = set()
    for i, scene in enumerate(scenes):
        prev = previous_by_prompt.get((scene["visual_prompt"], i))
        prev_path = Path(prev["image_path"]) if prev and prev.get("image_path") else None
        if prev_path and prev_path.exists() and i not in regenerate_images:
            image_paths.append(prev_path)
            scene.update({k: prev[k] for k in ("image_url", "image_provider", "image_path", "seed") if k in prev})
            providers_used.add(prev.get("image_provider", "cached"))
        else:
            seed = random.randint(1, 2_000_000_000)
            prompt = f"{scene['visual_prompt']}. Style: {style}. No text, no watermark."
            async def image_status(msg: str, i: int = i) -> None:
                await report("images", status="running", detail=f"{i}/{len(scenes)} - {msg}")

            img = await media.generate_image(
                prompt, aspect_ratio, seed, workdir / f"scene_{i + 1}_{seed}.jpg", status=image_status
            )
            image_paths.append(img.path)
            providers_used.add(img.provider)
            published = (await media.publish_file(img.path, "image"))["url"]
            scene.update(image_url=published, image_provider=img.provider, image_path=str(img.path), seed=seed)
        await report("images", status="running", detail=f"{i + 1}/{len(scenes)}", scenes=scenes)
    await report("images", status="completed", provider=", ".join(sorted(providers_used)), detail=f"{len(scenes)} images")

    # 4. Voice -----------------------------------------------------------
    await report("voice", status="running", detail=f"0/{len(scenes)}")
    voices: List[media.VoiceResult] = []
    for i, scene in enumerate(scenes):
        v = await media.synthesize_voice(scene["narration"], voice, workdir / f"voice_{i + 1}.mp3")
        voices.append(v)
        scene["duration"] = round(v.duration, 2)
        scene["voice_provider"] = v.provider
        await report("voice", status="running", detail=f"{i + 1}/{len(scenes)}")
    voice_providers = sorted({v.provider for v in voices})
    await report(
        "voice", status="completed", provider=", ".join(voice_providers),
        detail=f"{sum(v.duration for v in voices):.1f}s of narration",
    )

    # 5. Render ----------------------------------------------------------
    await report("render", status="running", detail=f"Scene 0/{len(scenes)}")
    clips: List[Path] = []
    for i, (scene, img, v) in enumerate(zip(scenes, image_paths, voices)):
        clip = workdir / f"clip_{i + 1}.mp4"
        await asyncio.to_thread(
            render_scene_clip,
            image=img, audio=v.path, duration=v.duration + 0.4, words=v.words,
            aspect_ratio=aspect_ratio, index=i, out=clip, heading=scene.get("on_screen_text", ""),
        )
        clips.append(clip)
        await report("render", status="running", detail=f"Scene {i + 1}/{len(scenes)}")
    final = workdir / f"final_{random.randint(1000, 9999)}.mp4"
    await asyncio.to_thread(concat_clips, clips, final)
    total = sum(v.duration + 0.4 for v in voices)
    width, height = media.dimensions(aspect_ratio)
    await report("render", status="completed", provider="ffmpeg", detail=f"{total:.1f}s at {width}x{height}")

    # 6. Publish ---------------------------------------------------------
    await report("publish", status="running")
    published = await media.publish_file(final, "video")
    for clip in clips:
        clip.unlink(missing_ok=True)
    for old in workdir.glob("final_*.mp4"):
        if old != final and published["provider"] == "local":
            old.unlink(missing_ok=True)
    if published["provider"] != "local":
        final.unlink(missing_ok=True)
    await report("publish", status="completed", provider=published["provider"])

    script["scenes"] = scenes
    return {
        "script": script,
        "video": {
            "url": published["url"],
            "bytes": published["bytes"],
            "storage": published["provider"],
            "duration": round(total, 1),
            "width": width,
            "height": height,
        },
        "providers": {
            "llm": script.get("provider"),
            "images": sorted(providers_used),
            "voice": voice_providers,
            "storage": published["provider"],
        },
    }


def cleanup_project_media(project_id: str) -> None:
    shutil.rmtree(media.MEDIA_DIR / project_id, ignore_errors=True)
