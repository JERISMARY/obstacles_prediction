@echo off
echo ============================================
echo    Urban Intelligence Platform
echo   Starting Frontend...
echo ============================================
cd /d "%~dp0frontend"

echo Installing npm packages...
npm install

echo.
echo Starting React frontend on http://localhost:5173
echo.
npm run dev
