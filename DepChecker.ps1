# ====================================
# Python Installation and Configuration Script
# ====================================

# Check if running with Administrator privileges
Function Test-Admin {
    $currentUser = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $currentUser.IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)
}

if (-not (Test-Admin)) {
    Write-Warning "This script must be run as an Administrator. Please restart PowerShell with Administrator privileges."
    exit 1
}

# Update Python version to 3.12.8
$pythonUrl = "https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe"

# Download directory: Current user's temporary directory
$currentUsername = $env:USERNAME
$tempDirectory = "C:\Users\$currentUsername\AppData\Local\Temp"

# Installation directory
$targetDir = "C:\Python312"

# Paths to Python and Scripts directories
$pythonExeTarget = Join-Path -Path $targetDir -ChildPath "python.exe"
$scriptsDirTarget = Join-Path -Path $targetDir -ChildPath "Scripts"

# Function: Check if Python is installed in the target directory
Function Is-PythonInstalledAtTargetDir {
    if (Test-Path $pythonExeTarget) {
        return $true
    }
    return $false
}

# Function: Check if Python is installed anywhere on the system
Function Is-PythonInstalledAnywhere {
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

# Function: Configure environment variables (only called if Python is installed in the target directory)
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
            Write-Information "Environment variable '$variableNameToAdd' added to Machine, Process, and User."
        }
        else {
            Write-Information "Environment variable '$variableNameToAdd' already exists."
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

    Function Add-EnvPathBeforeWindowsApps {
        Param (
            [string[]]$pathsToAdd
        )
        $currentPathList = Get-EnvPathList

        # Find the index of WindowsApps
        $windowsAppsIndex = -1
        for ($i = 0; $i -lt $currentPathList.Count; $i++) {
            if ($currentPathList[$i].ToLower().EndsWith("windowsapps")) {
                $windowsAppsIndex = $i
                break
            }
        }

        if ($windowsAppsIndex -ne -1) {
            # Remove existing paths
            foreach ($path in $pathsToAdd) {
                $currentPathList.RemoveAll({ $_.ToLower() -eq $path.ToLower() }) | Out-Null
            }

            # Insert new paths before WindowsApps in reverse order
            for ($j = $pathsToAdd.Length - 1; $j -ge 0; $j--) {
                $currentPathList.Insert($windowsAppsIndex, $pathsToAdd[$j])
            }
            Write-Output "Inserted paths before WindowsApps."
        }
        else {
            # If WindowsApps not found, append paths
            foreach ($path in $pathsToAdd) {
                if (-not ($currentPathList -contains $path)) {
                    $currentPathList.Add($path) | Out-Null
                }
            }
            Write-Output "WindowsApps path not found. Appended paths to PATH."
        }

        # Update the PATH environment variable
        $newPath = $currentPathList -join ";"
        [System.Environment]::SetEnvironmentVariable('PATH', $newPath, [System.EnvironmentVariableTarget]::Machine)
        [System.Environment]::SetEnvironmentVariable('PATH', $newPath, [System.EnvironmentVariableTarget]::Process)
        [System.Environment]::SetEnvironmentVariable('PATH', $newPath, [System.EnvironmentVariableTarget]::User)
        Write-Information "PATH environment variable updated."
    }

    # Add required path extensions
    Add-EnvExtension '.PY'
    Add-EnvExtension '.PYW'

    # Add Python installation directory and Scripts directory to PATH before WindowsApps
    $pathsToAdd = @($targetDir, $scriptsDirTarget)
    Add-EnvPathBeforeWindowsApps -pathsToAdd $pathsToAdd
}

# Function: Install Python
Function Install-Python {
    # Create download directory and get the installer
    $pythonNameLoc = Join-Path -Path $tempDirectory -ChildPath "python3128.exe"
    New-Item -ItemType Directory -Path $tempDirectory -Force | Out-Null
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Write-Output "Downloading Python from $pythonUrl..."
    try {
        (New-Object System.Net.WebClient).DownloadFile($pythonUrl, $pythonNameLoc)
        Write-Output "Python successfully downloaded to $pythonNameLoc."
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

# Function: Ensure pip is available (only called if Python is installed in the target directory)
Function Ensure-Pip {
    Write-Output "Checking if pip is available..."
    try {
        & $pythonExeTarget -m pip --version | Out-Null
        Write-Output "pip is available."
    }
    catch {
        Write-Output "pip is not available. Attempting to install pip..."
        try {
            & $pythonExeTarget -m ensurepip --upgrade
            Write-Output "pip has been installed successfully using ensurepip."
        }
        catch {
            Write-Output "Failed to install pip using ensurepip. Attempting to install pip using get-pip.py..."
            # Download get-pip.py and install pip
            $getPipUrl = "https://bootstrap.pypa.io/get-pip.py"
            $getPipPath = Join-Path -Path $tempDirectory -ChildPath "get-pip.py"
            try {
                (New-Object System.Net.WebClient).DownloadFile($getPipUrl, $getPipPath)
                & $pythonExeTarget $getPipPath
                if (& $pythonExeTarget -m pip --version) {
                    Write-Output "pip has been installed successfully using get-pip.py."
                }
                else {
                    Write-Error "Failed to install pip using get-pip.py."
                    exit 1
                }
            }
            catch {
                Write-Error "Failed to download or install pip using get-pip.py: $_"
                exit 1
            }
        }
    }
}

# Function: Install required Python packages (regardless of Python installation location)
Function Install-PythonPackages {
    Write-Output "Defining third-party packages to check..."
    # Add 'pillow' to the package list and specify version
    $packages = @(
        @{name="requests"; module="requests"; version="2.32.3"},
        @{name="beautifulsoup4"; module="bs4"; version="4.12.3"},
        @{name="pillow"; module="PIL"; version="11.0.0"}
    )

    Write-Output "Checking and installing/updating third-party packages..."
    foreach ($pkg in $packages) {
        $packageName = $pkg.name
        $moduleName = $pkg.module
        $requiredVersion = $pkg.version

        Write-Output "`nChecking if module '$moduleName' is installed..."
        try {
            # Get the currently installed module version
            $currentVersion = if ($pythonInstalledAtTarget) {
                & $pythonExeTarget -c "import $moduleName; print($moduleName.__version__)" 2>$null
            }
            else {
                & python -c "import $moduleName; print($moduleName.__version__)" 2>$null
            }

            if ($LASTEXITCODE -eq 0 -and $currentVersion) {
                # Compare versions
                if ([version]$currentVersion -lt [version]$requiredVersion) {
                    Write-Output "Module '$moduleName' version $currentVersion is less than required $requiredVersion. Upgrading..."
                    if ($pythonInstalledAtTarget) {
                        & $pythonExeTarget -m pip install --upgrade "$packageName==$requiredVersion"
                    }
                    else {
                        & python -m pip install --upgrade "$packageName==$requiredVersion"
                    }
                    if ($LASTEXITCODE -ne 0) {
                        Write-Error "Failed to upgrade package '$packageName' to version $requiredVersion."
                        exit 1
                    }
                    else {
                        Write-Output "Package '$packageName' upgraded to version $requiredVersion successfully."
                    }
                }
                else {
                    Write-Output "Module '$moduleName' version $currentVersion meets the requirement."
                }
            }
            else {
                Write-Output "Module '$moduleName' is not installed. Installing package '$packageName' version $requiredVersion..."
                if ($pythonInstalledAtTarget) {
                    & $pythonExeTarget -m pip install "$packageName==$requiredVersion"
                }
                else {
                    & python -m pip install "$packageName==$requiredVersion"
                }
                if ($LASTEXITCODE -ne 0) {
                    Write-Error "Failed to install package '$packageName' version $requiredVersion."
                    exit 1
                }
                else {
                    Write-Output "Package '$packageName' version $requiredVersion installed successfully."
                }
            }
        }
        catch {
            Write-Output "Module '$moduleName' is not installed. Installing package '$packageName' version $requiredVersion..."
            try {
                if ($pythonInstalledAtTarget) {
                    & $pythonExeTarget -m pip install "$packageName==$requiredVersion"
                }
                else {
                    & python -m pip install "$packageName==$requiredVersion"
                }
                Write-Output "Package '$packageName' version $requiredVersion installed successfully."
            }
            catch {
                Write-Error "Failed to install package '$packageName' version $requiredVersion."
                exit 1
            }
        }
    }
}

# Function: Check standard Python modules (regardless of Python installation location)
Function Check-StandardModules {
    Write-Output "`nChecking standard Python modules..."
    $standard_modules = @("os", "re", "time", "tkinter", "urllib.parse", "concurrent.futures")
    foreach ($module in $standard_modules) {
        Write-Output "`nVerifying module '$module'..."
        try {
            if ($pythonInstalledAtTarget) {
                & $pythonExeTarget -c "import $module" 2>$null
            }
            else {
                & python -c "import $module" 2>$null
            }
            if ($LASTEXITCODE -eq 0) {
                Write-Output "Module '$module' is available."
            }
            else {
                Write-Warning "Warning: Module '$module' could not be imported. There may be an issue with your Python installation."
            }
        }
        catch {
            Write-Warning "Warning: Module '$module' could not be imported. There may be an issue with your Python installation."
        }
    }
}

# Function: Run Python script
Function Run-PythonScript {
    # Modify script name to Multi-ThreadVer1.02.py
    $scriptPath = Join-Path -Path $PSScriptRoot -ChildPath "Multi-ThreadVer1.02.py"
    if (Test-Path $scriptPath) {
        Write-Output "`nRunning Multi-ThreadVer1.02.py..."
        try {
            if ($pythonInstalledAtTarget) {
                & $pythonExeTarget $scriptPath
            }
            else {
                & python $scriptPath
            }
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

# Determine Python installation status
$pythonInstalledAtTarget = Is-PythonInstalledAtTargetDir
$pythonInstalledElsewhere = $false

if (-not $pythonInstalledAtTarget) {
    $pythonInstalledElsewhere = Is-PythonInstalledAnywhere
}

if ($pythonInstalledAtTarget) {
    Write-Output "Python is installed at $targetDir. Proceeding with pip checks and environment configuration."
    # Ensure pip is available
    Ensure-Pip

    # Install/update specified version of Python packages
    Install-PythonPackages

    # Check standard Python modules
    Check-StandardModules
}
elseif ($pythonInstalledElsewhere) {
    Write-Output "Python is already installed elsewhere. Skipping Python installation and environment configuration."
    Write-Output "Continuing to check and install/update dependency packages."

    # Install/update specified version of Python packages using system Python
    Install-PythonPackages

    # Check standard Python modules
    Check-StandardModules
}
else {
    Write-Output "Python is not installed. Proceeding with installation and configuration."
    Install-Python

    # Ensure pip is available
    Ensure-Pip

    # Install/update specified version of Python packages
    Install-PythonPackages

    # Check standard Python modules
    Check-StandardModules
}

# Completion message
Write-Output "`n====================================="
Write-Output "All dependencies have been checked and installed as needed."
Write-Output "====================================="

# Run Python script
Run-PythonScript

# Completion success message
Write-Output "`n====================================="
Write-Output "Script completed successfully."
Write-Output "====================================="

# Pause the script to allow the user to see the messages
Write-Output "`nPress any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
