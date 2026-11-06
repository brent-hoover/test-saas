Feature: Groups display

  Scenario: Show who I am and my groups
    Given I am logged in
    When the client loads
    Then it calls `GET /api/groups` with my access token as a Bearer `Authorization` header
    Given `GET /api/groups` returns `username` "alice" and `groups` ["/admins", "/devs"]
    When the response arrives
    Then the client shows "alice" and lists exactly "/admins" and "/devs" in that order
    Given `GET /api/groups` returns `groups` []
    When the response arrives
    Then the client shows the `username` and a "no groups in token" message

  Scenario: API errors are visible
    Given I am logged in
    When `GET /api/groups` returns a non-200 status
    Then the client shows the HTTP status and the error message from the response body
    Given I am logged in
    When `GET /api/groups` returns a non-200 status
    Then the client shows no groups list
