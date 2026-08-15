from typing import Literal
from pydantic import BaseModel, Field


class RouteDecision(BaseModel):
    route: Literal[
        "knowledge_answer",
        "content_only",
        "strategy_only",
        "full_campaign",
    ] = Field(description="The best workflow for the user's request.")
    reason: str = Field(description="Short reason for the routing decision.")
