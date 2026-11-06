"""Verification of bearer tokens against the identity provider's signing keys.

The only module that handles a raw, untrusted bearer token.
"""

from typing import Any

import jwt

from test_saas.settings import Settings

__all__ = ["InvalidTokenError", "signing_keys_for", "verify_access_token"]

# Keycloak signs access tokens with RS256 by default. Pinning the algorithm
# blocks "alg: none" and HMAC-confusion attacks.
ACCEPTED_ALGORITHMS = ["RS256"]
REQUIRED_CLAIMS = ["exp", "iss", "aud"]


class InvalidTokenError(Exception):
    """The bearer token failed signature, expiry, issuer, or audience checks."""


def signing_keys_for(settings: Settings) -> jwt.PyJWKClient:
    return jwt.PyJWKClient(settings.jwks_url)


def verify_access_token(
    token: str, settings: Settings, signing_keys: jwt.PyJWKClient
) -> dict[str, Any]:
    """Return the token's claims once signature, expiry, issuer and audience pass.

    Claim values are arbitrary JSON, hence Any.
    """
    try:
        signing_key = signing_keys.get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            signing_key.key,
            algorithms=ACCEPTED_ALGORITHMS,
            audience=settings.audience,
            issuer=settings.issuer_url,
            options={"require": REQUIRED_CLAIMS},
        )
    except jwt.PyJWTError as error:
        raise InvalidTokenError(f"bearer token rejected: {error}") from error
