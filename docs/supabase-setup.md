# Supabase and Google Auth local setup

The application runs in local development mode until these settings are present. Never commit the real values.

## 1. Supabase project

1. Create a Supabase project.
2. Run `supabase/migrations/202608160001_foundation.sql` in the SQL editor or through the Supabase CLI.
3. Keep email confirmation enabled under Authentication settings.
4. Copy the project URL and **publishable** key into `.env`:

```dotenv
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_PUBLISHABLE_KEY=sb_publishable_your_key
APP_URL=http://localhost:8501
```

Do not add a secret or service-role key. The application rejects new-format secret keys.

## 2. Google identity

Create one Google OAuth Web client and enable the Google provider in Supabase Auth with that client ID and secret. Add these authorized redirect URIs in Google:

```text
http://localhost:8501/oauth2callback
https://YOUR_PROJECT_REF.supabase.co/auth/v1/callback
```

Create `.streamlit/secrets.toml` locally:

```toml
[auth]
redirect_uri = "http://localhost:8501/oauth2callback"
cookie_secret = "GENERATE_A_LONG_RANDOM_SECRET"
client_id = "YOUR_GOOGLE_CLIENT_ID"
client_secret = "YOUR_GOOGLE_CLIENT_SECRET"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
expose_tokens = "id"
```

Streamlit handles OIDC state, nonce, and its identity cookie. The server sends the exposed Google ID token directly to Supabase `sign_in_with_id_token`; Supabase then creates or links the user and issues the JWT used by RLS.

## 3. Required real checks

- Email sign-up → confirmation → sign-in → page rerun.
- Reset email → new password → sign-in.
- Google sign-in → Supabase user UUID → page refresh.
- Two different users cannot read or mutate each other's rows or Storage objects.

The normal pytest suite remains offline and does not use these credentials.
