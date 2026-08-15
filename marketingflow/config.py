"""Central runtime configuration for MarketingFlow AI."""

from dataclasses import dataclass
import os

from dotenv import load_dotenv


DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"
DEFAULT_EMBEDDING_MODEL = "models/gemini-embedding-001"


class ConfigurationError(RuntimeError):
    """Raised when required application configuration is unavailable."""


@dataclass(frozen=True, slots=True)
class Settings:
    google_api_key: str | None
    gemini_model: str
    gemini_embedding_model: str
    supabase_url: str | None
    supabase_publishable_key: str | None
    app_url: str

    @property
    def has_google_api_key(self) -> bool:
        return bool(self.google_api_key)

    @property
    def has_supabase(self) -> bool:
        return bool(self.supabase_url and self.supabase_publishable_key)


def get_settings(
    *,
    load_env_file: bool = True,
    require_google_api_key: bool = False,
) -> Settings:
    """Read settings once per call without retaining secret values globally.

    Tests can disable ``.env`` loading so they never depend on a developer's
    local credential file.
    """
    if load_env_file:
        load_dotenv(override=True)

    api_key = os.getenv("GOOGLE_API_KEY", "").strip() or None
    if require_google_api_key and not api_key:
        raise ConfigurationError(
            "GOOGLE_API_KEY is missing. Copy .env.example to .env and add your Gemini API key."
        )

    return Settings(
        google_api_key=api_key,
        gemini_model=os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL).strip()
        or DEFAULT_GEMINI_MODEL,
        gemini_embedding_model=os.getenv(
            "GEMINI_EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL
        ).strip()
        or DEFAULT_EMBEDDING_MODEL,
        supabase_url=os.getenv("SUPABASE_URL", "").strip() or None,
        supabase_publishable_key=os.getenv(
            "SUPABASE_PUBLISHABLE_KEY", ""
        ).strip()
        or None,
        app_url=os.getenv("APP_URL", "http://localhost:8501").strip()
        or "http://localhost:8501",
    )
