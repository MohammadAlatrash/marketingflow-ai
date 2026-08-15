from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore

from .llm import get_embeddings, get_llm
from .schemas import CampaignBrief, ContentPlan, ReviewResult, RouteDecision
from .state import MarketingState
from .utils import client_to_text, message_to_text

SUPPORTED_ROUTES = {
    "knowledge_answer",
    "content_only",
    "strategy_only",
    "full_campaign",
}
MAX_NOVELTY_REWRITES = 1


def supervisor_agent(state: MarketingState) -> dict:
    requested_route = state.get("requested_route")
    if requested_route in SUPPORTED_ROUTES:
        return {
            "route": requested_route,
            "route_reason": "Explicit task type selected by the user.",
        }

    client = state.get("client", {})
    request = state.get("request", "")
    llm = get_llm(temperature=0)
    router = llm.with_structured_output(RouteDecision)

    prompt = f"""
You are the Supervisor Agent for an AI marketing agency.
Choose exactly one route:
- knowledge_answer: factual question about the client's own business, products, offers, brand, or stored information.
- content_only: user wants copy/captions/posts and enough client context is already available; no market research or strategy is required.
- strategy_only: user wants marketing strategy/recommendations but not a full content calendar.
- full_campaign: user wants a content plan/calendar/campaign, or the task benefits from client knowledge + fresh web research + strategy + content creation.

Client snapshot:
{client_to_text(client)}

User request:
{request}
"""
    try:
        decision = router.invoke(prompt)
        return {"route": decision.route, "route_reason": decision.reason}
    except Exception:
        # A safe fallback keeps the workflow useful if structured routing fails.
        return {
            "route": "full_campaign",
            "route_reason": "Automatic routing was unavailable; full campaign fallback used.",
        }


def client_knowledge_agent(state: MarketingState) -> dict:
    """Small semantic RAG layer over onboarding data + optional client knowledge."""
    client = state.get("client", {})
    request = state.get("request", "")

    chunks: list[str] = []
    for key, value in client.items():
        if value not in (None, "", [], {}):
            chunks.append(f"{key.replace('_', ' ').title()}: {value}")

    if not chunks:
        return {"knowledge_context": "No client knowledge was provided."}

    # Split longer notes/documents into smaller retrieval chunks.
    expanded_chunks: list[str] = []
    for chunk in chunks:
        if len(chunk) <= 1200:
            expanded_chunks.append(chunk)
            continue
        paragraphs = [p.strip() for p in chunk.split("\n") if p.strip()]
        current = ""
        for paragraph in paragraphs:
            if len(current) + len(paragraph) + 1 > 1200 and current:
                expanded_chunks.append(current)
                current = paragraph
            else:
                current = f"{current}\n{paragraph}".strip()
        if current:
            expanded_chunks.append(current)

    documents = [Document(page_content=chunk) for chunk in expanded_chunks]
    try:
        vector_store = InMemoryVectorStore(embedding=get_embeddings())
        vector_store.add_documents(documents)
        results = vector_store.similarity_search(
            request or "client business information",
            k=min(6, len(documents)),
        )
        context = "\n".join(f"- {doc.page_content}" for doc in results)
        return {"knowledge_context": context}
    except Exception:
        # Keep the app usable if the embedding quota/network is temporarily unavailable.
        fallback = "\n".join(f"- {doc.page_content}" for doc in documents[:6])
        return {
            "knowledge_context": (
                "[Semantic retrieval unavailable; using verified client context.]\n"
                + fallback
            )
        }


def research_agent(state: MarketingState) -> dict:
    """Fresh web research using Gemini's built-in Google Search grounding."""
    client = state.get("client", {})
    request = state.get("request", "")
    knowledge = state.get("knowledge_context", "")

    model = get_llm(temperature=0.2)
    model_with_search = model.bind_tools([{"google_search": {}}])
    prompt = f"""
You are a marketing research agent. Use Google Search to research fresh, useful market insights for this task.
Focus on: current industry trends, customer pain points, competitor/content patterns, useful keywords, and content angles.
Do not invent facts. Keep the research concise and actionable. Mention source names/URLs when the tool provides them.

Client:
{client_to_text(client)}

Retrieved client context:
{knowledge}

Task:
{request}
"""
    try:
        response = model_with_search.invoke(prompt)
        return {"research": message_to_text(response)}
    except Exception:
        fallback_prompt = f"""
Web search could not run in this request. Do NOT claim that your information is current.
Using general marketing knowledge only, provide a concise fallback research brief and clearly label it as non-live research.

Client:
{client_to_text(client)}

Task:
{request}
"""
        response = model.invoke(fallback_prompt)
        return {
            "research": "Live web search unavailable.\n\n" + message_to_text(response)
        }


def knowledge_answer_agent(state: MarketingState) -> dict:
    llm = get_llm(temperature=0.1)
    prompt = f"""
Answer the user's question using ONLY the retrieved client context below.
If the answer is not present, clearly say that the client's stored information does not contain it.

User question:
{state.get('request', '')}

Retrieved client context:
{state.get('knowledge_context', '')}
"""
    response = llm.invoke(prompt)
    return {"final_output": message_to_text(response)}


def strategy_agent(state: MarketingState) -> dict:
    llm = get_llm(temperature=0.4)
    strategist = llm.with_structured_output(CampaignBrief)
    duration = state.get("duration_days", 7)
    prompt = f"""
You are a senior direct-response marketing strategist. Return a validated campaign brief.
Use the client's retrieved facts as the source of truth and web research only as external insight.
Cover audience awareness, pain/desire, offer, value proposition, big idea, reasons to believe,
objections, funnel stage, channel, primary objective, CTA, and proof restrictions.
The execution window is {duration} days. Never invent proof, guarantees, prices, or claims.

Client context:
{state.get('knowledge_context', '')}

Web research:
{state.get('research', 'Not requested.')}

User request:
{state.get('request', '')}
"""
    response = strategist.invoke(prompt)
    brief = (
        response
        if isinstance(response, CampaignBrief)
        else CampaignBrief.model_validate(response)
    )
    return {
        "strategy": brief.to_markdown(),
        "strategy_brief": brief.model_dump(),
    }


def content_creator_agent(state: MarketingState) -> dict:
    llm = get_llm(temperature=0.65)
    creator = llm.with_structured_output(ContentPlan)
    duration = state.get("duration_days", 7)
    rewrite_instruction = ""
    if state.get("rewrite_requested"):
        matched_patterns = "\n".join(
            f"- {match}" for match in state.get("novelty_matches", [])
        )
        rewrite_instruction = f"""
This is a single allowed novelty rewrite. Change the angle, hook, structure, and CTA.
Do not repeat these matched patterns:
{matched_patterns or '- A previously detected similar pattern.'}
"""
    prompt = f"""
You are a direct-response content creator. Return ready-to-use structured content, not ideas.
Create exactly {duration} days of content unless the user explicitly asks for something smaller.

For each day include:
- Day number
- Platform
- Format (post/reel/carousel/story/email/etc.)
- Objective
- Topic / hook
- Full caption or script
- CTA
- Suggested hashtags/keywords when relevant

Stay faithful to client facts. Do not invent prices, guarantees, offers, locations, or product claims.
Write in the language/tone requested by the client when available.
{rewrite_instruction}

Client context:
{state.get('knowledge_context', '')}

Research:
{state.get('research', 'Not requested.')}

Structured campaign brief:
{state.get('strategy_brief', state.get('strategy', 'Not requested.'))}

User request:
{state.get('request', '')}
"""
    response = creator.invoke(prompt)
    plan = response if isinstance(response, ContentPlan) else ContentPlan.model_validate(response)
    return {
        "content_plan": plan.to_markdown(),
        "content_items": [item.model_dump() for item in plan.items],
        "rewrite_requested": False,
    }


def novelty_gate_agent(state: MarketingState) -> dict:
    rewrite_count = state.get("rewrite_count", 0)
    should_rewrite = bool(state.get("novelty_requires_rewrite"))
    if should_rewrite and rewrite_count < MAX_NOVELTY_REWRITES:
        return {
            "rewrite_count": rewrite_count + 1,
            "rewrite_requested": True,
        }
    return {
        "rewrite_count": rewrite_count,
        "rewrite_requested": False,
    }


def reviewer_agent(state: MarketingState) -> dict:
    llm = get_llm(temperature=0.1)
    reviewer = llm.with_structured_output(ReviewResult)
    prompt = f"""
You are the quality reviewer for a marketing agency.
Review the draft against client facts and the requested task.
Check factual consistency, tone, repetition, CTA quality, completeness, and whether unsupported claims were invented.
Return a structured decision. `approved_content` is mandatory:
- For PASS, repeat the approved draft as structured content.
- For NEEDS_CHANGES, put the fully corrected structured content there.
Never approve unsupported claims. Never return an empty approved_content list.

Client context:
{state.get('knowledge_context', '')}

Task:
{state.get('request', '')}

Structured draft:
{state.get('content_items', [])}
"""
    try:
        response = reviewer.invoke(prompt)
        result = (
            response
            if isinstance(response, ReviewResult)
            else ReviewResult.model_validate(response)
        )
    except Exception:
        return {
            "review": "Quality review could not be completed. Content was withheld.",
            "review_status": "NEEDS_CHANGES",
            "review_issues": ["Quality review did not return a valid decision."],
            "approved_content_items": [],
            "approved_content_plan": "",
        }

    approved_plan = ContentPlan(items=result.approved_content)
    return {
        "review": result.to_markdown(),
        "review_status": result.status,
        "review_issues": result.issues,
        "approved_content_items": [item.model_dump() for item in result.approved_content],
        "approved_content_plan": approved_plan.to_markdown(),
    }


def finalizer_agent(state: MarketingState) -> dict:
    route = state.get("route", "full_campaign")
    if route == "strategy_only":
        final_output = state.get("strategy", "")
    else:
        review = state.get("review", "")
        content = state.get("approved_content_plan", "")
        strategy = state.get("strategy", "")
        research = state.get("research", "")
        if not content:
            content = "Content withheld pending a successful quality review."
        final_output = f"""# MarketingFlow AI Deliverable

## Strategy
{strategy or 'Not requested.'}

## Research Insights
{research or 'Not requested.'}

## Content
{content or 'Not requested.'}

## Quality Review
{review or 'Not requested.'}
""".strip()
    return {"final_output": final_output}
