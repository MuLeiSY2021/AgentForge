"""Agent 子命令。"""

from __future__ import annotations

import asyncio
from uuid import UUID

import typer
from rich.console import Console
from rich.table import Table

from agent_forge.engine.context import RuntimeContext
from agent_forge.models.agent import Agent

agent_app = typer.Typer(no_args_is_help=True)
console = Console()


def _ctx() -> RuntimeContext:
    return RuntimeContext()


@agent_app.command("list")
def agent_list() -> None:
    """列出所有 Agent。"""
    agents = asyncio.run(_ctx().agent_pool.list_all())
    if not agents:
        console.print("[dim]暂无 Agent。[/dim]")
        return
    table = Table(title="Agent Pool")
    table.add_column("ID", style="dim", max_width=8)
    table.add_column("Name", style="bold")
    table.add_column("Role")
    table.add_column("Tools")
    for a in agents:
        table.add_row(str(a.id)[:8], a.name, a.role, ", ".join(a.tool_names) or "-")
    console.print(table)


@agent_app.command("add")
def agent_add(
    name: str = typer.Argument(..., help="Agent 名称"),
    role: str = typer.Option("", "--role", "-r", help="角色描述"),
    backstory: str = typer.Option("", "--backstory", "-b", help="背景故事"),
) -> None:
    """手动添加一个 Agent。"""
    agent = Agent(name=name, role=role, backstory=backstory)
    asyncio.run(_ctx().agent_pool.add(agent))
    console.print(f"[green]Agent '{name}' created: {agent.id}[/green]")


@agent_app.command("show")
def agent_show(
    id: str = typer.Argument(..., help="Agent UUID"),
) -> None:
    """查看 Agent 详情。"""
    agent = asyncio.run(_ctx().agent_pool.get(UUID(id)))
    if agent is None:
        console.print(f"[red]Agent {id} not found.[/red]")
        raise typer.Exit(1)
    console.print(agent.model_dump_json(indent=2))


@agent_app.command("delete")
def agent_delete(
    id: str = typer.Argument(..., help="Agent UUID"),
) -> None:
    """删除一个 Agent。"""
    ok = asyncio.run(_ctx().agent_pool.delete(UUID(id)))
    if ok:
        console.print(f"[green]Agent {id} deleted.[/green]")
    else:
        console.print(f"[red]Agent {id} not found.[/red]")
