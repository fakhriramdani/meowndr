#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ ! -d "studio-ui/dist" ]; then
  (cd studio-ui && npm install && npm run build)
fi

export STUDIO_ENV="${STUDIO_ENV:-production}"
exec python3 -m uvicorn studio_api.app:create_app --factory --host 127.0.0.1 --port "${STUDIO_PORT:-8420}" --workers 1
