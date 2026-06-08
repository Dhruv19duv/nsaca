# NSACA Architecture

## System Overview

NSACA operates as a multi-stage pipeline that transforms natural language problem descriptions into production-grade software architectures.

## Pipeline Stages

### 1. Problem Parsing
- **Module**: `nsaca.core.problem_parser`
- Converts natural language → structured representation
- Extracts components, constraints, and requirements
- Uses LLM for semantic understanding

### 2. Graph Construction
- **Module**: `nsaca.graph.dependency_graph`
- Builds dependency DAG from parsed components
- Topological sorting for build order
- Cycle detection for circular dependency warnings

### 3. Knowledge Enrichment
- **Module**: `nsaca.graph.knowledge_graph`
- Maps problem to known patterns and technologies
- Queries historical solutions via vector similarity

### 4. Algorithm Selection
- **Module**: `nsaca.algorithms.selector`
- Rule-based + knowledge graph informed selection
- Considers input size, constraints, and requirements
- Suggests optimal data structures and algorithms

### 5. Architecture Simulation (MCTS)
- **Module**: `nsaca.reasoning.mcts`
- Monte Carlo Tree Search over architecture variants
- UCB1 for exploration/exploitation balance
- Heuristic evaluation of architecture quality

### 6. Code Generation & Optimization
- **Modules**: `nsaca.reasoning.llm_reasoner`, `nsaca.algorithms.optimizer`
- LLM-based code generation
- Compiler-inspired optimization passes:
  - Constant folding
  - Dead code elimination
  - Strength reduction

### 7. Self-Healing Debugging
- **Modules**: `nsaca.debugging.*`
- Automatic issue detection and fixing
- Adversarial test generation
- Edge case identification

### 8. Memory & Transfer Learning
- **Modules**: `nsaca.memory.*`
- Vector store for similar problem retrieval
- Graph memory for pattern storage
- Transfer learning from past solutions

### 9. Human Feedback Loop
- **Module**: `nsaca.feedback.human_loop`
- Interactive trade-off decisions
- Preference learning from engineer feedback

## Data Flow

```
Natural Language → Parser → Dependency Graph → Knowledge Graph
    ↓
Algorithm Selector → MCTS Reasoner → Architecture Candidates
    ↓
Code Generator → Optimizer → Debugger → Production Code
    ↓
Vector Store ← Memory Engine ← Graph Memory
```

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| AI Orchestration | Python 3.11+ | Main pipeline, LLM integration |
| DSA Engine | Rust | High-performance data structures |
| Knowledge Store | Neo4j | Graph database for patterns |
| Vector Store | ChromaDB | Similarity search |
| Containerization | Docker | Deployment and development |
| ML Models | Transformers | Code generation and analysis |
