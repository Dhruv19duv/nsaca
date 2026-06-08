"""Tests for memory modules."""

import pytest
from nsaca.memory.vector_store import VectorStore
from nsaca.memory.graph_memory import GraphMemory
from nsaca.memory.transfer import TransferLearner


class TestVectorStore:
    """Test suite for vector database memory."""

    def test_initialization(self):
        store = VectorStore()
        assert store.size() == 0
        assert store.dimension == 1536

    def test_initialization_custom_dim(self):
        store = VectorStore(dimension=512)
        assert store.dimension == 512

    def test_store_and_retrieve(self):
        store = VectorStore(dimension=128)
        entry_id = store.store("Build a cache system", {"name": "cache_arch"})
        assert entry_id is not None
        assert store.size() == 1

        entry = store.get(entry_id)
        assert entry is not None
        assert entry.problem == "Build a cache system"
        assert entry.architecture == {"name": "cache_arch"}

    def test_find_similar(self):
        store = VectorStore(dimension=128)
        store.store("Build a distributed cache", {"name": "cache1"})
        store.store("Design a messaging queue", {"name": "queue1"})
        store.store("Create a caching layer", {"name": "cache2"})

        results = store.find_similar("Build a cache system", top_k=2)
        assert len(results) <= 2
        assert len(results) > 0

    def test_find_similar_empty(self):
        store = VectorStore(dimension=128)
        results = store.find_similar("anything", top_k=5)
        assert results == []

    def test_delete(self):
        store = VectorStore(dimension=128)
        entry_id = store.store("test", {})
        assert store.size() == 1
        deleted = store.delete(entry_id)
        assert deleted
        assert store.size() == 0

    def test_delete_nonexistent(self):
        store = VectorStore(dimension=128)
        deleted = store.delete("nonexistent_id")
        assert not deleted

    def test_cosine_similarity(self):
        store = VectorStore(dimension=128)
        a = [1.0] + [0.0] * 127
        b = [1.0] + [0.0] * 127
        assert store._cosine_similarity(a, b) == pytest.approx(1.0)

        c = [0.0] * 128
        assert store._cosine_similarity(a, c) == 0.0

    def test_embedding_deterministic(self):
        store = VectorStore(dimension=128)
        emb1 = store._embed("hello world")
        emb2 = store._embed("hello world")
        assert emb1 == emb2

    def test_embedding_normalized(self):
        store = VectorStore(dimension=128)
        emb = store._embed("test")
        norm = sum(x * x for x in emb) ** 0.5
        assert norm == pytest.approx(1.0, abs=0.01)


class TestGraphMemory:
    """Test suite for graph-based memory."""

    def test_initialization(self):
        memory = GraphMemory()
        stats = memory.get_stats()
        assert stats["total_nodes"] == 0
        assert stats["total_edges"] == 0

    def test_store(self):
        memory = GraphMemory()
        parsed = {"components": [{"name": "cache"}]}
        architecture = {"name": "cache_arch", "components": [{"name": "cache"}]}
        memory.store(parsed, architecture)
        stats = memory.get_stats()
        assert stats["total_nodes"] > 0

    def test_store_multiple(self):
        memory = GraphMemory()
        for i in range(3):
            memory.store(
                {"components": [{"name": f"comp_{i}"}]},
                {"name": f"arch_{i}", "components": []},
            )
        stats = memory.get_stats()
        assert stats["total_nodes"] > 3

    def test_find_patterns(self):
        memory = GraphMemory()
        memory.store({}, {"name": "test_arch"})
        patterns = memory.find_patterns("architecture")
        assert isinstance(patterns, list)

    def test_get_related(self):
        memory = GraphMemory()
        memory.store(
            {"components": [{"name": "a"}, {"name": "b"}]},
            {"name": "arch1", "components": [{"name": "a"}, {"name": "b"}]},
        )
        # node_0 is the problem node
        related = memory.get_related("node_0", max_hops=2)
        assert isinstance(related, list)

    def test_get_related_nonexistent(self):
        memory = GraphMemory()
        related = memory.get_related("nonexistent")
        assert related == []


class TestTransferLearner:
    """Test suite for transfer learning engine."""

    def test_initialization(self):
        learner = TransferLearner()
        assert learner.similarity_threshold == 0.7

    def test_initialization_custom_threshold(self):
        learner = TransferLearner(similarity_threshold=0.5)
        assert learner.similarity_threshold == 0.5

    def test_find_candidates(self):
        from nsaca.memory.vector_store import MemoryEntry
        learner = TransferLearner(similarity_threshold=0.3)
        entries = [
            MemoryEntry(
                id="1",
                problem="Build a cache",
                architecture={"name": "cache"},
                metadata={"similarity": 0.8},
            ),
            MemoryEntry(
                id="2",
                problem="Design a queue",
                architecture={"name": "queue"},
                metadata={"similarity": 0.2},
            ),
        ]
        candidates = learner.find_transfer_candidates("Build a caching system", entries)
        assert len(candidates) == 1  # only the high-similarity one
        assert candidates[0].similarity == 0.8

    def test_find_candidates_empty(self):
        learner = TransferLearner()
        candidates = learner.find_transfer_candidates("test", [])
        assert candidates == []

    def test_adapt_architecture(self):
        learner = TransferLearner()
        arch = {"name": "original", "components": ["a", "b"]}
        adapted = learner._adapt_architecture(arch, "new problem")
        assert adapted["transferred_from"] == "original"
        assert "adaptations" in adapted
