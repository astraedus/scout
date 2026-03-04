"""
Google News extractor — finds recent news about a company using Nova Act.
"""
import asyncio
from typing import Optional
from backend.extractors.base import BaseExtractor
from backend.models.schemas import ExtractorResult
import logging

logger = logging.getLogger(__name__)


class GoogleNewsExtractor(BaseExtractor):
    source_name = "google_news"

    async def extract(self, company_name: str, website_url: Optional[str] = None) -> ExtractorResult:
        try:
            from nova_act import NovaAct

            search_url = f"https://news.google.com/search?q={company_name.replace(' ', '+')}"

            def _run():
                with NovaAct(starting_page=search_url) as nova:
                    data = nova.act_get(
                        f"Extract the top 5-8 recent news articles about {company_name}. "
                        "For each article, provide: headline, source publication, "
                        "approximate date, and a 1-sentence summary. "
                        "Focus on articles from the last 60 days. "
                        "If no recent news is found, say so."
                    ).response
                    return {"articles_raw": data}

            result = await asyncio.get_event_loop().run_in_executor(None, _run)
            return self._success(result)

        except ImportError:
            return self._failure("nova_act package not installed")
        except Exception as e:
            return self._failure(str(e))
