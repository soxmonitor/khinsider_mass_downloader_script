@echo off
setlocal enabledelayedexpansion

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python first.
    exit /b 1
)

:: Define the libraries to check
set libraries=requests beautifulsoup4

:: Loop through the library list
for %%L in (%libraries%) do (
    echo Checking if %%L is installed...
    python -c "import %%L" >nul 2>&1
    if %errorlevel% neq 0 (
        echo %%L is not installed, installing now...
        pip install %%L
    ) else (
        echo %%L is already installed.
    )
)

echo All libraries have been checked and installed.
pause
