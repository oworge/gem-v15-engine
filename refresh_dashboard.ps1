# ==========================================================
# gem-v15-live — Simple Dashboard Refresh
# ==========================================================
$ErrorActionPreference = "Continue"
Set-Location "C:\Users\georg\gem-v15-live"

Write-Host "`n🔄 Checking files..." -ForegroundColor Cyan

# Check core files exist
if (-not (Test-Path "app.py")) {
    Write-Host "❌ app.py not found — check folder path" -ForegroundColor Red
    exit 1
}
if (-not (Test-Path "learner.py")) {
    Write-Host "❌ learner.py not found" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Core files found" -ForegroundColor Green

# Syntax check first
Write-Host "`n🔍 Syntax check..." -ForegroundColor Cyan
python -m py_compile app.py learner.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Syntax error — fix above before continuing" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Syntax OK" -ForegroundColor Green

# List what files exist
Write-Host "`n📂 Files in project:" -ForegroundColor Cyan
Get-ChildItem *.py | Select-Object Name

Write-Host "`n✅ Ready — your engine is intact!" -ForegroundColor Green
Write-Host "Note: Daily picks will populate once your fixture feed runs successfully" -ForegroundColor Yellow
