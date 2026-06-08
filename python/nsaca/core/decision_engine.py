"""Decision engine for trade-off analysis.

Helps engineers navigate trade-offs between cost, latency, scalability,
and fault tolerance using multi-criteria decision analysis.
"""

from __future__ import annotations

import structlog
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


logger = structlog.get_logger()


class TradeOffCategory(Enum):
    """Categories of design trade-offs."""
    COST = "cost"
    LATENCY = "latency"
    SCALABILITY = "scalability"
    FAULT_TOLERANCE = "fault_tolerance"
    CONSISTENCY = "consistency"
    COMPLEXITY = "complexity"
    SECURITY = "security"


@dataclass
class TradeOffOption:
    """A single option in a trade-off decision."""
    name: str
    description: str
    scores: dict[TradeOffCategory, float] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def weighted_score(self, weights: dict[TradeOffCategory, float]) -> float:
        """Compute weighted score across all categories."""
        total = 0.0
        weight_sum = 0.0
        for cat, weight in weights.items():
            if cat in self.scores:
                total += self.scores[cat] * weight
                weight_sum += weight
        return total / weight_sum if weight_sum > 0 else 0.0


@dataclass
class DecisionContext:
    """Context for a trade-off decision."""
    problem_description: str
    options: list[TradeOffOption]
    weights: dict[TradeOffCategory, float]
    constraints: list[str] = field(default_factory=list)


@dataclass
class DecisionResult:
    """Result of trade-off analysis."""
    best_option: TradeOffOption
    rankings: list[tuple[str, float]]
    explanation: str
    risks: list[str] = field(default_factory=list)


class DecisionEngine:
    """Multi-criteria decision engine for architecture trade-offs.

    Evaluates architecture options against weighted criteria to help
    engineers make informed decisions about cost, latency, scalability,
    and fault tolerance.
    """

    # Default weights (balanced)
    DEFAULT_WEIGHTS = {
        TradeOffCategory.COST: 1.0,
        TradeOffCategory.LATENCY: 1.0,
        TradeOffCategory.SCALABILITY: 1.0,
        TradeOffCategory.FAULT_TOLERANCE: 1.0,
        TradeOffCategory.CONSISTENCY: 0.5,
        TradeOffCategory.COMPLEXITY: 0.8,
        TradeOffCategory.SECURITY: 1.0,
    }

    def __init__(self) -> None:
        logger.info("DecisionEngine initialized")

    def evaluate(
        self,
        context: DecisionContext,
        custom_weights: dict[TradeOffCategory, float] | None = None,
    ) -> DecisionResult:
        """Evaluate trade-off options and rank them.

        Args:
            context: The decision context with options and constraints.
            custom_weights: Optional override for default weights.

        Returns:
            DecisionResult with ranked options and explanation.
        """
        weights = custom_weights or self.DEFAULT_WEIGHTS

        # Score each option
        scored = []
        for option in context.options:
            score = option.weighted_score(weights)
            scored.append((option.name, score, option))

        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)

        rankings = [(name, score) for name, score, _ in scored]
        best = scored[0][2] if scored else context.options[0]

        # Generate explanation
        explanation = self._generate_explanation(best, rankings, context)

        # Identify risks
        risks = self._identify_risks(best, context)

        result = DecisionResult(
            best_option=best,
            rankings=rankings,
            explanation=explanation,
            risks=risks,
        )

        logger.info(
            "Decision evaluated",
            best=best.name,
            num_options=len(context.options),
        )
        return result

    def _generate_explanation(
        self,
        best: TradeOffOption,
        rankings: list[tuple[str, float]],
        context: DecisionContext,
    ) -> str:
        """Generate human-readable explanation for the decision."""
        lines = [f"Recommended: {best.name}"]
        lines.append(f"Description: {best.description}")
        if len(rankings) > 1:
            lines.append(
                f"Runner-up: {rankings[1][0]} (score: {rankings[1][1]:.2f})"
            )
        return "\n".join(lines)

    def _identify_risks(
        self, best: TradeOffOption, context: DecisionContext
    ) -> list[str]:
        """Identify potential risks with the chosen option."""
        risks = []
        for cat, score in best.scores.items():
            if score < 0.3:
                risks.append(f"Low {cat.value} score ({score:.1f})")
        return risks
