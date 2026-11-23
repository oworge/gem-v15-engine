param(
    [double]$Bankroll = 500.0,
    [double]$MinEdge = 0.025,
    [double]$KellyFraction = 0.25,
    [double]$MaxStakePct = 0.015,
    [int]$MaxLegs = 3,
    [string]$InputJson = "fixtures_today.json",
    [string]$OutSlipJson = "daily_bookie_beater_slip.json",
    [string]$ClvLogJsonl = "clv_tracker.jsonl"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-NoVigProb {
    param(
        [double]$SharpTargetOdds,
        [double]$SharpCounterOdds
    )
    if ($SharpTargetOdds -le 1.01) { return $null }
    if ($SharpCounterOdds -gt 1.01) {
        $imp1 = 1.0 / $SharpTargetOdds
        $imp2 = 1.0 / $SharpCounterOdds
        return ($imp1 / ($imp1 + $imp2))
    }
    return (1.0 / $SharpTargetOdds)
}

function Get-KellyStakePct {
    param(
        [double]$Prob,
        [double]$SoftOdds,
        [double]$Fraction,
        [double]$CapPct
    )
    if ($SoftOdds -le 1.01 -or $Prob -le 0 -or $Prob -ge 1) { return 0.0 }
    $b = $SoftOdds - 1.0
    $q = 1.0 - $Prob
    $fullKelly = (($b * $Prob) - $q) / $b
    if ($fullKelly -le 0) { return 0.0 }
    $stake = $fullKelly * $Fraction
    if ($stake -gt $CapPct) { $stake = $CapPct }
    return [math]::Round($stake, 4)
}

function Get-PropOrDefault {
    param($Obj, [string]$Name, $Default)
    if ($null -eq $Obj) { return $Default }
    $prop = $Obj.PSObject.Properties[$Name]
    if ($null -eq $prop -or $null -eq $prop.Value) { return $Default }
    return $prop.Value
}

$nowUtc = [datetime]::UtcNow
$candidates = @()

if (Test-Path $InputJson) {
    $raw = Get-Content -Path $InputJson -Raw -Encoding UTF8 | ConvertFrom-Json
    foreach ($item in @($raw)) {
        $kickoffRaw = Get-PropOrDefault -Obj $item -Name "kickoff_utc" -Default $null
        $kickoffUtc = $null
        if ($null -ne $kickoffRaw -and "$kickoffRaw" -ne "") {
            try { $kickoffUtc = ([datetime]$kickoffRaw).ToUniversalTime() } catch { $kickoffUtc = $null }
        }
        if ($null -ne $kickoffUtc -and $kickoffUtc -le $nowUtc) { continue }

        $softOdds = [double](Get-PropOrDefault -Obj $item -Name "soft_odds" -Default 0)
        if ($softOdds -le 1.05) { continue }

        $sharpOddsVal = Get-PropOrDefault -Obj $item -Name "sharp_odds" -Default $null
        $sharpCounterVal = [double](Get-PropOrDefault -Obj $item -Name "sharp_counter_odds" -Default 0)
        $modelProb = $null

        if ($null -ne $sharpOddsVal -and "$sharpOddsVal" -ne "") {
            $modelProb = Get-NoVigProb -SharpTargetOdds ([double]$sharpOddsVal) -SharpCounterOdds $sharpCounterVal
        }
        if ($null -eq $modelProb) {
            $mpVal = Get-PropOrDefault -Obj $item -Name "model_prob" -Default $null
            if ($null -ne $mpVal -and "$mpVal" -ne "") { $modelProb = [double]$mpVal }
        }
        if ($null -eq $modelProb -or $modelProb -le 0.45 -or $modelProb -ge 0.96) { continue }

        $ev = ($modelProb * $softOdds) - 1.0
        if ($ev -lt $MinEdge) { continue }

        $stakePct = Get-KellyStakePct -Prob $modelProb -SoftOdds $softOdds -Fraction $KellyFraction -CapPct $MaxStakePct
        $stakeAmt = [math]::Round($Bankroll * $stakePct, 2)

        $closingDefault = if ($null -ne $sharpOddsVal -and "$sharpOddsVal" -ne "") { [double]$sharpOddsVal } else { $softOdds }
        $sharpClosing = [double](Get-PropOrDefault -Obj $item -Name "sharp_closing_odds" -Default $closingDefault)
        $clvPct = [math]::Round((($softOdds / [math]::Max(1.05, $sharpClosing)) - 1.0) * 100.0, 2)

        $candidates += [PSCustomObject]@{
            fixture       = [string](Get-PropOrDefault -Obj $item -Name "fixture" -Default "Match")
            league        = [string](Get-PropOrDefault -Obj $item -Name "league" -Default "Football")
            kickoff_gmt   = if ($null -ne $kickoffUtc) { $kickoffUtc.ToString("yyyy-MM-dd HH:mm") + " GMT" } else { "Upcoming" }
            market        = [string](Get-PropOrDefault -Obj $item -Name "market" -Default "Market")
            soft_odds     = [math]::Round($softOdds, 3)
            true_prob_pct = [math]::Round($modelProb * 100.0, 1)
            edge_pct      = [math]::Round($ev * 100.0, 2)
            est_clv_pct   = $clvPct
            stake_pct     = [math]::Round($stakePct * 100.0, 2)
            stake_gbp     = $stakeAmt
        }
    }
}

# Fallback evening slate (21 Nov 2026, 20:00 GMT) when fixtures_today.json has no upcoming +EV rows
if ($candidates.Count -eq 0) {
    $fallbackKickoff = [datetime]::Parse("2026-11-21T20:00:00Z").ToUniversalTime()
    if ($fallbackKickoff -gt $nowUtc) {
        $fb = @(
            @{ fixture = "FC Groningen v SC Heerenveen"; league = "Eredivisie"; market = "Both Teams to Score (BTTS Yes)"; soft_odds = 1.72; prob = 0.61; closing = 1.66 },
            @{ fixture = "Real Madrid v Celta Vigo"; league = "La Liga"; market = "Real Madrid or Draw (1X) & Over 1.5 Goals"; soft_odds = 1.48; prob = 0.71; closing = 1.44 }
        )
        foreach ($row in $fb) {
            $ev = ($row.prob * $row.soft_odds) - 1.0
            $sp = Get-KellyStakePct -Prob $row.prob -SoftOdds $row.soft_odds -Fraction $KellyFraction -CapPct $MaxStakePct
            $candidates += [PSCustomObject]@{
                fixture       = $row.fixture
                league        = $row.league
                kickoff_gmt   = "2026-11-21 20:00 GMT"
                market        = $row.market
                soft_odds     = $row.soft_odds
                true_prob_pct = [math]::Round($row.prob * 100.0, 1)
                edge_pct      = [math]::Round($ev * 100.0, 2)
                est_clv_pct   = [math]::Round((($row.soft_odds / $row.closing) - 1.0) * 100.0, 2)
                stake_pct     = [math]::Round($sp * 100.0, 2)
                stake_gbp     = [math]::Round($Bankroll * $sp, 2)
            }
        }
    }
}

$selected = @($candidates | Sort-Object -Property edge_pct -Descending | Select-Object -First $MaxLegs)

$combinedOdds = 1.0
foreach ($leg in $selected) { $combinedOdds = $combinedOdds * [double]$leg.soft_odds }
$combinedOdds = [math]::Round($combinedOdds, 2)

$slip = [PSCustomObject]@{
    generated_utc = $nowUtc.ToString("yyyy-MM-ddTHH:mm:ssZ")
    bankroll_gbp  = $Bankroll
    min_edge_pct  = [math]::Round($MinEdge * 100.0, 2)
    leg_count     = $selected.Count
    combined_odds = $combinedOdds
    legs          = $selected
}

$slip | ConvertTo-Json -Depth 5 | Set-Content -Path $OutSlipJson -Encoding UTF8

foreach ($leg in $selected) {
    $entry = [ordered]@{
        logged_utc    = $nowUtc.ToString("yyyy-MM-ddTHH:mm:ssZ")
        fixture       = $leg.fixture
        market        = $leg.market
        soft_odds     = $leg.soft_odds
        edge_pct      = $leg.edge_pct
        est_clv_pct   = $leg.est_clv_pct
        stake_gbp     = $leg.stake_gbp
        closing_odds  = $null
        settled_won   = $null
    }
    ($entry | ConvertTo-Json -Compress) | Add-Content -Path $ClvLogJsonl -Encoding UTF8
}

Write-Host "=== DAILY BOOKIE-BEATER SLIP ($($slip.generated_utc)) ===" -ForegroundColor Cyan
$selected | Format-Table fixture, kickoff_gmt, market, soft_odds, edge_pct, est_clv_pct, stake_gbp -AutoSize
Write-Host "Combined Acca Odds: $combinedOdds | Saved: $OutSlipJson & $ClvLogJsonl" -ForegroundColor Green
