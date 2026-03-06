"""Group 子命令。"""

from __future__ import annotations

import asyncio
from uuid import UUID

import typer
from rich.console import Console
from rich.table import Table

from agent_forge.engine.context import RuntimeContext
from agent_forge.models.group import AgentGroup

group_app = typer.Typer(no_args_is_help=True)
console = Console()


def _ctx() -> RuntimeContext:
    return RuntimeContext()


@group_app.command("list")
def group_list() -> None:
    """列出所有 AgentGroup。"""
    groups = asyncio.run(_ctx().group_pool.list_all())
    if not groups:
        console.print("[dim]暂无 Group。[/dim]")
        return
    table = Table(title="Group Pool")
    table.add_column("ID", style="dim", max_width=8)
    table.add_column("Name", style="bold")
    table.add_column("Description")
    table.add_column("Agents", justify="right")
    for g in groups:
        table.add_row(str(g.id)[:8], g.name, g.description[:50], str(len(g.agent_ids)))
    console.print(table)


@group_app.command("show")
def group_show(
    id: str = typer.Argument(..., help="Group UUID"),
) -> None:
    """查看 Group 详情。"""
    group = asyncio.run(_ctx().group_pool.get(UUID(id)))
    if group is None:
        console.print(f"[red]Group {id} not found.[/red]")
        raise typer.Exit(1)
    console.print(group.model_dump_json(indent=2))


@group_app.command("delete")
def group_delete(
    id: str = typer.Argument(..., help="Group UUID"),
) -> None:
    """删除一个 Group。"""
    ok = asyncio.run(_ctx().group_pool.delete(UUID(id)))
    if ok:
        console.print(f"[green]Group {id} deleted.[/green]")
    else:
        console.print(f"[red]Group {id} not found.[/red]")
