"""Typer CLI 主入口。"""

from __future__ import annotations

import typer

from agent_forge.cli.agent_cmds import agent_app
from agent_forge.cli.group_cmds import group_app
from agent_forge.cli.run_cmds import run_app
from agent_forge.cli.tool_cmds import tool_app

app = typer.Typer(
    name="agent-forge",
    help="AgentForge — 自生长的多智能体编排系统。",
    no_args_is_help=True,
)

app.add_typer(agent_app, name="agent", help="管理 Agent 池。")
app.add_typer(group_app, name="group", help="管理 AgentGroup 池。")
app.add_typer(run_app, name="run", help="执行用户请求。")
app.add_typer(tool_app, name="tool", help="查看可用工具。")


@app.callback()
def main(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="启用详细日志"),
) -> None:
    from agent_forge.utils.logging import setup_logging

    setup_logging("DEBUG" if verbose else "INFO")
