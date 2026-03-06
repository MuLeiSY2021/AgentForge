"""Run 子命令 — 执行用户请求。"""

from __future__ import annotations

import asyncio

import typer
from rich.console import Console

from agent_forge.agents.meta_agent import MetaAgent
from agent_forge.agents.supervisor import SupervisorAgent
from agent_forge.engine.context import RuntimeContext

run_app = typer.Typer(no_args_is_help=True)
console = Console()


@run_app.command("request")
def run_request(
    request: str = typer.Argument(..., help="用户需求描述"),
    skip_review: bool = typer.Option(False, "--skip-review", help="跳过监督审查"),
) -> None:
    """提交一个需求，系统自动匹配/创建 Agent 并执行。"""
    asyncio.run(_run(request, skip_review))


async def _run(request: str, skip_review: bool) -> None:
    ctx = RuntimeContext()
    meta = MetaAgent(ctx)

    console.print(f"[bold]Processing request:[/bold] {request}")
    result = await meta.handle_request(request)

    console.print(f"\n[bold]Status:[/bold] {result.status.value}")
    console.print(f"[bold]Output:[/bold]\n{result.final_output}")

    if not skip_review:
        console.print("\n[dim]Running supervisor review...[/dim]")
        supervisor = SupervisorAgent(ctx)
        review = await supervisor.review(request, result)
        console.print(f"[bold]Review:[/bold] score={review.get('score', '?')}, satisfied={review.get('satisfied', '?')}")
        if review.get("feedback"):
            console.print(f"[bold]Feedback:[/bold] {review['feedback']}")
