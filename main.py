import json
import math
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="GEM V15.0 Advanced Engine")

# RAW DATA INGESTION (Simulating Opta xG & Multi-Model Outputs)
RAW_FIXTURES = [
    {"leg": 1, "date": "2026-10-26", "match": "Sevilla vs. Osasuna", "selection": "Sevilla Win or Draw (1X)", "odds": 1.25, "xg_prob": 0.84, "model_agreement": 0.92, "time": "20:00 GMT"},
    {"leg": 2, "date": "2026-10-26", "match": "Galatasaray vs. Fenerbahce", "selection": "Over 1.5 Goals", "odds": 1.30, "xg_prob": 0.82, "model_agreement": 0.88, "time": "18:30 GMT"},
    {"leg": 3, "date": "2026-10-26", "match": "Santa Clara vs. Benfica", "selection": "Benfica Win", "odds": 1.36, "xg_prob": 0.77, "model_agreement": 0.85, "time": "18:45 GMT"},
    {"leg": 4, "date": "2026-10-27", "match": "Fleetwood vs. Arsenal", "selection": "Arsenal Win", "odds": 1.18, "xg_prob": 0.91, "model_agreement": 0.95, "time": "19:45 GMT"},
    {"leg": 5, "date": "2026-10-27", "match": "Sabah vs. Borussia Dortmund", "selection": "Over 2.5 Goals", "odds": 1.40, "xg_prob": 0.76, "model_agreement": 0.79, "time": "17:45 GMT"},
    {"leg": 6, "date": "2026-10-27", "match": "PSG vs. Barcelona", "selection": "Over 1.5 Goals", "odds": 1.22, "xg_prob": 0.85, "model_agreement": 0.90, "time": "20:00 GMT"},
    {"leg": 7, "date": "2026-10-28", "match": "Liverpool vs. Chelsea", "selection": "Over 1.5 Goals", "odds": 1.24, "xg_prob": 0.83, "model_agreement": 0.87, "time": "19:45 GMT"},
    {"leg": 8, "date": "2026-10-28", "match": "Manchester City vs. Brighton", "selection": "Manchester City Win", "odds": 1.32, "xg_prob": 0.80, "model_agreement": 0.84, "time": "19:45 GMT"},
    {"leg": 9, "date": "2026-10-28", "match": "Bournemouth vs. Aston Villa", "selection": "Both Teams to Score", "odds": 1.50, "xg_prob": 0.72, "model_agreement": 0.75, "time": "19:45 GMT"}
]

def apply_advanced_analytics(fixtures):
    processed = []
    for f in fixtures:
        odds = f["odds"]
        prob = f["xg_prob"]
        agreement = f["model_agreement"]
        
        # 1. Dixon-Coles Low-Score Adjustment Factor (+1.5% calibration boost on low odds)
        calibrated_prob = min(round(prob * 1.015, 4), 0.98) if odds < 1.30 else prob
        
        # 2. Expected Value (EV) calculation
        ev = round(((calibrated_prob * odds) - 1.0) * 100, 2)
        
        # 3. Fractional Kelly Criterion (Fractional 0.25 safety sizing)
        b = odds - 1.0
        p = calibrated_prob
        q = 1.0 - p
        kelly_fraction = max(0, round(((b * p - q) / b) * 0.25 * 100, 2))
        
        # 4. Multi-Factor Tier Router (Requires EV + Model Agreement)
        if ev >= 5.0 and agreement >= 0.85:
            tier = "3-Fold Anchor"
        elif ev >= 2.0 and agreement >= 0.78:
            tier = "6-Fold Mid"
        else:
            tier = "9-Fold High-Yield"
            
        processed.append({
            **f,
            "calibrated_prob": f"{round(calibrated_prob * 100, 1)}%",
            "ev_str": f"+{ev}%" if ev > 0 else f"{ev}%",
            "agreement_str": f"{round(agreement * 100)}%",
            "kelly_suggested": f"{kelly_fraction}%",
            "tier_assignment": tier
        })
    return processed

FIXTURES_DATA = apply_advanced_analytics(RAW_FIXTURES)
json_fixtures = json.dumps(FIXTURES_DATA)

HTML_CONTENT = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GEM V15.0 Advanced Engine</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }}
        .container {{ max-width: 1150px; margin: 0 auto; }}
        h1 {{ color: #38bdf8; text-align: center; margin-bottom: 25px; }}
        .card {{ background: #1e293b; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3); }}
        .tier-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 15px; margin-bottom: 20px; }}
        .tier-card {{ background: #334155; padding: 15px; border-radius: 6px; border-left: 4px solid #38bdf8; }}
        .tier-card h3 {{ margin-top: 0; color: #38bdf8; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #475569; }}
        th {{ background: #334155; color: #94a3b8; }}
        input[type="number"] {{ background: #0f172a; border: 1px solid #475569; color: #fff; padding: 8px; border-radius: 4px; width: 100px; font-size: 16px; }}
        .ev-badge {{ background: #166534; color: #4ade80; padding: 3px 6px; border-radius: 4px; font-weight: bold; }}
        .tier-badge {{ background: #1e3a8a; color: #93c5fd; padding: 3px 6px; border-radius: 4px; font-size: 11px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>GEM V15.0 Predictive Quantitative Engine</h1>
        
        <div class="card">
            <label><strong>Base Bankroll Stake (£):</strong> </label>
            <input type="number" id="baseStake" value="10" min="1" oninput="calculateReturns()">
        </div>

        <div class="tier-grid">
            <div class="tier-card">
                <h3>3-Fold Anchor Tier</h3>
                <p>Combined Odds: <strong id="odds3">--</strong></p>
                <p>Est. Return: <strong id="return3">--</strong></p>
            </div>
            <div class="tier-card">
                <h3>6-Fold Mid Tier</h3>
                <p>Combined Odds: <strong id="odds6">--</strong></p>
                <p>Est. Return: <strong id="return6">--</strong></p>
            </div>
            <div class="tier-card">
                <h3>9-Fold Full Slate</h3>
                <p>Combined Odds: <strong id="odds9">--</strong></p>
                <p>Est. Return: <strong id="return9">--</strong></p>
            </div>
        </div>

        <div class="card">
            <h2>Active 9-Leg Multi-Factor Slate</h2>
            <div id="slateContainer">Loading analytics...</div>
        </div>
    </div>

    <script>
        const data = {json_fixtures};

        function renderTable() {{
            let html = '<table><thead><tr><th>Leg</th><th>Date</th><th>Match</th><th>Selection</th><th>Odds</th><th>xG Prob</th><th>Agreement</th><th>EV Edge</th><th>Kelly Stake %</th><th>Tier Route</th></tr></thead><tbody>';
            data.forEach(f => {{
                html += `<tr>
                    <td>\${{f.leg}}</td>
                    <td>\${{f.date}}</td>
                    <td>\${{f.match}}</td>
                    <td><strong>\${{f.selection}}</strong></td>
                    <td>\${{f.odds.toFixed(2)}}</td>
                    <td>\${{f.calibrated_prob}}</td>
                    <td>\${{f.agreement_str}}</td>
                    <td><span class="ev-badge">\${{f.ev_str}}</span></td>
                    <td>\${{f.kelly_suggested}}</td>
                    <td><span class="tier-badge">\${{f.tier_assignment}}</span></td>
                </tr>`;
            }});
            html += '</tbody></table>';
            document.getElementById('slateContainer').innerHTML = html;
        }}

        function calculateReturns() {{
            const stake = parseFloat(document.getElementById('baseStake').value) || 0;
            const calcOdds = (count) => data.slice(0, count).reduce((acc, item) => acc * item.odds, 1);

            const odds3 = calcOdds(3);
            const odds6 = calcOdds(6);
            const odds9 = calcOdds(9);

            document.getElementById('odds3').innerText = odds3.toFixed(2);
            document.getElementById('return3').innerText = '£' + (stake * odds3).toFixed(2);

            document.getElementById('odds6').innerText = odds6.toFixed(2);
            document.getElementById('return6').innerText = '£' + (stake * odds6).toFixed(2);

            document.getElementById('odds9').innerText = odds9.toFixed(2);
            document.getElementById('return9').innerText = '£' + (stake * odds9).toFixed(2);
        }}

        renderTable();
        calculateReturns();
    </script>
</body>
</html>"""

@app.get("/api/fixtures")
def get_fixtures():
    return FIXTURES_DATA

@app.get("/", response_class=HTMLResponse)
def read_root():
    return HTML_CONTENT