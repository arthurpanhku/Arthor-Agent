"""
Knowledge base: chunk, embed, store in Chroma; RAG query.
PRD §5.2.4; docs/01 — Chroma, sentence-transformers for embedding.
"""

import hashlib
import json
from pathlib import Path

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings
from app.models.parser import ParsedDocument


def _get_embeddings():
    if not hasattr(_get_embeddings, "_emb"):
        _get_embeddings._emb = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
        )
    return _get_embeddings._emb


class KnowledgeBaseService:
    """Single collection for MVP; persist to CHROMA_PERSIST_DIR."""

    CHUNK_SIZE = 1024
    CHUNK_OVERLAP = 128
    COLLECTION_NAME = "security_agent_kb"
    HISTORY_COLLECTION_NAME = "security_agent_history"

    def __init__(self) -> None:
        persist_dir = Path(settings.CHROMA_PERSIST_DIR)
        persist_dir.mkdir(parents=True, exist_ok=True)
        self._vectorstore = Chroma(
            collection_name=self.COLLECTION_NAME,
            embedding_function=_get_embeddings(),
            persist_directory=str(persist_dir),
        )
        self._history_store = Chroma(
            collection_name=self.HISTORY_COLLECTION_NAME,
            embedding_function=_get_embeddings(),
            persist_directory=str(persist_dir),
        )
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.CHUNK_SIZE,
            chunk_overlap=self.CHUNK_OVERLAP,
            separators=["\n\n", "\n", "。", " ", ""],
        )

    def add_document(
        self, parsed: ParsedDocument, document_id: str | None = None
    ) -> str:
        """Ingest one parsed document into the KB; return document id."""
        content = (
            parsed.content if isinstance(parsed.content, str) else str(parsed.content)
        )
        doc_id = document_id or hashlib.sha256(content.encode()).hexdigest()[:16]
        chunks = self._splitter.split_text(content)
        if not chunks:
            return doc_id
        docs = [
            Document(
                page_content=c,
                metadata={
                    "source": parsed.metadata.filename,
                    "document_id": doc_id,
                    "type": parsed.metadata.type,
                },
            )
            for c in chunks
        ]
        self._vectorstore.add_documents(
            docs, ids=[f"{doc_id}_{i}" for i in range(len(docs))]
        )
        return doc_id

    def query(self, query: str, top_k: int = 5) -> list[Document]:
        """RAG: return top_k relevant chunks."""
        return self._vectorstore.similarity_search(query, k=top_k)

    def add_history_response(
        self,
        task_id: str,
        version: int,
        scenario_id: str | None,
        report_json: dict,
    ) -> str:
        content = (
            f"task_id={task_id}\nversion={version}\nscenario_id={scenario_id}\n"
            f"{json.dumps(report_json, ensure_ascii=False)}"
        )
        doc_id = hashlib.sha256(content.encode()).hexdigest()[:16]
        chunks = self._splitter.split_text(content)
        docs = [
            Document(
                page_content=c,
                metadata={
                    "source": f"history/{task_id}/v{version}.json",
                    "document_id": doc_id,
                    "type": "history_response",
                    "task_id": task_id,
                    "version": version,
                    "scenario_id": scenario_id,
                    "chunk_id": f"{doc_id}_{i}",
                },
            )
            for i, c in enumerate(chunks)
        ]
        if docs:
            self._history_store.add_documents(
                docs, ids=[f"{doc_id}_{i}" for i in range(len(docs))]
            )
        return doc_id

    def query_history_responses(self, query: str, top_k: int = 3) -> list[Document]:
        return self._history_store.similarity_search(query, k=top_k)

    def reindex_directory(self, directory: str) -> dict:
        from app.parser import parse_file

        root = Path(directory)
        if not root.exists():
            return {
                "directory": directory,
                "indexed": 0,
                "errors": ["directory_not_found"],
            }
        indexed = 0
        errors: list[str] = []
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            suffix = path.suffix.lower()
            if suffix not in {".pdf", ".docx", ".xlsx", ".pptx", ".txt", ".md"}:
                continue
            try:
                parsed = parse_file(path.read_bytes(), path.name)
                self.add_document(parsed)
                indexed += 1
            except Exception as e:
                errors.append(f"{path.name}: {e!s}")
        return {"directory": str(root), "indexed": indexed, "errors": errors}
