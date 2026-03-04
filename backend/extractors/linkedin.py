"""
LinkedIn company page extractor using Nova Act.
"""
import asyncio
from typing import Optional
from backend.extractors.base import BaseExtractor
from backend.models.schemas import ExtractorResult
import logging

logger = logging.getLogger(__name__)


class LinkedInExtractor(BaseExtractor):
    source_name = "linkedin"

    async def extract(self, company_name: str, website_url: Optional[str] = None) -> ExtractorResult:
        try:
            from nova_act import NovaAct

            search_url = f"https://www.google.com/search?q={company_name}+site:linkedin.com/company"

            def _run():
                with NovaAct(starting_page=search_url) as nova:
                    # Navigate to the LinkedIn company page via Google
                    nova.act(
                        f"Click on the first LinkedIn company page result for {company_name}"
                    )

                    # Extract company info
                    about_data = nova.act(
                        f"Extract company information for {company_name} from this LinkedIn page: "
                        "company description/overview, industry, company size (employee count), "
                        "headquarters location, founded year, website URL, specialties. "
                        "Return all information as structured text."
                    ).response

                    # Try to get key people
                    people_data = ""
                    try:
                        nova.act("Navigate to the 'People' tab or section of this company page")
                        people_data = nova.act(
                            "List the key leadership: CEO, CTO, VP-level and above with names and titles. "
                            "Also note the total employee count shown."
                        ).response
                    except Exception:
                        people_data = "Could not access People section"

                    return {
                        "about": about_data,
                        "people": people_data,
                    }

            result = await asyncio.get_event_loop().run_in_executor(None, _run)
            return self._success(result)

        except ImportError:
            return self._failure("nova_act package not installed")
        except Exception as e:
            return self._failure(str(e))
