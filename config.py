"""Configuration settings."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    groq_api_key: str
    groq_model: str = "llama-3.3-70b-versatile"
    max_file_size_mb: int = 50
    chunk_size: int = 2000
    chunk_overlap: int = 200
    app_name: str = "Document Analysis API"
    debug: bool = False

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
