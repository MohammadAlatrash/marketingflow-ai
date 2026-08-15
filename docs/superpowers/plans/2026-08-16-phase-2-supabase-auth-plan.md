# Phase 2 implementation plan — Supabase foundation and Auth spike

Date: 2026-08-16

## Objective

Add the production persistence/security foundation without enabling a second identity system or using a service key in the application path.

## Decisions

- Supabase publishable key + the verified user's Supabase JWT is the only data-access path.
- Email/password/reset use Supabase Auth directly.
- Google uses Streamlit OIDC for secure browser cookie/state handling, then exchanges the exposed Google ID token through Supabase `sign_in_with_id_token`; the resulting Supabase user UUID owns the workspace.
- If Supabase is not configured, the existing local campaign UI remains available with a setup notice so development is not blocked.

## Definition of done

- Versioned SQL creates the minimum schema, indexes, RLS policies, and private bucket policies.
- No application code accepts or references a service-role key.
- Auth operations are wrapped behind a testable service and verify identity with `get_user`.
- Repository writes force `owner_id` and reads/updates/deletes filter by it in addition to RLS.
- Email sign-up/sign-in/reset/update and Google ID-token exchange are covered offline with fakes.
- Real integration requirements are documented explicitly when credentials are unavailable.

## Tasks

1. Add `supabase>=2.28,<3` and optional Supabase settings.
2. Create `supabase/migrations/202608160001_foundation.sql` with pgvector, tables, composite ownership constraints, indexes, grants, RLS, and private Storage policies.
3. Add `marketingflow/auth.py` and `marketingflow/repository.py`.
4. Add conditional native Streamlit auth UI without changing local unconfigured behavior.
5. Add offline tests and run compile, pytest, secret scan, and Streamlit health.

## External completion gate

Real Google/email and RLS integration testing requires a Supabase project URL and publishable key, running the migration, and Google OIDC credentials in local Streamlit secrets. These values are never committed.
