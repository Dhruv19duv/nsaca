"""Tests for graph modules."""

import pytest
from nsaca.graph.dependency_graph import DependencyGraph
from nsaca.graph.knowledge_graph import KnowledgeGraph


class TestDependencyGraph:
    """Test suite for DependencyGraph."""

    def test_initialization(self):
        graph = DependencyGraph()
        assert graph.graph.number_of_nodes() == 0

    def test_add_node(self):
        graph = DependencyGraph()
        from nsaca.graph.dependency_graph import GraphNode
        node = GraphNode(id="a", name="Service A", node_type="service")
        graph.add_node(node)
        assert "a" in graph.graph
        assert graph.nodes["a"].name == "Service A"

    def test_add_edge(self):
        graph = DependencyGraph()
        from nsaca.graph.dependency_graph import GraphNode, GraphEdge
        graph.add_node(GraphNode(id="a", name="A", node_type="service"))
        graph.add_node(GraphNode(id="b", name="B", node_type="service"))
        graph.add_edge(GraphEdge(source="a", target="b", dependency_type="calls"))
        assert graph.graph.has_edge("a", "b")

    def test_topological_sort(self):
        graph = DependencyGraph()
        from nsaca.graph.dependency_graph import GraphNode, GraphEdge
        graph.add_node(GraphNode(id="a", name="A", node_type="service"))
        graph.add_node(GraphNode(id="b", name="B", node_type="service"))
        graph.add_node(GraphNode(id="c", name="C", node_type="service"))
        graph.add_edge(GraphEdge(source="a", target="b", dependency_type="calls"))
        graph.add_edge(GraphEdge(source="b", target="c", dependency_type="calls"))
        order = graph.topological_sort()
        assert order.index("a") < order.index("b") < order.index("c")

    def test_cycle_detection(self):
        graph = DependencyGraph()
        from nsaca.graph.dependency_graph import GraphNode, GraphEdge
        graph.add_node(GraphNode(id="a", name="A", node_type="service"))
        graph.add_node(GraphNode(id="b", name="B", node_type="service"))
        graph.add_edge(GraphEdge(source="a", target="b", dependency_type="calls"))
        graph.add_edge(GraphEdge(source="b", target="a", dependency_type="calls"))
        cycles = graph.find_cycles()
        assert len(cycles) > 0

    def test_stats(self):
        graph = DependencyGraph()
        from nsaca.graph.dependency_graph import GraphNode
        graph.add_node(GraphNode(id="a", name="A", node_type="service"))
        stats = graph.get_stats()
        assert stats["nodes"] == 1
        assert stats["edges"] == 0


class TestKnowledgeGraph:
    """Test suite for KnowledgeGraph."""

    def test_initialization(self):
        kg = KnowledgeGraph()
        assert len(kg.concepts) > 0

    def test_add_concept(self):
        kg = KnowledgeGraph()
        from nsaca.graph.knowledge_graph import Concept
        concept = Concept(name="test_pattern", category="pattern", properties={"test": True})
        kg.add_concept(concept)
        assert "test_pattern" in kg.concepts

    def test_find_related(self):
        kg = KnowledgeGraph()
        related = kg.find_related("segment_tree", max_hops=2)
        assert isinstance(related, list)

    def test_suggest_patterns(self):
        kg = KnowledgeGraph()
        suggestions = kg.suggest_patterns(["low latency", "caching"])
        assert isinstance(suggestions, list)
