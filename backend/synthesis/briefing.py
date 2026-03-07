"""
AI synthesis using Amazon Nova 2 Lite via AWS Bedrock Converse API.
Takes all extracted data and produces a structured company briefing.
"""
import json
import logging
from backend.models.schemas import ExtractedData, Briefing
from backend.config import settings

logger = logging.getLogger(__name__)


SYNTHESIS_PROMPT = """You are a sales intelligence analyst. Given research data collected from multiple sources about a company, produce a structured briefing for a sales professional who has a meeting with this company.

## Source Data
{extracted_data}

## Output Format
Respond with ONLY a valid JSON object matching this schema (no markdown fences, no extra text):

{{
  "company_name": "string",
  "summary": "2-3 sentence executive summary",
  "business_model": "How they make money",
  "industry": "Primary industry",
  "stage": "Startup/Growth/Enterprise/Public",
  "founded": "Year or Unknown",
  "headquarters": "City, Country",
  "size": "Employee count or range",
  "website": "URL",
  "key_people": [
    {{"name": "string", "title": "string"}}
  ],
  "recent_news": [
    {{"headline": "string", "date": "string", "summary": "string"}}
  ],
  "tech_stack": {{
    "confirmed": ["technologies found on website or job listings"],
    "inferred": ["technologies implied by context"]
  }},
  "growth_signals": [
    "Concrete observation about growth"
  ],
  "competitive_landscape": ["Competitor names"],
  "talking_points": [
    "Suggested conversation starter referencing specific findings"
  ],
  "products_services": ["Product or service 1"],
  "funding": {{
    "total_raised": "Amount or Unknown",
    "last_round": "Type and amount",
    "investors": ["Investor names"]
  }},
  "confidence": 0.8
}}

## Rules
- Only include information from the source data. Never fabricate.
- If a field has no data, use null or empty array.
- Talking points should reference SPECIFIC findings.
- Growth signals must be concrete observations.
- Confidence: 0.9+ if 4+ sources succeeded, 0.7+ if 3, 0.5+ if 2, below 0.5 if only 1."""


async def synthesize_briefing(extracted_data: ExtractedData) -> Briefing:
    """Call Nova 2 Lite via Bedrock Converse API to synthesize a briefing."""
    try:
        import boto3

        data_text = _format_extracted_data(extracted_data)
        prompt = SYNTHESIS_PROMPT.format(extracted_data=data_text)

        client = boto3.client(
            "bedrock-runtime",
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id or None,
            aws_secret_access_key=settings.aws_secret_access_key or None,
        )

        response = client.converse(
            modelId=settings.bedrock_model_id,
            messages=[
                {
                    "role": "user",
                    "content": [{"text": prompt}],
                }
            ],
            inferenceConfig={
                "maxTokens": 2048,
                "temperature": 0.1,
            },
        )

        raw_text = response["output"]["message"]["content"][0]["text"]

        # Strip markdown fences if present (LLMs often add ```json ... ```)
        text = raw_text.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            # Remove first line (```json or ```) and last line (```)
            text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

        # Parse JSON response
        briefing_data = json.loads(text.strip())
        return Briefing(**briefing_data)

    except ImportError:
        logger.error("boto3 not installed")
        return Briefing(
            summary=f"Could not synthesize: boto3 not available.",
            confidence=0.0,
        )
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Nova response as JSON: {e}")
        return Briefing(
            summary=f"Data extracted but synthesis JSON parse failed: {e}",
            confidence=0.0,
        )
    except Exception as e:
        logger.error(f"Bedrock synthesis error: {e}")
        return Briefing(
            summary=f"Research data collected but synthesis failed: {str(e)}",
            confidence=0.0,
        )


def _format_extracted_data(extracted_data: ExtractedData) -> str:
    """Format extracted results into readable text for the LLM prompt."""
    parts = []
    for result in extracted_data.results:
        if result.success and result.data:
            parts.append(f"=== {result.source.upper()} ===")
            for key, value in result.data.items():
                parts.append(f"{key}: {value}")
        elif not result.success:
            parts.append(f"=== {result.source.upper()} === [FAILED: {result.error}]")
    return "\n".join(parts) if parts else "No data extracted."
