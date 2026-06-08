"""Edge case detection and analysis.

Identifies hidden edge cases, boundary conditions, and potential failure
modes in software architectures.
"""

from __future__ import annotations

import structlog
from dataclasses import dataclass, field
from typing import Any


logger = structlog.get_logger()


@dataclass
class EdgeCase:
    """A detected edge case."""
    name: str
    category: str  # boundary, concurrency, resource, data, temporal
    description: str
    severity: str  # critical, high, medium, low
    suggested_test: str


class EdgeCaseDetector:
    """Detects hidden edge cases in software designs.

    Analyzes architecture patterns to find:
    - Boundary conditions in data processing
    - Race conditions in concurrent systems
    - Resource exhaustion scenarios
    - Data consistency issues
    - Temporal ordering problems
    """

    def __init__(self) -> None:
        logger.info("EdgeCaseDetector initialized")

    def detect(self, architecture: dict[str, Any]) -> list[EdgeCase]:
        """Analyze architecture for potential edge cases.

        Args:
            architecture: Architecture specification.

        Returns:
            List of detected edge cases.
        """
        cases = []

        # Check for concurrency patterns
        components = architecture.get("components", [])
        if len(components) > 1:
            cases.append(EdgeCase(
                name="concurrent_access",
                category="concurrency",
                description="Multiple components may access shared state simultaneously",
                severity="high",
                suggested_test="Run with concurrent requests and verify data consistency",
            ))

        # Check for data flow
        if any("database" in str(c).lower() for c in components):
            cases.append(EdgeCase(
                name="database_connection_pool_exhaustion",
                category="resource",
                description="Connection pool may be exhausted under high load",
                severity="medium",
                suggested_test="Test with connection pool at max capacity",
            ))

        # Check for network dependencies
        if any("api" in str(c).lower() or "service" in str(c).lower() for c in components):
            cases.append(EdgeCase(
                name="network_partition",
                category="temporal",
                description="Network partition between services may cause stale data",
                severity="high",
                suggested_test="Simulate network partition and verify graceful degradation",
            ))

        # Check for data validation
        cases.append(EdgeCase(
            name="malformed_input",
            category="data",
            description="External input may contain unexpected formats",
            severity="medium",
            suggested_test="Fuzz test all input boundaries with malformed data",
        ))

        # Check for temporal ordering
        if len(components) > 3:
            cases.append(EdgeCase(
                name="event_ordering",
                category="temporal",
                description="Events may arrive out of order in distributed system",
                severity="medium",
                suggested_test="Replay events in random order and verify consistency",
            ))

        logger.info("Edge cases detected", count=len(cases))
        return cases
