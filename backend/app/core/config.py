from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PressPulse AI"
    environment: str = "development"
    llm_provider: str = "fake"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    allowed_origin: str = "http://localhost:3000"
    provider_timeout_seconds: float = 30.0

    model_config = SettingsConfigDict(env_file=".env", env_prefix="PRESSPULSE_", extra="ignore")


settings = Settings()
