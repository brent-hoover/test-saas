# API image: FastAPI served by uvicorn, non-root.
# Build: docker build -t ghcr.io/brent-hoover/test-saas-api:<tag> .

FROM ghcr.io/astral-sh/uv:0.12.24 AS uv

FROM python:3.15.0-slim-trixie AS build
COPY --from=uv /uv /bin/uv
# Use the image's Python, never a downloaded one, so build and runtime match.
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never
WORKDIR /app
# Dependencies first, so source edits don't invalidate this layer.
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --locked --no-dev --no-install-project
COPY src ./src
RUN uv sync --locked --no-dev --no-editable

FROM python:3.15.0-slim-trixie
# Fixed numeric UID so Kubernetes runAsNonRoot can verify it without a passwd lookup.
RUN useradd --system --uid 10001 --no-create-home --shell /usr/sbin/nologin app
COPY --from=build /app/.venv /app/.venv
ENV PATH=/app/.venv/bin:$PATH
USER 10001
EXPOSE 8000
# The factory loads OIDC_ISSUER_URL / OIDC_AUDIENCE and exits naming any missing one.
CMD ["uvicorn", "--factory", "test_saas.api:create_app_from_environment", "--host", "0.0.0.0", "--port", "8000"]
