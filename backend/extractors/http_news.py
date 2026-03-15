"""
HTTP-based Google News extractor — fallback when Nova Act is unavailable.
Parses Google News RSS feed for recent articles.
"""
import asyncio
import xml.etree.ElementTree as ET
from typing import Optional
from urllib.parse import quote
from backend.extractors.base import BaseExtractor
from backend.models.schemas import ExtractorResult
import logging

logger = logging.getLogger(__name__)


class HttpNewsExtractor(BaseExtractor):
    source_name = "google_news"

    async def extract(self, company_name: str, website_url: Optional[str] = None) -> ExtractorResult:
        try:
            import httpx

            rss_url = f"https://news.google.com/rss/search?q={quote(company_name)}&hl=en-US&gl=US&ceid=US:en"

            async with httpx.AsyncClient(timeout=15, headers={
                "User-Agent": "Mozilla/5.0 (compatible; ResearchBot/1.0)"
            }) as client:
                resp = await client.get(rss_url)
                resp.raise_for_status()

            root = ET.fromstring(resp.text)
            channel = root.find("channel")
            if not channel:
                return self._failure("No RSS channel found")

            items = channel.findall("item")[:8]
            articles = []
            for item in items:
                title = item.findtext("title", "")
                source = item.findtext("source", "")
                pub_date = item.findtext("pubDate", "")
                description = item.findtext("description", "")
                link = item.findtext("link", "")

                # Clean HTML from description
                import re
                clean_desc = re.sub(r"<[^>]+>", "", description).strip()[:200]

                articles.append(
                    f"- {title} ({source}, {pub_date[:16]})\n  {clean_desc}\n  URL: {link}"
                )

            if not articles:
                return self._success({"articles_raw": f"No recent news found for {company_name}", "method": "http_rss"})

            return self._success({
                "articles_raw": f"Recent news for {company_name}:\n" + "\n".join(articles),
                "method": "http_rss"
            })

        except ImportError as e:
            return self._failure(f"Missing dependency: {e}. Install: pip install httpx")
        except Exception as e:
            return self._failure(str(e))
