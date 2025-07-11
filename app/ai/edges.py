from typing import Literal

from langgraph.constants import END

from app.ai.state import StateBot


async def need_human_attention(state: StateBot) -> Literal["__end__", "memory_injection_node"]:
    intention = state.get("intention")
    if intention == "needs_human":
        return END
    return "memory_injection_node"

