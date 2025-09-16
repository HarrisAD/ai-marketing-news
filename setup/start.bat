@echo off
setlocal
cd /d "%~dp0.."
echo ============================================
echo   Starting AI Marketing News System
echo ============================================
echo.

REM Ensure .env exists
if not exist "backend\.env" (
    if exist "backend\.env.example" (
        echo Creating backend\.env from template...
        copy backend\.env.example backend\.env >nul
        echo You can paste your OpenAI API key in the dashboard after launch.
    ) else (
        echo ERROR: backend\.env.example not found. Please run setup first.
        pause
        exit /b 1
    )
)

findstr /C:"your_openai_api_key_here" backend\.env >nul
if not errorlevel 1 (
    echo WARNING: OpenAI API key not configured yet.
    echo You can paste it using the OpenAI API Key card on the dashboard once the app loads.
)

echo Starting backend server...
start "AI News Backend" cmd /k "cd /d %cd%\backend\src && python -m uvicorn main:app --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak > nul

echo Starting frontend server...
start "AI News Frontend" cmd /k "cd /d %cd%\frontend && npm run dev"

timeout /t 5 /nobreak > nul

echo.
echo ============================================
echo   AI Marketing News System is Starting!
echo ============================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Your AI news system will open automatically...
echo Close this window to stop the system.
echo.

timeout /t 3 /nobreak > nul
start http://localhost:3000

echo Press any key to stop the system...
pause > nul

echo Stopping servers...
taskkill /f /im "python.exe" 2>nul
taskkill /f /im "node.exe" 2>nul
