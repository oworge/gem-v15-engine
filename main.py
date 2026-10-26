import json
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="GEM V15.0 Engine")

# --- ACCURATE DAILY FIXTURES (26 OCT - 28 OCT 2026) ---
FIXTURES_DATA = [
    {"leg": 1, "date": "2026-10-26", "match": "Sevilla vs. Osasuna", "selection": "Sevilla Win or Draw (1X)", "odds": 1.25, "time": "20:00 GMT", "status": "UPCOMING"},
    {"leg": 2, "date": "2026-10-26", "match": "Galatasaray vs. Fenerbahce", "selection": "Over 1.5 Goals", "odds": 1.30, "time": "18:30 GMT", "status": "UPCOMING"},
    {"leg": 3, "date": "2026-10-26", "match": "Santa Clara vs. Benfica", "selection": "Benfica Win", "odds": 1.36, "time": "18:45 GMT", "status": "UPCOMING"},
    {"leg": 4, "date": "2026-10-27", "match": "Fleetwood vs. Arsenal", "selection": "Arsenal Win", "odds": 1.18, "time": "19:45 GMT", "status": "UPCOMING"},
    {"leg": 5, "date": "2026-10-27", "match": "Sabah vs. Borussia Dortmund", "selection": "Over 2.5 Goals", "odds": 1.40, "time": "17:45 GMT", "status": "UPCOMING"},
    {"leg": 6, "date": "2026-10-27", "match": "PSG vs. Barcelona", "selection": "Over 1.5 Goals", "odds": 1.22, "time": "20:00 GMT", "status": "UPCOMING"},
    {"leg": 7, "date": "2026-10-28", "match": "Liverpool vs. Chelsea", "selection": "Over 1.5 Goals", "odds": 1.24, "time": "19:45 GMT", "status": "UPCOMING"},
    {"leg": 8, "date": "2026-10-28", "match": "Manchester City vs. Brighton", "selection": "Manchester City Win", "odds": 1.32, "time": "19:45 GMT", "status": "UPCOMING"},
    {"leg": 9, "date": "2026-10-28", "match": "Bournemouth vs. Aston Villa", "selection": "Both Teams to Score", "odds": 1.50, "time": "19:45 GMT", "status": "UPCOMING"}
]

json_fixtures = json.dumps(FIXTURES_DATA)

HTML_CONTENT = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GEM V15.0 Engine</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }}
        .container {{ max-width: 950px; margin: 0 auto; }}
        h1 {{ color: #38bdf8; text-align: center; margin-bottom: 25px; }}
        .card {{ background: #1e293b; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3); }}
        .tier-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin-bottom: 20px; }}
        .tier-card {{ background: #334155; padding: 15px; border-radius: 6px; border-left: 4px solid #38bdf8; }}
        .tier-card h3 {{ margin-top: 0; color: #38bdf8; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #475569; }}
        th {{ background: #334155; color: #94a3b8; }}
        input[type="number"] {{ background: #0f172a; border: 1px solid #475569; color: #fff; padding: 8px; border-radius: 4px; width: 100px; font-size: 16px; }}
        .status {{ color: #4ade80; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>9-Leg Tactical Football Accumulator Pipeline</h1>
        
        <div class="card">
            <label><strong>Base Stake (£):</strong> </label>
            <input type="number" id="baseStake" value="10" min="1" oninput="calculateReturns()">
        </div>

        <div class="tier-grid">
            <div class="tier-card">
                <h3>3-Fold Tier</h3>
                <p>Combined Odds: <strong id="odds3">--</strong></p>
                <p>Est. Return: <strong id="return3">--</strong></p>
            </div>
            <div class="tier-card">
                <h3>6-Fold Tier</h3>
                <p>Combined Odds: <strong id="odds6">--</strong></p>
                <p>Est. Return: <strong id="return6">--</strong></p>
            </div>
            <div class="tier-card">
                <h3>9-Fold Tier</h3>
                <p>Combined Odds: <strong id="odds9">--</strong></p>
                <p>Est. Return: <strong id="return9">--</strong></p>
            </div>
        </div>

        <div class="card">
            <h2>Active 9-Leg Slate</h2>
            <div id="slateContainer">Loading fixtures...</div>
        </div>
    </div>

    <script>
        const data = {json_fixtures};

        function renderTable() {{
            let html = '<table><thead><tr><th>Leg</th><th>Date</th><th>Match</th><th>Selection</th><th>Odds</th><th>Time</th><th>Status</th></tr></thead><tbody>';
            data.forEach(f => {{
                html += `<tr>
                    <td>${{f.leg}}</td>
                    <td>${{f.date}}</td>
                    <td>${{f.match}}</td>
                    <td><strong>${{f.selection}}</strong></td>
                    <td>${{f.odds.toFixed(2)}}</td>
                    <td>${{f.time}}</td>
                    <td class="status">${{f.status}}</td>
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