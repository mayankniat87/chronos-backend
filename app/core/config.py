from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central application settings.

    NOTE: pydantic-settings already reads values from the environment (and,
    if present, a .env file) using the field name as the variable name.
    Do NOT wrap defaults in os.getenv(...) as well -- that duplicates the
    env-reading logic and makes precedence hard to reason about.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "Chronos Backend"
    ENVIRONMENT: str = "development"  # development | staging | production
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    DATABASE_URL: str = "sqlite:///./chronos.db"

    # CORS - comma-separated list of allowed origins in production.
    # Defaults to "*" for hackathon/demo convenience, but allow_credentials
    # is forced to False whenever origins is "*" (see main.py) because
    # browsers reject wildcard-origin + credentials combinations.
    CORS_ORIGINS: str = "*"

    # LLM Settings
    LLM_PROVIDER: str = "mock"  # Options: openai, gemini, mock
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4-turbo"

    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-pro"

    LLM_TIMEOUT_SECONDS: float = 20.0

    @property
    def cors_origin_list(self) -> List[str]:
        if self.CORS_ORIGINS.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()
