"""
Crunchbase extractor — funding rounds, investors, and company vitals.
"""
import asyncio
from typing import Optional
from backend.extractors.base import BaseExtractor
from backend.models.schemas import ExtractorResult
import logging

logger = logging.getLogger(__name__)


class CrunchbaseExtractor(BaseExtractor):
    source_name = "crunchbase"

    async def extract(self, company_name: str, website_url: Optional[str] = None) -> ExtractorResult:
        try:
            from nova_act import NovaAct

            search_url = f"https://www.google.com/search?q={company_name}+site:crunchbase.com"

            def _run():
                with NovaAct(starting_page=search_url) as nova:
                    # Navigate to Crunchbase page via Google
                    nova.act(
                        f"Click on the first Crunchbase result for {company_name}"
                    )

                    # Extract whatever is visible (Crunchbase may paywall)
                    data = nova.act_get(
                        f"Extract all visible company data for {company_name} from Crunchbase: "
                        "funding status, total raised, last funding round (type, amount, date), "
                        "key investors, revenue estimate, employee count, founded date, "
                        "categories/industries. "
                        "Note if any data is behind a paywall."
                    ).response

                    return {"crunchbase_data": data}

            result = await asyncio.get_event_loop().run_in_executor(None, _run)
            return self._success(result)

        except ImportError:
            return self._failure("nova_act package not installed")
        except Exception as e:
            return self._failure(str(e))
