"""Algorithm and data structure selector.

Dynamically chooses optimal algorithms and data structures based on
problem requirements, input characteristics, and complexity analysis.
"""

from __future__ import annotations

import structlog
from dataclasses import dataclass, field
from typing import Any


logger = structlog.get_logger()


@dataclass
class SelectionCriteria:
    """Criteria for algorithm selection."""
    input_size: int
    time_budget_ms: float | None = None
    memory_budget_bytes: int | None = None
    needs_sorted: bool = False
    needs_range_queries: bool = False
    needs_prefix_search: bool = False
    has_negative_weights: bool = False
    is_streaming: bool = False
    data_type: str = "integer"


@dataclass
class SelectedAlgorithm:
    """A selected algorithm or data structure."""
    name: str
    category: str  # "data_structure" or "algorithm"
    complexity: str
    reasoning: str
    alternatives: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class AlgorithmSelector:
    """Selects optimal algorithms and data structures.

    Uses a rule-based system informed by:
    - Input size and characteristics
    - Time/space complexity analysis
    - Problem domain requirements
    - Knowledge graph relationships
    """

    def __init__(self) -> None:
        self._build_rules()
        logger.info("AlgorithmSelector initialized")

    def _build_rules(self) -> None:
        """Build selection rules."""
        self.ds_rules = [
            {
                "condition": lambda c: c.needs_range_queries and c.input_size > 1000,
                "selection": "segment_tree",
                "reason": "Range queries on large dataset require segment tree (O(log n) query/update)",
            },
            {
                "condition": lambda c: c.needs_prefix_search,
                "selection": "trie",
                "reason": "Prefix search is O(k) with trie vs O(n log n) with sorting",
            },
            {
                "condition": lambda c: c.input_size > 1_000_000 and c.is_streaming,
                "selection": "bloom_filter",
                "reason": "Membership testing on large streaming data needs space-efficient probabilistic structure",
            },
            {
                "condition": lambda c: c.needs_sorted and c.input_size > 100_000,
                "selection": "suffix_array",
                "reason": "Sorted text data benefits from suffix array for string operations",
            },
            {
                "condition": lambda c: c.data_type == "string" and c.needs_prefix_search,
                "selection": "trie",
                "reason": "String prefix operations are optimal with trie",
            },
            {
                "condition": lambda c: c.input_size < 100,
                "selection": "simple_array",
                "reason": "Small input sizes don't benefit from complex data structures",
            },
        ]

        self.algo_rules = [
            {
                "condition": lambda c: c.input_size > 100_000 and c.has_negative_weights,
                "selection": "bellman_ford",
                "reason": "Negative weights require Bellman-Ford (O(VE))",
            },
            {
                "condition": lambda c: c.input_size > 100_000 and not c.has_negative_weights,
                "selection": "dijkstra",
                "reason": "Non-negative weights: Dijkstra with heap (O((V+E) log V))",
            },
            {
                "condition": lambda c: c.needs_sorted and c.input_size < 100_000,
                "selection": "binary_search",
                "reason": "Sorted data enables O(log n) search",
            },
        ]

    def select_for_problem(self, parsed: dict[str, Any]) -> list[SelectedAlgorithm]:
        """Select algorithms and data structures for a parsed problem.

        Args:
            parsed: Parsed problem representation.

        Returns:
            List of recommended algorithms/data structures.
        """
        criteria = self._extract_criteria(parsed)
        selections = []

        for rule in self.ds_rules:
            if rule["condition"](criteria):
                selections.append(SelectedAlgorithm(
                    name=rule["selection"],
                    category="data_structure",
                    complexity="varies",
                    reasoning=rule["reason"],
                ))

        for rule in self.algo_rules:
            if rule["condition"](criteria):
                selections.append(SelectedAlgorithm(
                    name=rule["selection"],
                    category="algorithm",
                    complexity="varies",
                    reasoning=rule["reason"],
                ))

        if not selections:
            selections.append(SelectedAlgorithm(
                name="hash_map",
                category="data_structure",
                complexity="O(1) average",
                reasoning="Default choice: hash map provides O(1) average-case performance",
            ))

        logger.info("Selections made", count=len(selections))
        return selections

    def _extract_criteria(self, parsed: dict[str, Any]) -> SelectionCriteria:
        """Extract selection criteria from parsed problem."""
        components = parsed.get("components", [])
        input_size = parsed.get("input_size", 1000)
        constraints = parsed.get("constraints", [])

        needs_range = any("range" in str(c).lower() for c in constraints)
        needs_prefix = any("prefix" in str(c).lower() or "autocomplete" in str(c).lower() for c in constraints)
        negative = any("negative" in str(c).lower() for c in constraints)
        streaming = any("stream" in str(c).lower() for c in constraints)

        return SelectionCriteria(
            input_size=input_size,
            needs_range_queries=needs_range,
            needs_prefix_search=needs_prefix,
            has_negative_weights=negative,
            is_streaming=streaming,
        )

    def select_for_requirements(self, requirements: list[str]) -> list[SelectedAlgorithm]:
        """Quick selection based on plain text requirements."""
        parsed = {"components": [], "constraints": requirements, "input_size": 10000}
        return self.select_for_problem(parsed)
