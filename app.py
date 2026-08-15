import os
from dotenv import load_dotenv
import streamlit as st

from marketingflow.graph import graph

load_dotenv(override=True)

st.set_page_config(page_title="MarketingFlow AI", page_icon="🚀", layout="wide")

st.title("🚀 MarketingFlow AI")
st.caption("Multi-Agent AI Marketing Agency — LangGraph + Gemini + Google Search + RAG")

if not os.getenv("GOOGLE_API_KEY"):
    st.warning("Add GOOGLE_API_KEY to a .env file before generating a campaign.")

with st.sidebar:
    st.header("Campaign Settings")
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
        except Exception as exc:
            st.error(f"Workflow failed: {exc}")
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
