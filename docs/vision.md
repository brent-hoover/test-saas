---
phase: vision
status: approved
approved: 2026-11-05
owner: Brent Hoover
date: 2026-11-05
---
<!-- CONTRACT: States what the product is, for whom, and what success looks
     like. NO technology choices — those live in stack.md. Module boundaries
     live in architecture.md. This doc is the sole home of out-of-scope. -->

# Test SaaS — Vision

## What & who
Test SaaS is a minimal web application that stands in for a real SaaS
product when validating OIDC (OpenID Connect) login. The only user is the
operator, who deploys it to validate identity provider and cluster setups.

## Problem
No SaaS application exists today to test OIDC login against. Without one,
the operator cannot confirm three things end to end. First, that a browser
outside the cluster logs in through the identity provider's redirect flow
with direct grants (the client collecting the user's password) disabled.
Second, that the issued token carries the expected `groups` claim. Third,
that an in-cluster backend accepts that token. Test SaaS gives a
repeatable target to deploy, check, and remove.

## System shape
- **Delivery form:** web service: a browser client plus a backend API,
  packaged as one deployment that installs and removes both components.
- **Topology:** distributed — it mirrors a real SaaS split, so an in-cluster
  backend independently verifies a token that the browser-facing client
  obtained.
- **Major components:** 2 built, 1 external:
  - **Client service (in cluster):** serves the browser client, which logs
    the user in through the identity provider and displays their groups.
  - **Backend API (in cluster):** returns the authenticated user's groups
    from a "get groups" endpoint.
  - **Identity provider (external, not built):** authenticates the user and
    issues tokens that carry a `groups` claim.

## Success criteria
1. From a browser outside the cluster, the operator loads the client, is
   redirected to the identity provider, logs in, and lands back in the
   client logged in.
2. Login succeeds with direct grants disabled on the identity provider's
   client configuration. The redirect back to the client carries an
   authorization code, not a token, and the client exchanges that code for
   tokens. The client never handles the operator's password.
3. The client displays the operator's username and exactly the groups the
   identity provider assigned them, as returned by the "get groups"
   endpoint.
4. The "get groups" endpoint returns an unauthorized response, and no
   groups, for a request with no token, a token with an invalid signature,
   or an expired token.
5. When the access token expires during a session, the client refreshes
   it without sending the operator back to the identity provider's login
   page. The "get groups" endpoint accepts the refreshed token.
6. Both components build into container images that push to a registry.
   This is an operator constraint, not a stack choice.
7. One install command deploys both components to the cluster, and one
   uninstall command removes them.

## Out of scope (v1)
- Group-based authorization: no endpoint or UI is restricted by group.
- Data or features beyond login, token refresh, and displaying groups.
- Logout.
- More than one identity provider.
- More than one user, and any user management in the application.
- Production hardening: high availability, scaling, observability.
