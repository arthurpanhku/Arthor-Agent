"""
Arthor Agent — FastAPI application.
PRD §5; docs/01-architecture-and-tech-stack.md.
"""

import asyncio
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import assessments, health, kb
from app.core.config import settings
from app.kb.service import KnowledgeBaseService


@asynccontextmanager
async def lifespan(app: FastAPI):
    sync_task = None
    if settings.KB_AUTO_SYNC_INTERVAL_SECONDS > 0:
        sync_task = asyncio.create_task(_kb_auto_sync_loop())
    yield
    if sync_task:
        sync_task.cancel()
        with suppress(asyncio.CancelledError):
            await sync_task


async def _kb_auto_sync_loop():
    while True:
        kb_service = KnowledgeBaseService()
        kb_service.reindex_directory(settings.KB_AUTO_SYNC_DIR)
        await asyncio.sleep(settings.KB_AUTO_SYNC_INTERVAL_SECONDS)


app = FastAPI(
    title="Arthor Agent API",
    description=(
        "Arthor Agent — automated security assessment for documents and "
        "questionnaires. PRD-aligned."
    ),
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api-docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(assessments.router, prefix=settings.API_PREFIX)
app.include_router(kb.router, prefix=settings.API_PREFIX)

# Mount docs directory for demo purposes
# The directory is mounted at /docs, so files are accessible at /docs/filename
app.mount("/docs", StaticFiles(directory="docs", html=True), name="docs")


@app.get("/")
async def root():
    return {
        "service": "Arthor Agent",
        "api_docs": "/api-docs",
        "demo": "/docs/demo.html",
        "health": "/health",
    }
