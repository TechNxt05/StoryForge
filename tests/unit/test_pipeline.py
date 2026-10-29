"""Tests for the LLM client, script helpers, captions and the ffmpeg renderer."""

import pytest

from apps.api.src import auth
from runtime import llm, media, pipeline


# --- LLM client ------------------------------------------------------------


@pytest.mark.parametrize(
    "text",
    [
        '{"scenes": [1]}',
        '```json\n{"scenes": [1]}\n```',
        'Sure! Here is the JSON:\n{"scenes": [1]}\nHope that helps.',
        '<think>reasoning {not json}</think>{"scenes": [1]}',
    ],
)
def test_extract_json_tolerates_llm_formatting(text: str) -> None:
    assert llm.extract_json(text) == {"scenes": [1]}


def test_extract_json_rejects_prose() -> None:
    with pytest.raises(ValueError):
        llm.extract_json("I cannot help with that.")


def test_configured_providers_respects_keys_and_disabled(monkeypatch) -> None:
    monkeypatch.setenv("LLM_DISABLED_PROVIDERS", "pollinations")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setenv("GROQ_API_KEY", "k")
    assert llm.configured_providers() == ["groq"]


@pytest.mark.asyncio
async def test_complete_fails_over_to_next_provider(monkeypatch) -> None:
    calls = []

    async def broken(*_args):
        calls.append("gemini")
        raise RuntimeError("quota exceeded")

    async def working(*_args):
        calls.append("groq")
        return llm.LLMResult(text="hello", provider="groq", model="m")

    monkeypatch.setattr(llm, "_PROVIDERS", [("gemini", None, broken), ("groq", None, working)])
    monkeypatch.setenv("LLM_DISABLED_PROVIDERS", "")
    result = await llm.complete("hi")
    assert (result.provider, result.text, calls) == ("groq", "hello", ["gemini", "groq"])


@pytest.mark.asyncio
async def test_complete_raises_when_all_fail(monkeypatch) -> None:
    async def broken(*_args):
        raise RuntimeError("down")

    monkeypatch.setattr(llm, "_PROVIDERS", [("a", None, broken)])
    monkeypatch.setenv("LLM_DISABLED_PROVIDERS", "")
    with pytest.raises(llm.LLMUnavailableError, match="down"):
        await llm.complete("hi")


# --- Script helpers --------------------------------------------------------


def test_normalize_scenes_accepts_legacy_keys_and_drops_empty() -> None:
    raw = {"scenes": [{"narration_text": "Hello there."}, {"narration": ""}, "junk", {"narration": "Two", "visual_prompt": "v"}]}
    scenes = pipeline.normalize_scenes(raw)
    assert [s["narration"] for s in scenes] == ["Hello there.", "Two"]
    assert scenes[0]["visual_prompt"] == "Hello there."  # falls back to narration


def test_normalize_scenes_rejects_empty_script() -> None:
    with pytest.raises(ValueError):
        pipeline.normalize_scenes({"scenes": []})


def test_template_script_uses_sources() -> None:
    sources = [{"title": "X", "url": "u", "extract": "The first fact is quite interesting indeed. The second fact is also true here."}]
    script = pipeline.template_script("Title", "topic", "history", 30, sources)
    assert "first fact" in script["scenes"][0]["narration"]


def test_build_script_prompt_includes_notes_and_sources() -> None:
    prompt = pipeline.build_script_prompt(
        title="T", topic="brief", pack="chess", notes="Mention Magnus", target_seconds=45,
        sources=[{"title": "Chess", "extract": "Chess is a board game."}], language="Hindi",
    )
    assert "Mention Magnus" in prompt and "Chess is a board game." in prompt and "Hindi" in prompt
    assert "Exactly 5 scenes" in prompt


def test_research_relevance_stems() -> None:
    assert pipeline._stems("Octopus") & pipeline._stems("Why octopuses are so smart")
    assert not pipeline._stems("Large language model") & pipeline._stems("Why octopuses are so smart")


# --- Captions --------------------------------------------------------------


def _words(text: str, step: float = 0.3):
    return [media.WordTiming(w, i * step, i * step + step * 0.9) for i, w in enumerate(text.split())]


def test_caption_chunks_break_on_punctuation_and_length() -> None:
    chunks = pipeline.caption_chunks(_words("Hello world. This is a longer caption line here"))
    assert [c.word for c in chunks] == ["Hello world.", "This is a longer", "caption line here"]
    for a, b in zip(chunks, chunks[1:]):
        assert a.end <= b.start


def test_build_ass_escapes_override_braces() -> None:
    ass = pipeline.build_ass(_words("use {braces} safely"), 576, 1024, heading="Title")
    assert "{braces}" not in ass and "(braces)" in ass
    assert "PlayResX: 576" in ass and "Heading" in ass


# --- Rendering (real ffmpeg, offline inputs) --------------------------------


@pytest.mark.asyncio
async def test_run_pipeline_renders_real_mp4(offline_media, monkeypatch) -> None:
    async def no_sources(*_a, **_k):
        return []

    monkeypatch.setattr(pipeline, "wikipedia_context", no_sources)
    events = []

    async def report(step, **fields):
        events.append((step, fields.get("status")))

    result = await pipeline.run_pipeline(
        project_id="unit-render", title="Tiny", topic="A tiny test", pack="technology",
        aspect_ratio="1:1", target_seconds=15, report=report,
    )
    video = result["video"]
    path = media.MEDIA_DIR / video["url"].removeprefix("/media/")
    assert path.exists() and path.stat().st_size > 1000
    assert (video["width"], video["height"]) == (576, 576)
    duration = media.probe_duration(path)
    assert abs(duration - video["duration"]) < 1.0
    assert ("render", "completed") in events and ("publish", "completed") in events
    pipeline.cleanup_project_media("unit-render")


def test_dimensions_are_even() -> None:
    for ratio in ("9:16", "16:9", "1:1"):
        w, h = media.dimensions(ratio)
        assert w % 2 == 0 and h % 2 == 0


# --- Auth ------------------------------------------------------------------


def test_password_hashing_is_salted_and_verifies() -> None:
    h1, h2 = auth.hash_password("pw12345678"), auth.hash_password("pw12345678")
    assert h1 != h2 and h1.startswith("pbkdf2$")
    assert auth.verify_password("pw12345678", h1)
    assert not auth.verify_password("wrong", h1)


def test_legacy_hashes_still_verify() -> None:
    import hashlib
    import hmac

    legacy = hmac.new(auth.SECRET_KEY.encode(), b"oldpass1", hashlib.sha256).hexdigest()
    assert auth.verify_password("oldpass1", legacy)


def test_tampered_token_is_rejected() -> None:
    token = auth.create_access_token("u1", "a@b.c")
    assert auth.decode_access_token(token)["sub"] == "u1"
    header, payload, sig = token.split(".")
    assert auth.decode_access_token(f"{header}.{payload}x.{sig}") is None


# --- Storage config ----------------------------------------------------------


@pytest.mark.parametrize(
    "value",
    ["cloudinary://123456:abc-SECRET_x@my-cloud", "CLOUDINARY_URL=cloudinary://123456:abc-SECRET_x@my-cloud"],
)
def test_cloudinary_url_is_parsed(monkeypatch, value) -> None:
    for k in ("CLOUDINARY_CLOUD_NAME", "CLOUDINARY_API_KEY", "CLOUDINARY_API_SECRET"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("CLOUDINARY_URL", value)
    assert media.cloudinary_credentials() == ("my-cloud", "123456", "abc-SECRET_x")
    assert media.cloudinary_configured()


def test_cloudinary_unconfigured(monkeypatch) -> None:
    for k in ("CLOUDINARY_URL", "CLOUDINARY_CLOUD_NAME", "CLOUDINARY_API_KEY", "CLOUDINARY_API_SECRET"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("CLOUDINARY_URL", "https://not-a-cloudinary-url")
    assert not media.cloudinary_configured()
