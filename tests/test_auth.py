from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from marketingflow.auth import AuthError, AuthService, SessionTokens
from marketingflow.auth import create_supabase_client
from marketingflow.config import ConfigurationError, get_settings


def make_client():
    return SimpleNamespace(
        auth=SimpleNamespace(
            sign_up=Mock(return_value="signed-up"),
            sign_in_with_password=Mock(return_value="signed-in"),
            reset_password_for_email=Mock(return_value="reset"),
            update_user=Mock(return_value="updated"),
            sign_in_with_id_token=Mock(return_value="google"),
            set_session=Mock(return_value="restored"),
            get_user=Mock(return_value=SimpleNamespace(user=SimpleNamespace(id="user-1"))),
            sign_out=Mock(),
        )
    )


def test_email_auth_flows_use_supabase_auth():
    client = make_client()
    service = AuthService(client)

    service.sign_up(" user@example.com ", "password123", "http://localhost:8501")
    service.sign_in(" user@example.com ", "password123")
    service.reset_password(" user@example.com ", "http://localhost:8501")
    service.update_password("new-password123")

    client.auth.sign_up.assert_called_once()
    client.auth.sign_in_with_password.assert_called_once_with(
        {"email": "user@example.com", "password": "password123"}
    )
    client.auth.reset_password_for_email.assert_called_once()
    client.auth.update_user.assert_called_once_with({"password": "new-password123"})


def test_google_id_token_is_exchanged_for_supabase_session():
    client = make_client()
    service = AuthService(client)

    service.sign_in_with_google_id_token("google-id-token", nonce="nonce")

    client.auth.sign_in_with_id_token.assert_called_once_with(
        {"provider": "google", "token": "google-id-token", "nonce": "nonce"}
    )


def test_verified_user_calls_server_verification():
    client = make_client()
    user = AuthService(client).verified_user("access-token")

    assert user.id == "user-1"
    client.auth.get_user.assert_called_once_with("access-token")


def test_provider_errors_are_sanitized():
    client = make_client()
    client.auth.sign_in_with_password.side_effect = RuntimeError("SECRET DETAIL")

    with pytest.raises(AuthError, match="could not be completed") as caught:
        AuthService(client).sign_in("user@example.com", "password")

    assert "SECRET DETAIL" not in str(caught.value)


def test_restore_session_and_token_extraction():
    client = make_client()
    service = AuthService(client)
    tokens = SessionTokens("access", "refresh")

    service.restore_session(tokens)
    response = SimpleNamespace(session=SimpleNamespace(access_token="a", refresh_token="r"))

    assert service.tokens_from(response) == SessionTokens("a", "r")
    client.auth.set_session.assert_called_once_with("access", "refresh")


def test_application_rejects_supabase_secret_key(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://project.supabase.co")
    monkeypatch.setenv("SUPABASE_PUBLISHABLE_KEY", "sb_secret_forbidden")
    settings = get_settings(load_env_file=False)

    with pytest.raises(ConfigurationError, match="secret keys are forbidden"):
        create_supabase_client(settings)
