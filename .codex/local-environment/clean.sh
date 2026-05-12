#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)
cd "$REPO_ROOT"

remove_path() {
    path=$1
    case "$path" in
        ""|"/"|".")
            echo "Refusing to remove unsafe path: $path" >&2
            exit 1
            ;;
    esac

    if [ -e "$path" ] || [ -L "$path" ]; then
        rm -rf -- "$path"
        echo "Removed $path"
    fi
}

remove_path ".venv"
remove_path ".uv-cache"
remove_path ".uv-python"
remove_path ".pytest_cache"
remove_path ".mypy_cache"
remove_path ".ruff_cache"
remove_path "build"
remove_path "dist"

find . \
    \( -path "./.git" -o -path "./.git/*" \) -prune -o \
    \( -type d -name "__pycache__" -o -type d -name "*.egg-info" \) \
    -print -exec rm -rf -- {} +
