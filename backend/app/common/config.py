from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Vectrion RAG"
    api_v1_prefix: str = "/api/v1"
    secret_key: str = "change_me"
    access_token_expire_minutes: int = 1440
    database_url: str = "postgresql+psycopg2://rag:rag@postgres:5432/ragdb"
    redis_url: str = "redis://redis:6379/0"
    cors_origins: str = "http://localhost:3000"
    groq_api_key: str = ""
    groq_model: str = "moonshotai/kimi-k2-instruct-0905"
    gemini_api_key: str = ""
    gemini_embed_model: str = "models/gemini-embedding-001"
    chroma_persist_directory: str = "/app/chroma"
    chroma_collection_name: str = "rag_documents"

    model_config = {"env_file": ".env", "extra": "ignore"}

    @property
    def cors_origins_list(self) -> list[str]:
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
