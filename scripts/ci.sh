#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."
uv sync --locked --dev
uv run --no-sync ruff check .
uv run --no-sync ruff format --check .
uv run --no-sync pytest --cov-report=xml --cov-report=html:coverage/html
