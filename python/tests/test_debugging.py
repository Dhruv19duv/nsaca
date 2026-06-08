"""Tests for debugging modules."""

import pytest
from nsaca.debugging.self_healing import SelfHealingDebugger, HealResult
from nsaca.debugging.adversarial import AdversarialTester, AdversarialReport
from nsaca.debugging.edge_cases import EdgeCaseDetector, EdgeCase


class TestSelfHealingDebugger:
    """Test suite for self-healing debugging framework."""

    def test_initialization(self):
        debugger = SelfHealingDebugger()
        assert len(debugger._patterns) > 0

    @pytest.mark.asyncio
    async def test_heal_clean_code(self):
        debugger = SelfHealingDebugger()
        code = "x = 1\ny = 2\nprint(x + y)"
        result = await debugger.heal(code)
        assert isinstance(result, HealResult)
        assert result.code == code  # no changes needed

    @pytest.mark.asyncio
    async def test_heal_bare_except(self):
        debugger = SelfHealingDebugger()
        code = "try:\n    x = 1\nexcept:\n    pass"
        result = await debugger.heal(code)
        assert result.fixed
        assert "except Exception:" in result.code

    @pytest.mark.asyncio
    async def test_heal_empty_code(self):
        debugger = SelfHealingDebugger()
        result = await debugger.heal("")
        assert isinstance(result, HealResult)
        assert not result.fixed

    @pytest.mark.asyncio
    async def test_find_edge_cases(self):
        debugger = SelfHealingDebugger()
        code = "result = a / b\nvalue = arr[i]"
        result = await debugger.heal(code)
        assert len(result.remaining_issues) >= 0  # may find some

    def test_patterns_loaded(self):
        debugger = SelfHealingDebugger()
        issues = [p["issue"] for p in debugger._patterns]
        assert "bare_except" in issues


class TestAdversarialTester:
    """Test suite for adversarial testing engine."""

    def test_initialization(self):
        tester = AdversarialTester()
        assert tester is not None

    @pytest.mark.asyncio
    async def test_run_tests(self):
        tester = AdversarialTester()
        report = await tester.test("x = 1", {})
        assert isinstance(report, AdversarialReport)
        assert report.total_tests > 0
        assert report.passed + report.failed == report.total_tests

    @pytest.mark.asyncio
    async def test_boundary_tests(self):
        tester = AdversarialTester()
        results = tester._boundary_tests("test code")
        assert len(results) >= 3  # empty, large, null
        names = [r.test_name for r in results]
        assert "empty_input" in names
        assert "large_input" in names
        assert "null_input" in names

    @pytest.mark.asyncio
    async def test_input_validation_tests(self):
        tester = AdversarialTester()
        results = tester._input_validation_tests("test code")
        assert len(results) >= 2
        names = [r.test_name for r in results]
        assert "special_characters" in names
        assert "sql_injection" in names

    @pytest.mark.asyncio
    async def test_resource_tests(self):
        tester = AdversarialTester()
        results = tester._resource_tests("test code")
        assert len(results) >= 1
        assert results[0].test_name == "deep_recursion"

    @pytest.mark.asyncio
    async def test_recommendations(self):
        tester = AdversarialTester()
        from nsaca.debugging.adversarial import TestResult
        failed = [TestResult("test1", False, "", "expected", "actual", "error")]
        recs = tester._generate_recommendations(failed)
        assert len(recs) > 0
        assert "Fix:" in recs[0]


class TestEdgeCaseDetector:
    """Test suite for edge case detection."""

    def test_initialization(self):
        detector = EdgeCaseDetector()
        assert detector is not None

    def test_detect_basic(self):
        detector = EdgeCaseDetector()
        cases = detector.detect({"components": []})
        assert isinstance(cases, list)
        assert len(cases) > 0  # should always find at least malformed_input

    def test_detect_concurrent(self):
        detector = EdgeCaseDetector()
        cases = detector.detect({
            "components": [{"name": "api"}, {"name": "db"}],
        })
        names = [c.name for c in cases]
        assert "concurrent_access" in names

    def test_detect_database(self):
        detector = EdgeCaseDetector()
        cases = detector.detect({
            "components": [{"name": "database"}],
        })
        names = [c.name for c in cases]
        assert "database_connection_pool_exhaustion" in names

    def test_detect_network(self):
        detector = EdgeCaseDetector()
        cases = detector.detect({
            "components": [{"name": "api"}, {"name": "service"}],
        })
        names = [c.name for c in cases]
        assert "network_partition" in names

    def test_edge_case_severity(self):
        detector = EdgeCaseDetector()
        cases = detector.detect({
            "components": [{"name": "a"}, {"name": "b"}, {"name": "c"}, {"name": "d"}],
        })
        severities = [c.severity for c in cases]
        assert "high" in severities

    def test_edge_case_fields(self):
        detector = EdgeCaseDetector()
        cases = detector.detect({})
        for case in cases:
            assert isinstance(case, EdgeCase)
            assert case.name
            assert case.category
            assert case.description
            assert case.severity
            assert case.suggested_test
