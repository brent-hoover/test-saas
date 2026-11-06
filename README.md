# Test SaaS

Minimal web application that stands in for a real SaaS product when
validating OIDC login: a browser client logs in through Keycloak's redirect
flow with direct grants disabled, and an in-cluster API returns the user's
groups.

Start with [docs/PLAN.md](docs/PLAN.md) slice 1. All planning docs are in
[docs/](docs/).
