[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$repoRoot = $PSScriptRoot
$claudeDir = Join-Path $HOME ".claude"
$codexDir = Join-Path $HOME ".codex"

function Resolve-Uv {
    $command = Get-Command uv -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }

    Write-Host "uv was not found. Installing it with winget..."
    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if (-not $winget) {
        throw "winget is required to install uv. Install uv from https://docs.astral.sh/uv/ and rerun this script."
    }

    & winget install --id astral-sh.uv -e --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -ne 0) {
        throw "uv installation failed with exit code $LASTEXITCODE."
    }

    $candidates = @(
        (Join-Path $HOME ".local\bin\uv.exe"),
        (Join-Path $env:LOCALAPPDATA "Microsoft\WinGet\Links\uv.exe")
    )
    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) {
            return $candidate
        }
    }

    $command = Get-Command uv -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }

    throw "uv was installed but is not visible in this shell. Open a new PowerShell window and rerun the script."
}

Write-Host "Installing Claude configuration..."
New-Item -ItemType Directory -Force -Path $claudeDir | Out-Null
Copy-Item (Join-Path $repoRoot "CLAUDE.md") (Join-Path $claudeDir "CLAUDE.md") -Force
Copy-Item (Join-Path $repoRoot "settings.windows.json") (Join-Path $claudeDir "settings.json") -Force
Copy-Item (Join-Path $repoRoot "skills") $claudeDir -Recurse -Force

Write-Host "Installing shared skills for Codex..."
New-Item -ItemType Directory -Force -Path $codexDir | Out-Null
Copy-Item (Join-Path $repoRoot "skills") $codexDir -Recurse -Force

$uv = Resolve-Uv
Write-Host "Installing or upgrading Graphify..."
& $uv tool install --upgrade graphifyy
if ($LASTEXITCODE -ne 0) {
    throw "Graphify installation failed with exit code $LASTEXITCODE."
}

$toolBin = (& $uv tool dir --bin).Trim()
$graphify = Join-Path $toolBin "graphify.exe"
if (-not (Test-Path $graphify)) {
    throw "Graphify installed, but graphify.exe was not found in $toolBin."
}

Write-Host "Registering Graphify with Claude Code..."
& $graphify install --platform windows
if ($LASTEXITCODE -ne 0) {
    throw "Claude Graphify registration failed with exit code $LASTEXITCODE."
}

Write-Host "Registering Graphify with Codex..."
& $graphify install --platform codex
if ($LASTEXITCODE -ne 0) {
    throw "Codex Graphify registration failed with exit code $LASTEXITCODE."
}

$codex = Get-Command codex -ErrorAction SilentlyContinue
if ($codex) {
    Write-Host "Enabling Codex multi-agent support..."
    & $codex.Source features enable multi_agent
    if ($LASTEXITCODE -ne 0) {
        throw "Codex multi-agent configuration failed with exit code $LASTEXITCODE."
    }
}
else {
    Write-Warning "Codex is not on PATH. Graphify's Codex skill was installed, but run 'codex features enable multi_agent' after installing Codex."
}

Write-Host ""
Write-Host "Setup complete. Restart Claude Code and Codex."
Write-Host "Claude: /graphify ."
Write-Host "Codex:  `$graphify ."
