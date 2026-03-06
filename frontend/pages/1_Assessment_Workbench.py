import streamlit as st
import time
import json
from utils import ApiClient

st.set_page_config(page_title="Assessment Workbench", page_icon="📝", layout="wide")

st.title("📝 Assessment Workbench")
st.markdown("Upload documents for AI-powered security analysis.")

if 'api_url' not in st.session_state:
    st.session_state.api_url = "http://localhost:8000"

client = ApiClient(st.session_state.api_url)

# Setup State
if 'task_id' not in st.session_state:
    st.session_state.task_id = None
if 'report' not in st.session_state:
    st.session_state.report = None

# Input Section
with st.container(border=True):
    col1, col2 = st.columns([2, 1])
    with col1:
        uploaded_files = st.file_uploader(
            "Select security documents (Questionnaires, Design Docs, etc.)", 
            accept_multiple_files=True,
            type=['pdf', 'docx', 'xlsx', 'pptx', 'txt', 'md']
        )
    with col2:
        scenario_id = st.text_input("Scenario ID", value="default")
        st.markdown("<br>", unsafe_allow_html=True)
        start_btn = st.button("🚀 Start Assessment", use_container_width=True, type="primary")

if start_btn:
    if not uploaded_files:
        st.warning("Please upload at least one file.")
    else:
        with st.status("🚀 Initializing assessment...", expanded=True) as status:
            st.write("Uploading files...")
            res = client.upload_assessment(uploaded_files, scenario_id)
            
            if res and 'task_id' in res:
                st.session_state.task_id = res['task_id']
                st.session_state.report = None
                
                st.write(f"Task ID created: `{st.session_state.task_id}`")
                st.write("AI Agent is analyzing the documents...")
                
                # Polling
                max_retries = 120
                for i in range(max_retries):
                    result = client.get_assessment_result(st.session_state.task_id)
                    if result:
                        status_str = result.get('status', 'processing')
                        
                        if status_str == 'completed' or (result.get('report') or result.get('summary')):
                            st.session_state.report = result.get('report') or result
                            status.update(label="✅ Assessment Complete!", state="complete", expanded=False)
                            break
                        elif status_str == 'failed':
                            st.error("Assessment failed on server.")
                            status.update(label="❌ Failed", state="error")
                            break
                    
                    st.write(f"Analyzing... (step {i+1})")
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
    st.info(report.get('summary', 'No summary available.'))
    
    # Stats
    risks = report.get('risk_items', [])
    gaps = report.get('compliance_gaps', [])
    remediations = report.get('remediations', [])
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Risks Identified", len(risks))
    c2.metric("Compliance Gaps", len(gaps))
    c3.metric("Remediation Steps", len(remediations))
    
    tab1, tab2, tab3, tab4 = st.tabs(["🔥 Risk Items", "⚖️ Compliance Gaps", "🛠️ Remediations", "📄 Raw Data"])
    
    with tab1:
        if not risks:
            st.write("No risks found.")
        for risk in risks:
            with st.expander(f"**{risk.get('severity', 'LOW').upper()}**: {risk.get('title')}"):
                st.write(risk.get('description'))
                st.caption(f"Source: {risk.get('source_ref')} | Category: {risk.get('category')}")
                
    with tab2:
        if not gaps:
            st.write("No compliance gaps found.")
        for gap in gaps:
            st.markdown(f"#### {gap.get('control_or_clause')}")
            st.write(gap.get('gap_description'))
            if gap.get('evidence_suggestion'):
                st.success(f"**Suggested Evidence**: {gap.get('evidence_suggestion')}")
            st.markdown("---")
            
    with tab3:
        if not remediations:
            st.write("No remediation needed.")
        for rem in remediations:
            priority = rem.get('priority', 'medium').upper()
            st.markdown(f"**[{priority}]** {rem.get('action')}")
            if rem.get('related_risk_ids'):
                st.caption(f"Related Risks: {', '.join(rem.get('related_risk_ids'))}")
            st.markdown("---")
            
    with tab4:
        st.json(report)
        st.download_button(
            "Download JSON Report",
            data=json.dumps(report, indent=2),
            file_name=f"assessment_{st.session_state.task_id}.json",
            mime="application/json"
        )
