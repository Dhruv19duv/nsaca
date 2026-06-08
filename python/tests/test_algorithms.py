"""Tests for algorithm selection and optimization."""

import pytest
from nsaca.algorithms.selector import AlgorithmSelector, SelectionCriteria
from nsaca.algorithms.complexity import ComplexityAnalyzer
from nsaca.algorithms.optimizer import CodeOptimizer, OptimizationPass


class TestAlgorithmSelector:
    """Test suite for AlgorithmSelector."""

    def test_initialization(self):
        selector = AlgorithmSelector()
        assert selector.ds_rules is not None
        assert selector.algo_rules is not None

    def test_select_for_range_queries(self):
        selector = AlgorithmSelector()
        parsed = {
            "components": [],
            "constraints": ["range queries on large dataset"],
            "input_size": 100000,
        }
        selections = selector.select_for_problem(parsed)
        assert len(selections) > 0
        names = [s.name for s in selections]
        assert "segment_tree" in names

    def test_select_for_prefix_search(self):
        selector = AlgorithmSelector()
        parsed = {
            "components": [],
            "constraints": ["prefix search autocomplete"],
            "input_size": 10000,
        }
        selections = selector.select_for_problem(parsed)
        names = [s.name for s in selections]
        assert "trie" in names

    def test_select_default(self):
        selector = AlgorithmSelector()
        parsed = {"components": [], "constraints": [], "input_size": 1000}
        selections = selector.select_for_problem(parsed)
        assert len(selections) >= 1


class TestComplexityAnalyzer:
    """Test suite for ComplexityAnalyzer."""

    def test_analyze_linear(self):
        analyzer = ComplexityAnalyzer()
        measurements = [(100, 1.0), (200, 2.0), (400, 4.0), (800, 8.0)]
        result = analyzer.analyze("linear_algo", measurements)
        assert result["algorithm"] == "linear_algo"
        assert "O(n)" in result["estimated"]

    def test_analyze_quadratic(self):
        analyzer = ComplexityAnalyzer()
        measurements = [(10, 1.0), (20, 4.0), (40, 16.0), (80, 64.0)]
        result = analyzer.analyze("quad_algo", measurements)
        assert result["algorithm"] == "quad_algo"

    def test_predict_bottlenecks(self):
        analyzer = ComplexityAnalyzer()
        analysis = {"max_nesting": 3, "cyclomatic": 15}
        bottlenecks = analyzer.predict_bottlenecks(analysis, input_size=1_000_000)
        assert len(bottlenecks) >= 2


class TestCodeOptimizer:
    """Test suite for CodeOptimizer."""

    def test_constant_folding(self):
        optimizer = CodeOptimizer(passes=[OptimizationPass.CONSTANT_FOLDING])
        code = "x = 3 + 4"
        result = optimizer.optimize(code)
        assert "7" in result.code

    def test_strength_reduction(self):
        optimizer = CodeOptimizer(passes=[OptimizationPass.STRENGTH_REDUCTION])
        code = "x = y * 2"
        result = optimizer.optimize(code)
        assert "<<" in result.code

    def test_optimization_metrics(self):
        optimizer = CodeOptimizer()
        code = "x = 3 + 4\nreturn x"
        result = optimizer.optimize(code)
        assert "chars" in result.metrics_before
        assert "chars" in result.metrics_after
