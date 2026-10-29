"""Scriptwriting & Narration Capability for StoryForge Runtime."""

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

    async def _call_llm(self, title: str, vision_context: str = "") -> str | None:
        """Call the first available free LLM (see runtime.llm) for script generation."""
        from .. import llm

        prompt = (
            f"You are an expert film director. Create a 4-scene short video blueprint for '{title}'.\n"
            "Determine the overall mood and choose a matching background music style.\n"
        )
        if vision_context:
            prompt += f"\nIncorporate these user-uploaded media into the scenes:\n{vision_context}\n"
        prompt += (
            "\nReturn a JSON object with keys: tone, music_style, scenes (list of objects with: scene_number, heading, "
            "narration_text, visual_prompt, camera_direction, estimated_duration_seconds, text_overlay)."
        )
        try:
            result = await llm.complete(prompt, system="You write short documentary scripts.", json_mode=True)
            return result.text
        except llm.LLMUnavailableError as e:
            print(f"[Scriptwriter] No LLM available: {e}")
            return None

    async def execute(
        self,
        title: str = "",
        outline: Dict[str, Any] | None = None,
        vision_descriptions: Dict[str, str] | None = None,
        words_per_minute: int = 150,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Generate timed script scenes from a story outline or title."""
        if not title:
            title = "The Dawn of AI Storytelling"

        artifact_id = f"scr-{uuid.uuid4().hex[:8]}"
        
        vision_context = ""
        if vision_descriptions:
            for k, v in vision_descriptions.items():
                vision_context += f"- Asset ID {k}: {v}\n"

        # Try live LLM
        llm_response = await self._call_llm(title, vision_context)

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
