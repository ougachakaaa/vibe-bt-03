[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Set-Location $RepoRoot

$env:UV_CACHE_DIR = if ($env:UV_CACHE_DIR) { $env:UV_CACHE_DIR } else { Join-Path $RepoRoot ".uv-cache" }
$env:UV_PYTHON_INSTALL_DIR = if ($env:UV_PYTHON_INSTALL_DIR) { $env:UV_PYTHON_INSTALL_DIR } else { Join-Path $RepoRoot ".uv-python" }

uv run python -m compileall -q src tests
uv run pytest -q
