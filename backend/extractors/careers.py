"""
Careers / job listings extractor — signals company growth and tech stack.
"""
from typing import Optional
from backend.extractors.base import BaseExtractor
from backend.models.schemas import ExtractorResult
from backend.config import settings
import logging

logger = logging.getLogger(__name__)


class CareersExtractor(BaseExtractor):
    """
    Extracts open job listings from the company careers page or LinkedIn jobs.
    Job listings signal tech stack, growth areas, and company priorities.
    """

    source_name = "careers"

    async def extract(self, company_name: str, website_url: Optional[str] = None) -> ExtractorResult:
        try:
            from nova_act import NovaAct

            # Try company careers page first, fall back to LinkedIn jobs
            if website_url:
                start_url = website_url
            else:
                start_url = f"https://www.google.com/search?q={company_name.replace(' ', '+')}+careers+jobs"

            with NovaAct(starting_url=start_url, api_key=settings.nova_act_api_key) as nova:
                # Navigate to careers section
                nova.act(
                    f"Navigate to the careers or jobs section of {company_name}. "
                    "Look for a 'Careers', 'Jobs', or 'Work with us' link and click it."
                )

                result = nova.act(
                    f"Extract job listings information for {company_name}. "
                    "Get: list of open roles (title + department), technologies mentioned in job descriptions, "
                    "total number of open positions, and which departments are hiring most.",
                    schema={
                        "type": "object",
                        "properties": {
                            "open_roles": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "title": {"type": "string"},
                                        "department": {"type": "string"},
                                        "location": {"type": "string"},
                                    },
                                },
                            },
                            "tech_stack": {"type": "array", "items": {"type": "string"}},
                            "total_openings": {"type": "integer"},
                            "top_hiring_departments": {"type": "array", "items": {"type": "string"}},
                            "remote_friendly": {"type": "boolean"},
                        },
                    },
                )

                data = result.parsed_response or {}
                return self._success(data)

        except ImportError:
            return self._failure("nova_act package not installed")
        except Exception as e:
            return self._failure(str(e))
