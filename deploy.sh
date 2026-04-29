#!/usr/bin/env bash
# Deploy The Cold Fusion Calendar.
#
# First-time setup:
#   cp .env.example .env
#   # edit .env to point at your own host/path
#   ./deploy.sh
#
# Each run rebuilds data.json + the og:image, then rsyncs the static
# site (excluding sources/build scripts) to the configured server.

set -euo pipefail

LOCAL_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$LOCAL_DIR"

if [[ ! -f .env ]]; then
    echo "ERROR: no .env file found." >&2
    echo "       Copy .env.example to .env and fill in your deployment target." >&2
    exit 1
fi

# shellcheck disable=SC1091
set -a; source .env; set +a

: "${DEPLOY_USER:?DEPLOY_USER must be set in .env}"
: "${DEPLOY_HOST:?DEPLOY_HOST must be set in .env}"
: "${DEPLOY_PATH:?DEPLOY_PATH must be set in .env}"
DEPLOY_URL="${DEPLOY_URL:-}"

echo "Rebuilding data.json from sources..."
python3 build_data.py

echo "Regenerating og:image with current event count..."
python3 build_og.py

echo "Generating iCal feed..."
python3 build_ical.py

echo "Generating RSS feed..."
python3 build_rss.py

echo "Generating per-date og:images..."
python3 build_og_per_date.py

echo "Syncing to ${DEPLOY_USER}@${DEPLOY_HOST}:${DEPLOY_PATH}"
rsync -avz --delete \
    --exclude='.git/' \
    --exclude='.gitignore' \
    --exclude='.env' \
    --exclude='.env.example' \
    --exclude='source_grab/' \
    --exclude='build_data.py' \
    --exclude='build_og.py' \
    --exclude='build_ical.py' \
    --exclude='build_rss.py' \
    --exclude='build_og_per_date.py' \
    --exclude='tests/' \
    --exclude='CHANGELOG.md' \
    --exclude='deploy.sh' \
    --exclude='README.md' \
    --exclude='PLAN.md' \
    --exclude='TODO.md' \
    --exclude='.DS_Store' \
    --exclude='__pycache__/' \
    "${LOCAL_DIR}/" \
    "${DEPLOY_USER}@${DEPLOY_HOST}:${DEPLOY_PATH}"

echo
if [[ -n "$DEPLOY_URL" ]]; then
    echo "Deployed → ${DEPLOY_URL}"
else
    echo "Deployed → ${DEPLOY_USER}@${DEPLOY_HOST}:${DEPLOY_PATH}"
fi
