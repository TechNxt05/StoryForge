"""Capabilities sub-package for StoryForge Runtime."""

from .research import DeepResearchCapability, ResearchArtifact
from .fact_checker import FactVerificationCapability, VerificationArtifact
from .story_structure import StoryStructureCapability, StoryOutlineArtifact
from .scriptwriter import ScriptwriterCapability, ScriptArtifact
from .storyboard import StoryboardGeneratorCapability, StoryboardArtifact
from .asset_planner import MediaAssetPlannerCapability, AssetPlanArtifact
from .image_generator import ImageGenerationPipelineCapability, ImageAssetsArtifact
from .video_generator import VideoGenerationPipelineCapability, VideoAssetsArtifact
from .voice_synthesizer import VoiceSynthesizerCapability, VoiceoverArtifact
from .subtitles import SubtitleAlignmentCapability, SubtitleArtifact
from .timeline import TimelineEngineCapability, TimelineArtifact
from .reviewer import QualityReviewerCapability, ReviewReportArtifact
from .revision import StoryRevisionCapability, RevisionArtifact
from .exporter import MultiPlatformExporterCapability, ExportAssetsArtifact
from .asset_manager import CloudinaryAssetManagerCapability, CDNAssetArtifact
from .vision_analyzer import VisionAnalyzerCapability, VisionAnalysisArtifact
from ..registry.store import CapabilityRegistry

# Register capabilities in CapabilityRegistry
_research_cap = DeepResearchCapability()
_fact_cap = FactVerificationCapability()
_structure_cap = StoryStructureCapability()
_script_cap = ScriptwriterCapability()
_storyboard_cap = StoryboardGeneratorCapability()
_asset_planner_cap = MediaAssetPlannerCapability()
_image_gen_cap = ImageGenerationPipelineCapability()
_video_gen_cap = VideoGenerationPipelineCapability()
_voice_synth_cap = VoiceSynthesizerCapability()
_subtitle_cap = SubtitleAlignmentCapability()
_timeline_cap = TimelineEngineCapability()
_reviewer_cap = QualityReviewerCapability()
_revision_cap = StoryRevisionCapability()
_exporter_cap = MultiPlatformExporterCapability()
_cdn_asset_mgr_cap = CloudinaryAssetManagerCapability()
_vision_analyzer_cap = VisionAnalyzerCapability()

CapabilityRegistry.register_capability(_research_cap.name, _research_cap)
CapabilityRegistry.register_capability(_fact_cap.name, _fact_cap)
CapabilityRegistry.register_capability(_structure_cap.name, _structure_cap)
CapabilityRegistry.register_capability(_script_cap.name, _script_cap)
CapabilityRegistry.register_capability(_storyboard_cap.name, _storyboard_cap)
CapabilityRegistry.register_capability(_asset_planner_cap.name, _asset_planner_cap)
CapabilityRegistry.register_capability(_image_gen_cap.name, _image_gen_cap)
CapabilityRegistry.register_capability(_video_gen_cap.name, _video_gen_cap)
CapabilityRegistry.register_capability(_voice_synth_cap.name, _voice_synth_cap)
CapabilityRegistry.register_capability(_subtitle_cap.name, _subtitle_cap)
CapabilityRegistry.register_capability(_timeline_cap.name, _timeline_cap)
CapabilityRegistry.register_capability(_reviewer_cap.name, _reviewer_cap)
CapabilityRegistry.register_capability(_revision_cap.name, _revision_cap)
CapabilityRegistry.register_capability(_exporter_cap.name, _exporter_cap)
CapabilityRegistry.register_capability(_cdn_asset_mgr_cap.name, _cdn_asset_mgr_cap)
CapabilityRegistry.register_capability(_vision_analyzer_cap.name, _vision_analyzer_cap)

__all__ = [
    "DeepResearchCapability",
    "ResearchArtifact",
    "FactVerificationCapability",
    "VerificationArtifact",
    "StoryStructureCapability",
    "StoryOutlineArtifact",
    "ScriptwriterCapability",
    "ScriptArtifact",
    "StoryboardGeneratorCapability",
    "StoryboardArtifact",
    "MediaAssetPlannerCapability",
    "AssetPlanArtifact",
    "ImageGenerationPipelineCapability",
    "ImageAssetsArtifact",
    "VideoGenerationPipelineCapability",
    "VideoAssetsArtifact",
    "VoiceSynthesizerCapability",
    "VoiceoverArtifact",
    "SubtitleAlignmentCapability",
    "SubtitleArtifact",
    "TimelineEngineCapability",
    "TimelineArtifact",
    "QualityReviewerCapability",
    "ReviewReportArtifact",
    "StoryRevisionCapability",
    "RevisionArtifact",
    "MultiPlatformExporterCapability",
    "ExportAssetsArtifact",
    "CloudinaryAssetManagerCapability",
    "CDNAssetArtifact",
    "VisionAnalyzerCapability",
    "VisionAnalysisArtifact",
]
