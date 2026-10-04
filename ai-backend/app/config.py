from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    app_name: str = "Nexus AI Backend"
    app_version: str = "0.1.0"
    debug: bool = False
    ai_backend_port: int = 8000
    ai_backend_host: str = "0.0.0.0"

    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:3001"]

    # Database
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "nexusai"
    db_password: str = "nexusai"
    db_name: str = "nexusai"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def sync_database_url(self) -> str:
        return (
            f"postgresql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    # JWT
    jwt_access_secret: str = "dev-secret"
    jwt_algorithm: str = "HS256"

    # LLM
    openai_api_key: str = ""
    llm_provider: str = "ollama"
    llm_model: str = "llama3.2"
    embedding_model: str = "bge-m3"
    ollama_url: str = "http://localhost:11434"

    # Celery
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"

    # Agent runtime
    agent_max_iterations: int = 10
    agent_timeout_seconds: float = 120.0

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "case_sensitive": False}


settings = Settings()
