"""Knowledge graph for architectural patterns and best practices.

Stores relationships between software concepts, patterns, and technologies
to inform algorithm selection and architecture decisions.
"""

from __future__ import annotations

import structlog
from dataclasses import dataclass, field
from typing import Any

import networkx as nx


logger = structlog.get_logger()


@dataclass
class Concept:
    """A concept in the knowledge graph."""
    name: str
    category: str  # "pattern", "technology", "algorithm", "data_structure"
    description: str = ""
    properties: dict[str, Any] = field(default_factory=dict)


class KnowledgeGraph:
    """Knowledge graph encoding software engineering best practices.

    Stores:
    - Architectural patterns (microservices, event-driven, etc.)
    - Algorithm families and their use cases
    - Data structure properties and trade-offs
    - Technology compatibility relationships
    """

    def __init__(self) -> None:
        self.graph = nx.DiGraph()
        self.concepts: dict[str, Concept] = {}
        self._seed_knowledge()
        logger.info("KnowledgeGraph initialized", concepts=len(self.concepts))

    def _seed_knowledge(self) -> None:
        """Seed the knowledge graph with fundamental concepts."""
        # Data structure properties
        ds_data = [
            ("hash_map", "data_structure", {"time_lookup": "O(1)", "space": "O(n)", "ordered": False}),
            ("binary_search_tree", "data_structure", {"time_lookup": "O(log n)", "space": "O(n)", "ordered": True}),
            ("segment_tree", "data_structure", {"time_query": "O(log n)", "time_update": "O(log n)", "use_case": "range_queries"}),
            ("trie", "data_structure", {"time_prefix": "O(k)", "use_case": "prefix_matching"}),
            ("bloom_filter", "data_structure", {"space": "O(1)", "false_positives": True, "use_case": "membership_testing"}),
            ("suffix_array", "data_structure", {"time_search": "O(m log n)", "use_case": "string_matching"}),
            ("heap", "data_structure", {"time_insert": "O(log n)", "time_min_max": "O(1)", "use_case": "priority_queue"}),
            ("skip_list", "data_structure", {"time_lookup": "O(log n)", "concurrent": True}),
            ("b_tree", "data_structure", {"time_lookup": "O(log n)", "use_case": "database_indexing"}),
        ]

        # Pattern relationships
        patterns = [
            ("microservices", "pattern", {"scale": "horizontal", "complexity": "high"}),
            ("event_driven", "pattern", {"decoupling": "high", "consistency": "eventual"}),
            ("cQRS", "pattern", {"read_write": "separated", "consistency": "eventual"}),
            ("cache_aside", "pattern", {"latency": "low", "consistency": "eventual"}),
            ("write_through", "pattern", {"latency": "medium", "consistency": "strong"}),
        ]

        # Algorithm families
        algorithms = [
            ("dijkstra", "algorithm", {"type": "shortest_path", "negative_weights": False}),
            ("bellman_ford", "algorithm", {"type": "shortest_path", "negative_weights": True}),
            ("topological_sort", "algorithm", {"type": "ordering", "requires_dag": True}),
            ("binary_search", "algorithm", {"type": "search", "time": "O(log n)", "requires_sorted": True}),
            ("dynamic_programming", "algorithm", {"type": "optimization", "overlap": True}),
            ("monte_carlo_tree_search", "algorithm", {"type": "search", "exploration": True}),
        ]

        for name, category, props in ds_data + patterns + algorithms:
            concept = Concept(name=name, category=category, properties=props)
            self.add_concept(concept)

        # Add relationships
        relationships = [
            ("segment_tree", "replaces", "binary_search_tree", {"when": "range_queries_needed"}),
            ("trie", "outperforms", "hash_map", {"when": "prefix_matching"}),
            ("bloom_filter", "space_optimized_version_of", "hash_set", {"tradeoff": "false_positives"}),
            ("cache_aside", "uses", "hash_map", {}),
            ("microservices", "benefits_from", "event_driven", {}),
            ("dijkstra", "special_case_of", "bellman_ford", {"when": "no_negative_weights"}),
            ("binary_search", "requires", "sorted_data", {}),
        ]

        for src, rel, tgt, props in relationships:
            self.graph.add_edge(src, tgt, relationship=rel, **props)

    def add_concept(self, concept: Concept) -> None:
        """Add a concept to the knowledge graph."""
        self.concepts[concept.name] = concept
        self.graph.add_node(concept.name, category=concept.category, **concept.properties)

    def enrich(self, parsed: dict[str, Any]) -> None:
        """Enrich parsed problem with knowledge graph insights."""
        logger.info("Enriching with knowledge graph")
        for comp in parsed.get("components", []):
            name = comp.get("name", "")
            if name in self.graph:
                neighbors = list(self.graph.successors(name))
                if neighbors:
                    logger.info("Found related concepts", concept=name, related=neighbors)

    def find_related(self, concept_name: str, max_hops: int = 2) -> list[str]:
        """Find related concepts within max_hops."""
        if concept_name not in self.graph:
            return []
        related = set()
        current = {concept_name}
        for _ in range(max_hops):
            next_level = set()
            for node in current:
                next_level.update(self.graph.successors(node))
                next_level.update(self.graph.predecessors(node))
            related.update(next_level - current - {concept_name})
            current = next_level
        return sorted(related)

    def suggest_patterns(self, requirements: list[str]) -> list[str]:
        """Suggest architectural patterns based on requirements."""
        suggestions = []
        for name, data in self.concepts.items():
            if data.category == "pattern":
                # Simple matching: if requirement keywords appear in pattern properties
                for req in requirements:
                    req_lower = req.lower()
                    for key, val in data.properties.items():
                        if req_lower in str(val).lower() or req_lower in key.lower():
                            suggestions.append(name)
                            break
        return list(set(suggestions))
