@echo off
echo ============================================
echo   Starting AI Marketing News System
echo ============================================
echo.

REM Check if .env file exists and has API key
if not exist "backend\.env" (
    echo ERROR: Configuration file not found!
    echo Please run setup.bat first
    pause
    exit /b 1
)

findstr /C:"your_openai_api_key_here" backend\.env >nul
if not errorlevel 1 (
    echo ERROR: OpenAI API key not configured!
    echo.
    echo Please edit backend\.env and add your OpenAI API key
    echo Get your key from: https://platform.openai.com/api-keys
    echo.
    pause
    exit /b 1
)

echo Starting backend server...
start "AI News Backend" cmd /k "cd backend\src && python -m uvicorn main:app --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak > nul

echo Starting frontend server...
start "AI News Frontend" cmd /k "cd frontend && npm run dev"

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