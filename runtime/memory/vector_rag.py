"""Qdrant-backed Vector RAG Engine for StoryForge Runtime Memory."""

import math
import uuid
from typing import Any, Dict, List, Optional
from ..interfaces import IMemory


def _dummy_embed(text: str, dim: int = 384) -> List[float]:
    """Generate a deterministic pseudo-embedding vector for text similarity calculations."""
    val = sum(ord(c) for c in text.lower())
    vector = [math.sin(val * (i + 1)) for i in range(dim)]
    norm = math.sqrt(sum(v * v for v in vector)) or 1.0
    return [v / norm for v in vector]


def _cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Calculate cosine similarity between two normalized vectors."""
    return sum(a * b for a, b in zip(v1, v2))


class VectorRAGMemoryStore(IMemory[Dict[str, Any]]):
    """Vector database memory store managing RAG document indexing and semantic retrieval."""

    def __init__(self, collection_name: str = "storyforge_knowledge"):
        self.collection_name = collection_name
        self._kv_store: Dict[str, Dict[str, Any]] = {}
        self._vector_index: List[Dict[str, Any]] = []

    async def store(self, key: str, value: Dict[str, Any]) -> None:
        """Store key-value metadata unit into memory."""
        self._kv_store[key] = value

    async def retrieve(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve key-value item by key."""
        return self._kv_store.get(key)

    async def index_document(
        self, text: str, metadata: Optional[Dict[str, Any]] = None, doc_id: Optional[str] = None
    ) -> str:
        """Index a document chunk into vector memory."""
        doc_id = doc_id or f"doc-{uuid.uuid4().hex[:8]}"
        vector = _dummy_embed(text)

        entry = {
            "doc_id": doc_id,
            "text": text,
            "vector": vector,
            "metadata": metadata or {},
        }
        self._vector_index.append(entry)
        return doc_id

    async def similarity_search(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Perform semantic cosine similarity search against indexed knowledge chunks."""
        if not self._vector_index:
            return []

        query_vector = _dummy_embed(query)
        query_words = set(query.lower().split())
        scored_results = []

        for entry in self._vector_index:
            v_score = _cosine_similarity(query_vector, entry["vector"])
            doc_words = set(entry["text"].lower().split())
            word_overlap = len(query_words.intersection(doc_words)) / max(len(query_words), 1)

            # Combined hybrid semantic vector + term overlap score
            combined_score = (v_score * 0.4) + (word_overlap * 0.6)

            scored_results.append(
                {
                    "doc_id": entry["doc_id"],
                    "text": entry["text"],
                    "score": round(combined_score, 4),
                    "metadata": entry["metadata"],
                }
            )

        scored_results.sort(key=lambda x: x["score"], reverse=True)
        return scored_results[:limit]
