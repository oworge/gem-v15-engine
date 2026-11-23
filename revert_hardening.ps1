# ==========================================================
# gem-v15-live — Revert to Last Backup
# ==========================================================
# Usage: .\revert_hardening.ps1
# Restores app.py and learner.py from most recent backup
# ==========================================================

$ErrorActionPreference = "Stop"

if (-not (Test-Path ".\.latest_backup")) {
    Write-Host "❌ No backup record found — check backup folders manually" -ForegroundColor Red
    exit 1
}

$BACKUP_DIR = Get-Content ".\.latest_backup" -Encoding utf8
if (-not (Test-Path $BACKUP_DIR)) {
    Write-Host "❌ Backup folder missing: $BACKUP_DIR" -ForegroundColor Red
    exit 1
}

Write-Host "`n⚠️  WARNING — This will overwrite:" -ForegroundColor Yellow
Write-Host "   app.py ← $BACKUP_DIR\app.py.bak"
Write-Host "   learner.py ← $BACKUP_DIR\learner.py.bak"

$confirm = Read-Host "`nType YES to confirm revert"
if ($confirm -ne "YES") {
    Write-Host "Cancelled — no changes made." -ForegroundColor Cyan
    exit 0
}

Copy-Item "$BACKUP_DIR\app.py.bak" "app.py" -Force
Copy-Item "$BACKUP_DIR\learner.py.bak" "learner.py" -Force

Write-Host "`n✅ Reverted successfully!" -ForegroundColor Green
Write-Host "Restored from: $BACKUP_DIR`n"

# Quick verification
python -m py_compile app.py learner.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Syntax check after revert: PASS`n" -ForegroundColor Green
} else {
    Write-Host "⚠️ Syntax warning after revert — check manually`n" -ForegroundColor Yellow
}
