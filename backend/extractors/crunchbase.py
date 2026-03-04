"""
Crunchbase extractor — funding rounds, investors, and company vitals.
"""
from typing import Optional
from backend.extractors.base import BaseExtractor
from backend.models.schemas import ExtractorResult
from backend.config import settings
import logging

logger = logging.getLogger(__name__)


class CrunchbaseExtractor(BaseExtractor):
    """
    Extracts funding, investor, and company data from Crunchbase.
    """

    source_name = "crunchbase"

    async def extract(self, company_name: str, website_url: Optional[str] = None) -> ExtractorResult:
        try:
            from nova_act import NovaAct

            search_url = f"https://www.crunchbase.com/textsearch?q={company_name.replace(' ', '%20')}"

            with NovaAct(starting_url=search_url, api_key=settings.nova_act_api_key) as nova:
                # Click through to company page
                nova.act(f"Click on the company result for {company_name}.")

                result = nova.act(
                    f"Extract funding and company data for {company_name} from Crunchbase. "
                    "Get: total funding amount, funding stage, last funding date, key investors, "
                    "founding year, number of employees, headquarters, and any notable acquisitions.",
                    schema={
                        "type": "object",
                        "properties": {
                            "total_funding": {"type": "string"},
                            "funding_stage": {"type": "string"},
                            "last_funding_date": {"type": "string"},
                            "last_funding_amount": {"type": "string"},
                            "investors": {"type": "array", "items": {"type": "string"}},
                            "founded": {"type": "string"},
                            "employee_count": {"type": "string"},
                            "headquarters": {"type": "string"},
                            "acquisitions": {"type": "array", "items": {"type": "string"}},
                        },
                    },
                )

                data = result.parsed_response or {}
                return self._success(data)

        except ImportError:
            return self._failure("nova_act package not installed")
        except Exception as e:
            return self._failure(str(e))
