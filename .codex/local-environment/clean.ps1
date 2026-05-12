[CmdletBinding(SupportsShouldProcess = $true)]
param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Set-Location $RepoRoot

function Remove-RepoPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    $FullPath = [System.IO.Path]::GetFullPath((Join-Path $RepoRoot $Path))
    $RootWithSeparator = $RepoRoot.TrimEnd('\') + '\'

    if (-not ($FullPath.Equals($RepoRoot, [System.StringComparison]::OrdinalIgnoreCase) -or
            $FullPath.StartsWith($RootWithSeparator, [System.StringComparison]::OrdinalIgnoreCase))) {
        throw "Refusing to remove path outside repository: $FullPath"
    }

    if (Test-Path -LiteralPath $FullPath) {
        if ($PSCmdlet.ShouldProcess($FullPath, "Remove")) {
            Remove-Item -LiteralPath $FullPath -Recurse -Force
            Write-Host "Removed $Path"
        }
    }
}

$Paths = @(
    ".venv",
    ".uv-cache",
    ".uv-python",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "build",
    "dist"
)

foreach ($Path in $Paths) {
    Remove-RepoPath $Path
}

Get-ChildItem -Path $RepoRoot -Recurse -Force -Directory -Filter "__pycache__" |
    ForEach-Object {
        if ($PSCmdlet.ShouldProcess($_.FullName, "Remove")) {
            Remove-Item -LiteralPath $_.FullName -Recurse -Force
            Write-Host "Removed $($_.FullName.Substring($RepoRoot.Length + 1))"
        }
    }

Get-ChildItem -Path $RepoRoot -Force -Directory -Filter "*.egg-info" |
    ForEach-Object {
        if ($PSCmdlet.ShouldProcess($_.FullName, "Remove")) {
            Remove-Item -LiteralPath $_.FullName -Recurse -Force
            Write-Host "Removed $($_.Name)"
        }
    }
