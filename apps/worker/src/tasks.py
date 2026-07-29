"""Celery Tasks for Background Video Rendering & Processing."""

from typing import Any, Dict
from .renderer import FFmpegVideoRenderer

renderer = FFmpegVideoRenderer()


async def render_story_video_task(timeline_data: Dict[str, Any], aspect_ratio: str = "9:16") -> Dict[str, Any]:
    """Background task to render story video from timeline specifications."""
    return await renderer.render_video(timeline_data, aspect_ratio=aspect_ratio)
