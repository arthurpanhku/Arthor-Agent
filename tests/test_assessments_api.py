"""Tests for assessment API (LLM mocked)."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

from app.models.assessment import AssessmentReport, ReportMetadata, SourceCitation


def _make_report(task_id):
    return AssessmentReport(
        version="2.0",
        task_id=str(task_id),
        status="completed",
        summary="Test summary",
        risk_items=[],
        compliance_gaps=[],
        remediations=[],
        confidence=0.93,
        sources=[
            SourceCitation(
                id="S1",
                file="policy.pdf",
                page=12,
                paragraph_id="p-1",
                excerpt="MFA is required for privileged access.",
                evidence_link="policy.pdf#p-1",
                score=0.89,
            )
        ],
        metadata=ReportMetadata(
            scenario_id=None,
            project_id=None,
            model_used="ollama",
            completed_at=datetime.now(timezone.utc),
        ),
    )


def test_submit_assessment_no_files_422(client):
    """POST /api/v1/assessments without files returns 422 (validation error)."""
    r = client.post("/api/v1/assessments")
    assert r.status_code == 422


def test_submit_assessment_with_txt_file(client):
    """
    POST /api/v1/assessments with a text file returns 200 and task_id (LLM mocked).
    """

    async def mock_run_assessment(
        task_id, parsed_documents, scenario_id=None, project_id=None
    ):
        return _make_report(task_id)

    with patch(
        "app.api.assessments.run_assessment",
        new_callable=AsyncMock,
        side_effect=mock_run_assessment,
    ):
        files = [
            (
                "files",
                ("sample.txt", b"Security questionnaire answer: Yes.", "text/plain"),
            )
        ]
        r = client.post(
            "/api/v1/assessments", data={"scenario_id": "default"}, files=files
        )
    assert r.status_code == 200
    data = r.json()
    assert data.get("status") == "accepted"
    assert "task_id" in data
    task_id = data["task_id"]
    r2 = client.get(f"/api/v1/assessments/{task_id}")
    assert r2.status_code == 200
    r2_data = r2.json()
    assert r2_data.get("status") in {"review_pending", "completed"}
    assert r2_data.get("report") is not None
    assert "confidence" in r2_data.get("report", {})
    assert "sources" in r2_data.get("report", {})


def test_review_comment_and_activity_flow(client):
    async def mock_run_assessment(
        task_id, parsed_documents, scenario_id=None, project_id=None
    ):
        return _make_report(task_id)

    with patch(
        "app.api.assessments.run_assessment",
        new_callable=AsyncMock,
        side_effect=mock_run_assessment,
    ):
        files = [("files", ("sample.txt", b"Access control policy", "text/plain"))]
        created = client.post("/api/v1/assessments", files=files).json()
    task_id = created["task_id"]

    comment = client.post(
        f"/api/v1/assessments/{task_id}/comment",
        json={
            "author": "analyst",
            "comment": "Please validate MFA evidence",
            "mention": "security.lead",
        },
    )
    assert comment.status_code == 200

    review = client.post(
        f"/api/v1/assessments/{task_id}/review",
        json={"action": "approve", "reviewer": "security.lead", "comment": "LGTM"},
    )
    assert review.status_code == 200
    assert review.json().get("status") == "approved"

    activity = client.get(f"/api/v1/assessments/{task_id}/activity")
    assert activity.status_code == 200
    body = activity.json()
    assert isinstance(body.get("activity"), list)
    assert isinstance(body.get("comments"), list)


def test_get_assessment_not_found_404(client):
    """GET /api/v1/assessments/{id} for unknown id returns 404."""
    r = client.get("/api/v1/assessments/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404
