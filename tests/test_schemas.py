import pytest
from pydantic import ValidationError

from marketingflow.schemas import CampaignBrief, ContentItem, ContentPlan, ReviewResult


def make_content_item(**overrides) -> ContentItem:
    values = {
        "day": 1,
        "platform": "Instagram",
        "format": "Post",
        "objective": "Generate qualified leads",
        "hook": "Busy but still want sustainable progress?",
        "body": "A practical plan can fit the week you already have.",
        "cta": "Book a consultation",
        "keywords": ["fitness", "sustainable habits"],
    }
    values.update(overrides)
    return ContentItem(**values)


def test_campaign_brief_renders_direct_response_fields():
    brief = CampaignBrief(
        audience_awareness="Problem aware",
        pain_points=["No time for long workouts"],
        desires=["Sustainable progress"],
        offer="Online coaching",
        value_proposition="Personal plans for busy schedules",
        big_idea="Your plan should fit your life",
        reasons_to_believe=["Personalized weekly plan"],
        objections=["I do not have enough time"],
        funnel_stage="Consideration",
        channel="Instagram",
        primary_objective="Qualified leads",
        cta="Book a consultation",
        proof_restrictions=["Do not promise instant results"],
    )

    rendered = brief.to_markdown()

    assert "Problem aware" in rendered
    assert "Your plan should fit your life" in rendered
    assert "Do not promise instant results" in rendered


def test_content_plan_requires_at_least_one_item():
    with pytest.raises(ValidationError):
        ContentPlan(items=[])


def test_content_plan_renders_validated_items():
    plan = ContentPlan(items=[make_content_item()])

    rendered = plan.to_markdown()

    assert "Day 1" in rendered
    assert "Busy but still want" in rendered
    assert "Book a consultation" in rendered


def test_review_requires_approved_or_corrected_content():
    with pytest.raises(ValidationError):
        ReviewResult(status="NEEDS_CHANGES", issues=["Weak CTA"], approved_content=[])

