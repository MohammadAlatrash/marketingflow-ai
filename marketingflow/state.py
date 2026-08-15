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
    requested_route: RouteName
    route: RouteName
    route_reason: str
    knowledge_context: str
    research: str
    strategy: str
    strategy_brief: dict[str, Any]
    content_plan: str
    content_items: list[dict[str, Any]]
    novelty_requires_rewrite: bool
    novelty_matches: list[str]
    rewrite_requested: bool
    rewrite_count: int
    review: str
    review_status: Literal["PASS", "NEEDS_CHANGES"]
    review_issues: list[str]
    approved_content_items: list[dict[str, Any]]
    approved_content_plan: str
    final_output: str
    errors: list[str]
