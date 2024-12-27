@echo off
setlocal enabledelayedexpansion

echo =====================================
echo Starting Dependency Checker
echo =====================================
echo.

:: -------------------------------
:: Check if Python is Installed
:: -------------------------------
echo Checking if Python is installed...

:: Attempt to get Python version
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Python is already installed.
    set "PYTHON_COMMAND=python"
) else (
    echo Python is not found via 'python'. Attempting to use 'py' launcher...
    py --version >nul 2>&1
    if %errorlevel% equ 0 (
        echo Python is available via 'py' launcher.
        set "PYTHON_COMMAND=py"
    ) else (
        echo 'py' launcher is not available. Python may not be installed or not added to PATH.
        echo Attempting to download and install Python...
        
        :: Define Python installer URL
        :: Update the version number as needed
        set "PYTHON_URL=https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe"
        set "PYTHON_INSTALLER=python_installer.exe"
        
        :: Download Python installer
        call :download_file "%PYTHON_URL%" "%PYTHON_INSTALLER%"
        if not exist "%PYTHON_INSTALLER%" (
            echo Failed to download Python installer.
            goto :end
        )
        
        :: Install Python silently and add to PATH
        echo Installing Python...
        "%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1
        if %errorlevel% neq 0 (
            echo Python installation failed.
            del "%PYTHON_INSTALLER%"
            goto :end
        )
        
        :: Remove installer after installation
        del "%PYTHON_INSTALLER%"
        
        :: Refresh environment variables
        :: Note: Environment variables are not updated in the current session. A restart is required.
        echo Please restart your terminal to apply the updated PATH.
        echo Python has been installed successfully.
        goto :end
    )
)

:: -------------------------------
:: Ensure pip is Available
:: -------------------------------
echo.
echo Checking if pip is available...
%PYTHON_COMMAND% -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo pip is not available. Attempting to install pip...
    %PYTHON_COMMAND% -m ensurepip --upgrade
    if %errorlevel% neq 0 (
        echo Failed to install pip.
        goto :end
    )
    echo pip has been installed successfully.
) else (
    echo pip is available.
)

:: -------------------------------
:: Define Third-Party Packages
:: -------------------------------
echo.
echo Defining third-party packages to check...
set "packages=requests beautifulsoup4"

:: -------------------------------
:: Check and Install Third-Party Packages
:: -------------------------------
echo.
echo Checking and installing third-party packages...
for %%P in (%packages%) do (
    call :map_package_to_module %%P
    echo.
    echo Checking if module !module! is installed...
    %PYTHON_COMMAND% -c "import !module!" >nul 2>&1
    if !errorlevel! neq 0 (
        echo Module !module! is not installed. Installing package %%P...
        %PYTHON_COMMAND% -m pip install %%P
        if !errorlevel! neq 0 (
            echo Failed to install package %%P.
            goto :end
        ) else (
            echo Package %%P installed successfully.
        )
    ) else (
        echo Module !module! is already installed.
    )
)

:: -------------------------------
:: Check Standard Python Modules
:: -------------------------------
echo.
echo Checking standard Python modules...
set "standard_modules=os re time tkinter urllib.parse concurrent.futures"
for %%M in (%standard_modules%) do (
    echo.
    echo Verifying module %%M...
    %PYTHON_COMMAND% -c "import %%M" >nul 2>&1
    if !errorlevel! neq 0 (
        echo Warning: Standard module %%M could not be imported. There may be an issue with your Python installation.
    ) else (
        echo Module %%M is available.
    )
)

:: -------------------------------
:: Completion Message
:: -------------------------------
echo.
echo =====================================
echo All dependencies have been checked and installed as needed.
echo =====================================

:: -------------------------------
:: Run Python Script
:: -------------------------------
echo.
echo =====================================
echo All dependencies have been checked and installed as needed.
echo =====================================
echo.

:: Check if the Python script exists
if exist "%~dp0Muti-ThreadVer1.01.py" (
    echo Running Muti-ThreadVer1.01.py...
    "%PYTHON_COMMAND%" "%~dp0Muti-ThreadVer1.01.py"
    if %errorlevel% neq 0 (
        echo.
        echo Error: Muti-ThreadVer1.01.py failed to run.
        goto :end
    ) else (
        echo.
        echo Muti-ThreadVer1.01.py executed successfully.
    )
) else (
    echo Error: Muti-ThreadVer1.01.py not found in %~dp0
    goto :end
)

pause
goto :eof

:: -------------------------------
:: Function to Download Files
:: -------------------------------
:download_file
set "url=%~1"
set "output=%~2"
echo.
echo Downloading from %url% ...
powershell -Command "try { Invoke-WebRequest -Uri '%url%' -OutFile '%output%' } catch { exit 1 }"
if %errorlevel% neq 0 (
    echo Failed to download %url%.
    exit /b 1
)
echo Downloaded successfully to %output%.
goto :eof

:: -------------------------------
:: Map Package Names to Module Names
:: -------------------------------
:map_package_to_module
set "package=%~1"
if /i "%package%"=="beautifulsoup4" (
    set "module=bs4"
) else (
    set "module=%package%"
)
goto :eof

:: -------------------------------
:: End of Script
:: -------------------------------
:end
echo.
echo =====================================
echo Script terminated due to errors.
echo =====================================
pause
goto :eof

