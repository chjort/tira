"""Streamlit application for TIRA — Thematic Investment Research Agent."""

import time

import streamlit as st

from frontend.api_client import get_result
from frontend.api_client import get_status
from frontend.api_client import submit_research

st.set_page_config(page_title="TIRA", page_icon=":chart_with_upwards_trend:")
st.title("TIRA — Thematic Investment Research Agent")
st.caption("AI-powered thematic investment research for portfolio managers")

# --- Input form ---
with st.form("research_form"):
    theme = st.text_input(
        "Investment Theme",
        placeholder="e.g., Quantum Computing, Clean Energy, Agentic AI",
    )
    submitted = st.form_submit_button("Start Research")

if submitted and theme:
    response = submit_research(theme)
    st.session_state["task_id"] = response["task_id"]
    st.session_state["theme"] = theme
    st.session_state["status"] = "PENDING"

# --- Status display and polling ---
if "task_id" in st.session_state:
    task_id = st.session_state["task_id"]
    theme_name = st.session_state.get("theme", "")

    status_data = get_status(task_id)
    status = status_data["status"]
    st.session_state["status"] = status

    st.divider()
    st.subheader(f"Research: {theme_name}")
    st.text(f"Task ID: {task_id}")

    if status in ("PENDING", "STARTED"):
        st.info(f"Status: **{status}** — research in progress...")
        time.sleep(3)
        st.rerun()

    elif status == "SUCCESS":
        st.success("Research complete!")
        result_data = get_result(task_id)
        report_md = result_data["result"]

        st.markdown(report_md)

        file_name = f"tira_{theme_name.replace(' ', '_').lower()}.md"
        st.download_button(
            label="Download Report",
            data=report_md,
            file_name=file_name,
            mime="text/markdown",
        )

    elif status == "FAILURE":
        st.error(f"Research failed: {status_data.get('error', 'Unknown error')}")

    elif status == "RETRY":
        st.warning("Task is being retried...")
        time.sleep(5)
        st.rerun()
