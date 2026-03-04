"""
Mock extractors for development without Nova Act API key.
Returns realistic sample data so the full pipeline can be tested.
"""
import asyncio
import random
from typing import Optional
from backend.extractors.base import BaseExtractor
from backend.models.schemas import ExtractorResult


MOCK_DATA = {
    "stripe": {
        "website": {
            "homepage": "Stripe is a financial infrastructure platform for businesses. They build economic infrastructure for the internet, offering payment processing, billing, and financial tools. Products include: Stripe Payments, Stripe Billing, Stripe Connect, Stripe Terminal, Stripe Atlas, Stripe Radar (fraud detection), Stripe Treasury. Technology: built on modern APIs, supports 135+ currencies.",
            "team": "Patrick Collison - CEO & Co-founder, John Collison - President & Co-founder, David Singleton - CTO, Dhivya Suryadevara - CFO. Founded 2010 in San Francisco. ~8,000+ employees globally.",
            "final_url": "https://stripe.com",
        },
        "google_news": {
            "articles_raw": "1. 'Stripe launches new AI-powered fraud detection features' - TechCrunch, Feb 2026. Stripe enhanced Radar with ML models reducing false declines by 30%. 2. 'Stripe valued at $91B in latest secondary market trading' - Bloomberg, Jan 2026. Valuation recovery after 2023 cuts. 3. 'Stripe expands to 5 new African markets' - Reuters, Feb 2026. Continued emerging market push. 4. 'Stripe and Anthropic partner on AI billing infrastructure' - The Verge, Mar 2026. New usage-based billing features for AI companies."
        },
        "linkedin": {
            "about": "Stripe is a technology company that builds economic infrastructure for the internet. Industry: Financial Technology. Size: 5,001-10,000 employees. HQ: San Francisco, CA. Founded: 2010. Specialties: Payments, Billing, Financial Infrastructure, Developer Tools, API Platform.",
            "people": "Key leadership: Patrick Collison (CEO), John Collison (President), David Singleton (CTO), Dhivya Suryadevara (CFO), Will Gaybrick (Chief Product Officer), Mike Clayville (Chief Revenue Officer). Total: 8,200+ employees on LinkedIn.",
        },
        "crunchbase": {
            "crunchbase_data": "Total Funding: $8.7B across 20 rounds. Last Round: Series I, $6.5B at $50B valuation (March 2023). Key Investors: Sequoia Capital, Andreessen Horowitz, Tiger Global, General Catalyst, Thrive Capital, GV (Google Ventures). Founded: 2010. Employees: 5,001-10,000. Revenue estimate: $14B+ ARR. Categories: FinTech, Payments, SaaS, Developer Tools."
        },
        "careers": {
            "careers_data": "Open positions: 280+. Engineering: 120 roles (Backend, Infrastructure, ML/AI, Mobile, Frontend). Product: 35 roles. Sales: 45 roles. Design: 15 roles. Operations: 65 roles. Technologies: Ruby, Go, Java, TypeScript, React, AWS, Kubernetes, Terraform. Seniority: mix of IC3-IC6. Locations: SF, Seattle, NYC, Dublin, Singapore, London, remote eligible. Heavy hiring in ML/AI and Infrastructure teams."
        },
    },
}

# Default mock data for unknown companies
DEFAULT_MOCK = {
    "website": {
        "homepage": "Company appears to be in the technology sector. Limited information available from public website. Main products/services could not be fully determined.",
        "team": "Leadership team not publicly listed on website.",
        "final_url": "https://example.com",
    },
    "google_news": {
        "articles_raw": "No significant recent news articles found in the last 60 days."
    },
    "linkedin": {
        "about": "Company profile found but limited public data available. Industry: Technology.",
        "people": "Key leadership not publicly visible on LinkedIn.",
    },
    "crunchbase": {
        "crunchbase_data": "Limited data available. Company may be privately held or not listed on Crunchbase."
    },
    "careers": {
        "careers_data": "No careers page found or no current open positions listed."
    },
}


def _get_mock_data(company_name: str, source: str) -> dict:
    """Get mock data for a company and source."""
    key = company_name.lower().strip()
    if key in MOCK_DATA and source in MOCK_DATA[key]:
        return MOCK_DATA[key][source]
    return DEFAULT_MOCK.get(source, {})


class MockWebsiteExtractor(BaseExtractor):
    source_name = "website"

    async def extract(self, company_name: str, website_url: Optional[str] = None) -> ExtractorResult:
        await asyncio.sleep(random.uniform(1.5, 3.0))  # Simulate delay
        return self._success(_get_mock_data(company_name, "website"))


class MockGoogleNewsExtractor(BaseExtractor):
    source_name = "google_news"

    async def extract(self, company_name: str, website_url: Optional[str] = None) -> ExtractorResult:
        await asyncio.sleep(random.uniform(2.0, 4.0))
        return self._success(_get_mock_data(company_name, "google_news"))


class MockLinkedInExtractor(BaseExtractor):
    source_name = "linkedin"

    async def extract(self, company_name: str, website_url: Optional[str] = None) -> ExtractorResult:
        await asyncio.sleep(random.uniform(2.5, 5.0))
        return self._success(_get_mock_data(company_name, "linkedin"))


class MockCrunchbaseExtractor(BaseExtractor):
    source_name = "crunchbase"

    async def extract(self, company_name: str, website_url: Optional[str] = None) -> ExtractorResult:
        await asyncio.sleep(random.uniform(2.0, 4.0))
        return self._success(_get_mock_data(company_name, "crunchbase"))


class MockCareersExtractor(BaseExtractor):
    source_name = "careers"

    async def extract(self, company_name: str, website_url: Optional[str] = None) -> ExtractorResult:
        await asyncio.sleep(random.uniform(1.5, 3.5))
        return self._success(_get_mock_data(company_name, "careers"))
