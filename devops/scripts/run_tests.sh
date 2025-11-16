#!/usr/bin/env bash
set -euo pipefail

# Resolve repo root (…/polyglot-captions)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${SCRIPT_DIR}/../.."

cd "$REPO_ROOT/app"

# Create venv (idempotent) and install deps
python -m venv .venv
# shellcheck source=/dev/null
source .venv/bin/activate

pip install -r requirements.txt

# Run tests
pytest -q
