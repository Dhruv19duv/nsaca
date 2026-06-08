"""Tests for reasoning modules."""

import pytest
from nsaca.reasoning.mcts import MCTSReasoner, MCTSNode
from nsaca.reasoning.gnn import GNNArchitect, GNNPrediction
from nsaca.reasoning.llm_reasoner import LLMReasoner, ReasoningResult


class TestMCTSReasoner:
    """Test suite for MCTS architecture simulator."""

    def test_initialization(self):
        mcts = MCTSReasoner(max_iterations=50)
        assert mcts.max_iterations == 50
        assert mcts.root is None

    def test_initialization_defaults(self):
        mcts = MCTSReasoner()
        assert mcts.max_iterations == 50
        assert mcts.exploration_weight == 1.41

    def test_ucb1_unvisited(self):
        node = MCTSNode(state={})
        assert node.ucb1() == float("inf")

    def test_ucb1_visited(self):
        parent = MCTSNode(state={})
        parent.visits = 10
        child = MCTSNode(state={}, parent=parent)
        child.visits = 5
        child.total_reward = 3.0
        ucb = child.ucb1()
        assert 0 < ucb < 10  # should be reasonable

    def test_q_value(self):
        node = MCTSNode(state={})
        node.visits = 10
        node.total_reward = 5.0
        assert node.q_value == 0.5

    def test_q_value_zero_visits(self):
        node = MCTSNode(state={})
        assert node.q_value == 0.0

    def test_simulate_basic(self):
        mcts = MCTSReasoner(max_iterations=20)
        parsed = {"components": [], "constraints": []}
        selections = ["segment_tree", "trie"]
        result = mcts.simulate(parsed, selections)
        assert "name" in result
        assert "score" in result
        assert result["iterations"] == 20

    def test_simulate_empty(self):
        mcts = MCTSReasoner(max_iterations=5)
        result = mcts.simulate({}, [])
        assert result["score"] >= 0


class TestGNNArchitect:
    """Test suite for GNN architecture predictor."""

    def test_initialization(self):
        gnn = GNNArchitect()
        assert gnn.hidden_dim == 128
        assert gnn.num_layers == 3
        assert not gnn.is_trained

    def test_initialization_custom(self):
        gnn = GNNArchitect(hidden_dim=256, num_layers=5)
        assert gnn.hidden_dim == 256
        assert gnn.num_layers == 5

    @pytest.mark.asyncio
    async def test_predict(self):
        gnn = GNNArchitect()
        graph_data = {
            "nodes": {"a": [1, 0], "b": [0, 1]},
            "edges": [("a", "b")],
        }
        result = await gnn.predict(graph_data)
        assert isinstance(result, GNNPrediction)
        assert "a" in result.node_embeddings
        assert "b" in result.node_embeddings
        assert len(result.graph_embedding) == 128
        assert "coupling_score" in result.predictions

    @pytest.mark.asyncio
    async def test_train(self):
        gnn = GNNArchitect()
        metrics = await gnn.train([{"graph": "test", "labels": {}}], epochs=10)
        assert "loss" in metrics
        assert "accuracy" in metrics
        assert gnn.is_trained


class TestLLMReasoner:
    """Test suite for LLM reasoning engine."""

    def test_initialization(self):
        reasoner = LLMReasoner(model="gpt-4")
        assert reasoner.model == "gpt-4"
        assert reasoner.temperature == 0.7

    def test_initialization_custom(self):
        reasoner = LLMReasoner(model="gpt-3.5-turbo", temperature=0.3)
        assert reasoner.model == "gpt-3.5-turbo"
        assert reasoner.temperature == 0.3

    def test_heuristic_reason(self):
        reasoner = LLMReasoner()
        result = reasoner._heuristic_reason("Build a cache system")
        assert isinstance(result, ReasoningResult)
        assert len(result.steps) == 3
        assert result.confidence > 0
        assert "heuristic" in result.conclusion.lower()

    @pytest.mark.asyncio
    async def test_reason_without_api_key(self):
        """Test that reasoning falls back to heuristic when no API key is set."""
        import os
        old_key = os.environ.pop("OPENAI_API_KEY", None)
        try:
            reasoner = LLMReasoner()
            result = await reasoner.reason("test problem")
            assert isinstance(result, ReasoningResult)
            # Should fall back to heuristic
            assert "heuristic" in result.conclusion.lower() or len(result.steps) > 0
        finally:
            if old_key:
                os.environ["OPENAI_API_KEY"] = old_key

    @pytest.mark.asyncio
    async def test_generate_code_fallback(self):
        import os
        old_key = os.environ.pop("OPENAI_API_KEY", None)
        try:
            reasoner = LLMReasoner()
            code = await reasoner.generate_code({"name": "test"})
            assert isinstance(code, str)
            assert "pass" in code or "Generated" in code
        finally:
            if old_key:
                os.environ["OPENAI_API_KEY"] = old_key

    @pytest.mark.asyncio
    async def test_review_code_fallback(self):
        import os
        old_key = os.environ.pop("OPENAI_API_KEY", None)
        try:
            reasoner = LLMReasoner()
            reviews = await reasoner.review_code("x = 1")
            assert isinstance(reviews, list)
            assert len(reviews) >= 1
        finally:
            if old_key:
                os.environ["OPENAI_API_KEY"] = old_key
