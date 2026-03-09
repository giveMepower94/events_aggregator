from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env",
                                      env_file_encoding="utf-8",
                                      extra="ignore")

    # Provider API
    events_provider_base_url: str
    events_provider_api_key: str

    # DB
    database_url: str

    # Caching
    seats_cache_ttl_seconds: int = 30


settings = Settings()
