Feature: Browser login

  Scenario: Log in through Keycloak
    Given I am not logged in
    When I load the client from a browser outside the cluster
    Then I am redirected to Keycloak's login page
    Given I am on Keycloak's login page
    When I log in successfully
    Then I am redirected back to the client with an authorization code and no token in the URL
    Given I returned to the client with an authorization code
    When the client finishes loading
    Then it shows me as logged in
    Given the Keycloak client has direct access grants disabled
    When I complete the login above
    Then login succeeds

  Scenario: Failed login is visible
    Given Keycloak redirects back with an `error` parameter
    When the client loads
    Then it displays the `error` and `error_description` values
    Given Keycloak redirects back with an `error` parameter
    When the client loads
    Then it stays on the client and does not redirect back to Keycloak
