"""
Base extractor class. All extractors inherit from this.
"""
from abc import ABC, abstractmethod
from typing import Optional
from backend.models.schemas import ExtractorResult
import logging

logger = logging.getLogger(__name__)


class BaseExtractor(ABC):
    """
    Abstract base for all company data extractors.
    Subclasses implement extract() and return an ExtractorResult.
    Errors must be caught internally — never raise from extract().
    """

    source_name: str = "unknown"

    @abstractmethod
    async def extract(self, company_name: str, website_url: Optional[str] = None) -> ExtractorResult:
        """
        Extract data for a given company.

        Args:
            company_name: The company name to research.
            website_url: Optional known website URL to speed up extraction.

        Returns:
            ExtractorResult with success=True and data dict, or
            success=False with error string. Never raises.
        """
        ...

    def _success(self, data: dict) -> ExtractorResult:
        return ExtractorResult(source=self.source_name, success=True, data=data)

    def _failure(self, error: str) -> ExtractorResult:
        logger.warning(f"[{self.source_name}] extraction failed: {error}")
        return ExtractorResult(source=self.source_name, success=False, error=error)
