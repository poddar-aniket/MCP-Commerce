@echo off
echo ====================================
echo MCP Shopping Assistant Startup
echo ====================================

echo [1/4] Installing Required Dependencies...
python -m pip install fastapi uvicorn pydantic python-dotenv "google-genai" "datasets>=2.16.1" --upgrade --user

echo.
echo [2/4] Starting MCP API Backend (Port 8000)...
start cmd /k "python server.py || echo ERROR: Backend failed to start. && pause"

echo.
echo [3/4] Starting Frontend UI Server (Port 8080)...
start cmd /k "python -m http.server 8080 || echo ERROR: Frontend failed to start. && pause"

echo.
echo [4/4] Opening Web Browser...
timeout /t 5 > nul
start http://localhost:8080

echo Done! You can close this window.
