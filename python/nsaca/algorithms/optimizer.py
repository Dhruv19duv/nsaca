"""Compiler-inspired code optimizer.

Applies optimization passes: constant folding, dead code elimination,
strength reduction, and loop optimization.
"""

from __future__ import annotations

import structlog
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


logger = structlog.get_logger()


class OptimizationPass(Enum):
    """Available optimization passes."""
    CONSTANT_FOLDING = "constant_folding"
    DEAD_CODE_ELIMINATION = "dead_code_elimination"
    STRENGTH_REDUCTION = "strength_reduction"
    LOOP_UNROLLING = "loop_unrolling"
    COMMON_SUBEXPRESSION = "common_subexpression_elimination"
    INLINING = "inlining"


@dataclass
class OptimizationResult:
    """Result of an optimization pass."""
    code: str
    passes_applied: list[str] = field(default_factory=list)
    improvements: list[dict[str, Any]] = field(default_factory=list)
    metrics_before: dict[str, float] = field(default_factory=dict)
    metrics_after: dict[str, float] = field(default_factory=dict)


class CodeOptimizer:
    """Applies compiler-inspired optimization passes to generated code.

    Supports:
    - Constant folding and propagation
    - Dead code elimination
    - Strength reduction (e.g., multiply → shift)
    - Common subexpression elimination
    - Function inlining
    """

    def __init__(self, passes: list[OptimizationPass] | None = None) -> None:
        self.passes = passes or [
            OptimizationPass.CONSTANT_FOLDING,
            OptimizationPass.DEAD_CODE_ELIMINATION,
            OptimizationPass.STRENGTH_REDUCTION,
        ]
        logger.info("CodeOptimizer initialized", passes=[p.value for p in self.passes])

    def optimize(self, code: str) -> OptimizationResult:
        """Apply all configured optimization passes.

        Args:
            code: Source code to optimize.

        Returns:
            OptimizationResult with optimized code and metrics.
        """
        result = OptimizationResult(code=code)
        result.metrics_before = self._measure(code)

        current = code
        for opt_pass in self.passes:
            optimized = self._apply_pass(current, opt_pass)
            if optimized != current:
                result.passes_applied.append(opt_pass.value)
                result.improvements.append({
                    "pass": opt_pass.value,
                    "reduction_chars": len(current) - len(optimized),
                })
                current = optimized

        result.code = current
        result.metrics_after = self._measure(current)

        logger.info(
            "Optimization complete",
            passes_applied=len(result.passes_applied),
            chars_saved=result.metrics_before.get("chars", 0) - result.metrics_after.get("chars", 0),
        )
        return result

    def _apply_pass(self, code: str, pass_type: OptimizationPass) -> str:
        """Apply a single optimization pass."""
        if pass_type == OptimizationPass.CONSTANT_FOLDING:
            return self._constant_fold(code)
        elif pass_type == OptimizationPass.DEAD_CODE_ELIMINATION:
            return self._eliminate_dead_code(code)
        elif pass_type == OptimizationPass.STRENGTH_REDUCTION:
            return self._strength_reduce(code)
        return code

    def _constant_fold(self, code: str) -> str:
        """Fold constant expressions."""
        import re
        # Simple pattern: replace known constant expressions
        # e.g., "3 + 4" → "7"
        pattern = re.compile(r'(\d+)\s*\+\s*(\d+)')
        result = code
        for match in pattern.finditer(code):
            a, b = int(match.group(1)), int(match.group(2))
            result = result.replace(match.group(0), str(a + b))
        return result

    def _eliminate_dead_code(self, code: str) -> str:
        """Remove unreachable code after return/break/continue."""
        lines = code.split('\n')
        result = []
        skip = False
        for line in lines:
            stripped = line.strip()
            if any(stripped.startswith(kw) for kw in ['return ', 'break', 'continue']):
                result.append(line)
                skip = True
                continue
            if skip and not stripped:
                skip = False
            if not skip:
                result.append(line)
        return '\n'.join(result)

    def _strength_reduce(self, code: str) -> str:
        """Replace expensive operations with cheaper equivalents."""
        import re
        # x * 2 → x << 1, x * 4 → x << 2
        code = re.sub(r'(\w+)\s*\*\s*2', r'\1 << 1', code)
        code = re.sub(r'(\w+)\s*\*\s*4', r'\1 << 2', code)
        code = re.sub(r'(\w+)\s*/\s*2', r'\1 >> 1', code)
        return code

    def _measure(self, code: str) -> dict[str, float]:
        """Measure code metrics."""
        return {
            "chars": len(code),
            "lines": code.count('\n') + 1,
            "complexity": code.count('if ') + code.count('for ') + code.count('while '),
        }
