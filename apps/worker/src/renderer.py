"""FFmpeg filtergraph planner for StoryForge Worker.

The production renderer (Ken Burns scenes, narration, burned-in captions) lives in
runtime/pipeline.py and is what the API uses. This module only builds filtergraphs
for timeline-based compositions and does not encode video itself.
"""

import os
import random
import shutil
import tempfile
import uuid
from typing import Any, Dict, List


class FFmpegVideoRenderer:
    """Renders final H.264/AAC MP4 videos by compositing video clips, audio tracks, and subtitle overlays."""

    def __init__(self, output_dir: str = os.path.join(tempfile.gettempdir(), "storyforge_renders")):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def is_ffmpeg_installed(self) -> bool:
        """Check if ffmpeg CLI binary is installed on system PATH."""
        return shutil.which("ffmpeg") is not None

    def build_filtergraph(
        self,
        video_clips: List[Dict[str, Any]],
        aspect_ratio: str = "9:16",
        has_subtitles: bool = True,
        project_title: str = "",
    ) -> str:
        """Construct FFmpeg filtergraph string for video concatenation and subtitle overlay."""
        width = 1080 if aspect_ratio == "9:16" else 1920
        height = 1920 if aspect_ratio == "9:16" else 1080

        filter_parts: List[str] = []

        # Scale & pad inputs to target resolution and apply brightness/contrast
        for idx, clip in enumerate(video_clips):
            filters = clip.get("filters", {})
            brightness = filters.get("brightness", 0)
            contrast = filters.get("contrast", 1)
            
            filter_parts.append(
                f"[{idx}:v]scale={width}:{height}:force_original_aspect_ratio=decrease,"
                f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,"
                f"eq=brightness={brightness}:contrast={contrast}[v{idx}];"
            )

        # Concat video streams
        concat_inputs = "".join(f"[v{i}]" for i in range(len(video_clips)))
        filter_parts.append(f"{concat_inputs}concat=n={len(video_clips)}:v=1:a=0[vconcat];")

        if has_subtitles:
            filter_parts.append("[vconcat]subtitles=subtitles.ass:force_style='FontSize=24,PrimaryColour=&H00FFFF&'[vfinal]")
        elif project_title:
            title_text = project_title.replace("'", "").replace(":", "")
            filter_parts.append(
                f"[vconcat]drawtext=text='{title_text}':fontcolor=white:fontsize=42:"
                f"box=1:boxcolor=black@0.6:boxborderw=10:x=(w-text_w)/2:y=h-150[vfinal]"
            )
        else:
            filter_parts.append("[vconcat]copy[vfinal]")

        return "".join(filter_parts)

    async def render_video(
        self,
        timeline_data: Dict[str, Any],
        aspect_ratio: str = "9:16",
        export_quality: str = "1080p",
    ) -> Dict[str, Any]:
        """Plan a render for a multi-track timeline (returns the filtergraph; does not encode)."""
        project_title = timeline_data.get("title", "Story Project")
        video_clips = timeline_data.get("video_track", [])
        total_duration = timeline_data.get("total_duration_seconds", 15.0)

        render_id = f"rnd-{uuid.uuid4().hex[:8]}"
        seed = random.randint(100000, 999999)

        filtergraph = self.build_filtergraph(video_clips, aspect_ratio=aspect_ratio, project_title=project_title)
        has_ffmpeg = self.is_ffmpeg_installed()

        output_filename = f"{render_id}_{seed}.mp4"
        output_file_path = os.path.join(self.output_dir, output_filename)

        file_size_mb = round(total_duration * 1.5, 2)  # ~1.5 MB/s for 1080p video

        return {
            "render_id": render_id,
            "project_title": project_title,
            "output_url": None,
            "output_file_path": output_file_path,
            "ffmpeg_installed": has_ffmpeg,
            "format": "mp4",
            "codec": "h264",
            "audio_codec": "aac",
            "aspect_ratio": aspect_ratio,
            "resolution": "1080x1920" if aspect_ratio == "9:16" else "1920x1080",
            "duration_seconds": total_duration,
            "file_size_mb": file_size_mb,
            "filtergraph": filtergraph,
            "status": "planned",
        }
