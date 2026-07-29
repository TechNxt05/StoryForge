"""Qdrant Vector Database Integration."""

import os
from typing import Any


def get_qdrant_url() -> str:
    return os.getenv("QDRANT_URL", "http://localhost:6333")


class QdrantCollections:
    STORY_KNOWLEDGE = "story_knowledge"
    SCRIPT_CHUNKS = "script_chunks"
    CONTENT_PACK_EMBEDDINGS = "content_pack_embeddings"


def get_qdrant_client() -> dict[str, Any]:
    """Qdrant vector collection setup configuration skeleton."""
    return {
        "url": get_qdrant_url(),
        "vector_size": 1536,  # OpenAI / standard embedding dimension
        "distance_metric": "Cosine",
        "collections": [
            QdrantCollections.STORY_KNOWLEDGE,
            QdrantCollections.SCRIPT_CHUNKS,
            QdrantCollections.CONTENT_PACK_EMBEDDINGS,
        ],
    }
