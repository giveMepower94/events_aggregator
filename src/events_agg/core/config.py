from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env",
                                      env_file_encoding="utf-8",
                                      populate_by_name=True,
                                      extra="ignore")

    # Provider API
    events_provider_base_url: str = Field(alias="EVENTS_PROVIDER_BASE_URL")

    events_provider_api_key: str = Field(alias="EVENTS_PROVIDER_API_KEY")

    # DB
    database_url: str = Field(alias="POSTGRES_CONNECTION_STRING")

    # Caching
    seats_cache_ttl_seconds: int = 30


settings = Settings()
