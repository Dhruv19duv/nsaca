"""Transfer learning engine.

Leverages knowledge from previously solved problems to accelerate
solving of new, similar problems.
"""

from __future__ import annotations

import structlog
from dataclasses import dataclass, field
from typing import Any


logger = structlog.get_logger()


@dataclass
class TransferCandidate:
    """A candidate solution from transfer learning."""
    source_problem: str
    similarity: float
    adapted_architecture: dict[str, Any]
    confidence: float


class TransferLearner:
    """Transfer learning engine for architecture reuse.

    Identifies similar past problems and adapts their solutions
    for new problems, reducing computation and improving quality.
    """

    def __init__(self, similarity_threshold: float = 0.7) -> None:
        self.similarity_threshold = similarity_threshold
        logger.info("TransferLearner initialized", threshold=similarity_threshold)

    def find_transfer_candidates(
        self,
        current_problem: str,
        similar_entries: list[Any],
    ) -> list[TransferCandidate]:
        """Find transferable solutions from similar past problems.

        Args:
            current_problem: The current problem description.
            similar_entries: Similar entries from vector store.

        Returns:
            List of adapted transfer candidates.
        """
        candidates = []
        for entry in similar_entries:
            embedding = getattr(entry, "embedding", [])
            similarity = getattr(entry, "metadata", {}).get("similarity", 0.5)

            if similarity >= self.similarity_threshold:
                adapted = self._adapt_architecture(
                    entry.architecture, current_problem
                )
                candidates.append(TransferCandidate(
                    source_problem=entry.problem[:100],
                    similarity=similarity,
                    adapted_architecture=adapted,
                    confidence=similarity * 0.9,
                ))

        logger.info("Transfer candidates found", count=len(candidates))
        return candidates

    def _adapt_architecture(
        self,
        architecture: dict[str, Any],
        new_problem: str,
    ) -> dict[str, Any]:
        """Adapt an existing architecture for a new problem."""
        adapted = dict(architecture)
        adapted["transferred_from"] = architecture.get("name", "unknown")
        adapted["adaptations"] = ["problem-specific tuning needed"]
        return adapted
