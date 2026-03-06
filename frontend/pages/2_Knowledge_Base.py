import streamlit as st
from utils import ApiClient

st.set_page_config(page_title="Knowledge Base", page_icon="📚", layout="wide")

st.title("📚 Knowledge Base Management")
st.markdown("Upload policies, standards, and guidelines to the Agent's memory.")

if "api_url" not in st.session_state:
    st.session_state.api_url = "http://localhost:8000"

client = ApiClient(st.session_state.api_url)

tab1, tab2, tab3 = st.tabs(
    ["📤 Upload Documents", "🔍 Query / Test", "🔄 Auto Reindex"]
)

with tab1:
    st.subheader("Add New Documents")
    col1, col2 = st.columns([2, 1])

    with col1:
        kb_file = st.file_uploader(
            "Upload policy/standard (PDF, Word, TXT)", type=["pdf", "docx", "txt", "md"]
        )

    with col2:
        c_size = st.number_input("Chunk Size", value=1000, step=100)
        c_overlap = st.number_input("Chunk Overlap", value=200, step=50)

    if st.button("📁 Upload to KB", type="primary"):
        if kb_file:
            with st.spinner("Processing and indexing document..."):
                res = client.upload_to_kb(kb_file, c_size, c_overlap)
                if res:
                    st.success("Successfully indexed document.")
                    st.info(f"Document ID: {res.get('document_id')}")
        else:
            st.warning("Please select a file.")

with tab2:
    st.subheader("Test RAG Retrieval")
    query = st.text_input("Enter a security question or policy topic")
    top_k = st.slider("Number of results (top_k)", 1, 10, 5)

    if st.button("🔍 Search KB"):
        if query:
            with st.spinner("Searching..."):
                res = client.query_kb(query, top_k)
                if res and "chunks" in res:
                    st.markdown(f"Found **{len(res['chunks'])}** relevant snippets.")
                    for i, r in enumerate(res["chunks"]):
                        with st.expander(
                            "Result "
                            f"{i + 1} "
                            f"(Score: {r.get('metadata', {}).get('score', 'N/A')})"
                        ):
                            st.write(r.get("content"))
                            st.caption(
                                f"Source: {r.get('metadata', {}).get('source')} | "
                                f"Page: {r.get('metadata', {}).get('page', 'N/A')}"
                            )
                else:
                    st.write("No results found.")
        else:
            st.warning("Please enter a query.")

with tab3:
    st.subheader("Reindex Local Policy Directory")
    directory = st.text_input("Directory path", value="./examples")
    if st.button("Run Reindex", type="primary"):
        with st.spinner("Reindexing..."):
            res = client.reindex_kb(directory)
            if res:
                st.success(f"Indexed {res.get('indexed', 0)} files.")
                if res.get("errors"):
                    st.warning("Some files failed during indexing.")
                    st.json(res.get("errors"))
