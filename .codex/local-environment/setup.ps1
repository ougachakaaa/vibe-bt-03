[CmdletBinding()]
param(
    [switch]$AllowLockUpdate,
    [switch]$RunChecks
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Set-Location $RepoRoot

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    throw "uv is required. Install uv first: https://docs.astral.sh/uv/"
}

$PythonVersion = (Get-Content (Join-Path $RepoRoot ".python-version") -Raw).Trim()
if (-not $PythonVersion) {
    throw ".python-version is empty"
}

$env:UV_CACHE_DIR = if ($env:UV_CACHE_DIR) { $env:UV_CACHE_DIR } else { Join-Path $RepoRoot ".uv-cache" }
$env:UV_PYTHON_INSTALL_DIR = if ($env:UV_PYTHON_INSTALL_DIR) { $env:UV_PYTHON_INSTALL_DIR } else { Join-Path $RepoRoot ".uv-python" }

Write-Host "Repository: $RepoRoot"
Write-Host "uv: $(uv --version)"
Write-Host "Python: $PythonVersion"
Write-Host "UV_CACHE_DIR: $env:UV_CACHE_DIR"
Write-Host "UV_PYTHON_INSTALL_DIR: $env:UV_PYTHON_INSTALL_DIR"

uv python install $PythonVersion

$SyncArgs = @("sync", "--all-groups")
if (-not $AllowLockUpdate -and $env:CODEX_UV_ALLOW_LOCK_UPDATE -ne "1") {
    $SyncArgs += "--frozen"
}

uv @SyncArgs
uv run python --version
uv run python -c "import sys; print(sys.executable)"

if ($RunChecks -or $env:CODEX_RUN_CHECKS -eq "1") {
    uv run pytest -q
}
