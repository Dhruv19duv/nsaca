"""Tests for visualization modules."""

import pytest
from nsaca.visualization.architecture import (
    ArchitectureVisualizer,
    ArchitectureDiagram,
    DiagramNode,
    DiagramEdge,
)
from nsaca.visualization.reasoning_display import ReasoningVisualizer


class TestArchitectureVisualizer:
    """Test suite for architecture visualization."""

    def test_initialization(self):
        viz = ArchitectureVisualizer()
        assert viz is not None

    def test_visualize_empty(self):
        viz = ArchitectureVisualizer()
        diagram = viz.visualize({"components": []})
        assert isinstance(diagram, ArchitectureDiagram)
        assert diagram.title == "NSACA Generated Architecture"
        assert len(diagram.nodes) == 0
        assert len(diagram.edges) == 0

    def test_visualize_with_components(self):
        viz = ArchitectureVisualizer()
        arch = {
            "components": [
                {"name": "API Gateway", "type": "service"},
                {"name": "Cache", "type": "cache"},
                {"name": "Database", "type": "database"},
            ]
        }
        diagram = viz.visualize(arch)
        assert len(diagram.nodes) == 3
        assert diagram.nodes[0].label == "API Gateway"
        assert diagram.nodes[0].node_type == "service"
        assert diagram.nodes[1].label == "Cache"

    def test_visualize_with_dependencies(self):
        viz = ArchitectureVisualizer()
        arch = {
            "components": [
                {"name": "API", "type": "service", "dependencies": ["Cache"]},
                {"name": "Cache", "type": "cache"},
            ]
        }
        diagram = viz.visualize(arch)
        assert len(diagram.edges) == 1
        assert diagram.edges[0].label == "depends on"

    def test_to_mermaid(self):
        viz = ArchitectureVisualizer()
        arch = {
            "components": [
                {"name": "Web", "type": "service"},
                {"name": "DB", "type": "database"},
            ]
        }
        diagram = viz.visualize(arch)
        mermaid = diagram.to_mermaid()
        assert "graph TD" in mermaid
        assert "Web" in mermaid
        assert "DB" in mermaid

    def test_to_dict(self):
        viz = ArchitectureVisualizer()
        arch = {"components": [{"name": "Test", "type": "service"}]}
        diagram = viz.visualize(arch)
        d = diagram.to_dict()
        assert "title" in d
        assert "nodes" in d
        assert "edges" in d
        assert len(d["nodes"]) == 1


class TestDiagramNode:
    """Test suite for DiagramNode."""

    def test_creation(self):
        node = DiagramNode(id="n1", label="Node 1", node_type="service")
        assert node.id == "n1"
        assert node.label == "Node 1"
        assert node.node_type == "service"

    def test_metadata(self):
        node = DiagramNode(id="n1", label="N", node_type="db", metadata={"key": "val"})
        assert node.metadata["key"] == "val"


class TestDiagramEdge:
    """Test suite for DiagramEdge."""

    def test_creation(self):
        edge = DiagramEdge(source="a", target="b", label="calls")
        assert edge.source == "a"
        assert edge.target == "b"
        assert edge.edge_type == "data_flow"


class TestReasoningVisualizer:
    """Test suite for reasoning display."""

    def test_initialization(self):
        viz = ReasoningVisualizer()
        assert viz is not None

    def test_format_reasoning_chain(self):
        viz = ReasoningVisualizer()
        steps = [
            {"thought": "Analyze problem", "action": "decompose", "observation": "Found 3 components", "confidence": 0.9},
            {"thought": "Select algorithms", "action": "select", "observation": "Chose trie", "confidence": 0.85},
        ]
        result = viz.format_reasoning_chain(steps)
        assert "NSACA Reasoning Chain" in result
        assert "Analyze problem" in result
        assert "Select algorithms" in result
        assert "90.0%" in result

    def test_format_empty_chain(self):
        viz = ReasoningVisualizer()
        result = viz.format_reasoning_chain([])
        assert "NSACA Reasoning Chain" in result

    def test_format_tradeoff_table(self):
        viz = ReasoningVisualizer()
        options = [
            {"name": "Option A", "score": 0.9, "latency": "10ms", "cost": "$100", "scalability": "high"},
            {"name": "Option B", "score": 0.7, "latency": "50ms", "cost": "$50", "scalability": "medium"},
        ]
        result = viz.format_tradeoff_table(options)
        assert "Option A" in result
        assert "Option B" in result
        assert "Score" in result

    def test_format_empty_tradeoff(self):
        viz = ReasoningVisualizer()
        result = viz.format_tradeoff_table([])
        assert "No options" in result
