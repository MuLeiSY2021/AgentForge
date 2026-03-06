"""Tool 子命令 — 查看可用工具。"""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from agent_forge.engine.context import RuntimeContext

tool_app = typer.Typer(no_args_is_help=True)
console = Console()


@tool_app.command("list")
def tool_list() -> None:
    """列出所有已注册工具。"""
    ctx = RuntimeContext()
    specs = ctx.tool_registry.list_specs()
    if not specs:
        console.print("[dim]暂无工具。[/dim]")
        return
    table = Table(title="Registered Tools")
    table.add_column("Name", style="bold")
    table.add_column("Description")
    table.add_column("Parameters")
    for s in specs:
        params = ", ".join(f"{p.name}:{p.type}" for p in s.parameters) or "-"
        table.add_row(s.name, s.description, params)
    console.print(table)
