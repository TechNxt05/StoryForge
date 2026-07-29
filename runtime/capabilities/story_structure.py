"""Story Structure Planner Capability for StoryForge Runtime."""

import uuid
from typing import Any, Dict, List
from ..interfaces import IArtifact, ICapability


class StoryOutlineArtifact(IArtifact):
    """Artifact containing narrative arc structure and act timings."""

    def __init__(
        self,
        artifact_id: str,
        topic: str,
        acts: List[Dict[str, Any]],
        total_duration_seconds: int,
        pacing_style: str,
    ):
        self._id = artifact_id
        self.topic = topic
        self.acts = acts
        self.total_duration_seconds = total_duration_seconds
        self.pacing_style = pacing_style

    @property
    def artifact_id(self) -> str:
        return self._id

    @property
    def artifact_type(self) -> str:
        return "story_outline"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "artifact_type": self.artifact_type,
            "topic": self.topic,
            "acts": self.acts,
            "total_duration_seconds": self.total_duration_seconds,
            "pacing_style": self.pacing_style,
        }


class StoryStructureCapability(ICapability):
    """Capability that organizes topic research into narrative acts (Hook, Setup, Conflict, Climax, Resolution)."""

    @property
    def name(self) -> str:
        return "story_structure_planner"

    async def execute(
        self, topic: str = "", target_duration: int = 60, pacing_style: str = "fast", **kwargs: Any
    ) -> Dict[str, Any]:
        """Generate a narrative act outline for the given topic."""
        if not topic:
            topic = "AI Storytelling Evolution"

        artifact_id = f"out-{uuid.uuid4().hex[:8]}"

        # Calculate act duration splits based on standard short-form narrative ratios
        hook_duration = max(3, int(target_duration * 0.10))
        setup_duration = int(target_duration * 0.25)
        conflict_duration = int(target_duration * 0.35)
        climax_duration = int(target_duration * 0.20)
        resolution_duration = target_duration - (hook_duration + setup_duration + conflict_duration + climax_duration)

        acts = [
            {
                "act_name": "Hook",
                "purpose": f"Grab viewer attention instantly about {topic}",
                "target_duration_seconds": hook_duration,
                "emotional_tone": "curious_dramatic",
            },
            {
                "act_name": "Setup",
                "purpose": f"Introduce context and key background for {topic}",
                "target_duration_seconds": setup_duration,
                "emotional_tone": "informative",
            },
            {
                "act_name": "Conflict",
                "purpose": f"Highlight core challenge or mystery in {topic}",
                "target_duration_seconds": conflict_duration,
                "emotional_tone": "tense_engaging",
            },
            {
                "act_name": "Climax",
                "purpose": f"Deliver pivotal breakthrough or climax moment",
                "target_duration_seconds": climax_duration,
                "emotional_tone": "inspiring_peak",
            },
            {
                "act_name": "Resolution",
                "purpose": f"Provide takeaway message and call to action",
                "target_duration_seconds": resolution_duration,
                "emotional_tone": "satisfying_conclusive",
            },
        ]

        artifact = StoryOutlineArtifact(
            artifact_id=artifact_id,
            topic=topic,
            acts=acts,
            total_duration_seconds=target_duration,
            pacing_style=pacing_style,
        )

        return artifact.to_dict()
