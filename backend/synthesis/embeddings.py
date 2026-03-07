"""
Nova Multimodal Embeddings via AWS Bedrock invoke_model API.
Used for semantic search across research briefings.
"""
import json
import logging
import math
from typing import Optional
from backend.config import settings

logger = logging.getLogger(__name__)


def get_embedding(text: str, purpose: str = "GENERIC_INDEX") -> Optional[list[float]]:
    """
    Generate a 384-dimensional embedding vector for the given text
    using Amazon Nova Embed Multimodal via Bedrock invoke_model.

    purpose: "GENERIC_INDEX" for storing, "TEXT_RETRIEVAL" for search queries.
    Returns None if Bedrock is unavailable (mock mode or missing credentials).
    """
    if settings.mock_mode:
        return None

    try:
        import boto3

        client = boto3.client(
            "bedrock-runtime",
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id or None,
            aws_secret_access_key=settings.aws_secret_access_key or None,
        )

        body = json.dumps({
            "schemaVersion": "nova-multimodal-embed-v1",
            "taskType": "SINGLE_EMBEDDING",
            "singleEmbeddingParams": {
                "embeddingPurpose": purpose,
                "embeddingDimension": 384,
                "text": {
                    "truncationMode": "END",
                    "value": text[:8000],
                },
            },
        })

        response = client.invoke_model(
            modelId=settings.nova_embed_model_id,
            body=body,
        )

        response_body = json.loads(response["body"].read())
        embeddings_list = response_body.get("embeddings", [])
        embedding = embeddings_list[0].get("embedding") if embeddings_list else None

        if not embedding:
            logger.warning("Nova Embed returned no embedding field in response")
            return None

        return [float(v) for v in embedding]

    except ImportError:
        logger.warning("boto3 not installed — embeddings unavailable")
        return None
    except Exception as e:
        logger.warning(f"Nova Embed error: {e}")
        return None


def compute_similarity(vec1: list[float], vec2: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.
    Assumes normalized vectors (Nova Embed normalizes by default).
    Falls back to full computation for safety.
    Returns a float in [-1, 1]; higher = more similar.
    """
    if len(vec1) != len(vec2):
        return 0.0

    dot = sum(a * b for a, b in zip(vec1, vec2))
    mag1 = math.sqrt(sum(a * a for a in vec1))
    mag2 = math.sqrt(sum(b * b for b in vec2))

    if mag1 == 0.0 or mag2 == 0.0:
        return 0.0

    return dot / (mag1 * mag2)
