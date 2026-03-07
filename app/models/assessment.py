"""
Assessment report and task models.
Aligned with docs/schemas/assessment-report.json and
docs/03-assessment-report-and-skill-contract.md.
"""

from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class RiskItem(BaseModel):
    id: str
    title: str
    severity: Literal["low", "medium", "high", "critical"]
    description: Optional[str] = None
    source_ref: Optional[str] = None
    category: Optional[str] = None


class ComplianceGap(BaseModel):
    id: str
    control_or_clause: str
    gap_description: str
    evidence_suggestion: Optional[str] = None
    framework: Optional[str] = None


class Remediation(BaseModel):
    id: str
    action: str
    priority: Optional[Literal["low", "medium", "high"]] = None
    related_risk_ids: list[str] = Field(default_factory=list)
    related_gap_ids: list[str] = Field(default_factory=list)


class SourceCitation(BaseModel):
    id: str
    file: str
    page: Optional[int] = None
    paragraph_id: Optional[str] = None
    excerpt: str
    evidence_link: Optional[str] = None
    score: Optional[float] = None


class ReportMetadata(BaseModel):
    scenario_id: Optional[str] = None
    project_id: Optional[str] = None
    model_used: Optional[str] = None
    completed_at: Optional[datetime] = None


class AssessmentReport(BaseModel):
    version: str = "1.0"
    task_id: str
    status: Literal["completed", "partial", "failed"]
    summary: str
    risk_items: list[RiskItem] = Field(default_factory=list)
    compliance_gaps: list[ComplianceGap] = Field(default_factory=list)
    remediations: list[Remediation] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    sources: list[SourceCitation] = Field(default_factory=list)
    metadata: Optional[ReportMetadata] = None
    format: Literal["json", "markdown"] = "json"


class AssessmentTaskCreated(BaseModel):
    task_id: UUID
    status: Literal["accepted", "queued"]
    message: Optional[str] = None


class AssessmentTaskResult(BaseModel):
    task_id: UUID
    status: Literal[
        "pending",
        "running",
        "review_pending",
        "approved",
        "rejected",
        "escalated",
        "completed",
        "failed",
    ]
    report: Optional[AssessmentReport] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    version: int = 1
    assignee: Optional[str] = None
    comments: list[dict] = Field(default_factory=list)
