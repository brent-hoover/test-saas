"""Shared fixtures: a local signing key and JWKS standing in for Keycloak."""

import json
import time
from collections.abc import Callable
from typing import Any, override

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient
from jwt.algorithms import RSAAlgorithm

from test_saas.api import create_app
from test_saas.settings import Settings

TEST_ISSUER_URL = "https://keycloak.test/realms/test-saas"
TEST_AUDIENCE = "test-saas"
TEST_KEY_ID = "test-signing-key"
TOKEN_LIFETIME_SECONDS = 300

# A JWT claims mapping; claim values are arbitrary JSON, hence Any.
type Claims = dict[str, Any]
type TokenMinter = Callable[[Claims], str]


class FixtureJwksClient(jwt.PyJWKClient):
    """PyJWKClient that serves a fixed JWKS instead of fetching over HTTP."""

    def __init__(self, uri: str, jwks: dict[str, Any]) -> None:
        super().__init__(uri)
        self._jwks = jwks

    @override
    def fetch_data(self) -> dict[str, Any]:
        return self._jwks


@pytest.fixture(scope="session")
def signing_key() -> rsa.RSAPrivateKey:
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture
def settings() -> Settings:
    return Settings(issuer_url=TEST_ISSUER_URL, audience=TEST_AUDIENCE)


@pytest.fixture
def groups_api_client(settings: Settings, signing_key: rsa.RSAPrivateKey) -> TestClient:
    public_jwk = json.loads(RSAAlgorithm.to_jwk(signing_key.public_key()))
    public_jwk |= {"kid": TEST_KEY_ID, "use": "sig", "alg": "RS256"}
    signing_keys = FixtureJwksClient(settings.jwks_url, {"keys": [public_jwk]})
    return TestClient(create_app(settings, signing_keys))


@pytest.fixture
def mint_access_token(signing_key: rsa.RSAPrivateKey) -> TokenMinter:
    """Return a minter that signs valid claims, overridden by the given ones."""

    def mint(claim_overrides: Claims) -> str:
        issued_at = int(time.time())
        claims: Claims = {
            "iss": TEST_ISSUER_URL,
            "aud": TEST_AUDIENCE,
            "iat": issued_at,
            "exp": issued_at + TOKEN_LIFETIME_SECONDS,
            "preferred_username": "alice",
        }
        claims |= claim_overrides
        return jwt.encode(
            claims, signing_key, algorithm="RS256", headers={"kid": TEST_KEY_ID}
        )

    return mint
