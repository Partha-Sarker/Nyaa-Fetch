#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$SCRIPT_DIR/.venv"

# 1. Create virtual environment if missing or broken
if [ ! -d "$VENV" ] || ! "$VENV/bin/python3" --version >/dev/null 2>&1; then
    echo "Setting up virtual environment..."
    rm -rf "$VENV"
    python3 -m venv "$VENV"
fi

# 2. Activate virtual environment
source "$VENV/bin/activate"

# 3. Install dependencies from requirements.txt
if ! python3 -c "import requests, bs4" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -r "$SCRIPT_DIR/requirements.txt" -q
fi

# 4. Execute the script with passed arguments
python3 "$SCRIPT_DIR/nyaa_dl.py" "$@"
