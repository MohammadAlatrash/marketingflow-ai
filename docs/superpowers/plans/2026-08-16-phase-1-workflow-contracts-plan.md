# Phase 1 implementation plan — workflow contracts and correctness

Date: 2026-08-16

Design source: `../specs/2026-08-16-marketingflow-v3-upgrade-design.md`

## Objective

Make the existing LangGraph workflow deterministic where possible and ensure that only reviewer-approved or reviewer-corrected content reaches the final deliverable. Add structured direct-response data without breaking the current Streamlit text fields.

## Definition of done

- Strategy, content, and review outputs have validated Pydantic contracts.
- Existing `strategy`, `content_plan`, `review`, and `final_output` strings remain available to the current UI.
- An explicit supported route bypasses the supervisor LLM; free-form requests retain the existing LLM fallback.
- Reviewer-corrected content is the content delivered by the finalizer.
- A reviewer parsing/provider failure withholds unapproved content instead of silently passing it.
- The novelty rewrite route can execute at most once per workflow run.
- All graph paths are protected by offline unit tests.

## Tasks

### 1. Define structured contracts

Files:

- Modify `marketingflow/schemas.py`.
- Modify `marketingflow/state.py`.
- Add `tests/test_schemas.py`.

Changes:

- Add `CampaignBrief`, `ContentItem`, `ContentPlan`, and `ReviewResult` models.
- Keep fields focused on direct response: awareness, pain/desire, offer, value proposition, big idea, proof, objections, funnel stage, channel, objective, CTA, and proof restrictions.
- Add state fields for the structured values, approved content, explicit route, novelty decision, and rewrite count.
- Provide deterministic Markdown rendering from validated objects for backward-compatible UI output.

### 2. Add explicit routing and structured nodes

Files:

- Modify `marketingflow/nodes.py`.
- Add `tests/test_nodes.py`.

Changes:

- Bypass the supervisor model when `requested_route` is valid.
- Ask the strategy and creator models for structured output.
- Make the reviewer return a validated decision and an always-explicit approved/corrected content list.
- Fail closed when reviewer structured output fails.
- Keep prompts faithful to client facts and direct-response constraints.

### 3. Add a bounded novelty route

Files:

- Modify `marketingflow/nodes.py`.
- Modify `marketingflow/graph.py`.
- Modify `tests/test_graph_structure.py`.

Changes:

- Insert `novelty_gate` between creator and reviewer.
- Use a state decision supplied by the future persistent similarity service.
- Allow one return to `content_creator`, then route to reviewer regardless of a repeated request.
- Do not add vector storage or a novelty LLM in this phase.

### 4. Correct final delivery behavior

Files:

- Modify `marketingflow/nodes.py`.
- Extend `tests/test_nodes.py`.

Changes:

- Build final content from `approved_content_plan`, never from a rejected original draft.
- Keep strategy-only behavior unchanged.
- Include a clear withheld message if review failed or approved content is absent.
- Replace raw exception text in user-visible routing, retrieval, research, and Streamlit fallbacks with stable safe messages.

### 5. Run the local gate

Commands:

```bash
.venv/bin/python -m compileall -q marketingflow app.py run_cli.py tests
.venv/bin/python -m pytest
.venv/bin/python -c "import marketingflow.graph; import run_cli"
```

Verify the already-running Streamlit health endpoint on `localhost:8501`. No generation is submitted during automated checks.

## Out of scope

- Supabase, Auth, migrations, persistence, and Storage.
- Real vector similarity, content history, or feedback retrieval.
- New Streamlit pages or visual redesign.
- Live Gemini integration tests.

## Rollback boundary

Phase 1 is committed independently on `upgrade/v3-foundation`. The existing `main` branch and Phase 0 checkpoint remain intact.
