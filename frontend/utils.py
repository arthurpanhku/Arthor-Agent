import requests
import streamlit as st


class ApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.api_prefix = "/api/v1"

    def health_check(self) -> bool:
        try:
            res = requests.get(f"{self.base_url}/health")
            return res.status_code == 200
        except Exception:
            return False

    def upload_assessment(
        self,
        files,
        scenario_id: str = "default",
        collaborative_mode: bool = True,
    ) -> dict | None:
        """Uploads files for assessment and returns task_id"""
        url = f"{self.base_url}{self.api_prefix}/assessments"
        files_payload = [("files", (f.name, f, f.type)) for f in files]
        data = {
            "scenario_id": scenario_id,
            "collaborative_mode": str(collaborative_mode).lower(),
        }

        try:
            res = requests.post(url, files=files_payload, data=data)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            st.error(f"API Error: {str(e)}")
            return None

    def get_assessment_result(self, task_id: str) -> dict | None:
        """Gets assessment result by task_id"""
        url = f"{self.base_url}{self.api_prefix}/assessments/{task_id}"
        try:
            res = requests.get(url)
            res.raise_for_status()
            return res.json()
        except Exception:
            # Don't show error for 404/processing if we are polling
            return None

    def review_assessment(
        self,
        task_id: str,
        action: str,
        reviewer: str,
        comment: str | None = None,
        assignee: str | None = None,
    ) -> dict | None:
        url = f"{self.base_url}{self.api_prefix}/assessments/{task_id}/review"
        payload = {
            "action": action,
            "reviewer": reviewer,
            "comment": comment,
            "assignee": assignee,
        }
        try:
            res = requests.post(url, json=payload)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            st.error(f"Review Error: {str(e)}")
            return None

    def comment_assessment(
        self,
        task_id: str,
        author: str,
        comment: str,
        mention: str | None = None,
    ) -> dict | None:
        url = f"{self.base_url}{self.api_prefix}/assessments/{task_id}/comment"
        payload = {"author": author, "comment": comment, "mention": mention}
        try:
            res = requests.post(url, json=payload)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            st.error(f"Comment Error: {str(e)}")
            return None

    def get_activity(self, task_id: str) -> dict | None:
        url = f"{self.base_url}{self.api_prefix}/assessments/{task_id}/activity"
        try:
            res = requests.get(url)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            st.error(f"Activity Error: {str(e)}")
            return None

    def get_reuse(self, task_id: str, top_k: int = 3) -> dict | None:
        url = f"{self.base_url}{self.api_prefix}/assessments/{task_id}/reuse"
        try:
            res = requests.get(url, params={"top_k": top_k})
            res.raise_for_status()
            return res.json()
        except Exception as e:
            st.error(f"Reuse Error: {str(e)}")
            return None

    def upload_to_kb(
        self, file, chunk_size: int = 1000, chunk_overlap: int = 200
    ) -> dict | None:
        """Uploads a document to Knowledge Base"""
        url = f"{self.base_url}{self.api_prefix}/kb/documents"
        files = {"file": (file.name, file, file.type)}
        data = {"chunk_size": chunk_size, "chunk_overlap": chunk_overlap}

        try:
            res = requests.post(url, files=files, data=data)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            st.error(f"KB Upload Error: {str(e)}")
            return None

    def query_kb(self, query: str, top_k: int = 5) -> dict | None:
        """Queries the Knowledge Base"""
        url = f"{self.base_url}{self.api_prefix}/kb/query"
        payload = {"query": query, "top_k": top_k}

        try:
            res = requests.post(url, json=payload)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            st.error(f"KB Query Error: {str(e)}")
            return None

    def reindex_kb(self, directory: str) -> dict | None:
        url = f"{self.base_url}{self.api_prefix}/kb/reindex"
        payload = {"directory": directory}
        try:
            res = requests.post(url, json=payload)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            st.error(f"KB Reindex Error: {str(e)}")
            return None
