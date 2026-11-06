Feature: Token refresh

  Scenario: Refresh the access token without logging in again
    Given I am logged in and Keycloak issued a refresh token
    When the access token's lifetime passes
    Then the browser stays on the client and is not sent to Keycloak's login page
    Given the client has refreshed the access token
    When I look at the page
    Then it shows the new access token's expiry time
    Given the client has refreshed the access token
    When it calls `GET /api/groups` with the new token
    Then the response is 200 and the client still shows my `username` and `groups`

  Scenario: Refresh failure is visible
    Given my refresh token is no longer valid
    When the client tries to refresh
    Then it shows the refresh error and a "log in again" action
    Given my refresh token is no longer valid
    When the client tries to refresh
    Then it stays on the client and does not redirect to Keycloak on its own
