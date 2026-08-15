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


class CampaignBrief(BaseModel):
    audience_awareness: str
    pain_points: list[str] = Field(min_length=1)
    desires: list[str] = Field(min_length=1)
    offer: str
    value_proposition: str
    big_idea: str
    reasons_to_believe: list[str] = Field(min_length=1)
    objections: list[str] = Field(default_factory=list)
    funnel_stage: str
    channel: str
    primary_objective: str
    cta: str
    proof_restrictions: list[str] = Field(default_factory=list)

    def to_markdown(self) -> str:
        return "\n".join(
            [
                "# Direct-response campaign brief",
                f"\n**Audience awareness:** {self.audience_awareness}",
                f"**Offer:** {self.offer}",
                f"**Value proposition:** {self.value_proposition}",
                f"**Big idea:** {self.big_idea}",
                f"**Funnel stage:** {self.funnel_stage}",
                f"**Channel:** {self.channel}",
                f"**Primary objective:** {self.primary_objective}",
                f"**CTA:** {self.cta}",
                _markdown_list("Pain points", self.pain_points),
                _markdown_list("Desires", self.desires),
                _markdown_list("Reasons to believe", self.reasons_to_believe),
                _markdown_list("Objections", self.objections),
                _markdown_list("Proof restrictions", self.proof_restrictions),
            ]
        ).strip()


class ContentItem(BaseModel):
    day: int = Field(ge=1)
    platform: str
    format: str
    objective: str
    hook: str
    body: str
    cta: str
    keywords: list[str] = Field(default_factory=list)

    def to_markdown(self) -> str:
        keywords = ", ".join(self.keywords) if self.keywords else "Not requested."
        return "\n".join(
            [
                f"## Day {self.day}: {self.hook}",
                f"- **Platform:** {self.platform}",
                f"- **Format:** {self.format}",
                f"- **Objective:** {self.objective}",
                "",
                self.body,
                "",
                f"**CTA:** {self.cta}",
                f"**Keywords:** {keywords}",
            ]
        )


class ContentPlan(BaseModel):
    items: list[ContentItem] = Field(min_length=1)

    def to_markdown(self) -> str:
        return "\n\n".join(item.to_markdown() for item in self.items)


class ReviewResult(BaseModel):
    status: Literal["PASS", "NEEDS_CHANGES"]
    issues: list[str] = Field(default_factory=list)
    approved_content: list[ContentItem] = Field(min_length=1)

    def to_markdown(self) -> str:
        return "\n".join(
            [
                f"**Status:** {self.status}",
                _markdown_list("Quality notes", self.issues),
            ]
        ).strip()


def _markdown_list(title: str, items: list[str]) -> str:
    if not items:
        return f"\n### {title}\n- None."
    return f"\n### {title}\n" + "\n".join(f"- {item}" for item in items)
