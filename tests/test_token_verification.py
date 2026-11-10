from fastapi.testclient import TestClient

from tests.conftest import TokenMinter


def test_id_token_is_rejected_as_bearer_token(
    groups_api_client: TestClient, mint_access_token: TokenMinter
) -> None:
    # Keycloak ID tokens can carry aud == client ID, which may equal the
    # configured audience; only access tokens (typ "Bearer") are accepted.
    id_token = mint_access_token({"typ": "ID"})

    response = groups_api_client.get(
        "/api/groups", headers={"Authorization": f"Bearer {id_token}"}
    )

    assert response.status_code == 401


def test_token_without_type_claim_is_rejected(
    groups_api_client: TestClient, mint_access_token: TokenMinter
) -> None:
    untyped_token = mint_access_token({"typ": None})

    response = groups_api_client.get(
        "/api/groups", headers={"Authorization": f"Bearer {untyped_token}"}
    )

    assert response.status_code == 401
