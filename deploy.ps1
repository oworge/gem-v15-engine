param([string]$Message = "chore: automated GEM engine update")
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
py -m py_compile app.py learner.py tests\test_clv_summary.py
if ($LASTEXITCODE -ne 0) { throw "py_compile failed" }
py check_vetting_gate.py
if ($LASTEXITCODE -ne 0) { throw "check_vetting_gate failed" }
py tests\test_clv_summary.py
if ($LASTEXITCODE -ne 0) { throw "test_clv_summary failed" }
git add -A
if (git diff --cached --quiet) {
    Write-Host "No changes to commit."
} else {
    git commit -m $Message
    git push origin main
}
