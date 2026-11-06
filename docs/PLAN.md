---
phase: plan
status: approved
approved: 2026-11-06
date: 2026-11-06
---
<!-- CONTRACT: Ordered milestone slices over the stories in STORIES.md.
     Each slice ships working software. Story content lives in STORIES.md —
     reference titles, don't restate criteria. -->

# Test SaaS — Plan

The cluster (with Istio routing and TLS) and the Keycloak realm already
exist. No slice waits on other infrastructure work.

Commands below use release name `test-saas` and `$HOST`, the hostname the
Istio configuration serves this app on. The client's redirect URI is
`https://$HOST/`.

## Slice 1: Walking skeleton (deployed)
- **Stories:** Get the authenticated user's groups; Log in through
  Keycloak; Show who I am and my groups; Build and push both images;
  Configure the client at deploy time; Install and remove with Helm
- **Why now:** Proves the whole path (browser → Keycloak → client → API →
  display) running from the Helm chart in the cluster. Every later slice
  extends this path.
- **Verify:**
  1. `uv run pytest` passes the scenarios for "Get the authenticated
     user's groups". The other stories in this slice are checked by hand
     in steps 2–4.
  2. `docker manifest inspect ghcr.io/brent-hoover/test-saas-api:<tag>` and
     `docker manifest inspect ghcr.io/brent-hoover/test-saas-client:<tag>`
     both succeed for the tag just pushed.
  3. `helm install test-saas` with the realm's issuer URL, audience, client
     ID, and `$HOST`: from a browser outside the cluster, log in at
     `https://$HOST/` and see your username and groups.
  4. Save `helm get manifest test-saas`, run `helm uninstall test-saas`,
     then `kubectl get` each resource in the saved manifest returns
     NotFound.

## Slice 2: Token rejection
- **Stories:** Reject requests without a valid token
- **Why now:** Slice 1 covers the valid-token path only. This proves the
  API rejects bad tokens (vision.md, criterion 4) before refresh is built
  on top of verification.
- **Verify:** `uv run pytest` passes the rejection scenarios, and
  `curl -i https://$HOST/api/groups` with no token against the deployed
  release returns 401.

## Slice 3: Token refresh
- **Stories:** Refresh the access token without logging in again
- **Why now:** Needs the working login session from slice 1.
- **Verify:** By hand against the deployed release, with the Keycloak
  access-token lifespan set to 1 minute: stay on the client past expiry
  and check the story's acceptance criteria.

## Slice 4: Diagnostics
- **Stories:** Failed login is visible; API errors are visible; Refresh
  failure is visible
- **Why now:** `should` stories. Error display is only testable once the
  flows it reports on exist (slices 1 and 3).
- **Verify:** By hand against the deployed release, force each failure and
  check the story's acceptance criteria:
  - Failed login: turn on "Consent required" on the Keycloak client and
    click "No" on the consent screen. Keycloak redirects back with
    `error=access_denied`.
  - API error: `helm upgrade test-saas` with an audience that does not
    match the token. The API returns 401 with an error body.
  - Refresh failure: keep the 1-minute access-token lifespan from slice 3,
    log in, revoke the user's session in Keycloak's admin console, then
    wait past expiry.
