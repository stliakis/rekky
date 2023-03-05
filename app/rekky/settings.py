from pydantic import BaseSettings


class Settings(BaseSettings):
    OPENAI_API_KEY: str
    OPENAI_EMBEDDINGS_MODEL: str = "text-embedding-ada-002"
    ELASTIC_SEARCH_HOST: str = "http://elasticsearch:9200"
    QDRANT_HOST: str = "http://qdrant:6333"
    INGEST_BATCH_SIZE = 100
    DELETE_BATCH_SIZE = 100


def get_settings() -> Settings:
    return Settings()
