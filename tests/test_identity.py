import pytest
from fastapi.testclient import TestClient

from tests.conftest import Claims, TokenMinter


@pytest.mark.parametrize(
    "malformed_claims",
    [
        # Keycloak's group mapper emits a scalar when "multivalued" is off.
        {"groups": "/admins"},
        {"groups": ["/admins", 7]},
        {"preferred_username": 42},
        {"preferred_username": ""},
    ],
    ids=["scalar-groups", "non-string-group", "non-string-username", "empty-username"],
)
def test_signed_token_with_malformed_identity_claims_is_rejected(
    groups_api_client: TestClient,
    mint_access_token: TokenMinter,
    malformed_claims: Claims,
) -> None:
    token = mint_access_token(malformed_claims)

    response = groups_api_client.get(
        "/api/groups", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"
