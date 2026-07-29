"""Vector RAG Engine Unit Tests."""

import pytest
from runtime.memory import VectorRAGMemoryStore


@pytest.mark.asyncio
async def test_vector_rag_kv_operations() -> None:
    store = VectorRAGMemoryStore()
    await store.store("key1", {"topic": "quantum", "facts_count": 5})

    retrieved = await store.retrieve("key1")
    assert retrieved is not None
    assert retrieved["topic"] == "quantum"


@pytest.mark.asyncio
async def test_vector_rag_similarity_search() -> None:
    store = VectorRAGMemoryStore()

    await store.index_document("Johannes Gutenberg invented movable type printing in Mainz Germany.", {"category": "history"})
    await store.index_document("Quantum computers utilize qubits in superposition and entanglement states.", {"category": "tech"})
    await store.index_document("Apollo 11 landed humans on the Moon in July 1969.", {"category": "space"})

    results = await store.similarity_search("Gutenberg printing press history", limit=2)

    assert len(results) == 2
    assert "Gutenberg" in results[0]["text"]
    assert results[0]["score"] > 0
