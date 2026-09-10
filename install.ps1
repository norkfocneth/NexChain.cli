# ========================================================
# NexChain AI CLI ? Windows Universal 1-Line Installer
# Supported: Windows PowerShell, PowerShell Core
# ========================================================

$ErrorActionPreference = "Stop"
$repoUrl = "https://github.com/norkfocneth/NexChain.cli.git"
$installDir = Join-Path $HOME ".nexchain"
$binDir = Join-Path $HOME ".local\bin"

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  NexChain AI CLI ? Windows 1-Line Installer" -ForegroundColor White
Write-Host "========================================================" -ForegroundColor Cyan

# Check if running locally inside cloned folder or remote 1-liner
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path -ErrorAction SilentlyContinue
if ($scriptDir -and (Test-Path "$scriptDir\nexchain.py")) {
    Write-Host "[*] Installing from local repo: $scriptDir" -ForegroundColor Yellow
    $installDir = $scriptDir
} else {
    if (-not (Test-Path $binDir)) {
        New-Item -ItemType Directory -Path $binDir -Force | Out-Null
    }
    if (Test-Path "$installDir\.git") {
        Write-Host "[*] Updating existing NexChain repository..." -ForegroundColor Yellow
        Push-Location $installDir
        git pull --quiet
        Pop-Location
    } else {
        Write-Host "[*] Cloning NexChain CLI to $installDir..." -ForegroundColor Yellow
        if (Test-Path $installDir) { Remove-Item -Recurse -Force $installDir }
        git clone --depth 1 $repoUrl $installDir
    }
}

# Setup venv & dependencies
Write-Host "[*] Setting up Python environment & dependencies..." -ForegroundColor Yellow
$venvPython = "$installDir\.venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    python -m venv "$installDir\.venv"
}

$pyExec = if (Test-Path $venvPython) { $venvPython } else { "python" }

if (Get-Command uv -ErrorAction SilentlyContinue) {
    uv pip install --python $pyExec --quiet rich typer httpx
} else {
    try {
        & $pyExec -m pip install --quiet rich typer httpx
    } catch {
        Write-Host "[!] Note: Ensure pip is installed if running without virtualenv." -ForegroundColor Yellow
    }
}

# Ensure global launcher in $binDir
if (-not (Test-Path $binDir)) {
    New-Item -ItemType Directory -Path $binDir -Force | Out-Null
}

$cmdContent = @"
@echo off
setlocal
set "NEXCHAIN_DIR=$installDir"
pushd "%NEXCHAIN_DIR%"
if exist "%NEXCHAIN_DIR%\.venv\Scripts\python.exe" (
    "%NEXCHAIN_DIR%\.venv\Scripts\python.exe" "%NEXCHAIN_DIR%\nexchain.py" %*
) else (
    python "%NEXCHAIN_DIR%\nexchain.py" %*
)
popd
"@
Set-Content -Path "$binDir\nexchain.cmd" -Value $cmdContent -Encoding Ascii
Set-Content -Path "$binDir\nexchain.bat" -Value $cmdContent -Encoding Ascii
Set-Content -Path "$binDir\nexsen.cmd" -Value $cmdContent -Encoding Ascii
Set-Content -Path "$binDir\nexsen.bat" -Value $cmdContent -Encoding Ascii

$psContent = @"
`$nexchainDir = "$installDir"
Push-Location `$nexchainDir
try {
    if (Test-Path "`$nexchainDir\.venv\Scripts\python.exe") {
        & "`$nexchainDir\.venv\Scripts\python.exe" "`$nexchainDir\nexchain.py" @args
    } else {
        python "`$nexchainDir\nexchain.py" @args
    }
} finally {
    Pop-Location
}
"@
Set-Content -Path "$binDir\nexchain.ps1" -Value $psContent -Encoding Ascii
Set-Content -Path "$binDir\nexsen.ps1" -Value $psContent -Encoding Ascii

# Ensure $binDir is in User PATH
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath -notlike "*$binDir*") {
    [Environment]::SetEnvironmentVariable("Path", "$userPath;$binDir", "User")
    $env:Path = "$env:Path;$binDir"
    Write-Host "[+] Added $binDir to User PATH environment." -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================================" -ForegroundColor Green
Write-Host "  ? NexChain AI CLI Installed Successfully!" -ForegroundColor Green
Write-Host "  ?? Run 'nexchain' from ANY terminal to start!" -ForegroundColor White
Write-Host "========================================================" -ForegroundColor Green
Write-Host ""

