@echo off
REM Lance l'API (FastAPI) et le frontend (React) du Projet 07 dans deux fenêtres séparées.
REM Double-clic, ou depuis un terminal : run_dev.bat

setlocal
cd /d "%~dp0"

if not exist "frontend\node_modules" (
    echo [1/2] Premiere installation des dependances frontend...
    pushd frontend
    call npm install
    popd
)

echo [2/2] Lancement de l'API et du frontend...

REM "uv run" installe/actualise l'environnement Python depuis pyproject.toml
REM automatiquement s'il manque une dependance (ex: fastapi, uvicorn).
start "Projet 07 - API (http://localhost:8000)" cmd /k "cd /d "%~dp0" && uv run uvicorn api.main:app --reload --port 8000"
start "Projet 07 - Frontend (http://localhost:5173)" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo Deux fenetres viennent de s'ouvrir :
echo   - API      : http://localhost:8000  (doc interactive : http://localhost:8000/docs)
echo   - Frontend : http://localhost:5173
echo.
echo Fermez ces fenetres (ou Ctrl+C dedans) pour arreter les serveurs.
