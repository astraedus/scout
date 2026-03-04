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
            import asyncio
            from nova_act import NovaAct

            start_url = website_url or f"https://www.google.com/search?q={company_name}+official+website"

            def _run_extraction():
                with NovaAct(starting_page=start_url) as nova:
                    # If we started from Google, navigate to the company site
                    if not website_url:
                        nova.act(f"Click on the first search result that looks like the official website for {company_name}")

                    # Extract main page info
                    homepage_data = nova.act(
                        f"Extract the following information about {company_name} from this page: "
                        "company name and tagline, what they do (1-2 sentences), "
                        "products or services offered, any technology or platform mentions, "
                        "contact information if visible. Return as structured text."
                    ).response

                    # Try to find and visit About/Team page
                    team_data = ""
                    try:
                        nova.act("Look for and click on an 'About', 'About Us', or 'Team' link in the navigation")
                        team_data = nova.act(
                            "Extract leadership team members with their names and titles. "
                            "Also note company size, founding year, mission statement if mentioned. "
                            "Return as structured text."
                        ).response
                    except Exception:
                        team_data = "About/Team page not found"

                    return {
                        "homepage": homepage_data,
                        "team": team_data,
                        "final_url": str(nova.page.url) if hasattr(nova, 'page') else start_url,
                    }

            # Nova Act is sync — run in thread pool
            data = await asyncio.get_event_loop().run_in_executor(None, _run_extraction)
            return self._success(data)

        except ImportError:
            return self._failure("nova_act package not installed")
        except Exception as e:
            return self._failure(str(e))
