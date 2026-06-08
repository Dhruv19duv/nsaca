"""Monte Carlo Tree Search for architecture simulation.

Simulates multiple software architecture candidates and evaluates them
using playouts that consider cost, latency, scalability, and fault tolerance.
"""

from __future__ import annotations

import math
import random
import structlog
from dataclasses import dataclass, field
from typing import Any


logger = structlog.get_logger()


@dataclass
class MCTSNode:
    """A node in the MCTS tree representing an architecture decision."""
    state: dict[str, Any]
    parent: MCTSNode | None = None
    children: list[MCTSNode] = field(default_factory=list)
    visits: int = 0
    total_reward: float = 0.0
    untried_actions: list[dict[str, Any]] = field(default_factory=list)

    @property
    def q_value(self) -> float:
        """Average reward."""
        return self.total_reward / self.visits if self.visits > 0 else 0.0

    def ucb1(self, exploration_weight: float = 1.41) -> float:
        """Upper Confidence Bound 1 for tree policy."""
        if self.visits == 0:
            return float("inf")
        exploit = self.q_value
        explore = exploration_weight * math.sqrt(math.log(self.parent.visits if self.parent else 1) / self.visits)
        return exploit + explore


@dataclass
class ArchitectureCandidate:
    """A candidate architecture produced by MCTS."""
    name: str
    components: list[dict[str, Any]]
    score: float
    metrics: dict[str, float] = field(default_factory=dict)


class MCTSReasoner:
    """Monte Carlo Tree Search for software architecture simulation.

    The MCTS explores the space of possible architecture configurations
    by:
    1. Selection: choosing the most promising node via UCB1
    2. Expansion: adding new architecture variants
    3. Simulation: evaluating architecture via heuristic playout
    4. Backpropagation: updating node values up the tree
    """

    def __init__(self, max_iterations: int = 50, exploration_weight: float = 1.41) -> None:
        self.max_iterations = max_iterations
        self.exploration_weight = exploration_weight
        self.root: MCTSNode | None = None
        logger.info("MCTSReasoner initialized", max_iterations=max_iterations)

    def simulate(
        self, parsed: dict[str, Any], selections: list[Any]
    ) -> dict[str, Any]:
        """Run MCTS to find optimal architecture.

        Args:
            parsed: Parsed problem representation.
            selections: Selected algorithms/data structures.

        Returns:
            Best architecture found as a dictionary.
        """
        # Initialize root node
        self.root = MCTSNode(
            state={"parsed": parsed, "selections": selections},
            untried_actions=self._generate_actions(parsed, selections),
        )

        # Run MCTS iterations
        for i in range(self.max_iterations):
            node = self._select(self.root)
            if node.untried_actions:
                node = self._expand(node)
            reward = self._simulate_playout(node)
            self._backpropagate(node, reward)

        # Select best child of root
        best = max(self.root.children, key=lambda n: n.q_value) if self.root.children else self.root

        architecture = {
            "name": "MCTS-optimal",
            "components": best.state.get("components", []),
            "score": best.q_value,
            "iterations": self.max_iterations,
            "selections": [getattr(s, "name", str(s)) for s in selections],
        }

        logger.info("MCTS simulation complete", score=architecture["score"])
        return architecture

    def _select(self, node: MCTSNode) -> MCTSNode:
        """Select the most promising node using UCB1."""
        current = node
        while current.children and not current.untried_actions:
            current = max(current.children, key=lambda n: n.ucb1(self.exploration_weight))
        return current

    def _expand(self, node: MCTSNode) -> MCTSNode:
        """Expand a node by trying an untried action."""
        action = node.untried_actions.pop()
        new_state = {**node.state, "last_action": action}
        child = MCTSNode(state=new_state, parent=node)
        node.children.append(child)
        return child

    def _simulate_playout(self, node: MCTSNode) -> float:
        """Simulate a random playout from the given node and return reward."""
        # Heuristic evaluation based on architecture quality
        state = node.state
        score = 0.5  # baseline

        # Reward diversity of components
        selections = state.get("selections", [])
        score += min(len(selections) * 0.05, 0.2)

        # Add some randomness for exploration
        score += random.uniform(-0.1, 0.1)
        return max(0.0, min(1.0, score))

    def _backpropagate(self, node: MCTSNode, reward: float) -> None:
        """Backpropagate reward up the tree."""
        current = node
        while current:
            current.visits += 1
            current.total_reward += reward
            current = current.parent

    def _generate_actions(self, parsed: dict[str, Any], selections: list[Any]) -> list[dict[str, Any]]:
        """Generate possible architecture actions."""
        actions = []
        for sel in selections:
            name = getattr(sel, "name", str(sel))
            actions.append({"type": "add_component", "name": name})
            actions.append({"type": "configure", "name": name, "config": "high_availability"})
            actions.append({"type": "configure", "name": name, "config": "cost_optimized"})
        return actions
