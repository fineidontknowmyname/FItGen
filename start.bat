@echo off
title FitGen AI - Startup
echo ============================================
echo  FitGen AI - Starting All Services
echo ============================================
echo.

cd /d "D:\Genesis tech\Github repo\koda"

REM ── 1. Check Redis ────────────────────────────────────────────────────────────
echo [1/5] Checking Redis...
redis-cli ping >nul 2>&1
if %errorlevel% == 0 (
    echo      Redis OK - already running
) else (
    echo      WARNING: Redis not responding
    echo      Start Redis manually if plan generation fails
)

REM ── 2. Check / start Ollama on port 11434 ────────────────────────────────────
echo [2/5] Checking Ollama on port 11434...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% == 0 (
    echo      Ollama OK - already running on port 11434
) else (
    echo      Ollama not found on port 11434 - starting now...
    start "Ollama" cmd /k "set OLLAMA_HOST=0.0.0.0:11434 && ollama serve"
    timeout /t 4 /nobreak >nul
)

REM ── Build temp helper scripts (avoids nested-quote issues with spaces in path)
echo @echo off                                                      > "%TEMP%\koda_fastapi.bat"
echo cd /d "D:\Genesis tech\Github repo\koda"                     >> "%TEMP%\koda_fastapi.bat"
echo call venv\Scripts\activate.bat                                >> "%TEMP%\koda_fastapi.bat"
echo set PYTHONPATH=src                                            >> "%TEMP%\koda_fastapi.bat"
echo uvicorn src.main:app --reload --port 8000 --reload-dir src   >> "%TEMP%\koda_fastapi.bat"

echo @echo off                                                      > "%TEMP%\koda_celery.bat"
echo cd /d "D:\Genesis tech\Github repo\koda"                     >> "%TEMP%\koda_celery.bat"
echo call venv\Scripts\activate.bat                                >> "%TEMP%\koda_celery.bat"
echo set PYTHONPATH=src                                            >> "%TEMP%\koda_celery.bat"
echo python -m celery -A workers.celery_app worker --loglevel=info --pool=solo >> "%TEMP%\koda_celery.bat"

echo @echo off                                                      > "%TEMP%\koda_frontend.bat"
echo cd /d "D:\Genesis tech\Github repo\koda\frontend"            >> "%TEMP%\koda_frontend.bat"
echo npm run dev                                                   >> "%TEMP%\koda_frontend.bat"

REM ── 3. Start FastAPI ──────────────────────────────────────────────────────────
echo [3/5] Starting FastAPI...
start "FastAPI - Koda Backend" cmd /k "%TEMP%\koda_fastapi.bat"
timeout /t 3 /nobreak >nul

REM ── 4. Start Celery ───────────────────────────────────────────────────────────
echo [4/5] Starting Celery Worker...
start "Celery Worker" cmd /k "%TEMP%\koda_celery.bat"
timeout /t 2 /nobreak >nul

REM ── 5. Start Frontend ─────────────────────────────────────────────────────────
echo [5/5] Starting Frontend...
start "Frontend - Next.js" cmd /k "%TEMP%\koda_frontend.bat"

echo.
echo ============================================
echo  All services started!
echo.
echo  FastAPI:  http://localhost:8000
echo  Frontend: http://localhost:3000
echo  API Docs: http://localhost:8000/docs
echo  Ollama:   http://localhost:11435
echo ============================================
echo.
echo  Press any key to open the app in browser...
pause >nul
start http://localhost:3000
