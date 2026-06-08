"""Reasoning display for explainable AI.

Provides human-readable displays of the AI's reasoning process,
decision chains, and trade-off analyses.
"""

from __future__ import annotations

import structlog
from dataclasses import dataclass, field
from typing import Any


logger = structlog.get_logger()


@dataclass
class ReasoningDisplay:
    """A formatted reasoning display entry."""
    step: int
    title: str
    content: str
    confidence: float
    children: list[ReasoningDisplay] = field(default_factory=list)


class ReasoningVisualizer:
    """Formats and displays AI reasoning chains for human review.

    Renders:
    - Step-by-step reasoning chains
    - Decision trees
    - Trade-off comparison tables
    - Confidence intervals and explanations
    """

    def __init__(self) -> None:
        logger.info("ReasoningVisualizer initialized")

    def format_reasoning_chain(self, steps: list[dict[str, Any]]) -> str:
        """Format a reasoning chain as readable text.

        Args:
            steps: List of reasoning step dictionaries.

        Returns:
            Formatted string representation.
        """
        lines = ["=== NSACA Reasoning Chain ===\n"]
        for i, step in enumerate(steps, 1):
            lines.append(f"Step {i}: {step.get('thought', 'Unknown')}")
            lines.append(f"  Action: {step.get('action', 'N/A')}")
            lines.append(f"  Observation: {step.get('observation', 'N/A')}")
            confidence = step.get('confidence', 0)
            bar = '#' * int(confidence * 20) + '.' * (20 - int(confidence * 20))
            lines.append(f"  Confidence: [{bar}] {confidence:.1%}")
            lines.append("")
        return "\n".join(lines)

    def format_tradeoff_table(self, options: list[dict[str, Any]]) -> str:
        """Format trade-off options as a comparison table."""
        if not options:
            return "No options to display"

        headers = ["Option", "Score", "Latency", "Cost", "Scalability"]
        lines = ["| ".join(f"{h:>12}" for h in headers)]
        lines.append("-" * len(lines[0]))

        for opt in options:
            row = [
                f"{opt.get('name', 'N/A'):>12}",
                f"{opt.get('score', 0):>12.2f}",
                f"{opt.get('latency', 'N/A'):>12}",
                f"{opt.get('cost', 'N/A'):>12}",
                f"{opt.get('scalability', 'N/A'):>12}",
            ]
            lines.append(" | ".join(row))

        return "\n".join(lines)
