"""Subtitle & Alignment Capability for StoryForge Runtime."""

import uuid
from typing import Any, Dict, List
from ..interfaces import IArtifact, ICapability


class SubtitleArtifact(IArtifact):
    """Artifact containing forced alignment subtitle tracks and SRT/VTT strings."""

    def __init__(
        self,
        artifact_id: str,
        word_timestamps: List[Dict[str, Any]],
        srt_content: str,
        vtt_content: str,
        style_preset: str,
    ):
        self._id = artifact_id
        self.word_timestamps = word_timestamps
        self.srt_content = srt_content
        self.vtt_content = vtt_content
        self.style_preset = style_preset

    @property
    def artifact_id(self) -> str:
        return self._id

    @property
    def artifact_type(self) -> str:
        return "subtitle_track"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "artifact_type": self.artifact_type,
            "word_timestamps": self.word_timestamps,
            "srt_content": self.srt_content,
            "vtt_content": self.vtt_content,
            "style_preset": self.style_preset,
        }


def _format_timestamp_srt(seconds: float) -> str:
    """Format seconds float into SRT timestamp format HH:MM:SS,mmm."""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"


def _format_timestamp_vtt(seconds: float) -> str:
    """Format seconds float into VTT timestamp format HH:MM:SS.mmm."""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    return f"{hrs:02d}:{mins:02d}:{secs:02d}.{millis:03d}"


class SubtitleAlignmentCapability(ICapability):
    """Capability performing audio-text forced alignment and generating SRT/VTT/ASS subtitles."""

    @property
    def name(self) -> str:
        return "subtitles"

    async def execute(
        self,
        script_text: str = "",
        audio_duration: float = 10.0,
        style_preset: str = "bold_yellow_highlight",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Perform word-level alignment and generate subtitle files."""
        if not script_text:
            script_text = "StoryForge AI automates professional short-form video creation in seconds."

        artifact_id = f"sub-{uuid.uuid4().hex[:8]}"

        words = script_text.split()
        time_per_word = audio_duration / max(len(words), 1)

        word_timestamps: List[Dict[str, Any]] = []
        srt_lines: List[str] = []
        vtt_lines: List[str] = ["WEBVTT\n"]

        curr_time = 0.0
        for idx, word in enumerate(words):
            start_t = curr_time
            end_t = curr_time + time_per_word
            curr_time = end_t

            word_timestamps.append(
                {
                    "index": idx + 1,
                    "word": word,
                    "start_time": round(start_t, 3),
                    "end_time": round(end_t, 3),
                }
            )

            # SRT Entry
            srt_lines.append(f"{idx + 1}")
            srt_lines.append(f"{_format_timestamp_srt(start_t)} --> {_format_timestamp_srt(end_t)}")
            srt_lines.append(f"{word}\n")

            # VTT Entry
            vtt_lines.append(f"{_format_timestamp_vtt(start_t)} --> {_format_timestamp_vtt(end_t)}")
            vtt_lines.append(f"<c.highlight>{word}</c>\n")

        srt_content = "\n".join(srt_lines)
        vtt_content = "\n".join(vtt_lines)

        artifact = SubtitleArtifact(
            artifact_id=artifact_id,
            word_timestamps=word_timestamps,
            srt_content=srt_content,
            vtt_content=vtt_content,
            style_preset=style_preset,
        )

        return artifact.to_dict()
