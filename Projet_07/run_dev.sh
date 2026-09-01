#!/usr/bin/env bash
# Lance l'API (FastAPI) et le frontend (React) du Projet 07 en parallèle (macOS/Linux).
# Usage : ./run_dev.sh   (Ctrl+C arrête les deux)
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -d "frontend/node_modules" ]; then
    echo "[1/2] Première installation des dépendances frontend..."
    (cd frontend && npm install)
fi

echo "[2/2] Lancement de l'API et du frontend..."
echo "  API      : http://localhost:8000  (doc interactive : http://localhost:8000/docs)"
echo "  Frontend : http://localhost:5173"

cleanup() {
    echo
    echo "Arrêt des serveurs..."
    kill "$API_PID" "$FRONTEND_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

uv run uvicorn api.main:app --reload --port 8000 &
API_PID=$!

(cd frontend && npm run dev) &
FRONTEND_PID=$!

wait
