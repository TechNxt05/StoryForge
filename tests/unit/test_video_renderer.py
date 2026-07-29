"""Video Renderer Unit Tests."""

import pytest
from apps.worker.src import FFmpegVideoRenderer, render_story_video_task


def test_ffmpeg_filtergraph_construction() -> None:
    renderer = FFmpegVideoRenderer()
    video_clips = [{"clip_id": "c1"}, {"clip_id": "c2"}]

    filtergraph_916 = renderer.build_filtergraph(video_clips, aspect_ratio="9:16", has_subtitles=True)
    assert "scale=1080:1920" in filtergraph_916
    assert "concat=n=2:v=1:a=0" in filtergraph_916
    assert "subtitles=subtitles.ass" in filtergraph_916

    filtergraph_169 = renderer.build_filtergraph(video_clips, aspect_ratio="16:9", has_subtitles=False)
    assert "scale=1920:1080" in filtergraph_169


@pytest.mark.asyncio
async def test_video_rendering_execution() -> None:
    renderer = FFmpegVideoRenderer()
    timeline_data = {
        "title": "Quantum Story",
        "video_track": [{"clip_id": "v1", "duration_seconds": 5.0}, {"clip_id": "v2", "duration_seconds": 5.0}],
        "total_duration_seconds": 10.0,
    }

    result = await renderer.render_video(timeline_data, aspect_ratio="9:16")

    assert result["project_title"] == "Quantum Story"
    assert result["format"] == "mp4"
    assert result["codec"] == "h264"
    assert result["resolution"] == "1080x1920"
    assert result["duration_seconds"] == 10.0
    assert result["file_size_mb"] == 15.0
    assert result["status"] == "completed"
    assert "cdn.storyforge.ai" in result["output_url"]


@pytest.mark.asyncio
async def test_render_story_video_task() -> None:
    timeline_data = {"title": "AI Documentary", "total_duration_seconds": 20.0}
    result = await render_story_video_task(timeline_data, aspect_ratio="16:9")

    assert result["project_title"] == "AI Documentary"
    assert result["resolution"] == "1920x1080"
