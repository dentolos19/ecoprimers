Set-Location "$PSScriptRoot/.."

Write-Host "Setting up virtual environment..."

if (-not (Test-Path ".venv")) {
    & py -m venv ".venv"
}

& .venv/Scripts/Activate.ps1
& pip install -r "requirements.txt" > $null