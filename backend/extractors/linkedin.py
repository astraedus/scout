"""
LinkedIn company page extractor using Nova Act.
"""
from typing import Optional
from backend.extractors.base import BaseExtractor
from backend.models.schemas import ExtractorResult
from backend.config import settings
import logging

logger = logging.getLogger(__name__)


class LinkedInExtractor(BaseExtractor):
    """
    Extracts company info from LinkedIn company page.
    Gets employee count, industry, specialties, and recent posts.
    """

    source_name = "linkedin"

    async def extract(self, company_name: str, website_url: Optional[str] = None) -> ExtractorResult:
        try:
            from nova_act import NovaAct

            search_url = (
                f"https://www.linkedin.com/search/results/companies/?keywords={company_name.replace(' ', '%20')}"
            )

            with NovaAct(starting_url=search_url, api_key=settings.nova_act_api_key) as nova:
                # Navigate to the company page
                nova.act(f"Click on the first result for {company_name} company page.")

                result = nova.act(
                    f"Extract company information from this LinkedIn page for {company_name}. "
                    "Get: employee count, industry, headquarters, founding year, company description, "
                    "specialties/focus areas, and any recent company updates.",
                    schema={
                        "type": "object",
                        "properties": {
                            "employee_count": {"type": "string"},
                            "industry": {"type": "string"},
                            "headquarters": {"type": "string"},
                            "founded": {"type": "string"},
                            "description": {"type": "string"},
                            "specialties": {"type": "array", "items": {"type": "string"}},
                            "followers": {"type": "string"},
                        },
                    },
                )

                data = result.parsed_response or {}
                return self._success(data)

        except ImportError:
            return self._failure("nova_act package not installed")
        except Exception as e:
            return self._failure(str(e))
