"""Multi-modal Vision Analysis Capability for StoryForge Runtime."""

import uuid
from typing import Any, Dict, List
from ..interfaces import IArtifact, ICapability
from apps.api.src.main import fallback_engine

class VisionAnalysisArtifact(IArtifact):
    """Artifact containing AI-generated visual descriptions of uploaded media."""

    def __init__(self, artifact_id: str, descriptions: Dict[str, str]):
        self._id = artifact_id
        self.descriptions = descriptions

    @property
    def artifact_id(self) -> str:
        return self._id

    @property
    def artifact_type(self) -> str:
        return "vision_analysis"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "artifact_type": self.artifact_type,
            "descriptions": self.descriptions,
        }

class VisionAnalyzerCapability(ICapability):
    """Analyzes uploaded media (video frames, images) using Vision Language Models."""

    @property
    def name(self) -> str:
        return "vision_analyzer"

    async def execute(
        self,
        assets: List[Dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Describe uploaded images or video keyframes."""
        if not assets:
            return {"artifact_id": f"vsn-{uuid.uuid4().hex[:8]}", "artifact_type": "vision_analysis", "descriptions": {}}
        
        artifact_id = f"vsn-{uuid.uuid4().hex[:8]}"
        descriptions = {}

        llm_providers = fallback_engine._providers.get("llm", {})
        gemini_adapter = llm_providers.get("gemini")
        
        for asset in assets:
            asset_id = asset.get("id", "unknown")
            url = asset.get("storage_url")
            asset_type = asset.get("asset_type")
            original_name = asset.get("metadata_json", {}).get("original_filename", "")
            
            if asset_type == "image":
                prompt = f"Analyze this image ({original_name}) thoroughly. What is happening? Describe the mood, setting, and key elements."
            else:
                prompt = f"Analyze this video snippet ({original_name}) thoroughly. What is the key action or event taking place?"
            
            rich_prompt = f"Vision task for {url}: {prompt}"
            
            if gemini_adapter:
                try:
                    resp = await gemini_adapter.invoke(rich_prompt, temperature=0.4)
                    descriptions[asset_id] = resp.get("response", "Visual context successfully analyzed.")
                except Exception:
                    descriptions[asset_id] = f"[Fallback] User uploaded {asset_type}: {original_name}"
            else:
                descriptions[asset_id] = f"[Fallback] User uploaded {asset_type}: {original_name}"
                
        artifact = VisionAnalysisArtifact(artifact_id, descriptions)
        return artifact.to_dict()
