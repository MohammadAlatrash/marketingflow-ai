# MarketingFlow AI V3 upgrade design

Date: 2026-08-16

Status: Approved direction; written specification awaiting final user review
Target: `/Users/imac/IMac/Mo/projects/Ai/marketingflow_ai`

## 1. Objective

Upgrade the working MarketingFlow AI project in place into a persistent multi-user marketing workspace without rebuilding the working LangGraph application or overlaying the unverified V3 ZIP wholesale.

The upgrade must maximize useful output per model call, preserve current behavior while migration is in progress, minimize dependencies and external services, and provide strong tenant isolation.

## 2. Current baseline

The current repository contains:

- A working Streamlit entry point in `app.py`.
- A compiled LangGraph with supervisor, client knowledge, research, strategy, creator, reviewer, knowledge answer, and finalizer nodes.
- Gemini generation, embeddings, and Google Search grounding.
- In-memory retrieval over form data and TXT/Markdown uploads.
- One graph-structure test, but no installed pytest in the local environment.
- No authentication, persistent application database, campaign history, content library, feedback memory, or persistent vector search.

The downloaded `MarketingFlow_AI_V3_Persistent.zip` contains useful prototype modules and UI ideas, but it is not the running repository and has not been validated by tests.

## 3. Approaches considered

### A. Selective in-place upgrade — selected

Keep the current repository as the master. Reuse reviewed V3 concepts and code in small commits, adapt them to the current codebase, and verify every phase before continuing.

Benefits:

- Preserves known working behavior.
- Produces small, reviewable changes.
- Allows unsafe V3 decisions to be corrected before they reach production.
- Avoids recreating working graph, prompts, and UI behavior.

### B. Overlay the V3 ZIP — rejected

This is faster initially but would introduce two identity systems, service-key database access, duplicated SQLite/Supabase repositories, incomplete novelty logic, and insufficient tests in one large change.

### C. Rebuild the application — rejected

This would waste the existing graph, UI, Gemini integration, and tested setup, while increasing risk and delivery time.

## 4. Target architecture

Runtime services are limited to:

1. **Gemini** for generation, structured extraction, embeddings, and optional grounded research.
2. **Supabase** for Auth, Postgres, Storage, and pgvector.

The application keeps:

- Streamlit as the UI.
- LangGraph as workflow orchestration.
- The existing Python package and graph export in `langgraph.json`.

The initial production path does not add Redis, Celery, Pinecone, Chroma, FAISS, a second authentication service, LangSmith hosting, or Edge Functions.

## 5. Component boundaries

### UI layer

- `app.py` remains the stable entry point to preserve existing run commands.
- When the persistent product pages are introduced, use `st.navigation` and an `app_pages/` directory.
- Candidate pages: overview, clients, campaigns, content library, and account.
- Page scripts contain UI only; reusable business logic remains under `marketingflow/`.
- Use native Streamlit widgets, Material icons, sentence casing, bordered containers, and `.streamlit/config.toml` theme tokens.
- Do not add deprecated `use_container_width` or `st.components.v1` usage.

### Application services

- `auth.py`: Supabase session and authenticated user boundary.
- `repository.py`: user-scoped persistence operations.
- `brand_identity.py`: deterministic extraction, structured Gemini extraction, chunking, and deduplication.
- `memory.py`: retrieval and similarity decisions.
- Existing `nodes.py`: marketing workflow behavior.
- Existing `graph.py`: routing and bounded rewrite loop.

Interfaces are introduced only when used by at least two consumers or necessary for isolated testing.

## 6. Authentication and authorization

Supabase Auth is the sole user identity system.

Supported flows:

- Email/password sign-up with email confirmation.
- Email/password sign-in and sign-out.
- Password reset and password update.
- Google OAuth through Supabase.

Rules:

- A Google and email login resolving to the same linked Supabase user sees the same workspace.
- The app uses the Supabase publishable key plus the authenticated user's access token.
- The Supabase secret/service key is not loaded by the Streamlit request path.
- `get_user()` or verified claims establish identity; unverified session payloads are not trusted for authorization.
- `st.session_state` may hold per-tab UI/session data, but it is not the permanent identity store.
- OAuth callback, refresh, page reload, and logout behavior are tested before building the rest of the account UI.

## 7. Persistent data model

All tenant-owned records include `owner_id uuid` referencing `auth.users(id)` where appropriate and have RLS enabled.

Minimum tables:

- `profiles`: display information keyed by the Auth user UUID.
- `clients`: identity and onboarding brief; flexible brand fields live in validated JSONB where schema churn would otherwise be high.
- `brand_documents`: file metadata, checksum, storage path, extraction status, and extracted text.
- `brand_chunks`: searchable chunks and `vector(768)` embeddings.
- `campaigns`: request, route, status, current stage, progress, outputs, and recoverable state JSONB.
- `content_items`: structured content, review outcome, lifecycle status, content hash, and embedding.
- `feedback`: raw feedback plus structured label/rating links to client, campaign, and content.

RLS policies use `auth.uid() = owner_id`. Foreign-key ownership is validated in policies or database functions so a user cannot attach records to another tenant's resources.

Storage uses one private `brand-assets` bucket with paths beginning with the authenticated user UUID. Storage RLS enforces the same owner boundary.

## 8. Persistence and resume semantics

The first version supports campaign-level persistence and resume:

- Save campaign inputs before generation.
- Update stage and progress at meaningful workflow boundaries.
- Save research, strategy, structured content, review, and final output.
- “Continue campaign” loads the stored campaign context and creates the next batch without repeating previous work.

It does not initially promise distributed mid-token or mid-node recovery. A dedicated LangGraph Postgres checkpointer is deferred until actual operating evidence requires it.

SQLite is not maintained as a parallel production backend. Tests use repository fakes. A local SQLite adapter can be added later only if a real offline demonstration requirement appears; the app already requires internet for Gemini generation.

## 9. Brand identity ingestion

Ingestion is incremental and idempotent:

1. Validate size, extension, and MIME type.
2. Calculate SHA-256 before processing.
3. Reuse an existing document when the same owner/client checksum already exists.
4. Store the original in the private bucket.
5. Prefer deterministic text extraction for TXT, MD, CSV, PDF, and DOCX.
6. Use Gemini structured extraction once per changed asset.
7. Use multimodal processing only for images or visually significant documents where text extraction is insufficient.
8. Chunk and embed the resulting knowledge once, then persist it.

The structured brand profile includes audience, offer, positioning, voice, proof, objections, visual cues, prohibited claims, and content do/don't rules. Unsupported fields remain empty rather than being invented.

## 10. Memory and anti-duplication

Novelty is a deterministic gate before it becomes an LLM task:

1. Exact normalized hash check.
2. Vector similarity search filtered by owner, client, content status, and relevant channel/format.
3. Only when similarity exceeds a calibrated threshold does the workflow request a rewrite.
4. The creator receives the matched patterns and must change angle, hook, structure, and CTA where necessary.
5. A maximum of one novelty rewrite is allowed per run.

The LLM novelty judge from the prototype is not called on every campaign. It may be retained as a secondary judge for borderline similarity only after evaluation shows value.

Feedback retrieval returns only recent and semantically relevant items. Approved/published content is positive memory; rejected content and explicit feedback become negative constraints.

## 11. Direct-response workflow

The existing graph is evolved instead of replaced.

- The supervisor uses an explicit UI task type when available; LLM routing is a fallback for free-form requests.
- Research runs only when freshness is required. Research is reused by a request fingerprint and freshness window.
- Strategy produces a structured campaign brief: awareness, pain/desire, offer, value proposition, big idea, reason to believe, objections, funnel stage, channel, primary objective, CTA, and proof restrictions.
- The creator returns structured `ContentItem` objects.
- Novelty runs as the bounded deterministic gate described above.
- The reviewer returns status, issues, and corrected/approved content. A reviewer failure never silently becomes PASS.
- The finalizer uses approved or corrected content, not the rejected original draft.

Target flow:

```text
Input → Route → Client/brand memory → Optional research → Direct-response brief
      → Structured content → Similarity gate → Optional one rewrite
      → Reviewer/correction → Persist → Finalize
```

## 12. Model and cost strategy

Use one provider with at most two configurable model roles:

- `GEMINI_FAST_MODEL`: routing, extraction, classification, and review.
- `GEMINI_QUALITY_MODEL`: strategy and final content when quality requires it.

Both roles may point to the same model during the pilot. Model choice is configuration, not duplicated agent code.

Cost controls:

- Do not embed unchanged documents or saved content twice.
- Do not run web search for content-only or knowledge-only work.
- Persist and reuse research within a freshness window.
- Retrieve a small relevant context instead of sending all history.
- Bound all rewrite/review loops.
- Store token/search usage metadata when the provider exposes it, without adding an observability service.

## 13. Streamlit performance design

- Render navigation, headings, filters, and result containers before slow calls.
- Put generation behind forms/buttons so typing and selection changes do not invoke models.
- Use `st.cache_resource` only for safe shared stateless resources. A user-token Supabase client remains session-scoped and is never shared across users.
- Use bounded `st.cache_data` only for non-sensitive or correctly user-keyed read results, and clear affected entries after mutations.
- Use fragments for independent content status/feedback controls and dashboard summaries.
- Guard expensive hidden tab or expander content.
- Use stable widget keys and initialize session state in one location.

## 14. Error handling and security

- No exception text containing tokens, database URLs, prompts with private brand data, or raw provider responses is displayed to users.
- External calls have bounded retries and actionable user messages.
- A failed structured output is recorded as an error or enters an explicit fallback; review and security checks fail closed.
- File processing limits page count/size and rejects unsupported content.
- Database writes validate status enums and ownership server-side.
- Campaign status is left recoverable after failures and can be retried intentionally.
- Logs use IDs and stages, not secrets or full client documents.

## 15. Testing strategy

No live API call is required for the normal test suite.

Tests cover:

- Existing graph imports and routes.
- Reviewer correction reaching the finalizer.
- Rewrite loop bounded to one pass.
- Deterministic routing avoiding unnecessary research.
- Repository ownership filters and status validation.
- Brand checksum deduplication and chunking.
- Similarity gate decisions with fixed vectors.
- Auth/session logic with mocked Supabase responses.
- Streamlit page/module imports where practical.

Separate opt-in integration tests cover Supabase Auth, RLS, Storage, and pgvector against a configured test project or local Supabase instance.

## 16. Delivery phases and definitions of done

### Phase 0 — Baseline protection

- Add test tooling and tests for current behavior.
- Add configuration validation without changing user-visible features.
- Capture the current graph and app smoke behavior.

Done when the current app and CLI import successfully, tests pass without network calls, and no current feature is removed.

### Phase 1 — Core correctness and workflow contracts

- Structured campaign brief/content/review contracts.
- Correct reviewer-to-finalizer behavior.
- Deterministic routing and bounded rewrite path.

Done when unit tests prove all graph paths and no unbounded loop exists.

### Phase 2 — Supabase foundation and Auth spike

- Migrations, RLS, private storage policies, user-scoped repository, and complete Auth spike.

Done when two test users cannot access each other's data and both Google and email users preserve a verified session across expected navigation/reload flows.

### Phase 3 — Clients, campaigns, and content persistence

- Persistent clients, campaign history/resume, content library, lifecycle statuses, and feedback.

Done when a user can close/reopen the app and continue a campaign with saved outputs and isolated ownership.

### Phase 4 — Brand ingestion and persistent retrieval

- Upload, checksum deduplication, extraction, Storage, chunks, embeddings, and filtered retrieval.

Done when an unchanged file causes no repeated extraction/embedding and another user's knowledge is never retrieved.

### Phase 5 — Memory, anti-duplication, and direct response

- Similarity RPC, feedback memory, research reuse, direct-response prompt contracts, and one bounded rewrite.

Done when tests and pilot examples demonstrate fresh content without unnecessary LLM novelty calls.

### Phase 6 — UI consolidation and release hardening

- Native multipage UI, performance work, end-to-end tests, documentation, and migration cleanup.

Done when the primary workflows pass end-to-end, secrets remain excluded, and the old one-shot behavior is either preserved as a supported route or deliberately migrated with user approval.

## 17. Migration rules

- Each phase is a separate review checkpoint and preferably a separate small commit series.
- Existing files are patched; they are not replaced by the V3 ZIP versions.
- `.env`, `.venv`, user data, and local secrets are never overwritten or committed.
- Dependencies are added only in the phase that needs them.
- No phase starts until the previous phase meets its written definition of done.

## 18. Final acceptance criteria

The upgrade is complete when:

- One Supabase identity can use Google or email/password and reaches one workspace.
- RLS and Storage policies enforce tenant isolation without a service key in the application data path.
- Clients, brand knowledge, campaigns, content, statuses, and feedback persist.
- Campaigns can continue from saved context.
- Unchanged brand files and repeated research are not reprocessed.
- Content novelty uses stored history and bounded rewrites.
- Reviewer corrections become the delivered content.
- Existing LangGraph and Streamlit entry points remain operational.
- Automated tests protect graph, persistence, security, and core user flows.
