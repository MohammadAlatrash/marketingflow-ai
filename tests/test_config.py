import pytest

from marketingflow.config import (
    ConfigurationError,
    DEFAULT_EMBEDDING_MODEL,
    DEFAULT_GEMINI_MODEL,
    get_settings,
)


def test_settings_use_safe_defaults_without_env_file(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    monkeypatch.delenv("GEMINI_EMBEDDING_MODEL", raising=False)

    settings = get_settings(load_env_file=False)

    assert settings.google_api_key is None
    assert settings.gemini_model == DEFAULT_GEMINI_MODEL
    assert settings.gemini_embedding_model == DEFAULT_EMBEDDING_MODEL
    assert settings.has_google_api_key is False
    assert settings.has_supabase is False


def test_settings_read_explicit_environment(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
    monkeypatch.setenv("GEMINI_MODEL", "test-generation-model")
    monkeypatch.setenv("GEMINI_EMBEDDING_MODEL", "test-embedding-model")

    settings = get_settings(load_env_file=False, require_google_api_key=True)

    assert settings.google_api_key == "test-key"
    assert settings.gemini_model == "test-generation-model"
    assert settings.gemini_embedding_model == "test-embedding-model"


def test_required_api_key_has_stable_non_secret_error(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    with pytest.raises(ConfigurationError, match="GOOGLE_API_KEY is missing"):
        get_settings(load_env_file=False, require_google_api_key=True)


def test_supabase_requires_url_and_publishable_key(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://project.supabase.co")
    monkeypatch.delenv("SUPABASE_PUBLISHABLE_KEY", raising=False)

    assert get_settings(load_env_file=False).has_supabase is False

    monkeypatch.setenv("SUPABASE_PUBLISHABLE_KEY", "sb_publishable_test")
    assert get_settings(load_env_file=False).has_supabase is True
