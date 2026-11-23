$root = "C:\Users\georg\gem-v15-live"
$tag = '<div id="bookie-beater-panel" data-tab-panel="bookie-beater" style="margin:16px 0;"></div>' + "`r`n" + '<script src="/static/bookie_beater_tab.js?v=2"></script>' + "`r`n" + '</body>'
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)

foreach ($rel in @("templates\index.html", "index.html")) {
    $p = Join-Path $root $rel
    if (Test-Path $p) {
        $txt = [IO.File]::ReadAllText($p)
        if ($txt -notmatch "bookie_beater_tab\.js" -and $txt -match "</body>") {
            $txt = $txt.Replace("</body>", $tag)
            [IO.File]::WriteAllText($p, $txt, $utf8NoBom)
            Write-Host "Updated $rel" -ForegroundColor Green
        }
    }
}

$jsPath = Join-Path $root "static\bookie_beater_tab.js"
if (Test-Path $jsPath) {
    $js = [IO.File]::ReadAllText($jsPath)
    if ($js -notmatch "fbBtn") {
        $btnCode = 'if(!document.getElementById("tab-bookie-beater")){var fbBtn=document.createElement("button");fbBtn.id="tab-bookie-beater";fbBtn.textContent="Bookie Beater";fbBtn.style.cssText="padding:8px 14px;margin:8px 0;font-weight:600;cursor:pointer;";(document.body||document.documentElement).prepend(fbBtn);fbBtn.addEventListener("click",function(){var el=document.getElementById("bookie-beater-panel");if(el)el.style.display="block";if(typeof loadSlip==="function")loadSlip();});}'
        $js = $js -replace '\}\)\(\);\s*$', ($btnCode + '})();')
        [IO.File]::WriteAllText($jsPath, $js, $utf8NoBom)
        Write-Host "Added fallback Bookie Beater button" -ForegroundColor Green
    }
}
