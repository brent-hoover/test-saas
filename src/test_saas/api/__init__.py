"""HTTP transport: the FastAPI app serving the API's endpoints under /api."""

import os
from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from test_saas.identity import (
    AuthenticatedUser,
    InvalidIdentityClaimsError,
    authenticated_user_from_claims,
)
from test_saas.settings import Settings, load_settings
from test_saas.token_verification import (
    InvalidTokenError,
    signing_keys_for,
    verify_access_token,
)

__all__ = ["create_app", "create_app_from_environment"]

# auto_error=False so a missing header is answered by our own 401 (with the
# Bearer challenge) instead of FastAPI's default 403.
bearer_scheme = HTTPBearer(auto_error=False)


def create_app_from_environment() -> FastAPI:
    """uvicorn factory: fails at startup, naming the variable, if settings are missing."""
    settings = load_settings(os.environ)
    return create_app(settings, signing_keys_for(settings))


def create_app(settings: Settings, signing_keys: jwt.PyJWKClient) -> FastAPI:
    app = FastAPI(title="Test SaaS API")

    def current_user(
        credentials: Annotated[
            HTTPAuthorizationCredentials | None, Depends(bearer_scheme)
        ],
    ) -> AuthenticatedUser:
        if credentials is None:
            raise _unauthorized("missing bearer token")
        try:
            claims = verify_access_token(
                credentials.credentials, settings, signing_keys
            )
            return authenticated_user_from_claims(claims)
        except (InvalidTokenError, InvalidIdentityClaimsError) as error:
            raise _unauthorized(str(error)) from error

    @app.get("/api/groups")
    def get_groups(
        user: Annotated[AuthenticatedUser, Depends(current_user)],
    ) -> AuthenticatedUser:
        return user

    # Liveness: the process is serving.
    @app.get("/api/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    # Readiness: the app only exists once settings loaded (create_app_from_environment
    # fails otherwise), so reaching this handler means ready. Keycloak is not called,
    # so an identity provider outage does not pull pods from the Service.
    @app.get("/api/readyz")
    def readyz() -> dict[str, str]:
        return {"status": "ready"}

    return app


def _unauthorized(reason: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=reason,
        headers={"WWW-Authenticate": "Bearer"},
    )
