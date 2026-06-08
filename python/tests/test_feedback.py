"""Tests for feedback module."""

import pytest
from nsaca.feedback.human_loop import (
    HumanInTheLoop,
    FeedbackRequest,
    FeedbackResponse,
)


class TestHumanInTheLoop:
    """Test suite for human-in-the-loop feedback engine."""

    def test_initialization(self):
        hitl = HumanInTheLoop()
        assert hitl.history == []
        assert hitl.preferences == {}

    def test_create_tradeoff_request(self):
        hitl = HumanInTheLoop()
        options = [
            {"name": "Option A", "pros": ["fast"], "cons": ["expensive"]},
            {"name": "Option B", "pros": ["cheap"], "cons": ["slow"]},
        ]
        request = hitl.create_tradeoff_request(options)
        assert isinstance(request, FeedbackRequest)
        assert request.question == "Please select the preferred architecture option:"
        assert len(request.options) == 2

    def test_create_tradeoff_request_with_context(self):
        hitl = HumanInTheLoop()
        context = {"budget": 1000, "latency_target": "10ms"}
        request = hitl.create_tradeoff_request(
            [{"name": "A"}],
            context=context,
        )
        assert request.context == context

    def test_record_response(self):
        hitl = HumanInTheLoop()
        response = FeedbackResponse(
            request_id="tradeoff_0",
            selected_option="Option A",
            reasoning="Better performance",
        )
        hitl.record_response(response)
        assert len(hitl.history) == 1
        assert hitl.preferences["Option A"] == 1

    def test_record_multiple_responses(self):
        hitl = HumanInTheLoop()
        for i in range(5):
            hitl.record_response(FeedbackResponse(
                request_id=f"req_{i}",
                selected_option="Option A" if i < 3 else "Option B",
            ))
        assert len(hitl.history) == 5
        assert hitl.preferences["Option A"] == 3
        assert hitl.preferences["Option B"] == 2

    def test_preference_summary(self):
        hitl = HumanInTheLoop()
        hitl.record_response(FeedbackResponse(request_id="r1", selected_option="A"))
        hitl.record_response(FeedbackResponse(request_id="r2", selected_option="A"))
        hitl.record_response(FeedbackResponse(request_id="r3", selected_option="B"))
        summary = hitl.get_preference_summary()
        assert summary["total_feedback"] == 3
        assert summary["preferences"]["A"]["count"] == 2
        assert summary["preferences"]["B"]["count"] == 1
        assert summary["preferences"]["A"]["ratio"] == pytest.approx(2 / 3)

    def test_suggest_based_on_history(self):
        hitl = HumanInTheLoop()
        hitl.record_response(FeedbackResponse(request_id="r1", selected_option="A"))
        hitl.record_response(FeedbackResponse(request_id="r2", selected_option="A"))
        hitl.record_response(FeedbackResponse(request_id="r3", selected_option="B"))
        suggestion = hitl.suggest_based_on_history(["A", "B", "C"])
        assert suggestion == "A"

    def test_suggest_no_history(self):
        hitl = HumanInTheLoop()
        suggestion = hitl.suggest_based_on_history(["A", "B"])
        assert suggestion is None

    def test_suggest_partial_history(self):
        hitl = HumanInTheLoop()
        hitl.record_response(FeedbackResponse(request_id="r1", selected_option="C"))
        suggestion = hitl.suggest_based_on_history(["A", "B"])
        assert suggestion is None  # C not in options
