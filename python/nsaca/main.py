"""NSACA CLI entry point.

Main command-line interface for the NeuroSymbolic Autonomous Code Architect.
"""

from __future__ import annotations

import asyncio
import sys

import click
import structlog
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from nsaca.core.orchestrator import NSACAOrchestrator, SystemState

logger = structlog.get_logger()
console = Console()


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option("--model", default="gpt-4", help="LLM model to use")
@click.pass_context
def cli(ctx: click.Context, verbose: bool, model: str) -> None:
    """NSACA - NeuroSymbolic Autonomous Code Architect

    AI software architect that designs, optimizes, and self-improves
    software systems from natural language descriptions.
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["model"] = model

    if verbose:
        structlog.configure(wrapper_class=structlog.make_filtering_bound_logger(10))

    console.print(Panel.fit(
        "[bold cyan]NSACA[/] - NeuroSymbolic Autonomous Code Architect\n"
        f"[dim]Model: {model}[/]",
        border_style="cyan",
    ))


@cli.command()
@click.argument("description")
@click.pass_context
def solve(ctx: click.Context, description: str) -> None:
    """Solve a software architecture problem from natural language."""
    model = ctx.obj.get("model", "gpt-4")
    orchestrator = NSACAOrchestrator(llm_model=model)

    console.print(f"\n[bold]Processing:[/] {description}\n")

    async def _run():
        result = await orchestrator.run(description)

        if result.state == SystemState.COMPLETE:
            console.print(Panel(
                f"[bold green]Solution found![/]\n\n"
                f"Score: {result.architecture.get('score', 'N/A')}\n"
                f"Components: {len(result.architecture.get('components', []))}\n"
                f"Explanations: {len(result.explanations)}",
                title="Architecture Result",
                border_style="green",
            ))
        else:
            console.print(f"[bold red]Failed:[/] {', '.join(result.errors)}")

    asyncio.run(_run())


@cli.command()
@click.pass_context
def status(ctx: click.Context) -> None:
    """Show current NSACA status and configuration."""
    table = Table(title="NSACA Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Model", ctx.obj.get("model", "gpt-4"))
    table.add_row("Verbose", str(ctx.obj.get("verbose", False)))
    table.add_row("Version", "0.1.0")
    console.print(table)


@cli.command()
@click.pass_context
def info(ctx: click.Context) -> None:
    """Show information about NSACA modules."""
    table = Table(title="NSACA Modules")
    table.add_column("Module", style="cyan")
    table.add_column("Description")
    table.add_row("core", "Orchestrator, problem parser, decision engine")
    table.add_row("graph", "Dependency graphs, knowledge graphs, ASTs")
    table.add_row("algorithms", "Algorithm selection, complexity analysis, optimization")
    table.add_row("reasoning", "MCTS, LLM reasoning, Graph Neural Networks")
    table.add_row("memory", "Vector store, graph memory, transfer learning")
    table.add_row("debugging", "Self-healing, adversarial testing, edge cases")
    table.add_row("visualization", "Architecture & reasoning display")
    table.add_row("execution", "Benchmarking, distributed execution")
    table.add_row("feedback", "Human-in-the-loop feedback")
    console.print(table)


if __name__ == "__main__":
    cli()
