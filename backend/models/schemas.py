"""
Pydantic models for Scout data structures.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ResearchStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    EXTRACTING = "extracting"
    SYNTHESIZING = "synthesizing"
    COMPLETE = "complete"
    FAILED = "failed"


class ExtractorResult(BaseModel):
    """Result from a single extractor."""
    source: str  # e.g. "website", "google_news", "linkedin", "crunchbase", "careers"
    success: bool
    data: dict = Field(default_factory=dict)
    error: Optional[str] = None
    extracted_at: datetime = Field(default_factory=datetime.utcnow)


class ExtractedData(BaseModel):
    """Aggregated data from all extractors."""
    company_name: str
    website_url: Optional[str] = None
    results: List[ExtractorResult] = Field(default_factory=list)


class Briefing(BaseModel):
    """AI-synthesized company briefing from Nova 2 Lite."""
    summary: str
    business_model: Optional[str] = None
    products_services: Optional[List[str]] = None
    target_market: Optional[str] = None
    funding_stage: Optional[str] = None
    key_people: Optional[List[str]] = None
    recent_news: Optional[List[str]] = None
    open_roles: Optional[List[str]] = None
    tech_stack: Optional[List[str]] = None
    competitive_landscape: Optional[str] = None
    sentiment: Optional[str] = None  # positive / neutral / negative
    confidence: float = 0.0  # 0-1


class CompanyResearch(BaseModel):
    """Full research record for a company."""
    id: str
    company_name: str
    status: ResearchStatus = ResearchStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    extracted_data: Optional[ExtractedData] = None
    briefing: Optional[Briefing] = None
    error: Optional[str] = None


class ResearchRequest(BaseModel):
    """Incoming API request to research a company."""
    company_name: str
    website_url: Optional[str] = None


class ResearchResponse(BaseModel):
    """Response from POST /api/research."""
    id: str
    status: ResearchStatus
    message: str


class ProgressEvent(BaseModel):
    """SSE progress event sent to frontend."""
    research_id: str
    status: ResearchStatus
    stage: str  # human-readable current stage
    progress: int  # 0-100
    message: Optional[str] = None
