"""Vector database memory for architecture retrieval.

Stores and retrieves previously solved architectures using vector
similarity search for transfer learning across problems.
"""

from __future__ import annotations

import hashlib
import structlog
from dataclasses import dataclass, field
from typing import Any


logger = structlog.get_logger()


@dataclass
class MemoryEntry:
    """A stored architecture memory."""
    id: str
    problem: str
    architecture: dict[str, Any]
    embedding: list[float] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class VectorStore:
    """In-memory vector store for architecture similarity search.

    Uses ChromaDB when available, falls back to in-memory cosine similarity.
    Stores previously solved architecture problems and their solutions
    for transfer learning.
    """

    def __init__(self, dimension: int = 1536) -> None:
        self.dimension = dimension
        self.entries: list[MemoryEntry] = []
        self._index: dict[str, MemoryEntry] = {}
        logger.info("VectorStore initialized", dimension=dimension)

    def store(self, problem: str, architecture: dict[str, Any]) -> str:
        """Store a problem-architecture pair.

        Args:
            problem: The original problem description.
            architecture: The solved architecture.

        Returns:
            ID of the stored entry.
        """
        entry_id = hashlib.sha256(problem.encode()).hexdigest()[:16]
        embedding = self._embed(problem)

        entry = MemoryEntry(
            id=entry_id,
            problem=problem,
            architecture=architecture,
            embedding=embedding,
        )

        self.entries.append(entry)
        self._index[entry_id] = entry

        logger.info("Stored architecture", id=entry_id, problem_length=len(problem))
        return entry_id

    def find_similar(self, problem: str, top_k: int = 5) -> list[MemoryEntry]:
        """Find similar past solutions using cosine similarity.

        Args:
            problem: Query problem description.
            top_k: Number of results to return.

        Returns:
            List of most similar MemoryEntry objects.
        """
        if not self.entries:
            return []

        query_embedding = self._embed(problem)
        scored = []

        for entry in self.entries:
            sim = self._cosine_similarity(query_embedding, entry.embedding)
            scored.append((sim, entry))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = [entry for _, entry in scored[:top_k]]

        logger.info("Similar search", query_length=len(problem), results=len(results))
        return results

    def get(self, entry_id: str) -> MemoryEntry | None:
        """Retrieve a specific memory by ID."""
        return self._index.get(entry_id)

    def delete(self, entry_id: str) -> bool:
        """Delete a memory entry."""
        if entry_id in self._index:
            del self._index[entry_id]
            self.entries = [e for e in self.entries if e.id != entry_id]
            return True
        return False

    def size(self) -> int:
        """Number of stored entries."""
        return len(self.entries)

    def _embed(self, text: str) -> list[float]:
        """Generate a simple embedding for text.

        Uses a hash-based pseudo-embedding for demo purposes.
        Replace with actual sentence-transformers embedding in production.
        """
        import random
        rng = random.Random(hashlib.sha256(text.encode()).digest())
        raw = [rng.random() for _ in range(self.dimension)]
        norm = sum(x * x for x in raw) ** 0.5
        return [x / norm for x in raw] if norm > 0 else raw

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)
