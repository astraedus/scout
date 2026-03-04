"""
Careers / job listings extractor — signals company growth and tech stack.
"""
import asyncio
from typing import Optional
from backend.extractors.base import BaseExtractor
from backend.models.schemas import ExtractorResult
import logging

logger = logging.getLogger(__name__)


class CareersExtractor(BaseExtractor):
    source_name = "careers"

    async def extract(self, company_name: str, website_url: Optional[str] = None) -> ExtractorResult:
        try:
            from nova_act import NovaAct

            # Search for careers page
            if website_url:
                start_url = website_url.rstrip('/') + '/careers'
            else:
                start_url = f"https://www.google.com/search?q={company_name}+careers+jobs+hiring"

            def _run():
                with NovaAct(starting_page=start_url) as nova:
                    if not website_url:
                        nova.act(
                            f"Click on the first result that looks like a careers or jobs page for {company_name}"
                        )

                    data = nova.act_get(
                        f"Extract job listing information for {company_name}: "
                        "number of open positions, job categories (engineering, sales, etc.), "
                        "specific technologies mentioned (programming languages, frameworks, tools), "
                        "seniority levels, location patterns (remote/hybrid/cities), "
                        "which departments are growing fastest. "
                        "Return as structured text."
                    ).response

                    return {"careers_data": data}

            result = await asyncio.get_event_loop().run_in_executor(None, _run)
            return self._success(result)

        except ImportError:
            return self._failure("nova_act package not installed")
        except Exception as e:
            return self._failure(str(e))
