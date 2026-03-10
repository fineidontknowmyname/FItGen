@echo off
title FitGen AI - Shutdown
echo ============================================
echo  FitGen AI - Stopping All Services
echo ============================================
echo.

REM Kill by window title (closes the CMD windows)
echo Stopping FastAPI...
taskkill /F /FI "WINDOWTITLE eq FastAPI - Koda Backend" >nul 2>&1

echo Stopping Celery...
taskkill /F /FI "WINDOWTITLE eq Celery Worker" >nul 2>&1

echo Stopping Frontend...
taskkill /F /FI "WINDOWTITLE eq Frontend - Next.js" >nul 2>&1

echo Stopping Ollama...
taskkill /F /FI "WINDOWTITLE eq Ollama" >nul 2>&1

REM Kill underlying processes by name (belt-and-suspenders)
echo Killing uvicorn processes...
taskkill /F /IM uvicorn.exe >nul 2>&1

echo Killing Celery (Python) processes...
REM Only kills Python processes with 'celery' in their command line
wmic process where "name='python.exe' and commandline like '%%celery%%'" delete >nul 2>&1

echo Killing Node.js (Next.js) processes...
taskkill /F /IM node.exe >nul 2>&1

echo.
echo ============================================
echo  All FitGen services stopped.
echo ============================================
echo.
pause
