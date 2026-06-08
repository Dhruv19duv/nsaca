"""NSACA core orchestrator.

Main entry point that coordinates all subsystems: problem parsing,
graph construction, algorithm selection, reasoning, debugging, and
human-in-the-loop feedback.
"""

from __future__ import annotations

import structlog
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from nsaca.graph.dependency_graph import DependencyGraph
from nsaca.graph.knowledge_graph import KnowledgeGraph
from nsaca.algorithms.selector import AlgorithmSelector
from nsaca.reasoning.mcts import MCTSReasoner
from nsaca.memory.vector_store import VectorStore
from nsaca.memory.graph_memory import GraphMemory
from nsaca.debugging.self_healing import SelfHealingDebugger
from nsaca.visualization.architecture import ArchitectureVisualizer

logger = structlog.get_logger()


class SystemState(Enum):
    """Lifecycle states of the NSACA pipeline."""
    IDLE = "idle"
    PARSING = "parsing"
    ANALYZING = "analyzing"
    OPTIMIZING = "optimizing"
    DEBUGGING = "debugging"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class PipelineResult:
    """Result of a complete NSACA pipeline run."""
    state: SystemState
    architecture: dict[str, Any]
    optimized_code: str | None = None
    benchmark_results: list[dict[str, Any]] = field(default_factory=list)
    explanations: list[str] = field(default_factory=list)
    human_feedback: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class NSACAOrchestrator:
    """Main orchestrator that coordinates all NSACA subsystems.

    The orchestrator follows this pipeline:
    1. Parse user problem → structured representation
    2. Build dependency graph from problem analysis
    3. Query knowledge graph for known patterns
    4. Select optimal algorithms and data structures
    5. Run MCTS to simulate architecture candidates
    6. Optimize generated code (compiler passes)
    7. Debug and self-heal any issues
    8. Visualize and explain reasoning
    """

    def __init__(
        self,
        llm_model: str = "gpt-4",
        enable_visualization: bool = True,
        max_architecture_candidates: int = 50,
    ) -> None:
        self.llm_model = llm_model
        self.enable_visualization = enable_visualization
        self.max_architecture_candidates = max_architecture_candidates
        self.state = SystemState.IDLE

        # Initialize subsystems
        self.dep_graph = DependencyGraph()
        self.knowledge_graph = KnowledgeGraph()
        self.algorithm_selector = AlgorithmSelector()
        self.mcts = MCTSReasoner(max_iterations=max_architecture_candidates)
        self.vector_store = VectorStore()
        self.graph_memory = GraphMemory()
        self.debugger = SelfHealingDebugger()
        self.visualizer = ArchitectureVisualizer() if enable_visualization else None

        logger.info("NSACA Orchestrator initialized", model=llm_model)

    async def run(self, problem_description: str) -> PipelineResult:
        """Execute the full NSACA pipeline on a problem description.

        Args:
            problem_description: Natural language problem description.

        Returns:
            PipelineResult with architecture, code, benchmarks, and explanations.
        """
        result = PipelineResult(state=SystemState.IDLE, architecture={})

        try:
            # Step 1: Parse the problem
            self.state = SystemState.PARSING
            logger.info("Parsing problem", length=len(problem_description))
            parsed = await self._parse_problem(problem_description)
            result.explanations.append(f"Parsed {len(parsed.get('components', []))} components")

            # Step 2: Build dependency graph
            self.state = SystemState.ANALYZING
            self.dep_graph.build_from_parsed(parsed)
            self.knowledge_graph.enrich(parsed)

            # Step 3: Check memory for similar past solutions
            similar = self.vector_store.find_similar(problem_description, top_k=5)
            if similar:
                result.explanations.append(
                    f"Found {len(similar)} similar past solutions in memory"
                )

            # Step 4: Select algorithms
            self.state = SystemState.ANALYZING
            selected = self.algorithm_selector.select_for_problem(parsed)
            result.explanations.append(
                f"Selected {len(selected)} algorithms/data structures"
            )

            # Step 5: MCTS architecture simulation
            architecture = self.mcts.simulate(parsed, selected)
            result.architecture = architecture

            # Step 6: Optimize
            self.state = SystemState.OPTIMIZING
            optimized = await self._optimize(architecture)
            result.optimized_code = optimized

            # Step 7: Debug
            self.state = SystemState.DEBUGGING
            debug_result = await self.debugger.heal(result.optimized_code or "")
            if debug_result.fixed:
                result.optimized_code = debug_result.code
                result.explanations.append(f"Self-healed {len(debug_result.fixes)} issues")

            # Step 8: Store in memory for future reference
            self.vector_store.store(problem_description, architecture)
            self.graph_memory.store(parsed, architecture)

            result.state = SystemState.COMPLETE
            logger.info("Pipeline complete")

        except Exception as e:
            result.state = SystemState.FAILED
            result.errors.append(str(e))
            logger.error("Pipeline failed", error=str(e))

        return result

    async def _parse_problem(self, description: str) -> dict[str, Any]:
        """Parse natural language problem into structured representation."""
        # Placeholder for LLM-based parsing
        return {
            "raw": description,
            "components": [],
            "constraints": [],
            "requirements": [],
        }

    async def _optimize(self, architecture: dict[str, Any]) -> str:
        """Generate optimized code from architecture."""
        # Placeholder for code generation and optimization
        return "// Generated optimized code placeholder"
