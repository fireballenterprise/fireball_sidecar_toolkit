# Windows setup — mirrors setup.sh (macOS/Linux). Run from the repo root in PowerShell:
#   .\setup.ps1

$ErrorActionPreference = "Stop"

function Install-Tools {
    Write-Host "INFO: Installing Tools (uv, user-local install — no admin required)"
    if (Get-Command uv -ErrorAction SilentlyContinue) {
        Write-Host "INFO: uv already installed"
    } else {
        irm https://astral.sh/uv/install.ps1 | iex
    }
}

function Setup-PythonEnv {
    Write-Host "`nINFO: Creating Python Virtual Environment"
    uv venv .venv --python 3.14 --clear

    Write-Host "`nINFO: Activating Python Virtual Environment"
    & .\.venv\Scripts\Activate.ps1

    Write-Host "`nINFO: Installing Libraries"
    uv sync
    Write-Host "INFO: Python Version: $(python --version)"
    Write-Host "INFO: uv Version: $(uv --version)"
}

function Configure-Properties {
    # Everything past this point is Python's job, not PowerShell's.
    Write-Host "`nINFO: Configuring properties.yml for this machine"
    uv run --no-sync invoke setup.properties
}

Install-Tools
Setup-PythonEnv
Configure-Properties
