import json

import httpx
from fastapi.testclient import TestClient
from pytest_bdd import given, parsers, scenarios, then, when

from tests.conftest import TokenMinter

scenarios("features/groups-api.feature")


@given(
    "a token signed by the Keycloak key, with `iss` equal to `Settings.issuer_url`, "
    '`aud` including `Settings.audience`, unexpired, `preferred_username` "alice", '
    'and `groups` ["/admins", "/devs"]',
    target_fixture="access_token",
)
def token_for_alice_with_two_groups(mint_access_token: TokenMinter) -> str:
    return mint_access_token(
        {"preferred_username": "alice", "groups": ["/admins", "/devs"]}
    )


@given(
    parsers.parse("a valid token whose `groups` claim is {groups_json}"),
    target_fixture="access_token",
)
def token_with_groups_claim(mint_access_token: TokenMinter, groups_json: str) -> str:
    return mint_access_token({"groups": json.loads(groups_json)})


@given("a valid token with no `groups` claim", target_fixture="access_token")
def token_without_groups_claim(mint_access_token: TokenMinter) -> str:
    return mint_access_token({})


@when("I call `GET /api/groups` with it", target_fixture="groups_response")
@when("I call `GET /api/groups`", target_fixture="groups_response")
def call_groups_endpoint(
    groups_api_client: TestClient, access_token: str
) -> httpx.Response:
    return groups_api_client.get(
        "/api/groups", headers={"Authorization": f"Bearer {access_token}"}
    )


@then(
    'the response is 200 with an `AuthenticatedUser` body whose `username` is "alice" '
    'and `groups` is ["/admins", "/devs"]'
)
def response_is_alice_with_two_groups(groups_response: httpx.Response) -> None:
    assert groups_response.status_code == 200
    assert groups_response.json() == {
        "username": "alice",
        "groups": ["/admins", "/devs"],
    }


@then(parsers.parse("`AuthenticatedUser.groups` is exactly {groups_json}"))
def response_groups_are_exactly(
    groups_response: httpx.Response, groups_json: str
) -> None:
    assert groups_response.json()["groups"] == json.loads(groups_json)


@then("the response is 200 with `AuthenticatedUser.groups` equal to []")
def response_has_empty_groups(groups_response: httpx.Response) -> None:
    assert groups_response.status_code == 200
    assert groups_response.json()["groups"] == []
