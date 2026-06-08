# NSACA Setup Guide

## Quick Setup (Windows)

Since bash isn't available in Codebuff, run these commands in **PowerShell** or **Command Prompt**:

### Step 1: Install Git for Windows (required for Codebuff terminal)

Download and install from: https://git-scm.com/download/win

After install, set the bash path:
```
set CODEBUFF_GIT_BASH_PATH=C:\Program Files\Git\bin\bash.exe
```

### Step 2: Install uv (Python package manager)

```
pip install uv
```

### Step 3: Install Python dependencies

```
cd C:\Users\paliw\nsaca
uv sync
```

### Step 4: Install Rust (for DSA engine)

Download from: https://rustup.rs

Then:
```
cd C:\Users\paliw\nsaca\rust
cargo build --release
```

### Step 5: Set up API key

```
copy .env.example .env
```

Edit `.env` and replace `sk-your-api-key-here` with your actual OpenAI API key from:
https://platform.openai.com/api-keys

### Step 6: Run tests

```
uv run pytest python/tests/ -v
```

### Step 7: Try the CLI

```
uv run python -m nsaca.main --help
uv run python -m nsaca.main solve "Design a distributed caching system"
```

## What Each Module Does

| Module | Purpose |
|--------|---------|
| `core/` | Orchestrator, problem parser, decision engine |
| `graph/` | Dependency graphs, knowledge graphs, ASTs |
| `algorithms/` | Algorithm selection, complexity analysis, optimization |
| `reasoning/` | MCTS, LLM reasoning, Graph Neural Networks |
| `memory/` | Vector store, graph memory, transfer learning |
| `debugging/` | Self-healing, adversarial testing, edge cases |
| `visualization/` | Architecture diagrams (Mermaid export) |
| `execution/` | Benchmarking, distributed execution |
| `feedback/` | Human-in-the-loop preference learning |
