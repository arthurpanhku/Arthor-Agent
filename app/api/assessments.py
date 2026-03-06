"""
Assessment API: submit task, get result.
PRD §6; docs/02-api-specification.yaml.
"""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from app.agent.orchestrator import run_assessment
from app.kb.service import KnowledgeBaseService
from app.models.assessment import AssessmentTaskCreated, AssessmentTaskResult
from app.parser import parse_file

router = APIRouter(prefix="/assessments", tags=["assessment"])

# In-memory task store for MVP (replace with DB/Redis later)
_tasks: dict = {}


class ReviewActionRequest(BaseModel):
    action: str
    reviewer: str
    comment: str | None = None
    assignee: str | None = None


class CommentRequest(BaseModel):
    author: str
    comment: str
    mention: str | None = None


@router.post("", response_model=AssessmentTaskCreated)
async def submit_assessment(
    files: list[UploadFile] = File(  # noqa: B008
        ..., description="Documents to assess"
    ),
    scenario_id: str | None = Form(None),
    project_id: str | None = Form(None),
    collaborative_mode: bool = Form(True),
):
    """Submit an assessment task; returns task_id for polling."""
    from app.core.config import settings

    if len(files) > settings.UPLOAD_MAX_FILES:
        raise HTTPException(413, f"Max {settings.UPLOAD_MAX_FILES} files allowed")
    if not files:
        raise HTTPException(400, "At least one file required")

    task_id = uuid4()
    parsed_list = []
    for f in files:
        content = await f.read()
        if len(content) > settings.upload_max_bytes:
            raise HTTPException(
                413, f"File {f.filename} exceeds {settings.UPLOAD_MAX_FILE_SIZE_MB}MB"
            )
        try:
            parsed = parse_file(content, f.filename or "unknown")
            parsed_list.append(parsed)
        except ValueError as e:
            raise HTTPException(400, str(e)) from e

    created_at = datetime.now(timezone.utc)
    _tasks[str(task_id)] = {
        "status": "running",
        "report": None,
        "error": None,
        "created_at": created_at,
        "completed_at": None,
        "collaborative_mode": collaborative_mode,
        "version": 1,
        "assignee": None,
        "comments": [],
        "activity": [
            {
                "type": "task_created",
                "at": created_at.isoformat(),
                "message": "Assessment task created",
            }
        ],
        "revisions": [],
    }

    try:
        report = await run_assessment(
            task_id, parsed_list, scenario_id=scenario_id, project_id=project_id
        )
        target_status = "review_pending" if collaborative_mode else "completed"
        _tasks[str(task_id)]["status"] = target_status
        _tasks[str(task_id)]["report"] = report.model_dump()
        _tasks[str(task_id)]["completed_at"] = datetime.now(timezone.utc)
        _tasks[str(task_id)]["revisions"].append(
            {
                "version": 1,
                "status": target_status,
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "report": report.model_dump(),
            }
        )
        _tasks[str(task_id)]["activity"].append(
            {
                "type": "draft_generated",
                "at": datetime.now(timezone.utc).isoformat(),
                "message": "AI generated draft report",
            }
        )
        try:
            kb = KnowledgeBaseService()
            kb.add_history_response(
                task_id=str(task_id),
                version=_tasks[str(task_id)]["version"],
                scenario_id=scenario_id,
                report_json=report.model_dump(),
            )
        except Exception:
            _tasks[str(task_id)]["activity"].append(
                {
                    "type": "history_index_skipped",
                    "at": datetime.now(timezone.utc).isoformat(),
                    "message": "History indexing unavailable in current runtime",
                }
            )
    except Exception as e:
        _tasks[str(task_id)]["status"] = "failed"
        _tasks[str(task_id)]["error"] = str(e)
        _tasks[str(task_id)]["completed_at"] = datetime.now(timezone.utc)

    return AssessmentTaskCreated(
        task_id=task_id,
        status="accepted",
        message=(
            "Assessment task created. Use GET /assessments/{task_id} "
            "to retrieve the result."
        ),
    )


@router.get("/{task_id}", response_model=AssessmentTaskResult)
async def get_assessment(task_id: str):
    """Get assessment task status and report."""
    if task_id not in _tasks:
        raise HTTPException(404, "Task not found")
    t = _tasks[task_id]
    from app.models.assessment import AssessmentReport

    report = None
    if t.get("report"):
        report = AssessmentReport(**t["report"])
    return AssessmentTaskResult(
        task_id=UUID(task_id),
        status=t["status"],
        report=report,
        error_message=t.get("error"),
        created_at=t["created_at"],
        completed_at=t.get("completed_at"),
        version=t.get("version", 1),
        assignee=t.get("assignee"),
        comments=t.get("comments", []),
    )


@router.post("/{task_id}/review")
async def review_assessment(task_id: str, body: ReviewActionRequest):
    if task_id not in _tasks:
        raise HTTPException(404, "Task not found")
    task = _tasks[task_id]
    if task.get("status") not in {"review_pending", "rejected", "escalated"}:
        raise HTTPException(409, "Task is not in a reviewable state")
    action = body.action.lower().strip()
    status_mapping = {
        "approve": "approved",
        "reject": "rejected",
        "escalate": "escalated",
    }
    if action not in status_mapping:
        raise HTTPException(400, "action must be one of: approve, reject, escalate")
    task["status"] = status_mapping[action]
    task["assignee"] = body.assignee or task.get("assignee")
    task["version"] = int(task.get("version", 1)) + 1
    activity_entry = {
        "type": "review_action",
        "at": datetime.now(timezone.utc).isoformat(),
        "reviewer": body.reviewer,
        "action": action,
        "comment": body.comment,
        "assignee": task.get("assignee"),
        "version": task["version"],
    }
    task["activity"].append(activity_entry)
    if body.comment:
        task["comments"].append(
            {
                "author": body.reviewer,
                "comment": body.comment,
                "at": datetime.now(timezone.utc).isoformat(),
            }
        )
    task["revisions"].append(
        {
            "version": task["version"],
            "status": task["status"],
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "report": task.get("report"),
        }
    )
    if task.get("report"):
        try:
            kb = KnowledgeBaseService()
            kb.add_history_response(
                task_id=task_id,
                version=task["version"],
                scenario_id=task.get("report", {})
                .get("metadata", {})
                .get("scenario_id"),
                report_json=task["report"],
            )
        except Exception:
            task["activity"].append(
                {
                    "type": "history_index_skipped",
                    "at": datetime.now(timezone.utc).isoformat(),
                    "message": "History indexing unavailable in current runtime",
                }
            )
    return {
        "task_id": task_id,
        "status": task["status"],
        "version": task["version"],
        "assignee": task.get("assignee"),
    }


@router.post("/{task_id}/comment")
async def comment_assessment(task_id: str, body: CommentRequest):
    if task_id not in _tasks:
        raise HTTPException(404, "Task not found")
    task = _tasks[task_id]
    item = {
        "author": body.author,
        "comment": body.comment,
        "mention": body.mention,
        "at": datetime.now(timezone.utc).isoformat(),
    }
    task["comments"].append(item)
    task["activity"].append({"type": "comment", **item})
    if body.mention:
        task["assignee"] = body.mention
    return {
        "task_id": task_id,
        "comments": task["comments"],
        "assignee": task["assignee"],
    }


@router.get("/{task_id}/activity")
async def get_assessment_activity(task_id: str):
    if task_id not in _tasks:
        raise HTTPException(404, "Task not found")
    task = _tasks[task_id]
    return {
        "task_id": task_id,
        "status": task["status"],
        "version": task.get("version", 1),
        "activity": task.get("activity", []),
        "comments": task.get("comments", []),
        "revisions": task.get("revisions", []),
    }


@router.get("/{task_id}/reuse")
async def get_reuse_candidates(task_id: str, top_k: int = 3):
    if task_id not in _tasks:
        raise HTTPException(404, "Task not found")
    task = _tasks[task_id]
    report = task.get("report") or {}
    query_text = f"{report.get('summary', '')}\n{task_id}"
    try:
        kb = KnowledgeBaseService()
        docs = kb.query_history_responses(query_text, top_k=top_k)
    except Exception:
        docs = []
    return {
        "task_id": task_id,
        "reused_candidates": [
            {"content": d.page_content, "metadata": d.metadata} for d in docs
        ],
    }
