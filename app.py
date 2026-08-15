import streamlit as st

from marketingflow.auth import AuthError, AuthService, SessionTokens, create_supabase_client
from marketingflow.config import get_settings
from marketingflow.graph import graph

settings = get_settings()

st.set_page_config(page_title="MarketingFlow AI", page_icon="🚀", layout="wide")

st.title("🚀 MarketingFlow AI")
st.caption("Multi-Agent AI Marketing Agency — LangGraph + Gemini + Google Search + RAG")


def require_authenticated_user():
    client = st.session_state.get("supabase_client")
    if client is None:
        client = create_supabase_client(settings)
        st.session_state.supabase_client = client
    service = AuthService(client)

    stored_tokens = st.session_state.get("supabase_tokens")
    if stored_tokens:
        try:
            tokens = SessionTokens(**stored_tokens)
            response = service.restore_session(tokens)
            refreshed = service.tokens_from(response)
            if refreshed:
                st.session_state.supabase_tokens = {
                    "access_token": refreshed.access_token,
                    "refresh_token": refreshed.refresh_token,
                }
                tokens = refreshed
            user = service.verified_user(tokens.access_token)
            if user:
                return user, service
        except AuthError:
            st.session_state.pop("supabase_tokens", None)

    google_logged_in = bool(getattr(st.user, "is_logged_in", False))
    if google_logged_in:
        id_token = st.user.tokens.get("id")
        if id_token:
            try:
                response = service.sign_in_with_google_id_token(id_token)
                tokens = service.tokens_from(response)
                if tokens:
                    st.session_state.supabase_tokens = {
                        "access_token": tokens.access_token,
                        "refresh_token": tokens.refresh_token,
                    }
                    st.rerun()
            except AuthError:
                st.error("Google sign-in could not be linked to the workspace.")

    st.subheader("Sign in to your workspace")
    mode = st.segmented_control(
        "Account action",
        ["Sign in", "Create account", "Reset password"],
        default="Sign in",
    )

    if mode == "Sign in":
        with st.form("sign_in_form", border=True):
            email = st.text_input("Email", key="sign_in_email")
            password = st.text_input("Password", type="password", key="sign_in_password")
            submitted = st.form_submit_button("Sign in", type="primary")
        if submitted:
            try:
                response = service.sign_in(email, password)
                tokens = service.tokens_from(response)
                if not tokens:
                    raise AuthError("Authentication request could not be completed.")
                st.session_state.supabase_tokens = {
                    "access_token": tokens.access_token,
                    "refresh_token": tokens.refresh_token,
                }
                st.rerun()
            except AuthError:
                st.error("Sign-in failed. Check your email and password.")
    elif mode == "Create account":
        with st.form("sign_up_form", border=True):
            email = st.text_input("Email", key="sign_up_email")
            password = st.text_input("Password", type="password", key="sign_up_password")
            submitted = st.form_submit_button("Create account", type="primary")
        if submitted:
            try:
                service.sign_up(email, password, settings.app_url)
                st.success("Check your email to confirm the account, then sign in.")
            except AuthError:
                st.error("The account could not be created.")
    else:
        with st.form("reset_password_form", border=True):
            email = st.text_input("Email", key="reset_email")
            submitted = st.form_submit_button("Send reset link", type="primary")
        if submitted:
            try:
                service.reset_password(email, settings.app_url)
                st.success("If the account exists, a reset link has been sent.")
            except AuthError:
                st.error("The reset request could not be completed.")

    try:
        google_oidc_configured = "auth" in st.secrets
    except Exception:
        google_oidc_configured = False
    if google_oidc_configured:
        if st.button("Continue with Google", icon=":material/account_circle:"):
            st.login()
    else:
        st.caption("Google sign-in becomes available after local OIDC secrets are configured.")
    st.stop()


authenticated_user = None
auth_service = None
if settings.has_supabase:
    authenticated_user, auth_service = require_authenticated_user()
else:
    st.info("Local development mode — Supabase is not configured yet.")

if not settings.has_google_api_key:
    st.warning("Add GOOGLE_API_KEY to a .env file before generating a campaign.")

with st.sidebar:
    st.header("Campaign Settings")
    if authenticated_user:
        st.caption(f"Workspace: {getattr(authenticated_user, 'email', 'Signed in user')}")
        if st.button("Sign out", icon=":material/logout:"):
            auth_service.sign_out()
            st.session_state.pop("supabase_tokens", None)
            if getattr(st.user, "is_logged_in", False):
                st.logout()
            st.rerun()
    duration_days = st.selectbox("Plan duration", [7, 14, 30], index=0)
    st.markdown("**Agents:** Supervisor → Client RAG → Web Research → Strategist → Creator → Reviewer")

with st.form("client_form"):
    col1, col2 = st.columns(2)
    with col1:
        business_name = st.text_input("Business name", "Demo Brand")
        industry = st.text_input("Industry / niche", "Fitness")
        products_services = st.text_area("Products / services", "Online fitness coaching")
        target_audience = st.text_area("Target audience", "Busy professionals aged 25-40")
        goal = st.text_input("Marketing goal", "Generate qualified leads")
    with col2:
        platforms = st.text_input("Platforms", "Instagram, Facebook")
        tone = st.text_input("Tone / brand voice", "Friendly, practical, motivating")
        special_offers = st.text_area("Offers / promotions", "Free first consultation")
        competitors = st.text_area("Known competitors (optional)", "")
        website = st.text_input("Website (optional)", "")

    extra_knowledge = st.text_area(
        "Extra client knowledge / brand notes",
        "We never promise instant results. We focus on sustainable habits and personalized plans.",
        height=120,
    )
    uploaded_files = st.file_uploader(
        "Optional client knowledge files (.txt / .md)",
        type=["txt", "md"],
        accept_multiple_files=True,
    )
    request = st.text_area(
        "What should the agency do?",
        f"Create a complete {duration_days}-day marketing strategy and ready-to-publish content plan.",
        height=100,
    )
    submitted = st.form_submit_button("Generate with Multi-Agent Workflow", type="primary")

if submitted:
    uploaded_knowledge_parts = []
    for uploaded_file in uploaded_files or []:
        try:
            uploaded_knowledge_parts.append(
                f"FILE: {uploaded_file.name}\n"
                + uploaded_file.getvalue().decode("utf-8", errors="ignore")
            )
        except Exception:
            pass

    client = {
        "business_name": business_name,
        "industry": industry,
        "products_services": products_services,
        "target_audience": target_audience,
        "goal": goal,
        "platforms": platforms,
        "tone": tone,
        "special_offers": special_offers,
        "competitors": competitors,
        "website": website,
        "extra_knowledge": extra_knowledge,
        "uploaded_client_documents": "\n\n".join(uploaded_knowledge_parts),
    }

    with st.spinner("Agents are working..."):
        try:
            result = graph.invoke(
                {
                    "client": client,
                    "request": request,
                    "duration_days": duration_days,
                }
            )
        except Exception:
            st.error("The workflow could not be completed. Please retry in a moment.")
            st.stop()

    st.success(f"Route: {result.get('route')} — {result.get('route_reason', '')}")

    tabs = st.tabs(["Final", "RAG Context", "Web Research", "Strategy", "Content", "Review"])
    with tabs[0]:
        final_text = result.get("final_output", "")
        st.markdown(final_text)
        st.download_button(
            "Download Markdown",
            data=final_text,
            file_name=f"{business_name.replace(' ', '_').lower()}_marketing_plan.md",
            mime="text/markdown",
        )
    with tabs[1]:
        st.code(result.get("knowledge_context", "Not used."))
    with tabs[2]:
        st.markdown(result.get("research", "Not used."))
    with tabs[3]:
        st.markdown(result.get("strategy", "Not used."))
    with tabs[4]:
        st.markdown(result.get("content_plan", "Not used."))
    with tabs[5]:
        st.markdown(result.get("review", "Not used."))
