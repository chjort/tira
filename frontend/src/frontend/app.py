"""Streamlit application for TIRA — Thematic Investment Research Agent."""

import time

import streamlit as st

from frontend.api_client import get_result, get_status, list_tasks, submit_research

TERMINAL_STATUSES: frozenset[str] = frozenset(
    {"SUCCESS", "FAILURE", "REVOKED", "GUARDRAIL"}
)
POLL_INTERVAL_SECONDS: int = 3


def _load_tasks_from_backend() -> list[dict]:
    """Fetch the task registry from the backend and build session-state dicts.

    Returns:
        List of task dicts compatible with session state.
    """
    try:
        registry_entries = list_tasks()
    except Exception:
        registry_entries = []

    return [
        {
            "task_id": entry["task_id"],
            "theme": entry["theme"],
            "status": "PENDING",
            "result": None,
            "error": None,
        }
        for entry in registry_entries
    ]


def _init_session_state() -> None:
    """Initialise session state keys on first load."""
    if "tasks" not in st.session_state:
        st.session_state["tasks"] = _load_tasks_from_backend()


def _handle_form_submission() -> None:
    """Render the research submission form and handle new task creation."""
    with st.form("research_form"):
        theme = st.text_input(
            "Investment Theme",
            placeholder="e.g., Quantum Computing, Clean Energy, Agentic AI",
        )
        submitted = st.form_submit_button("Start Research")

    if submitted and theme:
        response = submit_research(theme)
        task: dict = {
            "task_id": response["task_id"],
            "theme": theme,
            "status": "PENDING",
            "result": None,
            "error": None,
        }
        st.session_state["tasks"].append(task)


def _poll_and_update_tasks() -> bool:
    """Poll status for all non-terminal tasks and cache results.

    Returns:
        True if any tasks are still active (polling required), False otherwise.
    """
    has_active = False
    for task in st.session_state["tasks"]:
        if task["status"] in TERMINAL_STATUSES:
            continue

        has_active = True
        status_data = get_status(task["task_id"])
        task["status"] = status_data["status"]

        if task["status"] == "SUCCESS" and task["result"] is None:
            result_data = get_result(task["task_id"])
            result = result_data["result"]
            if isinstance(result, str) and result.startswith("GUARDRAIL:"):
                task["status"] = "GUARDRAIL"
                task["error"] = result
            else:
                task["result"] = result

        if task["status"] == "FAILURE" and task["error"] is None:
            task["error"] = status_data.get("error", "Unknown error")

    return has_active


def _render_task_list() -> None:
    """Render all research tasks as a list of expandable widgets."""
    tasks = st.session_state["tasks"]
    if not tasks:
        return

    st.divider()
    st.subheader("Research Tasks")

    for task in reversed(tasks):
        task_id = task["task_id"]
        theme = task["theme"]
        status = task["status"]
        label = f"{theme} — {status}"

        with st.expander(label):
            st.caption(f"Task ID: {task_id}")

            if status in ("PENDING", "STARTED", "RETRY"):
                st.info(f"Status: **{status}** — research in progress...")

            elif status == "SUCCESS":
                st.success("Research complete!")
                st.markdown(task["result"])
                file_name = f"tira_{theme.replace(' ', '_').lower()}.md"
                st.download_button(
                    label="Download Report",
                    data=task["result"],
                    file_name=file_name,
                    mime="text/markdown",
                    key=f"download_{task_id}",
                )

            elif status == "GUARDRAIL":
                st.error(f"Research blocked by guardrail: {task['error']}")

            elif status == "FAILURE":
                st.error(f"Research failed: {task['error']}")

            elif status == "REVOKED":
                st.warning("Task was revoked.")


# --- Main ---
st.set_page_config(page_title="TIRA", page_icon=":chart_with_upwards_trend:")
st.title("TIRA — Thematic Investment Research Agent")
st.caption("AI-powered thematic investment research for portfolio managers")

_init_session_state()
_handle_form_submission()
has_active = _poll_and_update_tasks()
_render_task_list()

if has_active:
    time.sleep(POLL_INTERVAL_SECONDS)
    st.rerun()
