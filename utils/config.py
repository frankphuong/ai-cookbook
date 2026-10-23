from pathlib import Path
from typing import Literal

from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parents[1] / ".env"


class ProviderConfig(BaseModel):
    base_url: str
    api_key: SecretStr = SecretStr("")
    default_model: str


class Settings(BaseSettings):
    active_provider: Literal["ollama", "nvidia", "openai", "hugging_face", "groq"] = (
        "ollama"
    )

    ollama: ProviderConfig | None = None
    nvidia: ProviderConfig | None = None
    openai: ProviderConfig | None = None
    hugging_face: ProviderConfig | None = None
    groq: ProviderConfig | None = None

    @property
    def active(self) -> ProviderConfig:
        cfg = getattr(self, self.active_provider)
        if cfg is None:
            raise ValueError(
                f"Provider '{self.active_provider}' doesn't configured in .env yet"
                f"(need {self.active_provider.upper()}__BASE_URL, ...)"
            )
        return cfg

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )


settings = Settings()
