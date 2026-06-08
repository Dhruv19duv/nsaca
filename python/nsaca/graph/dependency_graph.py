"""Dependency graph builder.

Constructs directed acyclic graphs (DAGs) representing software component
dependencies using graph theory and AST analysis.
"""

from __future__ import annotations

import structlog
from dataclasses import dataclass, field
from typing import Any

import networkx as nx


logger = structlog.get_logger()


@dataclass
class GraphNode:
    """A node in the dependency graph."""
    id: str
    name: str
    node_type: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphEdge:
    """A directed edge representing a dependency."""
    source: str
    target: str
    dependency_type: str  # "imports", "calls", "inherits", "uses"
    weight: float = 1.0


class DependencyGraph:
    """Builds and analyzes software dependency graphs.

    Uses NetworkX for graph operations including:
    - Topological sorting for build order
    - Cycle detection for circular dependency warnings
    - Critical path analysis for bottleneck identification
    - Module clustering for architecture decomposition
    """

    def __init__(self) -> None:
        self.graph = nx.DiGraph()
        self.nodes: dict[str, GraphNode] = {}
        logger.info("DependencyGraph initialized")

    def build_from_parsed(self, parsed: dict[str, Any]) -> None:
        """Build dependency graph from parsed problem representation.

        Args:
            parsed: Dict from ProblemParser with components and relations.
        """
        self.graph.clear()
        self.nodes.clear()

        # Add component nodes
        for comp in parsed.get("components", []):
            node = GraphNode(
                id=comp.get("name", ""),
                name=comp.get("name", ""),
                node_type=comp.get("type", "unknown"),
            )
            self.add_node(node)

        # Add dependency edges
        for relation in parsed.get("entity_relations", []):
            if len(relation) == 3:
                src, rel_type, tgt = relation
                self.add_edge(GraphEdge(source=src, target=tgt, dependency_type=rel_type))

        logger.info("Dependency graph built", nodes=len(self.nodes), edges=self.graph.number_of_edges())

    def add_node(self, node: GraphNode) -> None:
        """Add a node to the graph."""
        self.nodes[node.id] = node
        self.graph.add_node(node.id, **{"node_type": node.node_type, "name": node.name})

    def add_edge(self, edge: GraphEdge) -> None:
        """Add a directed edge to the graph."""
        self.graph.add_edge(
            edge.source, edge.target,
            dependency_type=edge.dependency_type,
            weight=edge.weight,
        )

    def topological_sort(self) -> list[str]:
        """Return topological ordering (build order)."""
        try:
            return list(nx.topological_sort(self.graph))
        except nx.NetworkXUnfeasible:
            logger.warning("Cycle detected in dependency graph")
            return list(nx.lexicographical_topological_sort(self.graph))

    def find_cycles(self) -> list[list[str]]:
        """Find all cycles in the dependency graph."""
        return [list(cycle) for cycle in nx.simple_cycles(self.graph)]

    def critical_path(self) -> list[str]:
        """Find the longest path through the dependency graph."""
        if not self.graph:
            return []
        try:
            return list(nx.dag_longest_path(self.graph))
        except nx.NetworkXError:
            return []

    def strongly_connected_components(self) -> list[set[str]]:
        """Find strongly connected components (potential modules)."""
        return list(nx.strongly_connected_components(self.graph))

    def get_stats(self) -> dict[str, Any]:
        """Get graph statistics."""
        return {
            "nodes": self.graph.number_of_nodes(),
            "edges": self.graph.number_of_edges(),
            "density": nx.density(self.graph),
            "is_dag": nx.is_directed_acyclic_graph(self.graph),
            "num_cycles": len(self.find_cycles()),
            "max_depth": len(self.critical_path()),
        }
