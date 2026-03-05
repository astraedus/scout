"""
HTTP-based website extractor — fallback when Nova Act is unavailable.
Uses requests + BeautifulSoup for lightweight scraping.
"""
import asyncio
import re
from typing import Optional
from backend.extractors.base import BaseExtractor
from backend.models.schemas import ExtractorResult
import logging

logger = logging.getLogger(__name__)


class HttpWebsiteExtractor(BaseExtractor):
    """
    Extracts company info via HTTP scraping.
    Fallback path when Nova Act is not available.
    """
    source_name = "website"

    async def extract(self, company_name: str, website_url: Optional[str] = None) -> ExtractorResult:
        try:
            import httpx
            from bs4 import BeautifulSoup

            # Resolve URL if not provided
            if not website_url:
                website_url = await self._resolve_url(company_name)
            if not website_url:
                return self._failure(f"Could not resolve URL for {company_name}")

            async with httpx.AsyncClient(timeout=15, follow_redirects=True, headers={
                "User-Agent": "Mozilla/5.0 (compatible; ResearchBot/1.0)"
            }) as client:
                resp = await client.get(website_url)
                soup = BeautifulSoup(resp.text, "html.parser")

            # Extract key fields
            title = soup.find("title")
            title_text = title.get_text(strip=True) if title else ""

            # Meta description
            meta_desc = soup.find("meta", attrs={"name": "description"}) or \
                        soup.find("meta", attrs={"property": "og:description"})
            description = meta_desc.get("content", "") if meta_desc else ""

            # Main heading
            h1 = soup.find("h1")
            h1_text = h1.get_text(strip=True) if h1 else ""

            # OG tags
            og_title = soup.find("meta", property="og:title")
            og_title_text = og_title.get("content", "") if og_title else ""

            # Key text blocks (hero/about)
            body_text = " ".join(soup.get_text(separator=" ").split()[:300])

            homepage_data = (
                f"Title: {title_text}\n"
                f"Tagline: {h1_text or og_title_text}\n"
                f"Description: {description}\n"
                f"Content preview: {body_text}"
            )

            return self._success({
                "homepage": homepage_data,
                "team": "Team info requires deeper extraction",
                "final_url": website_url,
                "method": "http"
            })

        except ImportError as e:
            return self._failure(f"Missing dependency: {e}. Install: pip install httpx beautifulsoup4")
        except Exception as e:
            return self._failure(str(e))

    async def _resolve_url(self, company_name: str) -> Optional[str]:
        """Use DuckDuckGo instant answers to find company URL."""
        try:
            import httpx
            query = company_name.replace(" ", "+") + "+official+website"
            async with httpx.AsyncClient(timeout=10, headers={
                "User-Agent": "Mozilla/5.0"
            }) as client:
                resp = await client.get(
                    f"https://api.duckduckgo.com/?q={query}&format=json&no_redirect=1"
                )
                data = resp.json()
                if data.get("AbstractURL"):
                    return data["AbstractURL"]
                # Fallback: construct likely URL
                slug = company_name.lower().replace(" ", "").replace(",", "").replace(".", "")
                return f"https://www.{slug}.com"
        except Exception:
            return None
