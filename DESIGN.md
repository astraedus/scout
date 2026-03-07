# Scout — Design Document

## Extraction Prompts (Nova Act)

### 1. Company Website Extractor
```
Navigate to {url}. Extract the following information:
- Company name and tagline
- What the company does (1-2 sentences)
- Products or services offered (list)
- Leadership team (names and titles, if visible on about/team page)
- Company size indicators (employee count mentions, office locations)
- Technology mentions (tech stack, platforms used)
- Recent announcements or news on the site
- Contact information (email, phone if visible)

If there's an "About" or "Team" page linked from the homepage, navigate to it first.
Return all findings as structured text.
```

### 2. Google News Extractor
```
Navigate to https://news.google.com. Search for "{company_name}".
Extract the top 5-8 recent news articles:
- Headline
- Source publication
- Date published
- 1-sentence summary of the article

Focus on articles from the last 60 days. If no recent news, note that.
Return findings as structured text.
```

### 3. LinkedIn Company Extractor
```
Navigate to https://www.linkedin.com/company/{company_slug}/about/
Extract:
- Company description/overview
- Industry
- Company size (employee count range)
- Headquarters location
- Founded year
- Website URL
- Specialties

Then navigate to the company's "People" tab. Note:
- Total employee count
- Key leadership (CEO, CTO, VP roles) with names

Return findings as structured text.
```

### 4. Crunchbase Extractor
```
Navigate to https://www.crunchbase.com/organization/{company_slug}
Extract whatever is visible without login:
- Funding status and total raised
- Last funding round (type, amount, date)
- Key investors
- Revenue estimate (if shown)
- Number of employees (range)
- Founded date
- Categories/industries

Note: Crunchbase may paywall some data. Extract what's visible.
Return findings as structured text.
```

### 5. Careers/Job Listings Extractor
```
Navigate to {company_url}/careers or {company_url}/jobs.
If no careers page, search Google for "{company_name} careers jobs".
Extract:
- Number of open positions
- Job categories (engineering, sales, marketing, etc.)
- Technology requirements mentioned (programming languages, frameworks, tools)
- Seniority levels (junior, senior, lead, VP)
- Location patterns (remote, hybrid, specific cities)
- Growth signals (how many roles, which departments growing fastest)

Return findings as structured text.
```

## Synthesis Prompt (Nova 2 Lite)

```
You are a sales intelligence analyst. Given research data collected from multiple sources about a company, produce a structured briefing for a sales professional who has a meeting with this company.

## Source Data
{extracted_data_from_all_sources}

## Output Format (JSON)
{
  "company_name": "string",
  "overview": {
    "description": "What they do in 2-3 sentences",
    "industry": "Primary industry",
    "stage": "Startup/Growth/Enterprise/Public",
    "founded": "Year or 'Unknown'",
    "headquarters": "City, State/Country",
    "size": "Employee count or range",
    "website": "URL"
  },
  "key_people": [
    {"name": "string", "title": "string", "linkedin": "URL or null"}
  ],
  "recent_news": [
    {"headline": "string", "date": "string", "source": "string", "summary": "string"}
  ],
  "tech_stack": {
    "confirmed": ["technologies mentioned on website or job listings"],
    "inferred": ["technologies implied by job listings or industry"]
  },
  "growth_signals": [
    "Signal 1: e.g., 'Hiring 15 engineers — aggressive growth'",
    "Signal 2: e.g., 'Series B raised 6 months ago'",
    "Signal 3: e.g., 'Expanding to European market'"
  ],
  "competitive_landscape": [
    "Competitor 1",
    "Competitor 2"
  ],
  "talking_points": [
    "Suggested conversation starter 1",
    "Suggested conversation starter 2",
    "Suggested conversation starter 3"
  ],
  "data_quality": {
    "sources_successful": ["website", "google_news", "linkedin"],
    "sources_failed": ["crunchbase"],
    "confidence": "high/medium/low",
    "last_updated": "ISO timestamp"
  }
}

## Rules
- Only include information you found in the source data. Never fabricate.
- If a field has no data, use null or empty array.
- Talking points should reference SPECIFIC things found (recent news, tech stack, growth).
- Growth signals should be concrete observations, not generic statements.
- Keep the overview concise — this is a quick-reference briefing, not a report.
```

## Data Schema (Pydantic)

```python
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ResearchStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class ExtractorResult(BaseModel):
    source: str  # "website", "google_news", "linkedin", "crunchbase", "careers"
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
    screenshot_path: Optional[str] = None
    extraction_time_seconds: Optional[float] = None

class KeyPerson(BaseModel):
    name: str
    title: str
    linkedin: Optional[str] = None

class NewsItem(BaseModel):
    headline: str
    date: Optional[str] = None
    source: Optional[str] = None
    summary: Optional[str] = None

class TechStack(BaseModel):
    confirmed: List[str] = []
    inferred: List[str] = []

class DataQuality(BaseModel):
    sources_successful: List[str] = []
    sources_failed: List[str] = []
    confidence: str = "low"
    last_updated: Optional[str] = None

class CompanyOverview(BaseModel):
    description: Optional[str] = None
    industry: Optional[str] = None
    stage: Optional[str] = None
    founded: Optional[str] = None
    headquarters: Optional[str] = None
    size: Optional[str] = None
    website: Optional[str] = None

class Briefing(BaseModel):
    company_name: str
    overview: CompanyOverview
    key_people: List[KeyPerson] = []
    recent_news: List[NewsItem] = []
    tech_stack: TechStack = TechStack()
    growth_signals: List[str] = []
    competitive_landscape: List[str] = []
    talking_points: List[str] = []
    data_quality: DataQuality = DataQuality()

class ResearchJob(BaseModel):
    id: str
    company_name: str
    status: ResearchStatus = ResearchStatus.PENDING
    created_at: datetime
    completed_at: Optional[datetime] = None
    extractor_results: List[ExtractorResult] = []
    briefing: Optional[Briefing] = None
    progress_messages: List[str] = []
```

## API Endpoints

### POST /api/research
Request: `{"company_name": "Stripe", "website_url": "https://stripe.com"}`
Response: `{"job_id": "abc123", "status": "pending"}`

### GET /api/research/{job_id}
Response: Full ResearchJob with current status, progress messages, and briefing when complete.

### GET /api/research/{job_id}/stream
SSE stream of progress updates:
```
data: {"type": "progress", "message": "Visiting company website..."}
data: {"type": "progress", "message": "Searching Google News..."}
data: {"type": "extractor_complete", "source": "website", "success": true}
data: {"type": "extractor_complete", "source": "google_news", "success": true}
data: {"type": "synthesis", "message": "Generating briefing..."}
data: {"type": "complete", "briefing": {...}}
```

### GET /api/history
Response: List of past ResearchJobs (id, company_name, status, created_at).

## Frontend Pages

### / (Dashboard)
- Search bar: "Research a company..."
- Below: list of recent research jobs with status
- Click a job → expand to full briefing

### /research/{id} (Briefing View)
- Company name + overview card
- Collapsible sections: Key People, News, Tech Stack, Growth Signals, Talking Points
- Evidence panel: screenshots from each source
- Data quality indicator: which sources succeeded/failed
- "Export as PDF" button (nice-to-have)

## Graceful Degradation Rules
1. If LinkedIn blocks → skip, note "LinkedIn data unavailable"
2. If Crunchbase paywalled → extract visible data, note limitation
3. If careers page not found → skip, note "No careers page found"
4. Minimum viable: company website + Google News (always accessible)
5. Always produce a briefing from whatever sources succeed
6. Timeout per extractor: 60 seconds. If exceeded, skip with note.
