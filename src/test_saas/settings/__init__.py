"""Runtime configuration of the API, read from environment variables."""

from collections.abc import Mapping

from pydantic import BaseModel, ConfigDict

__all__ = ["MissingSettingError", "Settings", "load_settings"]

ISSUER_URL_VARIABLE = "OIDC_ISSUER_URL"
AUDIENCE_VARIABLE = "OIDC_AUDIENCE"

# Keycloak serves a realm's signing keys at this fixed path below the issuer.
KEYCLOAK_JWKS_PATH = "/protocol/openid-connect/certs"


class MissingSettingError(Exception):
    """A required environment variable is unset or empty."""

    def __init__(self, variable_name: str) -> None:
        super().__init__(
            f"required environment variable {variable_name} is unset or empty; "
            "set it before starting the API"
        )
        self.variable_name = variable_name


class Settings(BaseModel):
    model_config = ConfigDict(frozen=True)

    # Kept as the raw string: compared to the token's `iss` claim exactly.
    issuer_url: str
    audience: str

    @property
    def jwks_url(self) -> str:
        return f"{self.issuer_url}{KEYCLOAK_JWKS_PATH}"


def load_settings(environment: Mapping[str, str]) -> Settings:
    return Settings(
        issuer_url=_required(environment, ISSUER_URL_VARIABLE),
        audience=_required(environment, AUDIENCE_VARIABLE),
    )


def _required(environment: Mapping[str, str], variable_name: str) -> str:
    value = environment.get(variable_name, "")
    if not value:
        raise MissingSettingError(variable_name)
    return value
