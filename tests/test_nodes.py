from unittest.mock import Mock

from marketingflow import nodes
from marketingflow.graph import after_novelty
from marketingflow.schemas import CampaignBrief, ContentItem, ContentPlan, ReviewResult


def make_content_item(body: str) -> ContentItem:
    return ContentItem(
        day=1,
        platform="Instagram",
        format="Post",
        objective="Lead generation",
        hook="A specific hook",
        body=body,
        cta="Book now",
        keywords=["marketing"],
    )


class FakeStructuredModel:
    def __init__(self, result=None, error: Exception | None = None):
        self.result = result
        self.error = error

    def invoke(self, _prompt):
        if self.error:
            raise self.error
        return self.result


class FakeLlm:
    def __init__(self, result=None, error: Exception | None = None):
        self.result = result
        self.error = error

    def with_structured_output(self, _schema):
        return FakeStructuredModel(self.result, self.error)


def test_explicit_route_bypasses_supervisor_model(monkeypatch):
    get_llm = Mock(side_effect=AssertionError("LLM should not be used"))
    monkeypatch.setattr(nodes, "get_llm", get_llm)

    result = nodes.supervisor_agent(
        {"requested_route": "content_only", "request": "Write a post"}
    )

    assert result == {
        "route": "content_only",
        "route_reason": "Explicit task type selected by the user.",
    }
    get_llm.assert_not_called()


def test_supervisor_failure_uses_safe_fallback_message(monkeypatch):
    monkeypatch.setattr(
        nodes,
        "get_llm",
        lambda **_kwargs: FakeLlm(error=RuntimeError("SECRET PROVIDER DETAIL")),
    )

    result = nodes.supervisor_agent({"request": "Build a campaign"})

    assert result["route"] == "full_campaign"
    assert "SECRET PROVIDER DETAIL" not in result["route_reason"]


def test_strategy_returns_validated_brief_and_compatible_markdown(monkeypatch):
    brief = CampaignBrief(
        audience_awareness="Problem aware",
        pain_points=["Inconsistent marketing"],
        desires=["Predictable qualified leads"],
        offer="Marketing strategy service",
        value_proposition="A practical system built around verified client facts",
        big_idea="Clarity before content volume",
        reasons_to_believe=["Structured research and review"],
        objections=["AI content may sound generic"],
        funnel_stage="Consideration",
        channel="LinkedIn",
        primary_objective="Qualified leads",
        cta="Book a discovery call",
        proof_restrictions=["Do not invent performance claims"],
    )
    monkeypatch.setattr(nodes, "get_llm", lambda **_kwargs: FakeLlm(result=brief))

    result = nodes.strategy_agent(
        {
            "request": "Build a strategy",
            "duration_days": 7,
            "knowledge_context": "Verified client facts",
            "research": "Verified market insight",
        }
    )

    assert result["strategy_brief"]["big_idea"] == "Clarity before content volume"
    assert "Book a discovery call" in result["strategy"]


def test_novelty_gate_allows_only_one_rewrite():
    first = nodes.novelty_gate_agent(
        {"novelty_requires_rewrite": True, "rewrite_count": 0}
    )
    assert first == {"rewrite_count": 1, "rewrite_requested": True}
    assert after_novelty(first) == "content_creator"

    second = nodes.novelty_gate_agent(
        {"novelty_requires_rewrite": True, "rewrite_count": 1}
    )
    assert second == {"rewrite_count": 1, "rewrite_requested": False}
    assert after_novelty(second) == "reviewer"


def test_reviewer_correction_reaches_finalizer(monkeypatch):
    corrected = make_content_item("Corrected and approved body")
    review = ReviewResult(
        status="NEEDS_CHANGES",
        issues=["Original claim was unsupported"],
        approved_content=[corrected],
    )
    monkeypatch.setattr(nodes, "get_llm", lambda **_kwargs: FakeLlm(result=review))

    reviewed = nodes.reviewer_agent(
        {
            "request": "Write a post",
            "knowledge_context": "Only verified facts",
            "content_plan": "UNAPPROVED ORIGINAL DRAFT",
            "content_items": [make_content_item("UNAPPROVED ORIGINAL DRAFT").model_dump()],
        }
    )
    final = nodes.finalizer_agent(
        {
            "route": "content_only",
            "approved_content_plan": reviewed["approved_content_plan"],
            "review": reviewed["review"],
        }
    )

    assert reviewed["review_status"] == "NEEDS_CHANGES"
    assert "Corrected and approved body" in final["final_output"]
    assert "UNAPPROVED ORIGINAL DRAFT" not in final["final_output"]


def test_reviewer_failure_withholds_unapproved_content(monkeypatch):
    monkeypatch.setattr(
        nodes,
        "get_llm",
        lambda **_kwargs: FakeLlm(error=RuntimeError("provider unavailable")),
    )

    reviewed = nodes.reviewer_agent(
        {
            "request": "Write a post",
            "knowledge_context": "Verified facts",
            "content_plan": "UNAPPROVED ORIGINAL DRAFT",
            "content_items": [make_content_item("UNAPPROVED ORIGINAL DRAFT").model_dump()],
        }
    )
    final = nodes.finalizer_agent(
        {
            "route": "content_only",
            "approved_content_plan": reviewed["approved_content_plan"],
            "review": reviewed["review"],
        }
    )

    assert reviewed["review_status"] == "NEEDS_CHANGES"
    assert reviewed["approved_content_plan"] == ""
    assert "withheld" in final["final_output"].lower()
    assert "UNAPPROVED ORIGINAL DRAFT" not in final["final_output"]


def test_creator_resets_rewrite_request_after_generation(monkeypatch):
    plan = ContentPlan(items=[make_content_item("Fresh rewritten body")])
    monkeypatch.setattr(nodes, "get_llm", lambda **_kwargs: FakeLlm(result=plan))

    result = nodes.content_creator_agent(
        {
            "duration_days": 1,
            "request": "Rewrite the similar content",
            "rewrite_requested": True,
            "novelty_matches": ["Previous repeated angle"],
        }
    )

    assert result["rewrite_requested"] is False
    assert result["content_items"][0]["body"] == "Fresh rewritten body"
