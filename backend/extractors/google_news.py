"""
Google News extractor — finds recent news about a company using Nova Act.
"""
from typing import Optional
from backend.extractors.base import BaseExtractor
from backend.models.schemas import ExtractorResult
from backend.config import settings
import logging

logger = logging.getLogger(__name__)


class GoogleNewsExtractor(BaseExtractor):
    """
    Searches Google News for recent articles about the company.
    Extracts headlines, dates, and summaries.
    """

    source_name = "google_news"

    async def extract(self, company_name: str, website_url: Optional[str] = None) -> ExtractorResult:
        try:
            from nova_act import NovaAct

            search_url = f"https://news.google.com/search?q={company_name.replace(' ', '+')}"

            with NovaAct(starting_url=search_url, api_key=settings.nova_act_api_key) as nova:
                result = nova.act(
                    f"Find recent news articles about {company_name}. "
                    "Extract up to 10 recent headlines with their dates and brief summaries. "
                    "Focus on funding announcements, product launches, partnerships, and company milestones.",
                    schema={
                        "type": "object",
                        "properties": {
                            "articles": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "headline": {"type": "string"},
                                        "date": {"type": "string"},
                                        "summary": {"type": "string"},
                                        "source": {"type": "string"},
                                    },
                                },
                            },
                            "sentiment": {"type": "string", "enum": ["positive", "neutral", "negative"]},
                        },
                    },
                )

                data = result.parsed_response or {"articles": []}
                return self._success(data)

        except ImportError:
            return self._failure("nova_act package not installed")
        except Exception as e:
            return self._failure(str(e))
