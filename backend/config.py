"""
Scout configuration — loads settings from environment variables.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Mock mode — set to "true" to use mock extractors/synthesis (no API keys needed)
    mock_mode: bool = True

    # Nova Act
    nova_act_api_key: str = ""

    # AWS Bedrock
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-1"
    bedrock_model_id: str = "us.amazon.nova-lite-v1:0"
    nova_embed_model_id: str = "amazon.nova-2-multimodal-embeddings-v1:0"

    # Database
    database_url: str = "sqlite:///./scout.db"

    # Server
    port: int = 8000
    cors_origins: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
