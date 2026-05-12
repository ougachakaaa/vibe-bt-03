#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

if [ "$(uname -s)" != "Darwin" ]; then
    echo "Warning: setup.macos.sh is intended for macOS; continuing anyway." >&2
fi

exec sh "$SCRIPT_DIR/setup.sh" "$@"
