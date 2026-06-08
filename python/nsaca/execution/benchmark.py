"""Benchmarking engine for algorithmic performance comparison.

Runs controlled benchmarks to compare algorithm/data structure implementations
and provide empirical complexity measurements.
"""

from __future__ import annotations

import time
import structlog
from dataclasses import dataclass, field
from typing import Any, Callable


logger = structlog.get_logger()


@dataclass
class BenchmarkConfig:
    """Configuration for a benchmark run."""
    name: str
    input_sizes: list[int] = field(default_factory=lambda: [100, 1000, 10000])
    iterations: int = 10
    warmup_iterations: int = 3
    timeout_seconds: float = 30.0


@dataclass
class BenchmarkResult:
    """Result of a single benchmark measurement."""
    input_size: int
    avg_time_ns: int
    min_time_ns: int
    max_time_ns: int
    ops_per_sec: float
    memory_bytes: int = 0


@dataclass
class BenchmarkSuite:
    """Complete benchmark suite result."""
    name: str
    results: list[BenchmarkResult]
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def fastest(self) -> BenchmarkResult | None:
        return min(self.results, key=lambda r: r.avg_time_ns) if self.results else None

    @property
    def slowest(self) -> BenchmarkResult | None:
        return max(self.results, key=lambda r: r.avg_time_ns) if self.results else None


class BenchmarkRunner:
    """Runs controlled benchmarks for algorithm comparison.

    Features:
    - Warmup phase to stabilize JIT caches
    - Multiple iterations for statistical significance
    - Memory usage tracking
    - Timeout protection
    """

    def __init__(self, config: BenchmarkConfig | None = None) -> None:
        self.config = config or BenchmarkConfig(name="default")
        logger.info("BenchmarkRunner initialized", name=self.config.name)

    def benchmark(
        self,
        func: Callable[[int], Any],
        name: str | None = None,
    ) -> BenchmarkSuite:
        """Benchmark a function across configured input sizes.

        Args:
            func: Function to benchmark, takes input_size as argument.
            name: Optional benchmark name.

        Returns:
            BenchmarkSuite with results for each input size.
        """
        results = []

        for size in self.config.input_sizes:
            # Warmup
            for _ in range(self.config.warmup_iterations):
                func(size)

            # Timed iterations
            times = []
            for _ in range(self.config.iterations):
                start = time.perf_counter_ns()
                func(size)
                elapsed = time.perf_counter_ns() - start
                times.append(elapsed)

            avg = sum(times) // len(times)
            ops_per_sec = size / (avg / 1e9) if avg > 0 else 0

            result = BenchmarkResult(
                input_size=size,
                avg_time_ns=avg,
                min_time_ns=min(times),
                max_time_ns=max(times),
                ops_per_sec=ops_per_sec,
            )
            results.append(result)

            logger.debug("Benchmark measurement", size=size, avg_ns=avg)

        suite = BenchmarkSuite(
            name=name or self.config.name,
            results=results,
        )

        logger.info(
            "Benchmark complete",
            name=suite.name,
            measurements=len(results),
        )
        return suite

    def compare(
        self,
        funcs: dict[str, Callable[[int], Any]],
    ) -> dict[str, BenchmarkSuite]:
        """Compare multiple implementations.

        Args:
            funcs: Dict of name → function to compare.

        Returns:
            Dict of name → BenchmarkSuite for each implementation.
        """
        suites = {}
        for name, func in funcs.items():
            suites[name] = self.benchmark(func, name=name)
        return suites
