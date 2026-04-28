#!/usr/bin/env bash
# Deploy The Cold Fusion Calendar to lackluster.org/cf/
# Usage: ./deploy.sh
set -euo pipefail

REMOTE_USER="esa"
REMOTE_HOST="lackluster.org"
REMOTE_PATH="/var/www/html/cf/"
LOCAL_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Rebuilding data.json from sources..."
cd "$LOCAL_DIR"
python3 build_data.py

echo "Syncing to ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}"
rsync -avz --delete \
    --exclude='.git/' \
    --exclude='.gitignore' \
    --exclude='source_grab/' \
    --exclude='build_data.py' \
    --exclude='deploy.sh' \
    --exclude='README.md' \
    --exclude='.DS_Store' \
    --exclude='__pycache__/' \
    "${LOCAL_DIR}/" \
    "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}"

echo
echo "Deployed → https://www.lackluster.org/cf/"
