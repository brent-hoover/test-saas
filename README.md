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

```bash
TAG=0.1.0
docker build -t ghcr.io/brent-hoover/test-saas-api:$TAG .
docker build -t ghcr.io/brent-hoover/test-saas-client:$TAG client/
docker push ghcr.io/brent-hoover/test-saas-api:$TAG
docker push ghcr.io/brent-hoover/test-saas-client:$TAG
```

Build for the cluster's architecture (e.g. `--platform linux/amd64` when
building on Apple silicon for amd64 nodes).

## Configure Keycloak

On the realm, create or edit the client the browser logs in with:

- Client authentication **off** (public client; the browser uses PKCE).
- Standard flow **on**; Direct access grants **off**.
- Valid redirect URI and Web origin: `https://<host>/`.
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
