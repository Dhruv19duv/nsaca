"""Tests for the NSACA orchestrator."""

import pytest
from nsaca.core.orchestrator import NSACAOrchestrator, PipelineResult, SystemState


class TestOrchestrator:
    """Test suite for NSACAOrchestrator."""

    def test_initialization(self):
        orchestrator = NSACAOrchestrator(llm_model="gpt-4")
        assert orchestrator.state == SystemState.IDLE
        assert orchestrator.llm_model == "gpt-4"

    def test_initialization_default(self):
        orchestrator = NSACAOrchestrator()
        assert orchestrator.state == SystemState.IDLE
        assert orchestrator.enable_visualization is True

    def test_initialization_no_viz(self):
        orchestrator = NSACAOrchestrator(enable_visualization=False)
        assert orchestrator.visualizer is None

    def test_pipeline_result_default(self):
        result = PipelineResult(state=SystemState.IDLE, architecture={})
        assert result.state == SystemState.IDLE
        assert result.architecture == {}
        assert result.benchmark_results == []
        assert result.explanations == []
        assert result.errors == []

    @pytest.mark.asyncio
    async def test_run_basic(self):
        orchestrator = NSACAOrchestrator(llm_model="test-model")
        result = await orchestrator.run("Build a distributed cache system")
        assert result.state == SystemState.COMPLETE
        assert "architect" in str(result.architecture) or result.architecture is not None

    @pytest.mark.asyncio
    async def test_run_empty_description(self):
        orchestrator = NSACAOrchestrator(llm_model="test-model")
        result = await orchestrator.run("")
        assert result.state == SystemState.COMPLETE
