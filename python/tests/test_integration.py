"""End-to-end integration tests for the full NSACA pipeline.

Tests the complete flow from problem description through to architecture output,
verifying that all subsystems work together correctly.
"""

import pytest
from nsaca.core.orchestrator import NSACAOrchestrator, SystemState
from nsaca.core.problem_parser import ProblemParser, ParsedProblem, ComponentType, Component
from nsaca.core.decision_engine import DecisionEngine, TradeOffCategory, TradeOffOption, DecisionContext
from nsaca.algorithms.selector import AlgorithmSelector
from nsaca.graph.dependency_graph import DependencyGraph
from nsaca.graph.knowledge_graph import KnowledgeGraph
from nsaca.reasoning.mcts import MCTSReasoner
from nsaca.memory.vector_store import VectorStore
from nsaca.memory.graph_memory import GraphMemory
from nsaca.debugging.self_healing import SelfHealingDebugger
from nsaca.debugging.adversarial import AdversarialTester
from nsaca.debugging.edge_cases import EdgeCaseDetector
from nsaca.visualization.architecture import ArchitectureVisualizer
from nsaca.execution.benchmark import BenchmarkRunner, BenchmarkConfig
from nsaca.feedback.human_loop import HumanInTheLoop, FeedbackResponse


class TestFullPipeline:
    """End-to-end tests for the complete NSACA pipeline."""

    @pytest.mark.asyncio
    async def test_full_pipeline_simple(self):
        """Test the complete pipeline on a simple problem."""
        orchestrator = NSACAOrchestrator(llm_model="test-model")
        result = await orchestrator.run(
            "Design a real-time chat system that supports 10,000 concurrent users"
        )
        assert result.state == SystemState.COMPLETE
        assert result.architecture is not None
        assert isinstance(result.explanations, list)

    @pytest.mark.asyncio
    async def test_full_pipeline_complex(self):
        """Test the complete pipeline on a complex problem."""
        orchestrator = NSACAOrchestrator(
            llm_model="test-model",
            max_architecture_candidates=10,
        )
        result = await orchestrator.run(
            "Build a distributed e-commerce platform with sub-100ms latency, "
            "supporting 1 million concurrent users, with real-time inventory "
            "management, payment processing, and recommendation engine"
        )
        assert result.state == SystemState.COMPLETE

    @pytest.mark.asyncio
    async def test_pipeline_empty_description(self):
        """Test pipeline handles empty description gracefully."""
        orchestrator = NSACAOrchestrator()
        result = await orchestrator.run("")
        assert result.state == SystemState.COMPLETE


class TestProblemParserIntegration:
    """Integration tests for the problem parser."""

    @pytest.mark.asyncio
    async def test_parse_distributed_system(self):
        """Test parsing a distributed system problem."""
        parser = ProblemParser()
        parsed = await parser.parse(
            "Build a distributed caching system with Redis that supports "
            "100k reads/sec and has sub-millisecond latency"
        )
        assert isinstance(parsed, ParsedProblem)
        assert parsed.raw_description is not None
        # Without API key, should return empty but not crash
        assert isinstance(parsed.components, list)
        assert isinstance(parsed.constraints, list)

    def test_build_relations(self):
        """Test relation building from components."""
        parser = ProblemParser()
        components = [
            Component(name="API", type=ComponentType.API, description="REST API", dependencies=["DB"]),
            Component(name="DB", type=ComponentType.DATABASE, description="PostgreSQL"),
        ]
        relations = parser._build_relations(components)
        assert ("API", "depends_on", "DB") in relations
        assert ("API", "is_type", "api") in relations
        assert ("DB", "is_type", "database") in relations


class TestDecisionEngineIntegration:
    """Integration tests for the decision engine."""

    def test_evaluate_tradeoffs(self):
        """Test full trade-off evaluation."""
        engine = DecisionEngine()
        options = [
            TradeOffOption(
                name="Microservices",
                description="Decomposed into services",
                scores={
                    TradeOffCategory.SCALABILITY: 0.9,
                    TradeOffCategory.COST: 0.4,
                    TradeOffCategory.LATENCY: 0.6,
                    TradeOffCategory.FAULT_TOLERANCE: 0.8,
                    TradeOffCategory.COMPLEXITY: 0.3,
                },
            ),
            TradeOffOption(
                name="Monolith",
                description="Single deployable unit",
                scores={
                    TradeOffCategory.SCALABILITY: 0.4,
                    TradeOffCategory.COST: 0.9,
                    TradeOffCategory.LATENCY: 0.8,
                    TradeOffCategory.FAULT_TOLERANCE: 0.5,
                    TradeOffCategory.COMPLEXITY: 0.9,
                },
            ),
        ]
        context = DecisionContext(
            problem_description="Build a scalable web app",
            options=options,
            weights=engine.DEFAULT_WEIGHTS,
        )
        result = engine.evaluate(context)
        assert result.best_option is not None
        assert len(result.rankings) == 2
        assert result.rankings[0][0] in ["Microservices", "Monolith"]

    def test_custom_weights(self):
        """Test evaluation with custom weights."""
        engine = DecisionEngine()
        options = [
            TradeOffOption(
                name="Fast",
                description="Optimized for speed",
                scores={TradeOffCategory.LATENCY: 0.9, TradeOffCategory.COST: 0.3},
            ),
            TradeOffOption(
                name="Cheap",
                description="Optimized for cost",
                scores={TradeOffCategory.LATENCY: 0.3, TradeOffCategory.COST: 0.9},
            ),
        ]
        # Favor latency heavily
        weights = {
            TradeOffCategory.LATENCY: 5.0,
            TradeOffCategory.COST: 1.0,
        }
        context = DecisionContext(
            problem_description="test",
            options=options,
            weights=weights,
        )
        result = engine.evaluate(context, custom_weights=weights)
        assert result.best_option.name == "Fast"


class TestAlgorithmSelectorIntegration:
    """Integration tests for algorithm selection."""

    def test_select_for_cache_system(self):
        """Test algorithm selection for a caching system."""
        selector = AlgorithmSelector()
        parsed = {
            "components": [{"name": "cache", "type": "cache"}],
            "constraints": ["high throughput", "prefix search for keys"],
            "input_size": 1_000_000,
        }
        selections = selector.select_for_problem(parsed)
        assert len(selections) > 0
        # Should suggest trie for prefix search
        names = [s.name for s in selections]
        assert "trie" in names

    def test_select_for_range_queries(self):
        """Test selection for range query heavy workload."""
        selector = AlgorithmSelector()
        parsed = {
            "components": [],
            "constraints": ["range queries", "aggregate over time windows"],
            "input_size": 500_000,
        }
        selections = selector.select_for_problem(parsed)
        names = [s.name for s in selections]
        assert "segment_tree" in names

    def test_select_for_streaming(self):
        """Test selection for streaming data."""
        selector = AlgorithmSelector()
        parsed = {
            "components": [],
            "constraints": ["streaming data", "membership testing"],
            "input_size": 10_000_000,
        }
        selections = selector.select_for_problem(parsed)
        names = [s.name for s in selections]
        assert "bloom_filter" in names


class TestGraphIntegration:
    """Integration tests for graph modules."""

    def test_dependency_graph_full_workflow(self):
        """Test building and analyzing a dependency graph."""
        graph = DependencyGraph()
        from nsaca.graph.dependency_graph import GraphNode, GraphEdge

        # Add components
        graph.add_node(GraphNode(id="api", name="API Gateway", node_type="service"))
        graph.add_node(GraphNode(id="auth", name="Auth Service", node_type="service"))
        graph.add_node(GraphNode(id="cache", name="Redis Cache", node_type="cache"))
        graph.add_node(GraphNode(id="db", name="PostgreSQL", node_type="database"))
        graph.add_node(GraphNode(id="queue", name="RabbitMQ", node_type="queue"))

        # Add dependencies
        graph.add_edge(GraphEdge(source="api", target="auth", dependency_type="calls"))
        graph.add_edge(GraphEdge(source="api", target="cache", dependency_type="uses"))
        graph.add_edge(GraphEdge(source="api", target="db", dependency_type="calls"))
        graph.add_edge(GraphEdge(source="auth", target="db", dependency_type="calls"))
        graph.add_edge(GraphEdge(source="cache", target="db", dependency_type="calls"))

        # Verify
        stats = graph.get_stats()
        assert stats["nodes"] == 5
        assert stats["edges"] == 5
        assert stats["is_dag"] is True

        # Topological sort
        order = graph.topological_sort()
        assert len(order) == 5
        assert order.index("api") < order.index("auth")
        assert order.index("api") < order.index("db")

        # Critical path
        path = graph.critical_path()
        assert len(path) > 0

    def test_knowledge_graph_pattern_suggestion(self):
        """Test pattern suggestion from knowledge graph."""
        kg = KnowledgeGraph()
        patterns = kg.suggest_patterns(["low latency", "caching", "distributed"])
        assert isinstance(patterns, list)

    def test_knowledge_graph_related_concepts(self):
        """Test finding related concepts."""
        kg = KnowledgeGraph()
        related = kg.find_related("trie", max_hops=2)
        assert isinstance(related, list)


class TestMemoryIntegration:
    """Integration tests for memory modules."""

    def test_vector_store_workflow(self):
        """Test storing and retrieving from vector store."""
        store = VectorStore(dimension=64)

        # Store several architectures
        store.store("Build a chat system", {"name": "chat_arch", "type": "microservices"})
        store.store("Design a cache layer", {"name": "cache_arch", "type": "standalone"})
        store.store("Create messaging queue", {"name": "queue_arch", "type": "event_driven"})

        assert store.size() == 3

        # Find similar
        results = store.find_similar("Build a real-time chat", top_k=2)
        assert len(results) > 0

    def test_graph_memory_workflow(self):
        """Test graph memory storage and retrieval."""
        memory = GraphMemory()

        # Store multiple architectures
        for i in range(5):
            memory.store(
                {"components": [{"name": f"comp_{i}"}]},
                {"name": f"arch_{i}", "components": [{"name": f"comp_{i}"}]},
            )

        stats = memory.get_stats()
        assert stats["total_nodes"] > 5

        patterns = memory.find_patterns("architecture")
        assert len(patterns) >= 5


class TestDebuggingIntegration:
    """Integration tests for debugging modules."""

    @pytest.mark.asyncio
    async def test_self_healing_workflow(self):
        """Test self-healing on problematic code."""
        debugger = SelfHealingDebugger()
        code = "try:\n    x = 1\nexcept:\n    pass\ny = 2"
        result = await debugger.heal(code)
        assert result.fixed
        assert "except Exception:" in result.code

    @pytest.mark.asyncio
    async def test_adversarial_testing_workflow(self):
        """Test adversarial testing on code."""
        tester = AdversarialTester()
        report = await tester.test("def process(x): return x * 2", {})
        assert report.total_tests > 0
        assert report.passed + report.failed == report.total_tests

    def test_edge_case_detection_workflow(self):
        """Test edge case detection on architecture."""
        detector = EdgeCaseDetector()
        arch = {
            "components": [
                {"name": "api", "type": "service"},
                {"name": "db", "type": "database"},
                {"name": "cache", "type": "cache"},
            ]
        }
        cases = detector.detect(arch)
        assert len(cases) > 0
        # Should detect concurrent access (multiple components)
        names = [c.name for c in cases]
        assert "concurrent_access" in names


class TestVisualizationIntegration:
    """Integration tests for visualization."""

    def test_architecture_to_mermaid(self):
        """Test generating Mermaid diagram from architecture."""
        viz = ArchitectureVisualizer()
        arch = {
            "components": [
                {"name": "API Gateway", "type": "service", "dependencies": ["Auth"]},
                {"name": "Auth", "type": "service", "dependencies": ["Database"]},
                {"name": "Database", "type": "database"},
            ]
        }
        diagram = viz.visualize(arch)
        mermaid = diagram.to_mermaid()
        assert "graph TD" in mermaid
        assert "API Gateway" in mermaid
        assert "Auth" in mermaid
        assert "Database" in mermaid


class TestBenchmarkIntegration:
    """Integration tests for benchmarking."""

    def test_benchmark_comparison(self):
        """Test comparing two implementations."""
        runner = BenchmarkRunner(BenchmarkConfig(
            name="algo_compare",
            input_sizes=[100, 500],
            iterations=5,
            warmup_iterations=1,
        ))
        suites = runner.compare({
            "list_sum": lambda n: sum(range(n)),
            "generator_sum": lambda n: sum(x for x in range(n)),
        })
        assert len(suites) == 2
        for name, suite in suites.items():
            assert suite.name == name
            assert len(suite.results) == 2


class TestHumanFeedbackIntegration:
    """Integration tests for human feedback."""

    def test_feedback_workflow(self):
        """Test complete feedback workflow."""
        hitl = HumanInTheLoop()

        # Create request
        request = hitl.create_tradeoff_request([
            {"name": "Option A", "pros": ["fast"]},
            {"name": "Option B", "pros": ["cheap"]},
        ])
        assert request is not None

        # Record responses
        for i in range(5):
            hitl.record_response(FeedbackResponse(
                request_id=request.id,
                selected_option="Option A" if i < 3 else "Option B",
            ))

        # Check preferences
        summary = hitl.get_preference_summary()
        assert summary["total_feedback"] == 5
        assert summary["preferences"]["Option A"]["count"] == 3

        # Get suggestion
        suggestion = hitl.suggest_based_on_history(["Option A", "Option B"])
        assert suggestion == "Option A"


class TestMCTSIntegration:
    """Integration tests for MCTS."""

    def test_mcts_architecture_search(self):
        """Test MCTS finding optimal architecture."""
        mcts = MCTSReasoner(max_iterations=30)
        parsed = {
            "components": [{"name": "api"}, {"name": "db"}, {"name": "cache"}],
            "constraints": ["low latency", "high availability"],
        }
        selections = ["segment_tree", "trie", "bloom_filter"]
        result = mcts.simulate(parsed, selections)
        assert "name" in result
        assert "score" in result
        assert result["iterations"] == 30
