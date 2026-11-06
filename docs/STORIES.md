---
phase: stories
status: approved
approved: 2026-11-06
date: 2026-11-05
---
<!-- CONTRACT: The v1 backlog. Story → Given/When/Then acceptance criteria,
     the same shape core:user-stories produces and bdd-specs consumes.
     Ordering/slicing lives in PLAN.md. -->
<!-- FORMAT RULES:
- Exactly the template shape: `## Epic:` / `### Story:` / "As a … I want
  … so that …" / `**Acceptance criteria:**` Given/When/Then bullets /
  `**Priority:**`. The scaffold phase parses these headings to generate
  .feature files — a story that breaks the shape breaks scaffolding.
- Criteria name real entities and fields from data-models.md.
- Every vision success criterion must be covered by at least one `must`
  story (the stories-reviewer checks this).
-->

# Test SaaS — Stories

## Epic: Browser login

### Story: Log in through Keycloak
As the operator, I want the client to send me to Keycloak to log in so that the app never handles my password.

**Acceptance criteria:**
- Given I am not logged in, When I load the client from a browser outside the cluster, Then I am redirected to Keycloak's login page
- Given I am on Keycloak's login page, When I log in successfully, Then I am redirected back to the client with an authorization code and no token in the URL
- Given I returned to the client with an authorization code, When the client finishes loading, Then it shows me as logged in
- Given the Keycloak client has direct access grants disabled, When I complete the login above, Then login succeeds

**Priority:** must

### Story: Failed login is visible
As the operator, I want a failed login to show Keycloak's error so that I can diagnose a misconfigured client.

**Acceptance criteria:**
- Given Keycloak redirects back with an `error` parameter, When the client loads, Then it displays the `error` and `error_description` values
- Given Keycloak redirects back with an `error` parameter, When the client loads, Then it stays on the client and does not redirect back to Keycloak

**Priority:** should

## Epic: Groups API

### Story: Get the authenticated user's groups
As the operator, I want `GET /api/groups` to return my username and groups from a valid token so that I can confirm the token carries the `groups` claim.

**Acceptance criteria:**
- Given a token signed by the Keycloak key, with `iss` equal to `Settings.issuer_url`, `aud` including `Settings.audience`, unexpired, `preferred_username` "alice", and `groups` ["/admins", "/devs"], When I call `GET /api/groups` with it, Then the response is 200 with an `AuthenticatedUser` body whose `username` is "alice" and `groups` is ["/admins", "/devs"]
- Given a valid token whose `groups` claim is ["/devs", "/admins", "/devs"], When I call `GET /api/groups`, Then `AuthenticatedUser.groups` is exactly ["/devs", "/admins", "/devs"]
- Given a valid token with no `groups` claim, When I call `GET /api/groups`, Then the response is 200 with `AuthenticatedUser.groups` equal to []

**Priority:** must

### Story: Reject requests without a valid token
As the operator, I want `GET /api/groups` to reject bad tokens so that I can confirm the API actually verifies them.

**Acceptance criteria:**
- Given no `Authorization` header, When I call `GET /api/groups`, Then the response is 401 with `WWW-Authenticate: Bearer` and no groups
- Given a token signed by a key not in the JWKS, When I call `GET /api/groups`, Then the response is 401 with no groups
- Given an expired token, When I call `GET /api/groups`, Then the response is 401 with no groups
- Given a token whose `iss` differs from `Settings.issuer_url`, When I call `GET /api/groups`, Then the response is 401 with no groups
- Given a token whose `aud` does not include `Settings.audience`, When I call `GET /api/groups`, Then the response is 401 with no groups
- Given an otherwise valid token with no `preferred_username` claim, When I call `GET /api/groups`, Then the response is 401 with no groups

**Priority:** must

## Epic: Groups display

### Story: Show who I am and my groups
As the operator, I want the client to display my username and groups from the API so that I can compare them with what Keycloak assigned.

**Acceptance criteria:**
- Given I am logged in, When the client loads, Then it calls `GET /api/groups` with my access token as a Bearer `Authorization` header
- Given `GET /api/groups` returns `username` "alice" and `groups` ["/admins", "/devs"], When the response arrives, Then the client shows "alice" and lists exactly "/admins" and "/devs" in that order
- Given `GET /api/groups` returns `groups` [], When the response arrives, Then the client shows the `username` and a "no groups in token" message

**Priority:** must

### Story: API errors are visible
As the operator, I want API failures shown in the client so that I can tell an identity provider problem from an API problem.

**Acceptance criteria:**
- Given I am logged in, When `GET /api/groups` returns a non-200 status, Then the client shows the HTTP status and the error message from the response body
- Given I am logged in, When `GET /api/groups` returns a non-200 status, Then the client shows no groups list

**Priority:** should

## Epic: Token refresh

### Story: Refresh the access token without logging in again
As the operator, I want the client to refresh an expiring access token so that my session continues without returning to Keycloak's login page.

**Acceptance criteria:**
- Given I am logged in and Keycloak issued a refresh token, When the access token's lifetime passes, Then the browser stays on the client and is not sent to Keycloak's login page
- Given the client has refreshed the access token, When I look at the page, Then it shows the new access token's expiry time
- Given the client has refreshed the access token, When it calls `GET /api/groups` with the new token, Then the response is 200 and the client still shows my `username` and `groups`

**Priority:** must

### Story: Refresh failure is visible
As the operator, I want a failed refresh shown so that I can diagnose refresh-token configuration.

**Acceptance criteria:**
- Given my refresh token is no longer valid, When the client tries to refresh, Then it shows the refresh error and a "log in again" action
- Given my refresh token is no longer valid, When the client tries to refresh, Then it stays on the client and does not redirect to Keycloak on its own

**Priority:** should

## Epic: Packaging and deployment

### Story: Build and push both images
As the operator, I want each component to build from its own Dockerfile and push to GHCR so that the cluster can pull them.

**Acceptance criteria:**
- Given the API image is built, When I run it, Then its process runs as a non-root user
- Given the API image is built, When I run it with the required environment variables, Then `GET /api/healthz` returns 200
- Given the client image is built, When I run it with the required environment variables, Then it serves the client on `/`
- Given I am logged in to GHCR, When I push both images, Then they are available as `ghcr.io/brent-hoover/test-saas-api` and `ghcr.io/brent-hoover/test-saas-client`

**Priority:** must

### Story: Configure the client at deploy time
As the operator, I want the client's Keycloak settings injected when its container starts so that one image works against any realm.

**Acceptance criteria:**
- Given the client container starts with the issuer URL, client ID, and redirect URI set as environment variables, When the browser loads `/config.js`, Then it contains those values
- Given a required client environment variable is unset, When the client container starts, Then it exits with an error that names the variable

**Priority:** must

### Story: Install and remove with Helm
As the operator, I want one command to install and one to uninstall so that I can deploy and clean up the test app quickly.

**Acceptance criteria:**
- Given image tags, issuer URL, audience, and client ID as chart values, When I run `helm install`, Then the `client` and `api` Deployments both become Ready
- Given the API is deployed with `OIDC_ISSUER_URL` unset, When the API pod starts, Then it exits with an error naming `OIDC_ISSUER_URL` and never becomes Ready
- Given the API is deployed with `OIDC_AUDIENCE` unset, When the API pod starts, Then it exits with an error naming `OIDC_AUDIENCE` and never becomes Ready
- Given the chart is installed and the API pod is running, When the kubelet probes `GET /api/healthz` and `GET /api/readyz`, Then both return 200
- Given the chart is installed, When I run `helm uninstall`, Then every resource the chart created is removed
- Given the chart, When I render it with `helm template`, Then it contains no Ingress and no TLS resources

**Priority:** must
