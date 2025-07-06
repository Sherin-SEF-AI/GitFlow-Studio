@echo off
REM GitFlow Studio Installation Script for Windows
REM This script installs GitFlow Studio with all dependencies

echo 🚀 GitFlow Studio Installation Script
echo ======================================

REM Check if Python is installed
echo [INFO] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed. Please install Python 3.9 or higher from python.org
    pause
    exit /b 1
)

python -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python version must be 3.9 or higher
    python --version
    pause
    exit /b 1
)

echo [SUCCESS] Python version is compatible

REM Check if pip is installed
echo [INFO] Checking pip installation...
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] pip is not installed. Please install pip.
    pause
    exit /b 1
)
echo [SUCCESS] pip found

REM Check if Git is installed
echo [INFO] Checking Git installation...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Git is not installed. Please install Git from git-scm.com
    pause
    exit /b 1
)
echo [SUCCESS] Git found

REM Create virtual environment
echo [INFO] Creating virtual environment...
if exist venv (
    echo [WARNING] Virtual environment already exists. Removing old one...
    rmdir /s /q venv
)

python -m venv venv
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)
echo [SUCCESS] Virtual environment created

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [SUCCESS] Virtual environment activated

REM Install dependencies
echo [INFO] Installing dependencies...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo [ERROR] Failed to upgrade pip
    pause
    exit /b 1
)

pip install -e .
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [SUCCESS] Dependencies installed successfully

REM Test installation
echo [INFO] Testing installation...
python -m studio --help >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] GitFlow Studio installation test failed
    pause
    exit /b 1
)
echo [SUCCESS] GitFlow Studio is working correctly

REM Show next steps
echo.
echo 🎉 Installation completed successfully!
echo ======================================
echo.
echo Next steps:
echo 1. Activate the virtual environment:
echo    venv\Scripts\activate.bat
echo.
echo 2. Try GitFlow Studio:
echo    gitflow-studio --help
echo    gitflow-studio --discover
echo    gitflow-studio --interactive
echo.
echo 3. Basic usage:
echo    gitflow-studio --repo C:\path\to\repo status
echo    gitflow-studio --repo C:\path\to\repo log --max-count 10
echo.
echo For more information, see:
echo - README.md - Basic usage and examples
echo - INSTALLATION.md - Detailed installation guide
echo - FEATURE_SUMMARY.md - Complete feature overview
echo.
pause 