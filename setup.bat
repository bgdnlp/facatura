@echo off
:: Setup script for facatura on Windows
:: This script creates a Python virtual environment and installs all dependencies

echo Setting up facatura development environment...

:: Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: Python is not installed or not in PATH. Please install Python and try again.
    exit /b 1
)

:: Create virtual environment
echo Creating virtual environment...
python -m venv venv

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

:: Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

:: Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

:: Install the package in development mode
echo Installing facatura in development mode...
pip install -e .

echo.
echo Setup complete! The virtual environment has been created and dependencies installed.
echo.
echo To activate the virtual environment, run:
echo   venv\Scripts\activate.bat
echo.
echo To deactivate the virtual environment when you're done, run:
echo   deactivate
echo.