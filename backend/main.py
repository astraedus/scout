"""
Scout FastAPI backend.
Orchestrates company research: browser extraction + Nova 2 Lite synthesis.
"""
import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import AsyncGenerator, Optional
from collections import defaultdict
import time

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from backend.config import settings
from backend.db.database import init_db, save_research, get_research, get_all_research
from backend.models.schemas import (
    CompanyResearch,
    ExtractedData,
    ResearchRequest,
    ResearchResponse,
    ResearchStatus,
    ProgressEvent,
)
from backend.config import settings as app_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if app_settings.mock_mode:
    from backend.extractors.mock import (
        MockWebsiteExtractor as WebsiteExtractor,
        MockGoogleNewsExtractor as GoogleNewsExtractor,
        MockLinkedInExtractor as LinkedInExtractor,
        MockCrunchbaseExtractor as CrunchbaseExtractor,
        MockCareersExtractor as CareersExtractor,
    )
    from backend.synthesis.mock_briefing import mock_synthesize_briefing as synthesize_briefing
elif app_settings.nova_act_api_key:
    # Nova Act available — use full browser automation
    from backend.extractors.website import WebsiteExtractor
    from backend.extractors.google_news import GoogleNewsExtractor
    from backend.extractors.linkedin import LinkedInExtractor
    from backend.extractors.crunchbase import CrunchbaseExtractor
    from backend.extractors.careers import CareersExtractor
    from backend.synthesis.briefing import synthesize_briefing
    logger.info("Mode: Nova Act (full browser automation)")
else:
    # HTTP fallback — real data via requests/scraping + Bedrock synthesis
    from backend.extractors.http_website import HttpWebsiteExtractor as WebsiteExtractor
    from backend.extractors.http_news import HttpNewsExtractor as GoogleNewsExtractor
    from backend.extractors.mock import (
        MockLinkedInExtractor as LinkedInExtractor,
        MockCrunchbaseExtractor as CrunchbaseExtractor,
        MockCareersExtractor as CareersExtractor,
    )
    from backend.synthesis.briefing import synthesize_briefing
    logger.info("Mode: HTTP fallback (requests + Bedrock synthesis)")

app = FastAPI(title="Scout API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory SSE event queues: research_id -> asyncio.Queue
_sse_queues: dict[str, asyncio.Queue] = {}


@app.on_event("startup")
async def startup():
    await init_db()
    logger.info("Scout API started. DB initialized.")


# ---------------------------------------------------------------------------
# Research orchestration
# ---------------------------------------------------------------------------

async def _push_event(research_id: str, event: ProgressEvent) -> None:
    """Push an SSE event to any listening client."""
    queue = _sse_queues.get(research_id)
    if queue:
        await queue.put(event)


async def _run_research(research: CompanyResearch, website_url: "Optional[str]") -> None:
    """
    Background task: run all extractors, then synthesize, then save.
    Sends progress events via SSE throughout.
    """
    extractors = [
        (WebsiteExtractor(), "Visiting company website", 15),
        (GoogleNewsExtractor(), "Searching Google News", 30),
        (LinkedInExtractor(), "Scanning LinkedIn", 50),
        (CrunchbaseExtractor(), "Checking Crunchbase", 65),
        (CareersExtractor(), "Reviewing job listings", 80),
    ]

    results = []

    try:
        # Update to EXTRACTING
        research.status = ResearchStatus.EXTRACTING
        research.updated_at = datetime.utcnow()
        await save_research(research)

        for extractor, stage_label, progress in extractors:
            await _push_event(
                research.id,
                ProgressEvent(
                    research_id=research.id,
                    status=ResearchStatus.EXTRACTING,
                    stage=stage_label,
                    progress=progress,
                ),
            )

            result = await extractor.extract(research.company_name, website_url)
            results.append(result)
            logger.info(f"[{research.id}] {extractor.source_name}: success={result.success}")

        # Assemble extracted data
        extracted = ExtractedData(
            company_name=research.company_name,
            website_url=website_url,
            results=results,
        )
        research.extracted_data = extracted
        research.updated_at = datetime.utcnow()
        await save_research(research)

        # Synthesize
        research.status = ResearchStatus.SYNTHESIZING
        research.updated_at = datetime.utcnow()
        await save_research(research)
        await _push_event(
            research.id,
            ProgressEvent(
                research_id=research.id,
                status=ResearchStatus.SYNTHESIZING,
                stage="Synthesizing with Nova 2 Lite",
                progress=90,
            ),
        )

        briefing = await synthesize_briefing(extracted)
        research.briefing = briefing
        research.status = ResearchStatus.COMPLETE
        research.updated_at = datetime.utcnow()
        await save_research(research)

        await _push_event(
            research.id,
            ProgressEvent(
                research_id=research.id,
                status=ResearchStatus.COMPLETE,
                stage="Research complete",
                progress=100,
            ),
        )

    except Exception as e:
        logger.exception(f"[{research.id}] Research failed: {e}")
        research.status = ResearchStatus.FAILED
        research.error = str(e)
        research.updated_at = datetime.utcnow()
        await save_research(research)

        await _push_event(
            research.id,
            ProgressEvent(
                research_id=research.id,
                status=ResearchStatus.FAILED,
                stage="Research failed",
                progress=0,
                message=str(e),
            ),
        )

    finally:
        # Signal SSE stream to close
        queue = _sse_queues.get(research.id)
        if queue:
            await queue.put(None)  # Sentinel: stream done


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

# Simple in-memory rate limiter: max 5 requests per IP per hour
_rate_limit: dict = defaultdict(list)

@app.post("/api/research", response_model=ResearchResponse)
async def start_research(request: ResearchRequest, background_tasks: BackgroundTasks, req: Request):
    """Start a new company research job. Returns immediately with job ID."""
    ip = req.headers.get("cf-connecting-ip") or req.headers.get("x-forwarded-for", "unknown").split(",")[0].strip()
    now = time.time()
    _rate_limit[ip] = [t for t in _rate_limit[ip] if now - t < 3600]
    if len(_rate_limit[ip]) >= 5:
        raise HTTPException(status_code=429, detail="Rate limit: 5 research requests per hour per IP")
    _rate_limit[ip].append(now)
    research_id = str(uuid.uuid4())
    research = CompanyResearch(
        id=research_id,
        company_name=request.company_name,
        status=ResearchStatus.PENDING,
    )
    await save_research(research)

    # Create SSE queue for this research job
    _sse_queues[research_id] = asyncio.Queue()

    background_tasks.add_task(_run_research, research, request.website_url)

    return ResearchResponse(
        id=research_id,
        status=ResearchStatus.PENDING,
        message=f"Research started for {request.company_name}",
    )


@app.get("/api/research/{research_id}")
async def get_research_status(research_id: str):
    """Get current status and results for a research job."""
    research = await get_research(research_id)
    if not research:
        raise HTTPException(status_code=404, detail="Research not found")
    return research


@app.get("/api/research/{research_id}/stream")
async def stream_research_progress(research_id: str):
    """
    SSE endpoint for real-time progress updates.
    Connect immediately after POST /api/research to receive live progress.
    """
    # Create queue if not already created (e.g. reconnect scenario)
    if research_id not in _sse_queues:
        existing = await get_research(research_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Research not found")
        if existing.status in (ResearchStatus.COMPLETE, ResearchStatus.FAILED):
            # Already done — send final event and close
            async def done_stream():
                event = ProgressEvent(
                    research_id=research_id,
                    status=existing.status,
                    stage="Research complete" if existing.status == ResearchStatus.COMPLETE else "Research failed",
                    progress=100 if existing.status == ResearchStatus.COMPLETE else 0,
                )
                yield f"data: {event.model_dump_json()}\n\n"
            return StreamingResponse(done_stream(), media_type="text/event-stream")

        _sse_queues[research_id] = asyncio.Queue()

    queue = _sse_queues[research_id]

    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            while True:
                event = await asyncio.wait_for(queue.get(), timeout=60.0)
                if event is None:
                    # Sentinel — research is done
                    break
                yield f"data: {event.model_dump_json()}\n\n"
        except asyncio.TimeoutError:
            yield "data: {\"type\": \"keepalive\"}\n\n"
        finally:
            _sse_queues.pop(research_id, None)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/api/history")
async def get_history(limit: int = 20):
    """Get recent research history."""
    records = await get_all_research(limit=limit)
    return {"results": records, "count": len(records)}


@app.get("/health")
async def health():
    return {"status": "ok", "service": "scout-api"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=settings.port, reload=True)
