"""Human-in-the-loop feedback engine.

Enables engineers to guide trade-offs, approve decisions, and provide
feedback that improves future architecture choices.
"""

from __future__ import annotations

import structlog
from dataclasses import dataclass, field
from typing import Any, Callable


logger = structlog.get_logger()


@dataclass
class FeedbackRequest:
    """A request for human feedback."""
    id: str
    question: str
    options: list[dict[str, Any]]
    context: dict[str, Any] = field(default_factory=dict)
    required: bool = True


@dataclass
class FeedbackResponse:
    """Human response to a feedback request."""
    request_id: str
    selected_option: str
    reasoning: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class HumanInTheLoop:
    """Interactive feedback engine for human-guided decision making.

    Supports:
    - Trade-off decisions (cost vs latency vs scalability)
    - Architecture approval gates
    - Constraint prioritization
    - Continuous learning from human preferences
    """

    def __init__(self) -> None:
        self.history: list[FeedbackResponse] = []
        self.preferences: dict[str, Any] = {}
        logger.info("HumanInTheLoop initialized")

    def create_tradeoff_request(
        self,
        options: list[dict[str, Any]],
        context: dict[str, Any] | None = None,
    ) -> FeedbackRequest:
        """Create a trade-off decision request for human review.

        Args:
            options: List of options with pros/cons.
            context: Additional context for the decision.

        Returns:
            FeedbackRequest ready for human review.
        """
        request = FeedbackRequest(
            id=f"tradeoff_{len(self.history)}",
            question="Please select the preferred architecture option:",
            options=options,
            context=context or {},
        )
        logger.info("Trade-off request created", options=len(options))
        return request

    def record_response(self, response: FeedbackResponse) -> None:
        """Record a human feedback response and update preferences."""
        self.history.append(response)

        # Update learned preferences
        self.preferences[response.selected_option] = (
            self.preferences.get(response.selected_option, 0) + 1
        )

        logger.info(
            "Feedback recorded",
            request_id=response.request_id,
            selected=response.selected_option,
        )

    def get_preference_summary(self) -> dict[str, Any]:
        """Get a summary of learned human preferences."""
        total = sum(self.preferences.values()) or 1
        return {
            "total_feedback": len(self.history),
            "preferences": {
                k: {"count": v, "ratio": v / total}
                for k, v in self.preferences.items()
            },
        }

    def suggest_based_on_history(self, options: list[str]) -> str | None:
        """Suggest the best option based on historical preferences."""
        best = None
        best_count = -1
        for opt in options:
            count = self.preferences.get(opt, 0)
            if count > best_count:
                best_count = count
                best = opt
        return best if best_count > 0 else None
