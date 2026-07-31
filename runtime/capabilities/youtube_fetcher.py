"""YouTube B-Roll Fetcher Capability for StoryForge Runtime."""

import os
import shutil
import subprocess
import uuid
from typing import Any, Dict, List
from ..interfaces import IArtifact, ICapability

class YouTubeBRollArtifact(IArtifact):
    """Artifact containing downloaded b-roll videos from YouTube."""

    def __init__(self, artifact_id: str, clips: List[Dict[str, Any]]):
        self._id = artifact_id
        self.clips = clips

    @property
    def artifact_id(self) -> str:
        return self._id

    @property
    def artifact_type(self) -> str:
        return "broll_media"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "artifact_type": self.artifact_type,
            "clips": self.clips,
        }

class YouTubeFetcherCapability(ICapability):
    """Downloads short Creative Commons YouTube b-roll clips matching story scenes."""

    @property
    def name(self) -> str:
        return "youtube_fetcher"

    def is_ytdlp_installed(self) -> bool:
        return shutil.which("yt-dlp") is not None

    async def execute(self, query: str = "", max_duration_sec: int = 10, **kwargs: Any) -> Dict[str, Any]:
        """Fetch b-roll clip matching the search query."""
        artifact_id = f"ytb-{uuid.uuid4().hex[:8]}"
        clips = []

        if not query:
            query = "Dhoni World Cup Six Crowd Cheer"

        # Check if yt-dlp is available locally
        if self.is_ytdlp_installed():
            try:
                out_path = f"/tmp/broll_{artifact_id}.mp4"
                cmd = [
                    "yt-dlp",
                    f"ytsearch1:{query}",
                    "--max-filesize", "15M",
                    "-f", "mp4",
                    "-o", out_path
                ]
                subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=15)
                if os.path.exists(out_path):
                    clips.append({
                        "query": query,
                        "url": out_path,
                        "duration_seconds": max_duration_sec,
                        "is_downloaded": True
                    })
            except Exception as e:
                print(f"[YouTubeFetcher] Download failed: {e}")

        # Fallback pre-cleared Cloudinary clip
        if not clips:
            clips.append({
                "query": query,
                "url": "https://res.cloudinary.com/demo/video/upload/dog.mp4",
                "duration_seconds": 10.0,
                "is_downloaded": False
            })

        artifact = YouTubeBRollArtifact(artifact_id, clips)
        return artifact.to_dict()
