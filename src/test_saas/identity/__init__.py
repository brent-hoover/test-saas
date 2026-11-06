"""The authenticated user, built from already-verified token claims."""

from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel, ConfigDict

__all__ = [
    "AuthenticatedUser",
    "MissingUsernameError",
    "authenticated_user_from_claims",
]

USERNAME_CLAIM = "preferred_username"
GROUPS_CLAIM = "groups"


class MissingUsernameError(Exception):
    """Verified claims carry no non-empty `preferred_username`."""


class AuthenticatedUser(BaseModel):
    model_config = ConfigDict(frozen=True)

    username: str
    groups: list[str]


def authenticated_user_from_claims(claims: Mapping[str, Any]) -> AuthenticatedUser:
    """Build the user from verified claims; claim values are arbitrary JSON.

    Groups are returned verbatim and in claim order, so the operator sees
    exactly what Keycloak issued. A missing groups claim is an empty list,
    which makes a missing groups mapper visible instead of an error.
    """
    username = claims.get(USERNAME_CLAIM)
    if not username:
        raise MissingUsernameError(f"verified claims have no {USERNAME_CLAIM} claim")
    return AuthenticatedUser(username=username, groups=claims.get(GROUPS_CLAIM, []))
