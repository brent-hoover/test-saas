# Client image: static browser client served by unprivileged nginx on :8080.
# Build: docker build -t ghcr.io/brent-hoover/test-saas-client:<tag> client/
# Runtime env (required): OIDC_ISSUER_URL, OIDC_CLIENT_ID, OIDC_REDIRECT_URI.

FROM nginxinc/nginx-unprivileged:1.29-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --chmod=755 render-config.sh /docker-entrypoint.d/40-render-config.sh
COPY site/ /usr/share/nginx/html/
