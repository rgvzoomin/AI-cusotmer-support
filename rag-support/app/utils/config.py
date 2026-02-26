from __future__ import annotations

from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and `.env`."""

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'AI-Powered Customer Support System'
    llm_provider: str = Field(default='openai_compatible', alias='LLM_PROVIDER')
    openai_api_key: str | None = Field(default=None, alias='OPENAI_API_KEY')
    openai_base_url: str | None = Field(default='https://api.openai.com/v1', alias='OPENAI_BASE_URL')
    openai_model: str = Field(default='gpt-4o-mini', alias='OPENAI_MODEL')
    embed_model: str = Field(default='all-MiniLM-L6-v2', alias='EMBED_MODEL')

    top_k: int = Field(default=5, alias='TOP_K')
    chunk_size: int = Field(default=1200, alias='CHUNK_SIZE')
    chunk_overlap: int = Field(default=200, alias='CHUNK_OVERLAP')

    db_url: str = Field(default='sqlite:///./data/app.db', alias='DB_URL')
    index_dir: str = './data/index'

    cache_ttl_seconds: int = 600
    cache_max_size: int = 1000
    rate_limit_per_minute: int = 120

    low_similarity_threshold: float = 0.35


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
