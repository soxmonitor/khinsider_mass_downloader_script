# ====================================
# Python Installation and Configuration Script
# ====================================

# Update the Python version to 3.12.8
$pythonUrl = "https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe"

# Directory where the installer will be downloaded
$tempDirectory = "C:\temp_provision\"

# Installation Directory
$targetDir = "C:\Python312"

# Function to check if Python is installed
Function Is-PythonInstalled {
    # Check if python.exe exists in the target directory
    if (Test-Path "$targetDir\python.exe") {
        return $true
    }
    # Alternatively, check if python is in PATH
    try {
        $pythonPath = & python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            return $true
        }
    } catch {
        return $false
    }
    return $false
}

# Function to add environment variables if Python is installed
Function Configure-EnvironmentVariables {
    Function Get-EnvVariableNameList {
        [cmdletbinding()]
        $allEnvVars = Get-ChildItem Env:
        $allEnvNamesArray = $allEnvVars.Name
        $pathEnvNamesList = New-Object System.Collections.ArrayList
        $pathEnvNamesList.AddRange($allEnvNamesArray)
        return $pathEnvNamesList
    }

    Function Add-EnvVarIfNotPresent {
        Param (
            [string]$variableNameToAdd,
            [string]$variableValueToAdd
        )
        $nameList = Get-EnvVariableNameList
        $alreadyPresentCount = ($nameList | Where-Object { $_ -eq $variableNameToAdd }).Count
        if ($alreadyPresentCount -eq 0) {
            [System.Environment]::SetEnvironmentVariable($variableNameToAdd, $variableValueToAdd, [System.EnvironmentVariableTarget]::Machine)
            [System.Environment]::SetEnvironmentVariable($variableNameToAdd, $variableValueToAdd, [System.EnvironmentVariableTarget]::Process)
            [System.Environment]::SetEnvironmentVariable($variableNameToAdd, $variableValueToAdd, [System.EnvironmentVariableTarget]::User)
            Write-Information "Environmental variable '$variableNameToAdd' added to Machine, Process, and User."
        }
        else {
            Write-Information "Environmental variable '$variableNameToAdd' already exists."
        }
    }

    Function Get-EnvExtensionList {
        [cmdletbinding()]
        $pathExtArray = ($env:PATHEXT).Split(";")
        $pathExtList = New-Object System.Collections.ArrayList
        $pathExtList.AddRange($pathExtArray)
        return $pathExtList
    }

    Function Add-EnvExtension {
        Param (
            [string]$pathExtToAdd
        )
        $pathList = Get-EnvExtensionList
        $alreadyPresentCount = ($pathList | Where-Object { $_ -eq $pathExtToAdd }).Count
        if ($alreadyPresentCount -eq 0) {
            $pathList.Add($pathExtToAdd) | Out-Null
            $returnPath = $pathList -join ";"
            [System.Environment]::SetEnvironmentVariable('PATHEXT', $returnPath, [System.EnvironmentVariableTarget]::Machine)
            [System.Environment]::SetEnvironmentVariable('PATHEXT', $returnPath, [System.EnvironmentVariableTarget]::Process)
            [System.Environment]::SetEnvironmentVariable('PATHEXT', $returnPath, [System.EnvironmentVariableTarget]::User)
            Write-Information "Path extension '$pathExtToAdd' added to PATHEXT."
        }
        else {
            Write-Information "Path extension '$pathExtToAdd' already exists in PATHEXT."
        }
    }

    Function Get-EnvPathList {
        [cmdletbinding()]
        $pathArray = ($env:PATH).Split(";")
        $pathList = New-Object System.Collections.ArrayList
        $pathList.AddRange($pathArray)
        return $pathList
    }

    Function Add-EnvPath {
        Param (
            [string]$pathToAdd
        )
        $pathList = Get-EnvPathList
        $alreadyPresentCount = ($pathList | Where-Object { $_ -eq $pathToAdd }).Count
        if ($alreadyPresentCount -eq 0) {
            $pathList.Add($pathToAdd) | Out-Null
            $returnPath = $pathList -join ";"
            [System.Environment]::SetEnvironmentVariable('PATH', $returnPath, [System.EnvironmentVariableTarget]::Machine)
            [System.Environment]::SetEnvironmentVariable('PATH', $returnPath, [System.EnvironmentVariableTarget]::Process)
            [System.Environment]::SetEnvironmentVariable('PATH', $returnPath, [System.EnvironmentVariableTarget]::User)
            Write-Information "Path '$pathToAdd' added to PATH."
        }
        else {
            Write-Information "Path '$pathToAdd' already exists in PATH."
        }
    }

    # Add required environment extensions
    Add-EnvExtension '.PY'
    Add-EnvExtension '.PYW'

    # Add Python installation directory to PATH
    Add-EnvPath $targetDir
}

# Function to install Python
Function Install-Python {
    # Create the download directory and get the exe file
    $pythonNameLoc = Join-Path -Path $tempDirectory -ChildPath "python3128.exe"
    New-Item -ItemType Directory -Path $tempDirectory -Force | Out-Null
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Write-Output "Downloading Python from $pythonUrl..."
    try {
        (New-Object System.Net.WebClient).DownloadFile($pythonUrl, $pythonNameLoc)
        Write-Output "Python downloaded successfully to $pythonNameLoc."
    }
    catch {
        Write-Error "Failed to download Python: $_"
        exit 1
    }

    # Silent installation arguments for Python 3.12.8
    $Arguments = @(
        "/quiet",
        "InstallAllUsers=1",
        "TargetDir=$targetDir",
        "PrependPath=1",
        "Include_doc=1",
        "Include_debug=1",
        "Include_dev=1",
        "Include_exe=1",
        "Include_launcher=1",
        "InstallLauncherAllUsers=1",
        "Include_lib=1",
        "Include_pip=1",
        "Include_symbols=1",
        "Include_tcltk=1",
        "Include_test=1",
        "Include_tools=1"
    )

    # Install Python
    Write-Output "Installing Python..."
    try {
        Start-Process -FilePath $pythonNameLoc -ArgumentList $Arguments -Wait -NoNewWindow
        Write-Output "Python installed successfully."
    }
    catch {
        Write-Error "Python installation failed: $_"
        exit 1
    }

    # Configure environment variables
    Configure-EnvironmentVariables
}

# Function to ensure pip is available
Function Ensure-Pip {
    Write-Output "Checking if pip is available..."
    try {
        & python -m pip --version | Out-Null
        Write-Output "pip is available."
    }
    catch {
        Write-Output "pip is not available. Attempting to install pip..."
        try {
            & python -m ensurepip --upgrade
            Write-Output "pip has been installed successfully."
        }
        catch {
            Write-Error "Failed to install pip."
            exit 1
        }
    }
}

# Function to install required Python packages
Function Install-PythonPackages {
    Write-Output "Defining third-party packages to check..."
    # 添加 'pillow' 到包列表
    $packages = @("requests", "beautifulsoup4", "pillow")

    Write-Output "Checking and installing third-party packages..."
    foreach ($pkg in $packages) {
        $module = if ($pkg -eq "beautifulsoup4") { "bs4" } elseif ($pkg -eq "pillow") { "PIL" } else { $pkg }
        Write-Output "`nChecking if module '$module' is installed..."
        try {
            & python -c "import $module" 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Output "Module '$module' is already installed."
            }
            else {
                Write-Output "Module '$module' is not installed. Installing package '$pkg'..."
                & python -m pip install $pkg
                if ($LASTEXITCODE -ne 0) {
                    Write-Error "Failed to install package '$pkg'."
                    exit 1
                }
                else {
                    Write-Output "Package '$pkg' installed successfully."
                }
            }
        }
        catch {
            Write-Output "Module '$module' is not installed. Installing package '$pkg'..."
            try {
                & python -m pip install $pkg
                Write-Output "Package '$pkg' installed successfully."
            }
            catch {
                Write-Error "Failed to install package '$pkg'."
                exit 1
            }
        }
    }
}

# Function to check standard Python modules
Function Check-StandardModules {
    Write-Output "`nChecking standard Python modules..."
    $standard_modules = @("os", "re", "time", "tkinter", "urllib.parse", "concurrent.futures")
    foreach ($module in $standard_modules) {
        Write-Output "`nVerifying module '$module'..."
        try {
            & python -c "import $module" 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Output "Module '$module' is available."
            }
            else {
                Write-Warning "Warning: Standard module '$module' could not be imported. There may be an issue with your Python installation."
            }
        }
        catch {
            Write-Warning "Warning: Standard module '$module' could not be imported. There may be an issue with your Python installation."
        }
    }
}

# Function to run the Python script
Function Run-PythonScript {
    # 修改脚本名称为 Multi-ThreadVer1.02.py
    $scriptPath = Join-Path -Path $PSScriptRoot -ChildPath "Multi-ThreadVer1.02.py"
    if (Test-Path $scriptPath) {
        Write-Output "`nRunning Multi-ThreadVer1.02.py..."
        try {
            & python $scriptPath
            if ($LASTEXITCODE -ne 0) {
                Write-Error "Error: Multi-ThreadVer1.02.py failed to run."
                exit 1
            }
            else {
                Write-Output "Multi-ThreadVer1.02.py executed successfully."
            }
        }
        catch {
            Write-Error "Failed to execute Multi-ThreadVer1.02.py: $_"
            exit 1
        }
    }
    else {
        Write-Error "Error: Multi-ThreadVer1.02.py not found in $PSScriptRoot."
        exit 1
    }
}

# =========================
# Main Execution Flow
# =========================

# Check if Python is already installed
if (Is-PythonInstalled) {
    Write-Output "Python is already installed. Skipping installation and environment configuration."
}
else {
    Write-Output "Python is not installed. Proceeding with installation."
    Install-Python
}

# Ensure pip is available
Ensure-Pip

# Install required Python packages
Install-PythonPackages

# Check standard Python modules
Check-StandardModules

# Completion Message
Write-Output "`n====================================="
Write-Output "All dependencies have been checked and installed as needed."
Write-Output "====================================="

# Run the Python script
Run-PythonScript

# Completion Success Message
Write-Output "`n====================================="
Write-Output "Script completed successfully."
Write-Output "====================================="

# Pause the script to allow the user to see the messages
Write-Output "`nPress any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
