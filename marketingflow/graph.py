from langgraph.graph import END, START, StateGraph

from .nodes import (
    client_knowledge_agent,
    content_creator_agent,
    finalizer_agent,
    knowledge_answer_agent,
    research_agent,
    reviewer_agent,
    strategy_agent,
    supervisor_agent,
)
from .state import MarketingState


def after_supervisor(state: MarketingState) -> str:
    return state.get("route", "full_campaign")


def after_knowledge(state: MarketingState) -> str:
    route = state.get("route", "full_campaign")
    if route == "knowledge_answer":
        return "knowledge_answer"
    if route == "content_only":
        return "content_creator"
    return "research"


builder = StateGraph(MarketingState)

builder.add_node("supervisor", supervisor_agent)
builder.add_node("client_knowledge", client_knowledge_agent)
builder.add_node("research", research_agent)
builder.add_node("strategy", strategy_agent)
builder.add_node("content_creator", content_creator_agent)
builder.add_node("reviewer", reviewer_agent)
builder.add_node("knowledge_answer", knowledge_answer_agent)
builder.add_node("finalizer", finalizer_agent)

builder.add_edge(START, "supervisor")
builder.add_conditional_edges(
    "supervisor",
    after_supervisor,
    {
        "knowledge_answer": "client_knowledge",
        "content_only": "client_knowledge",
        "strategy_only": "client_knowledge",
        "full_campaign": "client_knowledge",
    },
)
builder.add_conditional_edges(
    "client_knowledge",
    after_knowledge,
    {
        "knowledge_answer": "knowledge_answer",
        "content_creator": "content_creator",
        "research": "research",
    },
)

builder.add_edge("knowledge_answer", END)
builder.add_edge("research", "strategy")

# Strategy-only tasks stop after strategy; campaign tasks continue to content.
def after_strategy(state: MarketingState) -> str:
    return "finalizer" if state.get("route") == "strategy_only" else "content_creator"

builder.add_conditional_edges(
    "strategy",
    after_strategy,
    {
        "finalizer": "finalizer",
        "content_creator": "content_creator",
    },
)
builder.add_edge("content_creator", "reviewer")
builder.add_edge("reviewer", "finalizer")
builder.add_edge("finalizer", END)

graph = builder.compile()
