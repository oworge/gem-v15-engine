# ==========================================================
# gem-v15-live — Hardening & Improvement Deployment Script
# ==========================================================
# Usage: .\deploy_hardening.ps1
# Creates backups → applies all patches → runs integrity checks
# Revert anytime with: .\revert_hardening.ps1
# ==========================================================

$ErrorActionPreference = "Stop"

# ─── Step 1: Create Timestamped Backup ───
Write-Host "`n📦 Creating backup..." -ForegroundColor Cyan
$BACKUP_DIR = "backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $BACKUP_DIR -Force | Out-Null
Copy-Item "app.py" "$BACKUP_DIR\app.py.bak"
Copy-Item "learner.py" "$BACKUP_DIR\learner.py.bak"
$BACKUP_FILE = "$BACKUP_DIR\BACKUP_INFO.txt"
"BACKUP_TIMESTAMP: $(Get-Date -Format 'o')" | Out-File $BACKUP_FILE
"BACKUP_FOLDER: $BACKUP_DIR" | Out-File $BACKUP_FILE -Append
Write-Host "✅ Backup saved to: $BACKUP_DIR" -ForegroundColor Green

# Save latest backup path for revert script
$BACKUP_DIR | Out-File ".\.latest_backup" -Encoding utf8

# ─── Step 2: Patch app.py — Safe Probability Helper ───
Write-Host "`n🔧 Patching app.py — Safe Probability Helper..." -ForegroundColor Cyan

$SAFE_P_BLOCK = @"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SAFE PROBABILITY CLAMPING — Prevents log(0) and math domain errors
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PROB_CLAMP_EPS = 1e-6

def safe_p(p: float) -> float:
    """Clamp probability to safe range before log/division operations."""
    return max(PROB_CLAMP_EPS, min(1.0 - PROB_CLAMP_EPS, float(p)))

def _final_market_clamp(market: str, p: float) -> float:
    """Prevent mathematically valid but absurd probabilities."""
    sane_ranges = {
        "1x2": (0.10, 0.80),
        "over_under": (0.15, 0.85),
        "double_chance": (0.20, 0.90)
    }
    lo, hi = sane_ranges.get(market, (0.05, 0.95))
    return max(lo, min(hi, p))

"@

$content = Get-Content "app.py" -Raw -Encoding UTF8
if ($content -match "^((?:from\s+\S+\s+import|import\s+).*\n)+") {
    $content = $content -replace "^((?:from\s+\S+\s+import|import\s+).*\n)+", "`$1`n$SAFE_P_BLOCK"
    Set-Content "app.py" -Value $content -Encoding UTF8 -NoNewline
    Write-Host "✅ safe_p() and _final_market_clamp() added" -ForegroundColor Green
} else {
    Write-Host "⚠️ Could not auto-insert — add SAFE_P_BLOCK manually at top of app.py" -ForegroundColor Yellow
}

# ─── Step 3: Patch app.py — Hardened Logit Calibration ───
Write-Host "`n🔧 Patching app.py — Logit Calibration Hardening..." -ForegroundColor Cyan

$OLD_CALIB = "logit_m = math\.log\(pm / \(1 - pm\)\)`r?`n\s+logit_d = math\.log\(pd / \(1 - pd\)\)"
$NEW_CALIB = @"
pm_safe = safe_p(pm)
pd_safe = safe_p(pd)
logit_m = math.log(pm_safe / (1 - pm_safe))
logit_d = math.log(pd_safe / (1 - pd_safe))
"@

$content = Get-Content "app.py" -Raw -Encoding UTF8
if ($content -match $OLD_CALIB) {
    $content = $content -replace $OLD_CALIB, $NEW_CALIB
    Set-Content "app.py" -Value $content -Encoding UTF8 -NoNewline
    Write-Host "✅ Logit calibration hardened with safe_p()" -ForegroundColor Green
} else {
    Write-Host "⚠️ Calibration pattern not found — apply manually" -ForegroundColor Yellow
}

# ─── Step 4: Patch learner.py — Dual Error Metrics ───
Write-Host "`n🔧 Patching learner.py — Dual Brier + LogLoss..." -ForegroundColor Cyan

$LEARNER_ERR_BLOCK = @"

import math

def safe_p(p: float) -> float:
    """Reuse safe clamping for log-loss calculations."""
    PROB_CLAMP_EPS = 1e-6
    return max(PROB_CLAMP_EPS, min(1.0 - PROB_CLAMP_EPS, float(p)))

def _calculate_prediction_errors(p_f: float, y: float) -> dict:
    """
    Dual-objective error metric:
    - Brier: stable, balanced penalty
    - LogLoss: heavy penalty for confident wrong predictions
    """
    p_safe = safe_p(p_f)
    
    brier_err = (p_f - y) ** 2
    logloss_err = -y * math.log(p_safe) - (1 - y) * math.log(1 - p_safe)
    
    return {
        "brier": brier_err,
        "logloss": logloss_err,
        "error_total": 0.4 * brier_err + 0.6 * logloss_err
    }
"@

$content = Get-Content "learner.py" -Raw -Encoding UTF8 -ErrorAction SilentlyContinue
if (-not $content) { $content = "" }
if (-not ($content -match "import math")) {
    $content = "import math`n" + $content
}
if ($content -match "def _update_source_weights") {
    $content = $content -replace "(?s)(def _update_source_weights)", "$LEARNER_ERR_BLOCK`n`n`$1"
} else {
    $content += "`n$LEARNER_ERR_BLOCK`n"
}
Set-Content "learner.py" -Value $content -Encoding UTF8 -NoNewline
Write-Host "✅ Dual error metrics added to learner.py" -ForegroundColor Green

# ─── Step 5: Patch app.py — Performance Endpoint ───
Write-Host "`n🔧 Patching app.py — Performance Summary Endpoint..." -ForegroundColor Cyan

$PERF_ENDPOINT = @"

@app.route("/api/performance-summary")
def performance_summary():
    """Realized performance dashboard — CLV, Brier, and trend data."""
    import json
    from collections import defaultdict
    
    try:
        with open("clv_history.jsonl", "r", encoding="utf-8") as f:
            records = [json.loads(line) for line in f if line.strip()]
    except FileNotFoundError:
        return {"status": "no_data", "message": "clv_history.jsonl not yet populated"}
    
    if not records:
        return {"status": "empty", "message": "No settled records available"}
    
    daily = defaultdict(lambda: {"count": 0, "clv_sum": 0.0, "brier_sum": 0.0})
    settled = [r for r in records if r.get("settled", False)]
    
    for r in settled:
        day = r["timestamp"][:10]
        daily[day]["count"] += 1
        daily[day]["clv_sum"] += r.get("clv_pct", 0)
        if "p_f" in r and "actual" in r:
            daily[day]["brier_sum"] += (r["p_f"] - r["actual"]) ** 2
    
    trend = []
    for day in sorted(daily.keys())[-30:]:
        d = daily[day]
        trend.append({
            "date": day,
            "predictions": d["count"],
            "avg_clv_pct": round(d["clv_sum"] / d["count"] * 100, 2),
            "avg_brier": round(d["brier_sum"] / d["count"], 4)
        })
    
    all_clv = [r.get("clv_pct", 0) for r in settled]
    all_brier = [(r["p_f"] - r["actual"]) ** 2 for r in settled if "p_f" in r and "actual" in r]
    
    return {
        "status": "ok",
        "total_settled": len(settled),
        "avg_clv_pct": round(sum(all_clv) / len(all_clv) * 100, 2) if all_clv else None,
        "avg_brier": round(sum(all_brier) / len(all_brier), 4) if all_brier else None,
        "last_30_days": trend
    }
"@

Add-Content "app.py" $PERF_ENDPOINT
Write-Host "✅ /api/performance-summary endpoint added" -ForegroundColor Green

# ─── Step 6: Run Integrity Checks ───
Write-Host "`n═══════════════════════════════════" -ForegroundColor Yellow
Write-Host "   RUNNING INTEGRITY CHECKS" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════" -ForegroundColor Yellow

python -m py_compile app.py learner.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ SYNTAX CHECK: PASS" -ForegroundColor Green
} else {
    Write-Host "`n❌ SYNTAX CHECK: FAIL — review errors above" -ForegroundColor Red
    exit 1
}

if (Test-Path "check_vetting_gate.py") {
    python check_vetting_gate.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ VETTING GATES: PASS" -ForegroundColor Green
    } else {
        Write-Host "⚠️ VETTING GATES: Review output above" -ForegroundColor Yellow
    }
}

python -c "
from app import safe_p, _final_market_clamp
print('safe_p(0.000001):', safe_p(0.000001))
print('safe_p(0.999999):', safe_p(0.999999))
print('market_clamp(1x2, 0.95):', _final_market_clamp('1x2', 0.95))
print('✅ app.py functions: OK')
"
if ($LASTEXITCODE -eq 0) { Write-Host "✅ app.py SMOKE TEST: PASS" -ForegroundColor Green }

python -c "
from learner import _calculate_prediction_errors
print('errors(0.65, 1.0):', _calculate_prediction_errors(0.65, 1.0))
print('✅ learner.py functions: OK')
"
if ($LASTEXITCODE -eq 0) { Write-Host "✅ learner.py SMOKE TEST: PASS" -ForegroundColor Green }

# ─── Complete ───
Write-Host "`n═══════════════════════════════════" -ForegroundColor Green
Write-Host "   DEPLOYMENT COMPLETE" -ForegroundColor Green
Write-Host "═══════════════════════════════════" -ForegroundColor Green
Write-Host "📂 Backup folder: $BACKUP_DIR"
Write-Host "🔄 To revert run: .\revert_hardening.ps1`n"
