#!/bin/sh
# Renders /config.js from environment variables at container start.
# Run by the nginx image's /docker-entrypoint.sh, which stops the container if
# this script exits non-zero, so a missing variable fails the start loudly.
set -eu

CONFIG_DIR=/tmp/test-saas
CONFIG_FILE="$CONFIG_DIR/config.js"

require() {
  name="$1"
  value="$(printenv "$name" || true)"
  if [ -z "$value" ]; then
    echo "render-config: required environment variable $name is unset or empty" >&2
    exit 1
  fi
  # Values are written inside a JS string literal; refuse characters that could
  # break out of it rather than escaping them.
  case "$value" in
    *'"'* | *'\'* | *'<'* )
      echo "render-config: $name contains a quote, backslash, or '<'; refusing to render" >&2
      exit 1
      ;;
  esac
  printf '%s' "$value"
}

issuer_url="$(require OIDC_ISSUER_URL)"
client_id="$(require OIDC_CLIENT_ID)"
redirect_uri="$(require OIDC_REDIRECT_URI)"

mkdir -p "$CONFIG_DIR"
cat > "$CONFIG_FILE" <<EOF
window.TEST_SAAS_CONFIG = {
  "issuerUrl": "$issuer_url",
  "clientId": "$client_id",
  "redirectUri": "$redirect_uri"
};
EOF
echo "render-config: wrote $CONFIG_FILE"
