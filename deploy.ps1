param([string]$Message = "chore: automated GEM engine update")
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
py -m py_compile app.py learner.py tests\test_clv_summary.py
py check_vetting_gate.py
py tests\test_clv_summary.py
git add -A
if (git diff --cached --quiet) {
    Write-Host "No changes to commit."
} else {
    git commit -m $Message
    git push origin main
}
