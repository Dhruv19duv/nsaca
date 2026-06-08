"""Graph-based memory for architecture pattern storage.

Stores relationships between solved problems, architectures, and their
components in a graph structure for pattern-based retrieval.
"""

from __future__ import annotations

import structlog
from dataclasses import dataclass, field
from typing import Any

import networkx as nx


logger = structlog.get_logger()


@dataclass
class MemoryPattern:
    """A stored architectural pattern."""
    name: str
    pattern_type: str  # "architecture", "algorithm", "optimization"
    graph_data: dict[str, Any]
    success_count: int = 0
    failure_count: int = 0

    @property
    def success_rate(self) -> float:
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.0


class GraphMemory:
    """Graph-based memory for storing and retrieving architecture patterns.

    Uses NetworkX to maintain a knowledge graph of:
    - Problem types and their solutions
    - Component relationships in successful architectures
    - Algorithm effectiveness patterns
    - Optimization outcomes
    """

    def __init__(self) -> None:
        self.graph = nx.DiGraph()
        self.patterns: dict[str, MemoryPattern] = {}
        logger.info("GraphMemory initialized")

    def store(self, parsed: dict[str, Any], architecture: dict[str, Any]) -> None:
        """Store a parsed problem and its architecture in graph memory.

        Args:
            parsed: Parsed problem representation.
            architecture: The resulting architecture.
        """
        problem_node = f"problem_{len(self.graph.nodes)}"
        arch_node = f"arch_{len(self.graph.nodes)}"

        self.graph.add_node(problem_node, type="problem", data=parsed)
        self.graph.add_node(arch_node, type="architecture", data=architecture)
        self.graph.add_edge(problem_node, arch_node, relationship="solved_by")

        # Store component relationships
        for comp in architecture.get("components", []):
            comp_name = comp.get("name", f"comp_{len(self.graph.nodes)}")
            self.graph.add_node(comp_name, type="component", data=comp)
            self.graph.add_edge(arch_node, comp_name, relationship="contains")

        logger.info("Pattern stored in graph memory", problem=problem_node, arch=arch_node)

    def find_patterns(self, pattern_type: str = "architecture") -> list[dict[str, Any]]:
        """Find stored patterns by type."""
        patterns = []
        for node, data in self.graph.nodes(data=True):
            if data.get("type") == pattern_type:
                patterns.append(data.get("data", {}))
        return patterns

    def get_related(self, node_name: str, max_hops: int = 2) -> list[str]:
        """Get related nodes within max_hops."""
        if node_name not in self.graph:
            return []
        related = set()
        current = {node_name}
        for _ in range(max_hops):
            next_level = set()
            for n in current:
                next_level.update(self.graph.successors(n))
                next_level.update(self.graph.predecessors(n))
            related.update(next_level - current - {node_name})
            current = next_level
        return sorted(related)

    def get_stats(self) -> dict[str, Any]:
        """Get memory statistics."""
        node_types = {}
        for _, data in self.graph.nodes(data=True):
            t = data.get("type", "unknown")
            node_types[t] = node_types.get(t, 0) + 1
        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "node_types": node_types,
        }
