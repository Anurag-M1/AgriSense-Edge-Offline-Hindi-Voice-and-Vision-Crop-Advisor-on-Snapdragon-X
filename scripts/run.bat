@echo off
REM AgriSense Edge — Run Script
REM Starts both backend and frontend

echo ============================================
echo   AgriSense Edge — Starting...
echo ============================================

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Start backend in background
start "AgriSense Backend" cmd /c "python -m app.backend.main"

REM Wait for backend to start
timeout /t 3 /nobreak > nul

REM Start frontend
cd app\frontend
start "AgriSense Frontend" cmd /c "npm run dev"
cd ..\..

echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Press Ctrl+C in each window to stop.
pause
