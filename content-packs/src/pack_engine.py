"""Niche Content Packs Engine for StoryForge Runtime."""

from typing import Any, Dict, List, Optional


class ContentPack:
    """Represents a domain-specific content pack configuration."""

    def __init__(
        self,
        name: str,
        domain: str,
        visual_style: str,
        default_music: str,
        terminology: List[str],
        prompt_templates: Dict[str, str],
    ):
        self.name = name
        self.domain = domain
        self.visual_style = visual_style
        self.default_music = default_music
        self.terminology = terminology
        self.prompt_templates = prompt_templates

    def enrich_prompt(self, base_prompt: str) -> str:
        """Enrich a prompt with domain-specific style and visual guidance."""
        return f"{base_prompt}. Aesthetic Style: {self.visual_style}. Domain Terms: {', '.join(self.terminology[:3])}."

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "domain": self.domain,
            "visual_style": self.visual_style,
            "default_music": self.default_music,
            "terminology": self.terminology,
            "prompt_templates": self.prompt_templates,
        }


class ContentPackEngine:
    """Manages loading, validation, and retrieval of domain content packs."""

    def __init__(self) -> None:
        self._packs: Dict[str, ContentPack] = {}
        self._initialize_built_in_packs()

    def _initialize_built_in_packs(self) -> None:
        """Initialize built-in domain content packs."""
        built_ins = [
            ContentPack(
                name="history",
                domain="history",
                visual_style="cinematic_sepia_vintage_lighting_photorealistic",
                default_music="https://cdn.storyforge.ai/music/epic_orchestral.mp3",
                terminology=["archival_manuscript", "monumental_breakthrough", "historical_epoch"],
                prompt_templates={"script": "Historical documentary narrative focus on {topic}."},
            ),
            ContentPack(
                name="technology",
                domain="technology",
                visual_style="futuristic_neon_cyberpunk_volumetric_dark",
                default_music="https://cdn.storyforge.ai/music/ambient_tech.mp3",
                terminology=["quantum_superposition", "neural_architecture", "algorithmic_breakthrough"],
                prompt_templates={"script": "Tech overview highlighting {topic}."},
            ),
            ContentPack(
                name="cricket",
                domain="sports",
                visual_style="high_speed_stadium_lights_dynamic_motion",
                default_music="https://cdn.storyforge.ai/music/high_energy_rock.mp3",
                terminology=["cover_drive", "wicket_delivery", "stadium_crowd_roar"],
                prompt_templates={"script": "Cricket match milestone breakdown of {topic}."},
            ),
            ContentPack(
                name="travel",
                domain="lifestyle",
                visual_style="vibrant_golden_hour_scenic_drone_footage",
                default_music="https://cdn.storyforge.ai/music/acoustic_breeze.mp3",
                terminology=["scenic_viewpoint", "local_culture", "hidden_gem"],
                prompt_templates={"script": "Travel exploration guide of {topic}."},
            ),
            ContentPack(
                name="chess",
                domain="games",
                visual_style="dramatic_shadows_carved_wooden_pieces_macro",
                default_music="https://cdn.storyforge.ai/music/pensive_piano.mp3",
                terminology=["grandmaster_gambit", "tactical_sacrifice", "checkmate_sequence"],
                prompt_templates={"script": "Chess grandmaster strategy breakdown of {topic}."},
            ),
        ]

        for pack in built_ins:
            self._packs[pack.name] = pack

    def get_pack(self, pack_name: str) -> ContentPack:
        """Retrieve content pack by name with fallback to 'history'."""
        return self._packs.get(pack_name.lower(), self._packs["history"])

    def list_packs(self) -> List[Dict[str, Any]]:
        """List all available content packs."""
        return [pack.to_dict() for pack in self._packs.values()]
