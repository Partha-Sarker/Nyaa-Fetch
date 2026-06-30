#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$SCRIPT_DIR/.venv"

if [ ! -d "$VENV" ]; then
    echo "Setting up virtual environment..."
    python3 -m venv "$VENV"
fi

if ! "$VENV/bin/python3" -c "import requests, bs4" 2>/dev/null; then
    echo "Installing dependencies..."
    "$VENV/bin/pip" install requests beautifulsoup4 -q
fi

"$VENV/bin/python3" "$SCRIPT_DIR/nyaa_dl.py" "$@"
