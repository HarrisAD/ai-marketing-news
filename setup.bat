@echo off
echo ============================================
echo   AI Marketing News System - Easy Setup
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo Please download Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed!
    echo Please download Node.js from: https://nodejs.org/
    pause
    exit /b 1
)

echo Python and Node.js found! Setting up your AI news system...
echo.

REM Install Python dependencies
echo Installing Python dependencies...
cd backend
pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install Python dependencies
    pause
    exit /b 1
)
cd..

REM Install Node.js dependencies
echo Installing Node.js dependencies...
cd frontend
npm install
if errorlevel 1 (
    echo Failed to install Node.js dependencies
    pause
    exit /b 1
)
cd..

REM Setup environment file
echo.
echo Setting up configuration...
copy backend\.env.example backend\.env

echo.
echo ============================================
echo   Setup Complete! 
echo ============================================
echo.
echo IMPORTANT: You need to add your OpenAI API key!
echo.
echo 1. Get your API key from: https://platform.openai.com/api-keys
echo 2. Open the file: backend\.env
echo 3. Replace "your_openai_api_key_here" with your actual API key
echo 4. Save the file
echo.
echo Then run: start.bat to start your AI news system
echo.
pause