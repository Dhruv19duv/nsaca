"""Tests for execution modules."""

import pytest
import time
from nsaca.execution.benchmark import (
    BenchmarkRunner,
    BenchmarkConfig,
    BenchmarkResult,
    BenchmarkSuite,
)
from nsaca.execution.distributed import (
    DistributedExecutor,
    WorkerTask,
    WorkerResult,
)


class TestBenchmarkRunner:
    """Test suite for benchmark runner."""

    def test_initialization(self):
        runner = BenchmarkRunner()
        assert runner.config.name == "default"

    def test_initialization_custom_config(self):
        config = BenchmarkConfig(name="custom", input_sizes=[10, 20])
        runner = BenchmarkRunner(config)
        assert runner.config.name == "custom"

    def test_benchmark_basic(self):
        runner = BenchmarkRunner(BenchmarkConfig(
            name="test_bench",
            input_sizes=[10, 50],
            iterations=5,
            warmup_iterations=1,
        ))
        result = runner.benchmark(lambda n: sum(range(n)))
        assert isinstance(result, BenchmarkSuite)
        assert result.name == "test_bench"
        assert len(result.results) == 2
        assert all(isinstance(r, BenchmarkResult) for r in result.results)

    def test_benchmark_measurements(self):
        runner = BenchmarkRunner(BenchmarkConfig(
            name="test",
            input_sizes=[100],
            iterations=3,
            warmup_iterations=1,
        ))
        result = runner.benchmark(lambda n: sum(range(n)))
        assert len(result.results) == 1
        r = result.results[0]
        assert r.input_size == 100
        assert r.avg_time_ns > 0
        assert r.min_time_ns > 0
        assert r.ops_per_sec > 0

    def test_benchmark_fastest_slowest(self):
        runner = BenchmarkRunner(BenchmarkConfig(
            name="test",
            input_sizes=[10, 1000],
            iterations=5,
            warmup_iterations=1,
        ))
        result = runner.benchmark(lambda n: sum(range(n)))
        assert result.fastest is not None
        assert result.slowest is not None
        assert result.fastest.avg_time_ns <= result.slowest.avg_time_ns

    def test_compare(self):
        runner = BenchmarkRunner(BenchmarkConfig(
            name="compare",
            input_sizes=[100],
            iterations=5,
            warmup_iterations=1,
        ))
        funcs = {
            "sum_range": lambda n: sum(range(n)),
            "list_sum": lambda n: list(range(n)),
        }
        suites = runner.compare(funcs)
        assert len(suites) == 2
        assert "sum_range" in suites
        assert "list_sum" in suites


class TestDistributedExecutor:
    """Test suite for distributed executor."""

    def test_initialization(self):
        executor = DistributedExecutor()
        assert executor.max_workers == 4
        assert executor.max_retries == 2

    def test_initialization_custom(self):
        executor = DistributedExecutor(max_workers=8, max_retries=3)
        assert executor.max_workers == 8
        assert executor.max_retries == 3

    def test_submit(self):
        executor = DistributedExecutor()
        task = WorkerTask(id="t1", func_name="test", args={})
        executor.submit(task)
        assert len(executor.task_queue) == 1

    def test_submit_batch(self):
        executor = DistributedExecutor()
        tasks = [
            WorkerTask(id=f"t{i}", func_name="test", args={})
            for i in range(5)
        ]
        executor.submit_batch(tasks)
        assert len(executor.task_queue) == 5

    @pytest.mark.asyncio
    async def test_execute_all(self):
        executor = DistributedExecutor()
        tasks = [
            WorkerTask(id=f"t{i}", func_name="test", args={})
            for i in range(3)
        ]
        executor.submit_batch(tasks)
        results = await executor.execute_all()
        assert len(results) == 3
        assert all(isinstance(r, WorkerResult) for r in results)

    @pytest.mark.asyncio
    async def test_execute_empty(self):
        executor = DistributedExecutor()
        results = await executor.execute_all()
        assert results == []

    def test_stats(self):
        executor = DistributedExecutor()
        stats = executor.get_stats()
        assert stats["total_tasks"] == 0
        assert stats["queued"] == 0

    @pytest.mark.asyncio
    async def test_stats_after_execution(self):
        executor = DistributedExecutor()
        executor.submit(WorkerTask(id="t1", func_name="test", args={}))
        await executor.execute_all()
        stats = executor.get_stats()
        assert stats["total_tasks"] == 1
        assert stats["completed"] + stats["failed"] == 1

    def test_priority_ordering(self):
        executor = DistributedExecutor()
        executor.submit(WorkerTask(id="low", func_name="test", args={}, priority=1))
        executor.submit(WorkerTask(id="high", func_name="test", args={}, priority=10))
        assert executor.task_queue[0].id == "high"
        assert executor.task_queue[1].id == "low"
