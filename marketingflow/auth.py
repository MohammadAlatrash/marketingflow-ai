"""Supabase Auth boundary. No privileged key is accepted here."""

from dataclasses import dataclass
from typing import Any

from .config import ConfigurationError, Settings


class AuthError(RuntimeError):
    """Stable application error that never exposes provider details."""


@dataclass(frozen=True, slots=True)
class SessionTokens:
    access_token: str
    refresh_token: str


def create_supabase_client(settings: Settings):
    if not settings.has_supabase:
        raise ConfigurationError("Supabase is not configured.")
    key = settings.supabase_publishable_key or ""
    if key.startswith("sb_secret_"):
        raise ConfigurationError("A Supabase publishable key is required; secret keys are forbidden.")

    from supabase import create_client

    return create_client(settings.supabase_url, key)


class AuthService:
    def __init__(self, client: Any):
        self.client = client

    def sign_up(self, email: str, password: str, redirect_to: str):
        return self._call(
            self.client.auth.sign_up,
            {
                "email": email.strip(),
                "password": password,
                "options": {"email_redirect_to": redirect_to},
            },
        )

    def sign_in(self, email: str, password: str):
        return self._call(
            self.client.auth.sign_in_with_password,
            {"email": email.strip(), "password": password},
        )

    def reset_password(self, email: str, redirect_to: str):
        return self._call(
            self.client.auth.reset_password_for_email,
            email.strip(),
            {"redirect_to": redirect_to},
        )

    def update_password(self, password: str):
        return self._call(self.client.auth.update_user, {"password": password})

    def sign_in_with_google_id_token(self, id_token: str, nonce: str | None = None):
        credentials = {"provider": "google", "token": id_token}
        if nonce:
            credentials["nonce"] = nonce
        return self._call(self.client.auth.sign_in_with_id_token, credentials)

    def restore_session(self, tokens: SessionTokens):
        return self._call(
            self.client.auth.set_session,
            tokens.access_token,
            tokens.refresh_token,
        )

    def verified_user(self, access_token: str | None = None):
        response = (
            self._call(self.client.auth.get_user, access_token)
            if access_token
            else self._call(self.client.auth.get_user)
        )
        return getattr(response, "user", None)

    def sign_out(self) -> None:
        self._call(self.client.auth.sign_out)

    @staticmethod
    def tokens_from(response: Any) -> SessionTokens | None:
        session = getattr(response, "session", None)
        if not session:
            return None
        access_token = getattr(session, "access_token", "")
        refresh_token = getattr(session, "refresh_token", "")
        if not access_token or not refresh_token:
            return None
        return SessionTokens(access_token=access_token, refresh_token=refresh_token)

    @staticmethod
    def _call(function, *args):
        try:
            return function(*args)
        except Exception as error:
            raise AuthError("Authentication request could not be completed.") from error
