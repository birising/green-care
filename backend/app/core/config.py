from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables or .env file."""

    app_name: str = "Green Care API"
    database_url: str = Field(..., env="DATABASE_URL")
    sql_echo: bool = Field(False, env="SQL_ECHO")
    telemetry_api_tokens: str = Field("telemetry-token", env="TELEMETRY_API_TOKENS")

    @property
    def telemetry_tokens(self) -> list[str]:
        tokens = [token.strip() for token in self.telemetry_api_tokens.split(",")]
        return [token for token in tokens if token]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


def get_settings() -> Settings:
    return Settings()


settings = get_settings()
