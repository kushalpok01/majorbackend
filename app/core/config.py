from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PRIMARY_TTS_ENGINE: str = "hybrid"
    FALLBACK_TTS_ENGINE: str = "none"

    GTTS_DEFAULT_LANG: str = "ne"
    GTTS_FALLBACK_LANG: str = "en"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
