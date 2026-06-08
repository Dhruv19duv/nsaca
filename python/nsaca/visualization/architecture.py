"""Architecture visualization engine.

Generates interactive diagrams and visual representations of software
architectures for human review and feedback.
"""

from __future__ import annotations

import structlog
from dataclasses import dataclass, field
from typing import Any


logger = structlog.get_logger()


@dataclass
class DiagramNode:
    """A node in an architecture diagram."""
    id: str
    label: str
    node_type: str  # service, database, cache, queue, etc.
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DiagramEdge:
    """An edge in an architecture diagram."""
    source: str
    target: str
    label: str
    edge_type: str = "data_flow"  # data_flow, control_flow, dependency


@dataclass
class ArchitectureDiagram:
    """A complete architecture diagram."""
    title: str
    nodes: list[DiagramNode]
    edges: list[DiagramEdge]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_mermaid(self) -> str:
        """Export diagram as Mermaid syntax."""
        lines = [f"graph TD"]
        for node in self.nodes:
            shape = {"service": "[]", "database": "{/}", "cache": "([])"}.get(node.node_type, "[]")
            lines.append(f"    {node.id}{shape[0]}{node.label}{shape[1]}")
        for edge in self.edges:
            lines.append(f"    {edge.source} -->|{edge.label}| {edge.target}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Export diagram as dictionary."""
        return {
            "title": self.title,
            "nodes": [{"id": n.id, "label": n.label, "type": n.node_type} for n in self.nodes],
            "edges": [{"source": e.source, "target": e.target, "label": e.label} for e in self.edges],
        }


class ArchitectureVisualizer:
    """Generates visual representations of software architectures.

    Supports:
    - Component relationship diagrams
    - Data flow diagrams
    - Deployment topology diagrams
    - Export to Mermaid, JSON, and interactive formats
    """

    def __init__(self) -> None:
        logger.info("ArchitectureVisualizer initialized")

    def visualize(self, architecture: dict[str, Any]) -> ArchitectureDiagram:
        """Generate a diagram from architecture specification.

        Args:
            architecture: Architecture specification.

        Returns:
            ArchitectureDiagram ready for rendering.
        """
        nodes = []
        edges = []

        components = architecture.get("components", [])
        for i, comp in enumerate(components):
            name = comp.get("name", f"component_{i}")
            nodes.append(DiagramNode(
                id=f"node_{i}",
                label=name,
                node_type=comp.get("type", "service"),
            ))

        # Add edges based on dependencies
        for i, comp in enumerate(components):
            for dep in comp.get("dependencies", []):
                dep_idx = next((j for j, c in enumerate(components) if c.get("name") == dep), None)
                if dep_idx is not None:
                    edges.append(DiagramEdge(
                        source=f"node_{i}",
                        target=f"node_{dep_idx}",
                        label="depends on",
                        edge_type="dependency",
                    ))

        diagram = ArchitectureDiagram(
            title="NSACA Generated Architecture",
            nodes=nodes,
            edges=edges,
        )

        logger.info("Architecture visualized", nodes=len(nodes), edges=len(edges))
        return diagram
