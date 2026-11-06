"""The authenticated user, built from already-verified token claims."""

from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError

__all__ = [
    "AuthenticatedUser",
    "InvalidIdentityClaimsError",
    "authenticated_user_from_claims",
]

USERNAME_CLAIM = "preferred_username"
GROUPS_CLAIM = "groups"


class InvalidIdentityClaimsError(Exception):
    """Verified claims lack a non-empty string username or a list-of-strings groups."""


class AuthenticatedUser(BaseModel):
    # strict: claims are shown verbatim, so no coercion (e.g. 42 -> "42").
    model_config = ConfigDict(frozen=True, strict=True)

    username: str = Field(min_length=1)
    groups: list[str]


def authenticated_user_from_claims(claims: Mapping[str, Any]) -> AuthenticatedUser:
    """Build the user from verified claims; claim values are arbitrary JSON.

    Groups are returned verbatim and in claim order, so the operator sees
    exactly what Keycloak issued. A missing groups claim is an empty list,
    which makes a missing groups mapper visible instead of an error.
    """
    try:
        return AuthenticatedUser.model_validate(
            {
                "username": claims.get(USERNAME_CLAIM),
                "groups": claims.get(GROUPS_CLAIM, []),
            }
        )
    except ValidationError as error:
        raise InvalidIdentityClaimsError(
            f"token claims {USERNAME_CLAIM!r}/{GROUPS_CLAIM!r} are missing or malformed: "
            f"{error.errors(include_url=False)}"
        ) from error
