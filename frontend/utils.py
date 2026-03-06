import streamlit as st
import requests
import json
import time
from typing import Optional, Dict, Any, List

class ApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.api_prefix = "/api/v1"
    
    def health_check(self) -> bool:
        try:
            res = requests.get(f"{self.base_url}/health")
            return res.status_code == 200
        except:
            return False

    def upload_assessment(self, files, scenario_id: str = "default") -> Optional[Dict]:
        """Uploads files for assessment and returns task_id"""
        url = f"{self.base_url}{self.api_prefix}/assessments"
        files_payload = [('files', (f.name, f, f.type)) for f in files]
        data = {'scenario_id': scenario_id}
        
        try:
            res = requests.post(url, files=files_payload, data=data)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            st.error(f"API Error: {str(e)}")
            return None

    def get_assessment_result(self, task_id: str) -> Optional[Dict]:
        """Gets assessment result by task_id"""
        url = f"{self.base_url}{self.api_prefix}/assessments/{task_id}"
        try:
            res = requests.get(url)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            # Don't show error for 404/processing if we are polling
            return None

    def upload_to_kb(self, file, chunk_size: int = 1000, chunk_overlap: int = 200) -> Optional[Dict]:
        """Uploads a document to Knowledge Base"""
        url = f"{self.base_url}{self.api_prefix}/kb/documents"
        files = {'file': (file.name, file, file.type)}
        data = {'chunk_size': chunk_size, 'chunk_overlap': chunk_overlap}
        
        try:
            res = requests.post(url, files=files, data=data)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            st.error(f"KB Upload Error: {str(e)}")
            return None

    def query_kb(self, query: str, top_k: int = 5) -> Optional[Dict]:
        """Queries the Knowledge Base"""
        url = f"{self.base_url}{self.api_prefix}/kb/query"
        payload = {'query': query, 'top_k': top_k}
        
        try:
            res = requests.post(url, json=payload)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            st.error(f"KB Query Error: {str(e)}")
            return None
