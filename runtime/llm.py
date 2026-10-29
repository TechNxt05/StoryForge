"""Free-tier LLM client with automatic provider failover.

Order of attempts (each is skipped if its key is missing):
  1. Google Gemini      GEMINI_API_KEY      (free tier via AI Studio)
  2. Groq               GROQ_API_KEY        (free tier, very fast)
  3. OpenRouter         OPENROUTER_API_KEY  (free ":free" models / openrouter/free router)
  4. Pollinations       POLLINATIONS_API_KEY optional - works anonymously, rate limited

Every model name can be overridden with an env var, because free-tier model
rosters change often.
"""

from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, List, Optional

import httpx

logger = logging.getLogger("storyforge.llm")

DEFAULT_TIMEOUT = 60.0


class LLMUnavailableError(RuntimeError):
    """Raised when every configured provider failed."""


@dataclass
class LLMResult:
    text: str
    provider: str
    model: str


def _env(name: str, default: str = "") -> str:
    return (os.getenv(name) or default).strip()


async def _gemini(client: httpx.AsyncClient, system: str, prompt: str, json_mode: bool, temperature: float) -> LLMResult:
    key = _env("GEMINI_API_KEY")
    model = _env("GEMINI_MODEL", "gemini-2.5-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    generation_config: dict[str, Any] = {"temperature": temperature}
    if json_mode:
        generation_config["responseMimeType"] = "application/json"
    payload = {
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": generation_config,
    }
    resp = await client.post(url, json=payload, headers={"x-goog-api-key": key})
    resp.raise_for_status()
    data = resp.json()
    parts = data["candidates"][0]["content"]["parts"]
    text = "".join(p.get("text", "") for p in parts if not p.get("thought"))
    return LLMResult(text=text, provider="gemini", model=model)


async def _openai_compatible(
    client: httpx.AsyncClient,
    *,
    url: str,
    key: str,
    model: str,
    provider: str,
    system: str,
    prompt: str,
    json_mode: bool,
    temperature: float,
    extra_headers: Optional[dict[str, str]] = None,
) -> LLMResult:
    payload: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
    headers = {"Content-Type": "application/json", **(extra_headers or {})}
    if key:
        headers["Authorization"] = f"Bearer {key}"
    resp = await client.post(url, json=payload, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    text = data["choices"][0]["message"]["content"] or ""
    return LLMResult(text=text, provider=provider, model=data.get("model", model))


async def _groq(client: httpx.AsyncClient, system: str, prompt: str, json_mode: bool, temperature: float) -> LLMResult:
    return await _openai_compatible(
        client,
        url="https://api.groq.com/openai/v1/chat/completions",
        key=_env("GROQ_API_KEY"),
        model=_env("GROQ_MODEL", "openai/gpt-oss-120b"),
        provider="groq",
        system=system,
        prompt=prompt,
        json_mode=json_mode,
        temperature=temperature,
    )


async def _openrouter(client: httpx.AsyncClient, system: str, prompt: str, json_mode: bool, temperature: float) -> LLMResult:
    return await _openai_compatible(
        client,
        url="https://openrouter.ai/api/v1/chat/completions",
        key=_env("OPENROUTER_API_KEY"),
        model=_env("OPENROUTER_MODEL", "openrouter/free"),
        provider="openrouter",
        system=system,
        prompt=prompt,
        # Many free models reject response_format; we parse JSON leniently instead.
        json_mode=False,
        temperature=temperature,
        extra_headers={"X-Title": "StoryForge AI"},
    )


async def _pollinations(client: httpx.AsyncClient, system: str, prompt: str, json_mode: bool, temperature: float) -> LLMResult:
    key = _env("POLLINATIONS_API_KEY")
    if key:
        url = "https://gen.pollinations.ai/v1/chat/completions"
    else:
        url = "https://text.pollinations.ai/openai"
    return await _openai_compatible(
        client,
        url=url,
        key=key,
        model=_env("POLLINATIONS_TEXT_MODEL", "openai"),
        provider="pollinations",
        system=system,
        prompt=prompt,
        json_mode=False,
        temperature=temperature,
    )


ProviderFn = Callable[[httpx.AsyncClient, str, str, bool, float], Awaitable[LLMResult]]

# (name, required env var or None if it works anonymously, call)
_PROVIDERS: List[tuple[str, Optional[str], ProviderFn]] = [
    ("gemini", "GEMINI_API_KEY", _gemini),
    ("groq", "GROQ_API_KEY", _groq),
    ("openrouter", "OPENROUTER_API_KEY", _openrouter),
    ("pollinations", None, _pollinations),
]


def configured_providers() -> List[str]:
    """Names of LLM providers that will be attempted, in order."""
    disabled = {p.strip() for p in _env("LLM_DISABLED_PROVIDERS").split(",") if p.strip()}
    return [
        name
        for name, env_key, _ in _PROVIDERS
        if name not in disabled and (env_key is None or _env(env_key))
    ]


async def complete(
    prompt: str,
    *,
    system: str = "You are a helpful assistant.",
    json_mode: bool = False,
    temperature: float = 0.7,
    only: Optional[List[str]] = None,
) -> LLMResult:
    """Run a completion against the first provider that succeeds (optionally restricted to `only`)."""
    enabled = set(configured_providers())
    if only is not None:
        enabled &= set(only)
    errors: List[str] = []
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        for name, _, fn in _PROVIDERS:
            if name not in enabled:
                continue
            try:
                result = await fn(client, system, prompt, json_mode, temperature)
                if result.text.strip():
                    return result
                errors.append(f"{name}: empty response")
            except httpx.HTTPStatusError as exc:
                body = exc.response.text[:200].replace("\n", " ")
                errors.append(f"{name}: HTTP {exc.response.status_code} {body}")
            except Exception as exc:  # network errors, malformed payloads
                errors.append(f"{name}: {type(exc).__name__}: {exc}")
            logger.warning("LLM provider failed: %s", errors[-1])
    raise LLMUnavailableError("; ".join(errors) or "no LLM providers configured")


def extract_json(text: str) -> Any:
    """Parse JSON from an LLM reply, tolerating code fences, prose and <think> blocks."""
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", cleaned, flags=re.DOTALL)
    if fence:
        cleaned = fence.group(1).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    # Fall back to the outermost {...} or [...] span.
    for open_ch, close_ch in (("{", "}"), ("[", "]")):
        start, end = cleaned.find(open_ch), cleaned.rfind(close_ch)
        if start != -1 and end > start:
            try:
                return json.loads(cleaned[start : end + 1])
            except json.JSONDecodeError:
                continue
    raise ValueError("LLM response did not contain valid JSON")


async def complete_json(prompt: str, *, system: str, temperature: float = 0.7) -> tuple[Any, LLMResult]:
    """Like complete(), but parses JSON and retries the next provider on bad JSON."""
    result = await complete(prompt, system=system, json_mode=True, temperature=temperature)
    try:
        return extract_json(result.text), result
    except ValueError:
        logger.warning("Provider %s returned invalid JSON, retrying with stricter prompt", result.provider)
        retry = await complete(
            prompt + "\n\nReturn ONLY valid minified JSON. No prose, no markdown.",
            system=system,
            json_mode=True,
            temperature=0.3,
        )
        return extract_json(retry.text), retry
