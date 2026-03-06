"""
Agent orchestration: multi-agent flow with citations, confidence, and history reuse.
"""

from datetime import datetime, timezone
from uuid import UUID

from app.core.config import settings
from app.kb.service import KnowledgeBaseService
from app.llm.base import invoke_llm
from app.models.assessment import (
    AssessmentReport,
    ComplianceGap,
    Remediation,
    ReportMetadata,
    RiskItem,
    SourceCitation,
)
from app.models.parser import ParsedDocument


async def run_assessment(
    task_id: UUID,
    parsed_documents: list[ParsedDocument],
    scenario_id: str | None = None,
    project_id: str | None = None,
) -> AssessmentReport:
    doc_context = _build_document_context(parsed_documents)
    policy_chunks, history_chunks = _policy_and_history_agent(doc_context["query_seed"])
    evidence_context = _evidence_agent(parsed_documents)
    draft_raw = await _drafter_agent(
        doc_context["full_text"],
        policy_chunks,
        history_chunks,
    )
    reviewed_raw = await _reviewer_agent(
        draft_raw,
        evidence_context,
        policy_chunks,
        history_chunks,
    )
    report = await _parse_llm_output_to_report(
        raw=reviewed_raw,
        task_id=task_id,
        scenario_id=scenario_id,
        project_id=project_id,
        policy_chunks=policy_chunks,
        history_chunks=history_chunks,
    )
    return report


def _build_document_context(parsed_documents: list[ParsedDocument]) -> dict[str, str]:
    doc_texts: list[str] = []
    for d in parsed_documents:
        c = d.content if isinstance(d.content, str) else str(d.content)
        doc_texts.append(f"[{d.metadata.filename}]\n{c}")
    combined_input = "\n\n---\n\n".join(doc_texts)
    return {"full_text": combined_input, "query_seed": combined_input[:2000]}


def _policy_and_history_agent(query_seed: str) -> tuple[list, list]:
    kb = KnowledgeBaseService()
    policy_chunks = []
    history_chunks = []
    try:
        policy_chunks = kb.query(query_seed, top_k=5)
    except Exception:
        policy_chunks = []
    try:
        history_chunks = kb.query_history_responses(query_seed, top_k=3)
    except Exception:
        history_chunks = []
    return policy_chunks, history_chunks


def _evidence_agent(parsed_documents: list[ParsedDocument]) -> str:
    evidence_lines: list[str] = []
    for d in parsed_documents:
        content = d.content if isinstance(d.content, str) else str(d.content)
        for i, line in enumerate(content.splitlines()):
            ln = line.strip()
            if not ln:
                continue
            if any(k in ln.lower() for k in ["password", "encrypt", "access", "token"]):
                evidence_lines.append(f"{d.metadata.filename}#L{i + 1}: {ln[:240]}")
    return (
        "\n".join(evidence_lines[:20])
        or "No explicit security evidence lines extracted."
    )


async def _drafter_agent(
    full_text: str,
    policy_chunks: list,
    history_chunks: list,
) -> str:
    policy_context = _format_chunks_with_ids(policy_chunks, prefix="POL")
    history_context = _format_chunks_with_ids(history_chunks, prefix="HIS")
    system_prompt = (
        "You are DrafterAgent in a multi-agent security workflow. "
        "Create an assessment draft in JSON only with keys: summary, risk_items, "
        "compliance_gaps, remediations. For each risk item include source_ref and "
        "optional category."
    )
    user_prompt = (
        f"## Documents\n{full_text[:12000]}\n\n"
        f"## Policy Chunks\n{policy_context[:5000]}\n\n"
        f"## Historical Answers\n{history_context[:3000]}\n\n"
        "Generate draft JSON."
    )
    return await invoke_llm(system_prompt, user_prompt)


async def _reviewer_agent(
    draft_raw: str,
    evidence_context: str,
    policy_chunks: list,
    history_chunks: list,
) -> str:
    policy_context = _format_chunks_with_ids(policy_chunks, prefix="POL")
    history_context = _format_chunks_with_ids(history_chunks, prefix="HIS")
    system_prompt = (
        "You are ReviewerAgent. Validate and improve the draft for consistency and "
        "hallucination resistance. Output JSON only with keys: summary, confidence, "
        "risk_items, compliance_gaps, remediations, sources. "
        "confidence is 0.0-1.0. sources is array of "
        "{id,file,page,paragraph_id,excerpt,evidence_link,score}."
    )
    user_prompt = (
        f"## Draft\n{draft_raw[:8000]}\n\n"
        f"## Evidence Lines\n{evidence_context[:2000]}\n\n"
        f"## Policy Chunks\n{policy_context[:3000]}\n\n"
        f"## Historical Answers\n{history_context[:2000]}\n\n"
        "Keep only well-supported findings. Add explicit sources and confidence."
    )
    return await invoke_llm(system_prompt, user_prompt)


def _format_chunks_with_ids(chunks: list, prefix: str) -> str:
    formatted: list[str] = []
    for i, d in enumerate(chunks):
        metadata = d.metadata or {}
        src = metadata.get("source", "unknown")
        page = metadata.get("page")
        c_id = f"{prefix}-{i + 1}"
        formatted.append(f"[{c_id}] {src} p={page}\n{d.page_content[:600]}")
    return "\n\n".join(formatted)


def _derive_sources_from_chunks(
    policy_chunks: list,
    history_chunks: list,
) -> list[SourceCitation]:
    combined = []
    combined.extend([(d, "policy") for d in policy_chunks[:5]])
    combined.extend([(d, "history") for d in history_chunks[:3]])
    citations: list[SourceCitation] = []
    for i, (doc, origin) in enumerate(combined):
        metadata = doc.metadata or {}
        file = metadata.get("source") or "unknown"
        page = metadata.get("page")
        paragraph_id = metadata.get("chunk_id") or metadata.get("document_id")
        citations.append(
            SourceCitation(
                id=f"S{i + 1}",
                file=file,
                page=page if isinstance(page, int) else None,
                paragraph_id=str(paragraph_id) if paragraph_id else None,
                excerpt=doc.page_content[:240],
                evidence_link=f"{file}#chunk={paragraph_id}" if paragraph_id else None,
                score=float(metadata.get("score")) if metadata.get("score") else None,
            )
        )
        if origin == "history" and citations[-1].evidence_link:
            citations[-1].evidence_link = f"history://{citations[-1].evidence_link}"
    return citations


async def _estimate_confidence(
    summary: str,
    risk_count: int,
    source_count: int,
) -> float:
    system_prompt = (
        "You are ConfidenceAgent. Output only one float between 0 and 1 based on "
        "evidence strength and consistency."
    )
    user_prompt = (
        f"summary={summary[:500]}\n"
        f"risk_count={risk_count}\n"
        f"source_count={source_count}\n"
        "Return float only."
    )
    try:
        raw = await invoke_llm(system_prompt, user_prompt)
        value = float(str(raw).strip().split()[0])
        if value < 0:
            return 0.0
        if value > 1:
            return 1.0
        return value
    except Exception:
        heuristic = 0.55 + min(source_count, 5) * 0.06 - min(risk_count, 6) * 0.02
        if heuristic < 0.0:
            return 0.0
        if heuristic > 1.0:
            return 1.0
        return round(heuristic, 2)


async def _parse_llm_output_to_report(
    raw: str,
    task_id: UUID,
    scenario_id: str | None,
    project_id: str | None,
    policy_chunks: list,
    history_chunks: list,
) -> AssessmentReport:
    import json
    import re

    risk_items: list[RiskItem] = []
    compliance_gaps: list[ComplianceGap] = []
    remediations: list[Remediation] = []
    sources: list[SourceCitation] = []
    summary = "Assessment completed."
    confidence = 0.0

    json_match = re.search(r"\{[\s\S]*\}", raw)
    if json_match:
        try:
            data = json.loads(json_match.group(0))
            summary = data.get("summary") or summary
            for i, r in enumerate(data.get("risk_items") or []):
                risk_items.append(
                    RiskItem(
                        id=r.get("id") or f"risk-{i}",
                        title=r.get("title") or "Unnamed risk",
                        severity=r.get("severity") or "medium",
                        description=r.get("description"),
                        source_ref=r.get("source_ref"),
                        category=r.get("category"),
                    )
                )
            for i, g in enumerate(data.get("compliance_gaps") or []):
                compliance_gaps.append(
                    ComplianceGap(
                        id=g.get("id") or f"gap-{i}",
                        control_or_clause=g.get("control_or_clause") or "",
                        gap_description=g.get("gap_description") or "",
                        evidence_suggestion=g.get("evidence_suggestion"),
                        framework=g.get("framework"),
                    )
                )
            for i, rem in enumerate(data.get("remediations") or []):
                remediations.append(
                    Remediation(
                        id=rem.get("id") or f"rem-{i}",
                        action=rem.get("action") or "",
                        priority=rem.get("priority"),
                        related_risk_ids=rem.get("related_risk_ids") or [],
                        related_gap_ids=rem.get("related_gap_ids") or [],
                    )
                )
            for i, s in enumerate(data.get("sources") or []):
                sources.append(
                    SourceCitation(
                        id=s.get("id") or f"S{i + 1}",
                        file=s.get("file") or "unknown",
                        page=s.get("page"),
                        paragraph_id=s.get("paragraph_id"),
                        excerpt=s.get("excerpt") or "",
                        evidence_link=s.get("evidence_link"),
                        score=s.get("score"),
                    )
                )
            if data.get("confidence") is not None:
                confidence = float(data.get("confidence"))
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            summary = (
                "Assessment completed with partial parsing; "
                "raw output may contain more."
            )

    if not sources:
        sources = _derive_sources_from_chunks(policy_chunks, history_chunks)
    if confidence <= 0:
        confidence = await _estimate_confidence(
            summary=summary,
            risk_count=len(risk_items),
            source_count=len(sources),
        )

    return AssessmentReport(
        version="2.0",
        task_id=str(task_id),
        status="completed",
        summary=summary,
        risk_items=risk_items,
        compliance_gaps=compliance_gaps,
        remediations=remediations,
        confidence=confidence,
        sources=sources,
        metadata=ReportMetadata(
            scenario_id=scenario_id,
            project_id=project_id,
            model_used=settings.LLM_PROVIDER,
            completed_at=datetime.now(timezone.utc),
        ),
        format="json",
    )
