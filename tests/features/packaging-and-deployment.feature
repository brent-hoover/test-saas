Feature: Packaging and deployment

  Scenario: Build and push both images
    Given the API image is built
    When I run it
    Then its process runs as a non-root user
    Given the API image is built
    When I run it with the required environment variables
    Then `GET /api/healthz` returns 200
    Given the client image is built
    When I run it with the required environment variables
    Then it serves the client on `/`
    Given I am logged in to GHCR
    When I push both images
    Then they are available as `ghcr.io/brent-hoover/test-saas-api` and `ghcr.io/brent-hoover/test-saas-client`

  Scenario: Configure the client at deploy time
    Given the client container starts with the issuer URL, client ID, and redirect URI set as environment variables
    When the browser loads `/config.js`
    Then it contains those values
    Given a required client environment variable is unset
    When the client container starts
    Then it exits with an error that names the variable

  Scenario: Install and remove with Helm
    Given image tags, issuer URL, audience, and client ID as chart values
    When I run `helm install`
    Then the `client` and `api` Deployments both become Ready
    Given the API is deployed with `OIDC_ISSUER_URL` unset
    When the API pod starts
    Then it exits with an error naming `OIDC_ISSUER_URL` and never becomes Ready
    Given the API is deployed with `OIDC_AUDIENCE` unset
    When the API pod starts
    Then it exits with an error naming `OIDC_AUDIENCE` and never becomes Ready
    Given the chart is installed and the API pod is running
    When the kubelet probes `GET /api/healthz` and `GET /api/readyz`
    Then both return 200
    Given the chart is installed
    When I run `helm uninstall`
    Then every resource the chart created is removed
    Given the chart
    When I render it with `helm template`
    Then it contains no Ingress and no TLS resources
