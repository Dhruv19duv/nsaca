"""LLM-based reasoning engine.

Uses large language models for code generation, problem decomposition,
and architectural decision making.
"""

from __future__ import annotations

import json
import structlog
from dataclasses import dataclass, field
from typing import Any

from nsaca.core.llm_client import chat_completion, strip_json_fences


logger = structlog.get_logger()


@dataclass
class ReasoningStep:
    """A single step in the LLM reasoning chain."""
    step_number: int
    thought: str
    action: str
    observation: str
    confidence: float = 0.0


@dataclass
class ReasoningResult:
    """Complete reasoning chain result."""
    steps: list[ReasoningStep]
    conclusion: str
    confidence: float
    metadata: dict[str, Any] = field(default_factory=dict)


class LLMReasoner:
    """Chain-of-thought reasoning engine using LLMs.

    Provides structured reasoning for:
    - Problem decomposition
    - Algorithm selection justification
    - Architecture trade-off analysis
    - Code review and improvement suggestions
    """

    def __init__(self, model: str = "gpt-4", temperature: float = 0.7) -> None:
        self.model = model
        self.temperature = temperature
        logger.info("LLMReasoner initialized", model=model)

    async def _chat(self, system_prompt: str, user_prompt: str) -> str:
        """Make an OpenAI chat completion call via shared client."""
        return await chat_completion(
            model=self.model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=self.temperature,
        )

    async def reason(self, problem: str, context: dict[str, Any] | None = None) -> ReasoningResult:
        """Execute chain-of-thought reasoning on a problem.

        Uses GPT-4 to perform structured chain-of-thought reasoning:
        1. Decompose the problem into subproblems
        2. Identify applicable patterns and algorithms
        3. Evaluate candidate solutions
        """
        context_str = json.dumps(context, indent=2) if context else "None"

        system_prompt = (
            "You are an expert software architect. Perform chain-of-thought reasoning "
            "on the given problem. Return a JSON object with:\n"
            "- steps: array of {step_number, thought, action, observation, confidence}\n"
            "- conclusion: string summary\n"
            "- confidence: float 0-1\n"
            "Return ONLY valid JSON, no markdown fences."
        )

        user_prompt = (
            f"Problem: {problem}\n\n"
            f"Context: {context_str}\n\n"
            "Perform your analysis and return the JSON result."
        )

        try:
            raw = await self._chat(system_prompt, user_prompt)
            data = json.loads(strip_json_fences(raw))

            steps = []
            for s in data.get("steps", []):
                steps.append(ReasoningStep(
                    step_number=s.get("step_number", len(steps) + 1),
                    thought=s.get("thought", ""),
                    action=s.get("action", ""),
                    observation=s.get("observation", ""),
                    confidence=s.get("confidence", 0.0),
                ))

            return ReasoningResult(
                steps=steps,
                conclusion=data.get("conclusion", "Analysis complete"),
                confidence=data.get("confidence", 0.0),
            )

        except (json.JSONDecodeError, KeyError, ImportError, ValueError) as e:
            logger.warning("LLM reasoning failed, falling back to heuristic", error=str(e))
            return self._heuristic_reason(problem)

    def _heuristic_reason(self, problem: str) -> ReasoningResult:
        """Fallback heuristic reasoning when LLM is unavailable."""
        steps = [
            ReasoningStep(1, "Decompose problem", "decompose", f"Analyzing: {problem[:100]}", 0.7),
            ReasoningStep(2, "Match patterns", "pattern_match", "Querying knowledge base", 0.65),
            ReasoningStep(3, "Evaluate options", "evaluate", "Ranking candidates", 0.6),
        ]
        return ReasoningResult(
            steps=steps,
            conclusion="Heuristic analysis complete (LLM unavailable)",
            confidence=0.65,
        )

    async def generate_code(self, specification: dict[str, Any]) -> str:
        """Generate code from a structured specification using LLM."""
        logger.info("Generating code from specification")

        system_prompt = (
            "You are an expert software engineer. Generate clean, well-documented "
            "code based on the given specification. Return ONLY the code, no explanations."
        )
        user_prompt = f"Generate code for this specification:\n\n{json.dumps(specification, indent=2)}"

        try:
            return await self._chat(system_prompt, user_prompt)
        except (ImportError, ValueError) as e:
            logger.warning("LLM code generation failed", error=str(e))
            return f"# Generated code placeholder\n# Specification: {specification.get('name', 'unknown')}\npass"

    async def review_code(self, code: str) -> list[dict[str, Any]]:
        """Review code and suggest improvements using LLM."""
        system_prompt = (
            "You are a senior code reviewer. Analyze the code and return a JSON array "
            "of review items, each with: type (bug/style/perf/security), line (int), "
            "message (string), severity (low/medium/high). Return ONLY valid JSON."
        )
        user_prompt = f"Review this code:\n\n```\n{code}\n```"

        try:
            raw = await self._chat(system_prompt, user_prompt)
            return json.loads(strip_json_fences(raw))
        except (json.JSONDecodeError, ImportError, ValueError) as e:
            logger.warning("LLM code review failed", error=str(e))
            return [{
                "type": "info",
                "line": 1,
                "message": f"LLM review unavailable: {e}",
                "severity": "low",
            }]
