"""AgentForge — 自生长的多智能体编排系统。

跟现有框架（CrewAI、AutoGen）不同，它们需要开发者手动定义 Agent 和工作流。
AgentForge 有一个 Agent 池和 Group 池，用户提出需求后，系统通过 RAG 自动匹配
最合适的 AgentGroup；如果没有合适的，系统会自动规划并创建新的 Agent 和工作流，
执行完后存入池中供未来复用。系统会越用越聪明。
"""

__version__ = "0.1.0"
