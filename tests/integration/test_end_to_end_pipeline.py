"""Comprehensive End-to-End Pipeline Integration Test Suite."""

import pytest
import runtime.capabilities  # Auto-registers capabilities in CapabilityRegistry
from runtime import CapabilityRegistry
from apps.worker.src import FFmpegVideoRenderer


@pytest.mark.asyncio
async def test_full_storyforge_e2e_pipeline() -> None:
    topic = "The Invention of Printing Press"
    content_pack = "history"
    aspect_ratio = "9:16"

    # Step 1: Deep Research
    research_cap = CapabilityRegistry.get_capability("deep_research")
    research_res = await research_cap.execute(topic=topic, content_pack=content_pack)
    assert research_res["artifact_type"] == "research_data"
    assert len(research_res["facts"]) >= 3

    # Step 2: Fact Verification
    fact_cap = CapabilityRegistry.get_capability("fact_verification")
    fact_res = await fact_cap.execute(claims=research_res["facts"])
    assert fact_res["artifact_type"] == "verification_report"
    assert fact_res["overall_confidence_score"] > 0.8

    # Step 3: Story Structure Planning
    structure_cap = CapabilityRegistry.get_capability("story_structure_planner")
    outline_res = await structure_cap.execute(topic=topic, target_duration=60)
    assert outline_res["artifact_type"] == "story_outline"
    assert len(outline_res["acts"]) == 5

    # Step 4: Scriptwriting
    script_cap = CapabilityRegistry.get_capability("scriptwriter")
    script_res = await script_cap.execute(title=topic, outline=outline_res)
    assert script_res["artifact_type"] == "script_text"
    assert len(script_res["scenes"]) >= 4

    # Step 5: Storyboard Generation
    storyboard_cap = CapabilityRegistry.get_capability("storyboard_generator")
    storyboard_res = await storyboard_cap.execute(script_data=script_res, aspect_ratio=aspect_ratio)
    assert storyboard_res["artifact_type"] == "storyboard_spec"
    assert len(storyboard_res["frames"]) >= 4

    # Step 6: Asset Planning
    asset_planner_cap = CapabilityRegistry.get_capability("asset_planner")
    asset_plan_res = await asset_planner_cap.execute(storyboard_data=storyboard_res, script_data=script_res)
    assert asset_plan_res["artifact_type"] == "asset_plan"
    assert len(asset_plan_res["image_jobs"]) >= 4

    # Step 7: Image Generation Pipeline
    image_gen_cap = CapabilityRegistry.get_capability("image_generator")
    image_res = await image_gen_cap.execute(image_jobs=asset_plan_res["image_jobs"], provider="flux", aspect_ratio=aspect_ratio)
    assert image_res["artifact_type"] == "image_assets"

    # Step 8: Video Generation Pipeline
    video_gen_cap = CapabilityRegistry.get_capability("video_generator")
    video_res = await video_gen_cap.execute(video_jobs=asset_plan_res["video_jobs"], provider="veo", aspect_ratio=aspect_ratio)
    assert video_res["artifact_type"] == "video_assets"

    # Step 9: Voice Synthesis
    voice_cap = CapabilityRegistry.get_capability("voice_synthesizer")
    voice_res = await voice_cap.execute(audio_jobs=asset_plan_res["audio_jobs"], provider="kokoro")
    assert voice_res["artifact_type"] == "voiceover_audio"

    # Step 10: Subtitle Alignment
    subtitle_cap = CapabilityRegistry.get_capability("subtitles")
    sub_res = await subtitle_cap.execute(script_text=script_res["scenes"][0]["narration_text"], audio_duration=6.0)
    assert sub_res["artifact_type"] == "subtitle_track"

    # Step 11: Multi-Track Timeline Composition
    timeline_cap = CapabilityRegistry.get_capability("timeline_engine")
    timeline_res = await timeline_cap.execute(
        video_assets=video_res["video_clips"],
        audio_assets=voice_res["audio_clips"],
        subtitle_assets=sub_res,
        title=topic,
    )
    assert timeline_res["artifact_type"] == "project_timeline"
    assert timeline_res["is_valid"] is True

    # Step 12: FFmpeg Video Render
    renderer = FFmpegVideoRenderer()
    render_res = await renderer.render_video(timeline_res, aspect_ratio=aspect_ratio)
    assert render_res["status"] == "completed"
    assert "cdn.storyforge.ai" in render_res["output_url"]

    # Step 13: Multi-Platform Export
    exporter_cap = CapabilityRegistry.get_capability("media_exporter")
    export_res = await exporter_cap.execute(render_data=render_res, title=topic)
    assert export_res["artifact_type"] == "platform_export_package"
    assert export_res["total_platforms_exported"] == 4
