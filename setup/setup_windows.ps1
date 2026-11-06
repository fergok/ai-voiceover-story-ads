# One-time setup on Windows. In PowerShell, from the repo folder:
#   powershell -ExecutionPolicy Bypass -File setup\setup_windows.ps1
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
$py = Get-Command py -ErrorAction SilentlyContinue
if ($py) { $python = "py"; $pyargs = @("-3") } else {
  $py = Get-Command python -ErrorAction SilentlyContinue
  if (-not $py) { Write-Host "Python isn't installed. Get it from https://www.python.org/downloads/ (tick 'Add python.exe to PATH') and run this again."; exit 1 }
  $python = "python"; $pyargs = @()
}
& $python @pyargs -m venv .venv
& .venv\Scripts\python.exe -m pip install --upgrade pip -q
& .venv\Scripts\python.exe -m pip install -r requirements.txt -q
& .venv\Scripts\python.exe tools\doctor.py
