"""Scriptwriting & Narration Capability for StoryForge Runtime."""

import os
import uuid
from typing import Any, Dict, List
from ..interfaces import IArtifact, ICapability


class ScriptArtifact(IArtifact):
    """Artifact containing complete timed script scenes and narration text."""

    def __init__(
        self,
        artifact_id: str,
        title: str,
        scenes: List[Dict[str, Any]],
        total_word_count: int,
        estimated_total_duration_seconds: float,
    ):
        self._id = artifact_id
        self.title = title
        self.scenes = scenes
        self.total_word_count = total_word_count
        self.estimated_total_duration_seconds = estimated_total_duration_seconds

    @property
    def artifact_id(self) -> str:
        return self._id

    @property
    def artifact_type(self) -> str:
        return "script_text"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "artifact_type": self.artifact_type,
            "title": self.title,
            "scenes": self.scenes,
            "total_word_count": self.total_word_count,
            "estimated_total_duration_seconds": self.estimated_total_duration_seconds,
        }


class ScriptwriterCapability(ICapability):
    """Capability that crafts engaging voiceover narration, timing cues, and scene descriptions."""

    @property
    def name(self) -> str:
        return "scriptwriter"

    async def _call_llm(self, title: str) -> str | None:
        """Call Gemini or Groq for real script generation."""
        import httpx

        # Try Gemini first
        gemini_key = os.getenv("GEMINI_API_KEY", "")
        if gemini_key:
            try:
                prompt = (
                    f"Write a 4-scene short video script for a 60-second documentary reel about '{title}'. "
                    f"For each scene provide: scene_number, heading (e.g. ACT 1: HOOK), narration_text (2-3 sentences), "
                    f"visual_prompt (cinematic image description), camera_direction, estimated_duration_seconds. "
                    f"Return as JSON array of scene objects."
                )
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.7},
                }
                async with httpx.AsyncClient(timeout=25.0) as client:
                    resp = await client.post(url, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        return data["candidates"][0]["content"]["parts"][0]["text"]
            except Exception as e:
                print(f"[Scriptwriter] Gemini call failed: {e}")

        # Try Groq as backup
        groq_key = os.getenv("GROQ_API_KEY", "")
        if groq_key:
            try:
                prompt = (
                    f"Write a 4-scene short video script for '{title}'. "
                    f"Each scene: scene_number, heading, narration_text, visual_prompt, camera_direction, estimated_duration_seconds. "
                    f"Return JSON array."
                )
                url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"}
                payload = {
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                }
                async with httpx.AsyncClient(timeout=20.0) as client:
                    resp = await client.post(url, headers=headers, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        return data["choices"][0]["message"]["content"]
            except Exception as e:
                print(f"[Scriptwriter] Groq call failed: {e}")

        return None

    async def execute(
        self,
        title: str = "",
        outline: Dict[str, Any] | None = None,
        words_per_minute: int = 150,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Generate timed script scenes from a story outline or title."""
        if not title:
            title = "The Dawn of AI Storytelling"

        artifact_id = f"scr-{uuid.uuid4().hex[:8]}"

        # Try live LLM
        llm_response = await self._call_llm(title)

        if llm_response:
            import json as json_mod
            try:
                clean = llm_response.strip()
                if "```json" in clean:
                    clean = clean.split("```json")[1].split("```")[0].strip()
                elif "```" in clean:
                    clean = clean.split("```")[1].split("```")[0].strip()

                scenes_data = json_mod.loads(clean)
                if isinstance(scenes_data, dict) and "scenes" in scenes_data:
                    scenes_data = scenes_data["scenes"]
                if not isinstance(scenes_data, list):
                    raise ValueError("Expected list of scenes")

                # Normalize scene keys
                for i, scene in enumerate(scenes_data):
                    scene.setdefault("scene_number", i + 1)
                    scene.setdefault("heading", f"Scene {i + 1}")
                    scene.setdefault("narration_text", "")
                    scene.setdefault("visual_prompt", "Cinematic documentary shot")
                    scene.setdefault("camera_direction", "Standard")
                    scene.setdefault("estimated_duration_seconds", 10.0)
                    scene["word_count"] = len(scene.get("narration_text", "").split())

            except Exception:
                # LLM returned non-parseable text — use it as a single scene
                scenes_data = [{
                    "scene_number": 1,
                    "heading": f"Script: {title}",
                    "narration_text": llm_response[:500],
                    "visual_prompt": f"Cinematic imagery for {title}",
                    "camera_direction": "Dynamic",
                    "estimated_duration_seconds": 40.0,
                    "word_count": len(llm_response.split()),
                }]
        else:
            # Fallback template
            scenes_data = [
                {
                    "scene_number": 1,
                    "heading": "ACT 1: HOOK - The Spark",
                    "narration_text": f"What if a single topic could transform into a cinema-quality documentary in seconds? Welcome to {title}.",
                    "visual_prompt": f"Dramatic cinematic lighting revealing glowing digital particles forming {title}.",
                    "camera_direction": "Slow zoom in with dramatic atmosphere",
                    "estimated_duration_seconds": 6.0,
                },
                {
                    "scene_number": 2,
                    "heading": "ACT 2: SETUP - Background",
                    "narration_text": "For decades, video production required studios, crews, and endless editing hours. Today, intelligent agents orchestrate the entire process.",
                    "visual_prompt": "Fast-paced montage of traditional video editing suites morphing into modern AI code nodes.",
                    "camera_direction": "Panning right over timeline tracks",
                    "estimated_duration_seconds": 12.0,
                },
                {
                    "scene_number": 3,
                    "heading": "ACT 3: CONFLICT & CLIMAX - The Breakthrough",
                    "narration_text": "By unifying research, scriptwriting, voice synthesis, and visual rendering into a single graph, boundaries disappear.",
                    "visual_prompt": "High-tech neural network nodes pulsing in rhythm with voice waves and image frames.",
                    "camera_direction": "Dynamic rotation around central neural core",
                    "estimated_duration_seconds": 15.0,
                },
                {
                    "scene_number": 4,
                    "heading": "ACT 4: RESOLUTION - Call to Action",
                    "narration_text": "The future of storytelling isn't just automated—it's agentic. Forge your story today.",
                    "visual_prompt": "Sleek dark-mode studio interface glowing with a prominent call to action button.",
                    "camera_direction": "Static hero shot with subtle particle floating",
                    "estimated_duration_seconds": 7.0,
                },
            ]

        total_words = 0
        for scene in scenes_data:
            word_cnt = len(scene.get("narration_text", "").split())
            scene["word_count"] = word_cnt
            total_words += word_cnt

        estimated_duration = round((total_words / words_per_minute) * 60, 1)

        artifact = ScriptArtifact(
            artifact_id=artifact_id,
            title=title,
            scenes=scenes_data,
            total_word_count=total_words,
            estimated_total_duration_seconds=estimated_duration,
        )

        return artifact.to_dict()
