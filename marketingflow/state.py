from typing import Any, Literal, TypedDict

RouteName = Literal[
    "knowledge_answer",
    "content_only",
    "strategy_only",
    "full_campaign",
]


class MarketingState(TypedDict, total=False):
    client: dict[str, Any]
    request: str
    duration_days: int
    route: RouteName
    route_reason: str
    knowledge_context: str
    research: str
    strategy: str
    content_plan: str
    review: str
    final_output: str
    errors: list[str]
