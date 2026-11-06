Feature: Groups API

  Scenario: Get the authenticated user's groups
    Given a token signed by the Keycloak key, with `iss` equal to `Settings.issuer_url`, `aud` including `Settings.audience`, unexpired, `preferred_username` "alice", and `groups` ["/admins", "/devs"]
    When I call `GET /api/groups` with it
    Then the response is 200 with an `AuthenticatedUser` body whose `username` is "alice" and `groups` is ["/admins", "/devs"]
    Given a valid token whose `groups` claim is ["/devs", "/admins", "/devs"]
    When I call `GET /api/groups`
    Then `AuthenticatedUser.groups` is exactly ["/devs", "/admins", "/devs"]
    Given a valid token with no `groups` claim
    When I call `GET /api/groups`
    Then the response is 200 with `AuthenticatedUser.groups` equal to []

  Scenario: Reject requests without a valid token
    Given no `Authorization` header
    When I call `GET /api/groups`
    Then the response is 401 with `WWW-Authenticate: Bearer` and no groups
    Given a token signed by a key not in the JWKS
    When I call `GET /api/groups`
    Then the response is 401 with no groups
    Given an expired token
    When I call `GET /api/groups`
    Then the response is 401 with no groups
    Given a token whose `iss` differs from `Settings.issuer_url`
    When I call `GET /api/groups`
    Then the response is 401 with no groups
    Given a token whose `aud` does not include `Settings.audience`
    When I call `GET /api/groups`
    Then the response is 401 with no groups
    Given an otherwise valid token with no `preferred_username` claim
    When I call `GET /api/groups`
    Then the response is 401 with no groups
