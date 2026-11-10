# Test SaaS

Minimal web application that stands in for a real SaaS product when
validating OIDC login: a browser client logs in through Keycloak's redirect
flow with direct grants disabled, and an in-cluster API returns the user's
groups.

Start with [docs/PLAN.md](docs/PLAN.md) slice 1. All planning docs are in
[docs/](docs/).

## Develop

```bash
uv sync
uv run pytest            # architecture tests + BDD scenarios
uv run ruff check . && uv run ruff format --check . && uv run ty check
```

## Build and push the images

Pushing a version tag runs the `images` GitHub Actions workflow, which builds
both images for linux/amd64 and linux/arm64 and pushes them to GHCR, tagged
with the version without the `v`:

```bash
TAG=0.1.0                 # keep equal to appVersion in chart/test-saas/Chart.yaml
git tag v$TAG && git push origin v$TAG
gh run watch              # follow the build
```

Packages GHCR creates on the first push are private; make
`test-saas-api` and `test-saas-client` public in the package settings so the
cluster can pull without a pull secret.

To build locally instead (for your machine's architecture):

```bash
docker build -t test-saas-api:dev .
docker build -t test-saas-client:dev client/
```

## Configure Keycloak

On the realm, create or edit the client the browser logs in with:

- Client authentication **off** (public client; the browser uses PKCE).
- Standard flow **on**; Direct access grants **off**.
- Valid redirect URI: `https://<host>/`.
- Web origin: `https://<host>` (no trailing slash; it must match the browser's
  `Origin` header, or CORS blocks the code exchange).
- A **groups** mapper (Group Membership) adding `groups` to the access token.
- An **audience** mapper adding the value you pass as `oidc.audience` to the
  access token's `aud`.
- To exercise token refresh (PLAN slice 3), set a short access-token
  lifespan, e.g. 1 minute.

## Install and remove

The chart creates two Deployments and two Services, and no Ingress or TLS.
Route `https://<host>/` in Istio: `/api` to Service `<release>-api` and `/`
to Service `<release>-client`, both on port 80.

```bash
helm install test-saas chart/test-saas \
  --set host=<host> \
  --set oidc.issuerUrl=https://<keycloak>/realms/<realm> \
  --set oidc.clientId=<client-id> \
  --set oidc.audience=<audience> \
  --set api.image.tag=$TAG --set client.image.tag=$TAG

helm uninstall test-saas
```
