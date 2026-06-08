"""Complexity analysis for algorithms and data structures."""

from __future__ import annotations

import math
import structlog
from dataclasses import dataclass
from typing import Any


logger = structlog.get_logger()


@dataclass
class ComplexityProfile:
    """Time-space complexity profile of an algorithm."""
    name: str
    best_case: str
    average_case: str
    worst_case: str
    space: str
    stable: bool = True
    in_place: bool = False


class ComplexityAnalyzer:
    """Analyzes and compares algorithmic complexity.

    Provides Big-O analysis, empirical complexity measurement,
    and bottleneck prediction.
    """

    def __init__(self) -> None:
        logger.info("ComplexityAnalyzer initialized")

    def analyze(self, algorithm_name: str, measurements: list[tuple[int, float]]) -> dict[str, Any]:
        """Empirically estimate complexity class from input-size/time measurements.

        Args:
            algorithm_name: Name of the algorithm.
            measurements: List of (input_size, execution_time) pairs.

        Returns:
            Dictionary with estimated complexity class and parameters.
        """
        if len(measurements) < 2:
            return {"algorithm": algorithm_name, "estimated": "unknown"}

        # Fit to common complexity classes
        classes = {
            "O(1)": lambda n: 1,
            "O(log n)": lambda n: math.log2(max(n, 1)),
            "O(n)": lambda n: n,
            "O(n log n)": lambda n: n * math.log2(max(n, 1)),
            "O(n^2)": lambda n: n * n,
            "O(n^3)": lambda n: n * n * n,
            "O(2^n)": lambda n: 2**min(n, 30),
        }

        best_fit = "unknown"
        best_r_squared = -1.0

        for name, func in classes.items():
            try:
                # Simple least squares fit
                xs = [m[0] for m in measurements]
                ys = [m[1] for m in measurements]
                fs = [func(x) for x in xs]
                if all(f == 0 for f in fs):
                    continue

                # Compute R^2
                mean_y = sum(ys) / len(ys)
                ss_tot = sum((y - mean_y) ** 2 for y in ys)
                # Scale factor
                scale = sum(y * f for y, f in zip(ys, fs)) / sum(f * f for f in fs)
                predicted = [scale * f for f in fs]
                ss_res = sum((y - p) ** 2 for y, p in zip(ys, predicted))
                r_squared = 1 - ss_res / max(ss_tot, 1e-10)

                if r_squared > best_r_squared:
                    best_r_squared = r_squared
                    best_fit = name
            except (ZeroDivisionError, ValueError):
                continue

        return {
            "algorithm": algorithm_name,
            "estimated": best_fit,
            "confidence": best_r_squared,
        }

    def predict_bottlenecks(
        self,
        code_analysis: dict[str, Any],
        input_size: int,
    ) -> list[dict[str, Any]]:
        """Predict performance bottlenecks based on code analysis.

        Args:
            code_analysis: AST/code analysis results.
            input_size: Expected input size.

        Returns:
            List of potential bottlenecks.
        """
        bottlenecks = []

        # Check for nested loops (O(n^2) or worse)
        if code_analysis.get("max_nesting", 0) >= 2:
            bottlenecks.append({
                "type": "nested_loops",
                "severity": "high",
                "suggestion": "Consider using a more efficient algorithm or data structure",
            })

        # Check for high cyclomatic complexity
        cyclomatic = code_analysis.get("cyclomatic", 1)
        if cyclomatic > 10:
            bottlenecks.append({
                "type": "high_complexity",
                "severity": "medium",
                "suggestion": "Refactor complex logic into smaller functions",
            })

        # Large input size with simple algorithms
        if input_size > 1_000_000:
            bottlenecks.append({
                "type": "large_input",
                "severity": "high",
                "suggestion": "Consider divide-and-conquer or streaming approaches",
            })

        return bottlenecks
