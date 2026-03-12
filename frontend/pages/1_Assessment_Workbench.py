import json
import time

import streamlit as st
from utils import ApiClient

st.set_page_config(page_title="Assessment Workbench", page_icon="📝", layout="wide")

st.title("📝 Assessment Workbench")
st.markdown("Upload documents for AI-powered security analysis.")

if "api_url" not in st.session_state:
    st.session_state.api_url = "http://localhost:8000"

client = ApiClient(st.session_state.api_url)

# --- Sidebar: Task Configuration ---
st.sidebar.header("Task Config")
scenario = st.sidebar.selectbox("Scenario", ["Security Questionnaire", "Design Review", "Compliance Audit"])
project_id = st.sidebar.text_input("Project ID", "PROJ-001")

# Skill Selection
try:
    skills = client.fetch_api(f"{st.session_state.api_url}/api/v1/skills/")
    skill_options = {s["name"]: s["id"] for s in skills}
    selected_skill_name = st.sidebar.selectbox("Assessor Persona", list(skill_options.keys()))
    selected_skill_id = skill_options[selected_skill_name]

    # Show skill details
    current_skill = next((s for s in skills if s["id"] == selected_skill_id), None)
    if current_skill:
        st.sidebar.caption(f"**Focus**: {', '.join(current_skill.get('risk_focus', []))}")
except Exception:
    st.sidebar.warning("Could not load skills.")
    selected_skill_id = None

st.sidebar.markdown("---")

# Setup State
if "task_id" not in st.session_state:
    st.session_state.task_id = None
if "report" not in st.session_state:
    st.session_state.report = None

# Input Section
with st.container(border=True):
    col1, col2 = st.columns([2, 1])
    with col1:
        uploaded_files = st.file_uploader(
            "Select security documents (Questionnaires, Design Docs, etc.)",
            accept_multiple_files=True,
            type=["pdf", "docx", "xlsx", "pptx", "txt", "md"],
        )
    with col2:
        collaborative_mode = st.checkbox("Enable collaborative review", value=True)
        reviewer = st.text_input("Reviewer", value="security.lead")
        st.markdown("<br>", unsafe_allow_html=True)
        start_btn = st.button(
            "🚀 Start Assessment", use_container_width=True, type="primary"
        )

if start_btn:
    if not uploaded_files:
        st.warning("Please upload at least one file.")
    else:
        with st.status("🚀 Initializing assessment...", expanded=True) as status:
            st.write("Uploading files...")
            res = client.upload_assessment(
                uploaded_files,
                scenario_id=scenario,
                project_id=project_id,
                skill_id=selected_skill_id,
                collaborative_mode=collaborative_mode,
            )

            if res and "task_id" in res:
                st.session_state.task_id = res["task_id"]
                st.session_state.report = None

                st.write(f"Task ID created: `{st.session_state.task_id}`")
                st.write("AI Agent is analyzing the documents...")

                # Polling
                max_retries = 120
                for i in range(max_retries):
                    result = client.get_assessment_result(st.session_state.task_id)
                    if result:
                        status_str = result.get("status", "processing")

                        if status_str in {
                            "review_pending",
                            "approved",
                            "completed",
                        } or (
                            result.get("report") or result.get("summary")
                        ):
                            st.session_state.report = result.get("report") or result
                            status.update(
                                label=(
                                    "✅ Assessment "
                                    f"{status_str.replace('_', ' ').title()}"
                                ),
                                state="complete",
                                expanded=False,
                            )
                            break
                        elif status_str == "failed":
                            st.error("Assessment failed on server.")
                            status.update(label="❌ Failed", state="error")
                            break

                    st.write(f"Analyzing... (step {i + 1})")
                    time.sleep(2)
                else:
                    st.error("Timeout waiting for results.")
                    status.update(label="⌛ Timeout", state="error")
            else:
                status.update(label="❌ Upload Failed", state="error")

# Results Section
if st.session_state.report:
    report = st.session_state.report

    st.markdown("---")
    st.header("📋 Assessment Report")

    # Summary
    st.info(report.get("summary", "No summary available."))

    # Stats
    risks = report.get("risk_items", [])
    gaps = report.get("compliance_gaps", [])
    remediations = report.get("remediations", [])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Risks Identified", len(risks))
    c2.metric("Compliance Gaps", len(gaps))
    c3.metric("Remediation Steps", len(remediations))
    c4.metric("Confidence", f"{float(report.get('confidence', 0)):.2f}")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        [
            "🔥 Risk Items",
            "⚖️ Compliance Gaps",
            "🛠️ Remediations",
            "� Sources",
            "🤝 Collaboration",
            "�� Raw Data",
        ]
    )

    with tab1:
        if not risks:
            st.write("No risks found.")
        for risk in risks:
            with st.expander(
                f"**{risk.get('severity', 'LOW').upper()}**: {risk.get('title')}"
            ):
                st.write(risk.get("description"))
                st.caption(
                    f"Source: {risk.get('source_ref')} | "
                    f"Category: {risk.get('category')}"
                )

    with tab2:
        if not gaps:
            st.write("No compliance gaps found.")
        for gap in gaps:
            st.markdown(f"#### {gap.get('control_or_clause')}")
            st.write(gap.get("gap_description"))
            if gap.get("evidence_suggestion"):
                st.success(f"**Suggested Evidence**: {gap.get('evidence_suggestion')}")
            st.markdown("---")

    with tab3:
        if not remediations:
            st.write("No remediation needed.")
        for rem in remediations:
            priority = rem.get("priority", "medium").upper()
            st.markdown(f"**[{priority}]** {rem.get('action')}")
            if rem.get("related_risk_ids"):
                st.caption(f"Related Risks: {', '.join(rem.get('related_risk_ids'))}")
            st.markdown("---")

    with tab4:
        sources = report.get("sources", [])
        if not sources:
            st.write("No source citations available.")
        for src in sources:
            st.markdown(f"**{src.get('id', 'S')}** · `{src.get('file', 'unknown')}`")
            st.caption(
                f"Page: {src.get('page')} | Paragraph: {src.get('paragraph_id')} | "
                f"Score: {src.get('score')}"
            )
            st.code(src.get("excerpt", ""), language="text")
            if src.get("evidence_link"):
                st.text(src.get("evidence_link"))
            st.markdown("---")

    with tab5:
        if st.session_state.task_id:
            action_col, assign_col = st.columns(2)
            with action_col:
                action = st.selectbox(
                    "Review action",
                    ["approve", "reject", "escalate"],
                )
            with assign_col:
                assignee = st.text_input("Assign to", value="")
            review_comment = st.text_area("Review comment")
            if st.button("Submit Review Action", use_container_width=True):
                review_res = client.review_assessment(
                    task_id=st.session_state.task_id,
                    action=action,
                    reviewer=reviewer,
                    comment=review_comment or None,
                    assignee=assignee or None,
                )
                if review_res:
                    st.success(f"Updated status: {review_res.get('status')}")
            comment_text = st.text_input("Add a collaboration comment")
            mention = st.text_input("Mention user", value="")
            if st.button("Post Comment", use_container_width=True):
                comment_res = client.comment_assessment(
                    task_id=st.session_state.task_id,
                    author=reviewer,
                    comment=comment_text,
                    mention=mention or None,
                )
                if comment_res:
                    st.success("Comment posted")
            activity = client.get_activity(st.session_state.task_id) or {}
            st.markdown("### Activity")
            st.json(activity.get("activity", []))
            st.markdown("### Reuse Candidates")
            reuse_data = client.get_reuse(st.session_state.task_id, top_k=3) or {}
            st.json(reuse_data.get("reused_candidates", []))

    with tab6:
        st.json(report)
        st.download_button(
            "Download JSON Report",
            data=json.dumps(report, indent=2),
            file_name=f"assessment_{st.session_state.task_id}.json",
            mime="application/json",
        )
