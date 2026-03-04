"""
Pydantic models for Scout data structures.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ResearchStatus(str, Enum):
    PENDING = "pending"
    EXTRACTING = "extracting"
    SYNTHESIZING = "synthesizing"
    COMPLETE = "complete"
    FAILED = "failed"


class ExtractorResult(BaseModel):
    """Result from a single extractor."""
    source: str  # "website", "google_news", "linkedin", "crunchbase", "careers"
    success: bool
    data: dict = Field(default_factory=dict)
    error: Optional[str] = None
    extracted_at: datetime = Field(default_factory=datetime.utcnow)


class ExtractedData(BaseModel):
    """Aggregated data from all extractors."""
    company_name: str
    website_url: Optional[str] = None
    results: List[ExtractorResult] = Field(default_factory=list)


class KeyPerson(BaseModel):
    name: str
    title: str

class NewsItem(BaseModel):
    headline: str
    date: Optional[str] = None
    summary: Optional[str] = None

class TechStack(BaseModel):
    confirmed: List[str] = Field(default_factory=list)
    inferred: List[str] = Field(default_factory=list)

class FundingInfo(BaseModel):
    total_raised: Optional[str] = None
    last_round: Optional[str] = None
    investors: List[str] = Field(default_factory=list)


class Briefing(BaseModel):
    """AI-synthesized company briefing from Nova 2 Lite."""
    company_name: Optional[str] = None
    summary: str
    business_model: Optional[str] = None
    industry: Optional[str] = None
    stage: Optional[str] = None
    founded: Optional[str] = None
    headquarters: Optional[str] = None
    size: Optional[str] = None
    website: Optional[str] = None
    products_services: List[str] = Field(default_factory=list)
    key_people: List[KeyPerson] = Field(default_factory=list)
    recent_news: List[NewsItem] = Field(default_factory=list)
    tech_stack: TechStack = Field(default_factory=TechStack)
    growth_signals: List[str] = Field(default_factory=list)
    competitive_landscape: List[str] = Field(default_factory=list)
    talking_points: List[str] = Field(default_factory=list)
    funding: Optional[FundingInfo] = None
    confidence: float = 0.0


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
    stage: str
    progress: int  # 0-100
    message: Optional[str] = None
