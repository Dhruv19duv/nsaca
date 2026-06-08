"""Problem parser: converts natural language to structured representation.

Uses LLM reasoning to extract components, constraints, requirements,
and dependencies from user problem descriptions.
"""

from __future__ import annotations

import json
import structlog
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from nsaca.core.llm_client import chat_completion, strip_json_fences


logger = structlog.get_logger()


class ComponentType(Enum):
    """Types of software components the parser can identify."""
    SERVICE = "service"
    DATABASE = "database"
    CACHE = "cache"
    QUEUE = "queue"
    API = "api"
    ALGORITHM = "algorithm"
    DATA_STRUCTURE = "data_structure"
    UI = "ui"
    AUTH = "auth"
    STORAGE = "storage"
    COMPUTE = "compute"
    NETWORK = "network"


@dataclass
class Component:
    """A single software component extracted from problem description."""
    name: str
    type: ComponentType
    description: str
    dependencies: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Constraint:
    """A constraint on the system design."""
    category: str  # latency, throughput, cost, scalability, consistency
    description: str
    priority: int = 1  # 1=critical, 2=important, 3=nice-to-have


@dataclass
class ParsedProblem:
    """Structured representation of a user problem."""
    raw_description: str
    components: list[Component] = field(default_factory=list)
    constraints: list[Constraint] = field(default_factory=list)
    requirements: list[str] = field(default_factory=list)
    entity_relations: list[tuple[str, str, str]] = field(default_factory=list)


class ProblemParser:
    """Converts natural language problem descriptions into structured representations.

    Uses LLM to:
    - Extract software components and their types
    - Identify constraints (latency, cost, scalability)
    - Map entity relationships for knowledge graph construction
    - Discover implicit requirements
    """

    def __init__(self, llm_model: str = "gpt-4") -> None:
        self.llm_model = llm_model
        logger.info("ProblemParser initialized", model=llm_model)

    async def parse(self, description: str) -> ParsedProblem:
        """Parse a natural language description into structured form.

        Args:
            description: Natural language problem description.

        Returns:
            ParsedProblem with extracted components, constraints, and relations.
        """
        logger.info("Parsing problem", length=len(description))

        # Extract components
        components = await self._extract_components(description)

        # Extract constraints
        constraints = await self._extract_constraints(description)

        # Extract requirements
        requirements = await self._extract_requirements(description)

        # Build entity relations
        relations = self._build_relations(components)

        parsed = ParsedProblem(
            raw_description=description,
            components=components,
            constraints=constraints,
            requirements=requirements,
            entity_relations=relations,
        )

        logger.info(
            "Problem parsed",
            components=len(components),
            constraints=len(constraints),
            relations=len(relations),
        )
        return parsed

    async def _chat(self, system_prompt: str, user_prompt: str) -> str:
        """Make an OpenAI chat completion call via shared client."""
        return await chat_completion(
            model=self.llm_model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.3,
        )

    async def _extract_components(self, description: str) -> list[Component]:
        """Use LLM to extract software components from description."""
        system_prompt = (
            "Extract software components from the problem description. "
            "Return a JSON array of objects with: name (string), type (one of: "
            "service, database, cache, queue, api, algorithm, data_structure, ui, auth, "
            "storage, compute, network), description (string), dependencies (array of strings). "
            "Return ONLY valid JSON."
        )
        try:
            raw = await self._chat(system_prompt, description)
            data = json.loads(strip_json_fences(raw))
            components = []
            for item in data if isinstance(data, list) else []:
                try:
                    ct = ComponentType(item.get("type", "service"))
                except ValueError:
                    ct = ComponentType.SERVICE
                components.append(Component(
                    name=item.get("name", "unknown"),
                    type=ct,
                    description=item.get("description", ""),
                    dependencies=item.get("dependencies", []),
                ))
            return components
        except (json.JSONDecodeError, ImportError, ValueError) as e:
            logger.warning("LLM component extraction failed", error=str(e))
            return []

    async def _extract_constraints(self, description: str) -> list[Constraint]:
        """Use LLM to extract system constraints."""
        system_prompt = (
            "Extract system constraints from the problem description. "
            "Return a JSON array of objects with: category (one of: latency, throughput, "
            "cost, scalability, consistency, security), description (string), priority (1-3). "
            "Return ONLY valid JSON."
        )
        try:
            raw = await self._chat(system_prompt, description)
            data = json.loads(strip_json_fences(raw))
            constraints = []
            for item in data if isinstance(data, list) else []:
                constraints.append(Constraint(
                    category=item.get("category", "general"),
                    description=item.get("description", ""),
                    priority=item.get("priority", 2),
                ))
            return constraints
        except (json.JSONDecodeError, ImportError, ValueError) as e:
            logger.warning("LLM constraint extraction failed", error=str(e))
            return []

    async def _extract_requirements(self, description: str) -> list[str]:
        """Use LLM to extract functional requirements."""
        system_prompt = (
            "Extract functional requirements from the problem description. "
            "Return a JSON array of requirement strings. "
            "Return ONLY valid JSON."
        )
        try:
            raw = await self._chat(system_prompt, description)
            data = json.loads(strip_json_fences(raw))
            return data if isinstance(data, list) else []
        except (json.JSONDecodeError, ImportError, ValueError) as e:
            logger.warning("LLM requirement extraction failed", error=str(e))
            return []

    def _build_relations(
        self, components: list[Component]
    ) -> list[tuple[str, str, str]]:
        """Build entity-component relationships for knowledge graph."""
        relations = []
        for comp in components:
            for dep in comp.dependencies:
                relations.append((comp.name, "depends_on", dep))
            relations.append((comp.name, "is_type", comp.type.value))
        return relations
