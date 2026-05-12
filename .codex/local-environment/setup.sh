#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)
cd "$REPO_ROOT"

if ! command -v uv >/dev/null 2>&1; then
    echo "uv is required. Install uv first: https://docs.astral.sh/uv/" >&2
    exit 127
fi

PYTHON_VERSION=$(tr -d '[:space:]' < .python-version)
if [ -z "$PYTHON_VERSION" ]; then
    echo ".python-version is empty" >&2
    exit 1
fi

export UV_CACHE_DIR="${UV_CACHE_DIR:-$REPO_ROOT/.uv-cache}"
export UV_PYTHON_INSTALL_DIR="${UV_PYTHON_INSTALL_DIR:-$REPO_ROOT/.uv-python}"

echo "Repository: $REPO_ROOT"
echo "uv: $(uv --version)"
echo "Python: $PYTHON_VERSION"
echo "UV_CACHE_DIR: $UV_CACHE_DIR"
echo "UV_PYTHON_INSTALL_DIR: $UV_PYTHON_INSTALL_DIR"

uv python install "$PYTHON_VERSION"

SYNC_ARGS="--all-groups --frozen"
if [ "${CODEX_UV_ALLOW_LOCK_UPDATE:-0}" = "1" ]; then
    SYNC_ARGS="--all-groups"
fi

uv sync $SYNC_ARGS
uv run python --version
uv run python -c 'import sys; print(sys.executable)'

if [ "${CODEX_RUN_CHECKS:-0}" = "1" ]; then
    uv run pytest -q
fi
