from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, loaded from the .env file."""

    project_name: str = "Sentinel API"
    environment: str = "development"
    secret_key: str
    database_url: str
    redis_url: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Instantiate the settings object.
settings = Settings()  # type: ignore
