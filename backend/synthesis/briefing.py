"""
AI synthesis using Amazon Nova 2 Lite via AWS Bedrock.
Takes all extracted data and produces a structured company briefing.
"""
import json
import logging
from backend.models.schemas import ExtractedData, Briefing
from backend.config import settings

logger = logging.getLogger(__name__)


SYNTHESIS_PROMPT_TEMPLATE = """You are an expert business analyst. You have been given raw data extracted from multiple sources about a company.
Your task is to synthesize this data into a concise, actionable company briefing.

Company: {company_name}

Extracted Data:
{extracted_data}

Based on the above data, provide a structured briefing. Be factual and only use information present in the extracted data.
If data is missing or contradictory, note it. Output valid JSON matching the schema below.

Required JSON schema:
{{
  "summary": "2-3 sentence executive summary of the company",
  "business_model": "How the company makes money (SaaS, marketplace, services, etc.)",
  "products_services": ["list", "of", "key", "products", "or", "services"],
  "target_market": "Who are their primary customers",
  "funding_stage": "Bootstrap / Seed / Series A / Series B / Series C+ / Public / Unknown",
  "key_people": ["Founder Name - Role", "..."],
  "recent_news": ["Notable recent development 1", "..."],
  "open_roles": ["Role Title - Department", "..."],
  "tech_stack": ["Technology 1", "..."],
  "competitive_landscape": "Brief note on competitors and positioning",
  "sentiment": "positive|neutral|negative",
  "confidence": 0.0
}}

Respond with only the JSON object, no markdown fences."""


async def synthesize_briefing(extracted_data: ExtractedData) -> Briefing:
    """
    Call Amazon Nova 2 Lite via Bedrock to synthesize a company briefing.

    Args:
        extracted_data: Aggregated extraction results from all extractors.

    Returns:
        Briefing object. On failure, returns a minimal briefing with error info.
    """
    try:
        import boto3

        # Build a condensed representation of all extracted data
        data_summary = _format_extracted_data(extracted_data)

        prompt = SYNTHESIS_PROMPT_TEMPLATE.format(
            company_name=extracted_data.company_name,
            extracted_data=data_summary,
        )

        client = boto3.client(
            "bedrock-runtime",
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id or None,
            aws_secret_access_key=settings.aws_secret_access_key or None,
        )

        body = json.dumps({
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}],
                }
            ],
            "inferenceConfig": {
                "max_new_tokens": 1024,
                "temperature": 0.1,
            },
        })

        response = client.invoke_model(
            modelId=settings.bedrock_model_id,
            contentType="application/json",
            accept="application/json",
            body=body,
        )

        response_body = json.loads(response["body"].read())
        raw_text = response_body["output"]["message"]["content"][0]["text"]

        # Parse the JSON response
        briefing_data = json.loads(raw_text.strip())
        return Briefing(**briefing_data)

    except ImportError:
        logger.error("boto3 not installed")
        return Briefing(
            summary=f"Could not synthesize briefing for {extracted_data.company_name}: boto3 not available.",
            confidence=0.0,
        )
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Nova response as JSON: {e}")
        return Briefing(
            summary=f"Data extracted but synthesis failed (JSON parse error): {e}",
            confidence=0.0,
        )
    except Exception as e:
        logger.error(f"Bedrock synthesis error: {e}")
        return Briefing(
            summary=f"Research data collected but synthesis failed: {str(e)}",
            confidence=0.0,
        )


def _format_extracted_data(extracted_data: ExtractedData) -> str:
    """Format extracted results into a readable string for the LLM prompt."""
    parts = []
    for result in extracted_data.results:
        if result.success and result.data:
            parts.append(f"=== {result.source.upper()} ===")
            parts.append(json.dumps(result.data, indent=2))
        elif not result.success:
            parts.append(f"=== {result.source.upper()} === [FAILED: {result.error}]")
    return "\n".join(parts) if parts else "No data extracted."
