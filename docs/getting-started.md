# Getting Started with NSACA

## Prerequisites

- Python 3.11 or higher
- Rust 1.75 or higher (for DSA engine)
- Docker & Docker Compose (optional, for containerized development)
- [uv](https://github.com/astral-sh/uv) package manager

## Installation

### Option 1: Local Development

```bash
# Clone the repository
git clone <repo-url>
cd nsaca

# Install Python dependencies
uv sync

# Build the Rust DSA engine
cd rust && cargo build --release && cd ..

# Copy environment config
cp .env.example .env
# Edit .env with your API keys
```

### Option 2: Docker

```bash
# Copy environment config
cp .env.example .env

# Start all services
docker compose up --build
```

## Usage

### CLI

```bash
# Get help
uv run python -m nsaca.main --help

# Solve a problem
uv run python -m nsaca.main solve "Design a real-time chat system that supports 1M concurrent users"

# Check status
uv run python -m nsaca.main status

# List modules
uv run python -m nsaca.main info
```

### Python API

```python
import asyncio
from nsaca.core.orchestrator import NSACAOrchestrator

async def main():
    orchestrator = NSACAOrchestrator(llm_model="gpt-4")
    result = await orchestrator.run(
        "Build a distributed caching system with sub-millisecond latency"
    )
    print(f"State: {result.state}")
    print(f"Architecture: {result.architecture}")

asyncio.run(main())
```

### Individual Modules

```python
# Algorithm selection
from nsaca.algorithms.selector import AlgorithmSelector

selector = AlgorithmSelector()
selections = selector.select_for_requirements([
    "range queries",
    "prefix search",
    "large dataset"
])
for s in selections:
    print(f"{s.name}: {s.reasoning}")

# Benchmarking
from nsaca.execution.benchmark import BenchmarkRunner, BenchmarkConfig

runner = BenchmarkRunner(BenchmarkConfig(
    name="sort_compare",
    input_sizes=[1000, 10000, 100000]
))

# MCTS Architecture Search
from nsaca.reasoning.mcts import MCTSReasoner

mcts = MCTSReasoner(max_iterations=100)
architecture = mcts.simulate(parsed_problem, algorithm_selections)
```

## Testing

```bash
# Run Python tests
uv run pytest python/tests/ -v

# Run Rust tests
cd rust && cargo test

# Run with coverage
uv run pytest python/tests/ --cov=nsaca
```

## Project Structure

```
nsaca/
├── python/nsaca/           # AI orchestration (Python)
│   ├── core/               # Orchestrator, parser, decision engine
│   ├── graph/              # Dependency & knowledge graphs
│   ├── algorithms/         # Selection, complexity, optimization
│   ├── reasoning/          # MCTS, LLM, GNN
│   ├── memory/             # Vector store, graph memory
│   ├── debugging/          # Self-healing, adversarial
│   ├── visualization/      # Architecture diagrams
│   ├── execution/          # Benchmarking
│   └── feedback/           # Human-in-the-loop
├── rust/                   # DSA engine (Rust)
├── docker/                 # Dockerfiles
└── docs/                   # Documentation
```

## Next Steps

1. Set up your OpenAI API key in `.env`
2. Try the CLI with a simple problem description
3. Explore individual modules (start with `algorithms.selector`)
4. Run the test suite to verify everything works
5. Build the Rust engine for high-performance operations
