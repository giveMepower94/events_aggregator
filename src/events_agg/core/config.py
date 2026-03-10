from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env",
                                      env_file_encoding="utf-8",
                                      populate_by_name=True,
                                      extra="ignore")

    events_provider_base_url: str = Field(alias="EVENTS_PROVIDER_BASE_URL")
    events_provider_api_key: str = Field(alias="EVENTS_PROVIDER_API_KEY")
    database_url: str = Field(alias="POSTGRES_CONNECTION_STRING")

    # Caching
    seats_cache_ttl_seconds: int = 30

    sync_hour: int = 3
    sync_minute: int = 0

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+asyncpg://", 1)
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+asyncpg://", 1)
        return value


settings = Settings()
