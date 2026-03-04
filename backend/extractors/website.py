"""
Company website extractor using Nova Act browser automation.
"""
from typing import Optional
from backend.extractors.base import BaseExtractor
from backend.models.schemas import ExtractorResult
from backend.config import settings
import logging

logger = logging.getLogger(__name__)


class WebsiteExtractor(BaseExtractor):
    """
    Extracts company information from their main website.
    Uses Nova Act to browse the homepage, about page, and products page.
    """

    source_name = "website"

    async def extract(self, company_name: str, website_url: Optional[str] = None) -> ExtractorResult:
        try:
            from nova_act import NovaAct

            start_url = website_url or f"https://www.google.com/search?q={company_name}+official+website"

            with NovaAct(starting_url=start_url, api_key=settings.nova_act_api_key) as nova:
                # Get main page content
                result = nova.act(
                    f"You are researching {company_name}. "
                    "Extract the following from this webpage: "
                    "1. Company description/tagline "
                    "2. Main products or services "
                    "3. Target market/customers "
                    "4. Any mentioned team members or founders "
                    "Return as structured text.",
                    schema={
                        "type": "object",
                        "properties": {
                            "description": {"type": "string"},
                            "products_services": {"type": "array", "items": {"type": "string"}},
                            "target_market": {"type": "string"},
                            "team_members": {"type": "array", "items": {"type": "string"}},
                            "website_url": {"type": "string"},
                        },
                    },
                )

                data = result.parsed_response or {}
                data["website_url"] = nova.page.url
                return self._success(data)

        except ImportError:
            return self._failure("nova_act package not installed")
        except Exception as e:
            return self._failure(str(e))
