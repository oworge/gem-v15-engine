import json
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="GEM V15.0 Value Finder Engine")

ACCUMULATOR_SLATE = [
    {"leg": 1, "date": "2026-10-26", "match": "Sevilla vs. Osasuna", "selection": "Sevilla Win or Draw (1X)", "odds": 1.25, "model_prob": 0.84, "agreement": 0.92, "time": "20:00 GMT"},
    {"leg": 2, "date": "2026-10-26", "match": "Galatasaray vs. Fenerbahce", "selection": "Over 1.5 Goals", "odds": 1.30, "model_prob": 0.82, "agreement": 0.88, "time": "18:30 GMT"},
    {"leg": 3, "date": "2026-10-26", "match": "Santa Clara vs. Benfica", "selection": "Benfica Win", "odds": 1.36, "model_prob": 0.77, "agreement": 0.85, "time": "18:45 GMT"},
    {"leg": 4, "date": "2026-10-27", "match": "Fleetwood vs. Arsenal", "selection": "Arsenal Win", "odds": 1.18, "model_prob": 0.91, "agreement": 0.95, "time": "19:45 GMT"},
    {"leg": 5, "date": "2026-10-27", "match": "Sabah vs. Borussia Dortmund", "selection": "Over 2.5 Goals", "odds": 1.40, "model_prob": 0.76, "agreement": 0.79, "time": "17:45 GMT"},
    {"leg": 6, "date": "2026-10-27", "match": "PSG vs. Barcelona", "selection": "Over 1.5 Goals", "odds": 1.22, "model_prob": 0.85, "agreement": 0.90, "time": "20:00 GMT"},
    {"leg": 7, "date": "2026-10-28", "match": "Liverpool vs. Chelsea", "selection": "Over 1.5 Goals", "odds": 1.24, "model_prob": 0.83, "agreement": 0.87, "time": "19:45 GMT"},
    {"leg": 8, "date": "2026-10-28", "match": "Manchester City vs. Brighton", "selection": "Manchester City Win", "odds": 1.32, "model_prob": 0.80, "agreement": 0.84, "time": "19:45 GMT"},
    {"leg": 9, "date": "2026-10-28", "match": "Bournemouth vs. Aston Villa", "selection": "Both Teams to Score", "odds": 1.50, "model_prob": 0.72, "agreement": 0.75, "time": "19:45 GMT"}
]

GLOBAL_FIXTURE_POOL = [
    {"date": "2026-10-26", "league": "Brazil Serie A U20", "match": "Cruzeiro U20 vs. Atletico Mineiro U20", "selection": "Over 2.5 Goals", "odds": 1.57, "model_prob": 0.75, "time": "18:00 GMT"},
    {"date": "2026-10-26", "league": "La Liga", "match": "Sevilla vs. Osasuna", "selection": "Sevilla Win or Draw (1X)", "odds": 1.25, "model_prob": 0.85, "time": "20:00 GMT"},
    {"date": "2026-10-26", "league": "Super Lig", "match": "Galatasaray vs. Fenerbahce", "selection": "Over 1.5 Goals", "odds": 1.30, "model_prob": 0.82, "time": "18:30 GMT"},
    {"date": "2026-10-26", "league": "Romania Liga I", "match": "Sepsi OSK vs. U Craiova", "selection": "Away Win", "odds": 1.50, "model_prob": 0.715, "time": "18:00 GMT"},
    {"date": "2026-10-26", "league": "Argentina Liga Prof", "match": "Union Santa Fe vs. Estudiantes", "selection": "Double Chance (12)", "odds": 1.36, "model_prob": 0.77, "time": "22:00 GMT"},
    {"date": "2026-10-27", "league": "Serie A (Italy)", "match": "Torino vs. Como", "selection": "Como Win", "odds": 1.73, "model_prob": 0.64, "time": "19:45 GMT"},
    {"date": "2026-10-27", "league": "Serie B (Italy)", "match": "Ascoli vs. Sampdoria", "selection": "Ascoli Win", "odds": 2.28, "model_prob": 0.48, "time": "12:00 GMT"},
    {"date": "2026-10-27", "league": "EFL Cup", "match": "Fleetwood vs. Arsenal", "selection": "Arsenal Win", "odds": 1.18, "model_prob": 0.91, "time": "19:45 GMT"},
    {"date": "2026-10-27", "league": "Friendly", "match": "Sabah vs. Dortmund", "selection": "Over 2.5 Goals", "odds": 1.40, "model_prob": 0.76, "time": "17:45 GMT"},
    {"date": "2026-10-28", "league": "EFL Cup", "match": "Liverpool vs. Chelsea", "selection": "Over 1.5 Goals", "odds": 1.24, "model_prob": 0.83, "time": "19:45 GMT"},
    {"date": "2026-10-28", "league": "EFL Cup", "match": "Man City vs. Brighton", "selection": "Man City Win", "odds": 1.32, "model_prob": 0.80, "time": "19:45 GMT"},
    {"date": "2026-10-28", "league": "EFL Cup", "match": "Bournemouth vs. Aston Villa", "selection": "Both Teams to Score", "odds": 1.50, "model_prob": 0.72, "time": "19:45 GMT"}
]

def process_accumulator_slate(fixtures):
    processed = []
    for f in fixtures:
        odds = f["odds"]
        prob = f["model_prob"]
        ev = round(((prob * odds) - 1.0) * 100, 2)
        tier = "3-Fold Anchor" if ev >= 6.0 and prob >= 0.80 else ("6-Fold Mid" if ev >= 4.0 else "9-Fold High-Yield")
        processed.append({
            **f,
            "ev_str": f"+{ev}%" if ev > 0 else f"{ev}%",
            "tier_assignment": tier
        })
    return processed

def process_value_picks(fixtures, min_ev_threshold=4.0):
    value_picks = []
    for f in fixtures:
        odds = f["odds"]
        prob = f["model_prob"]
        implied_prob = round(1.0 / odds, 4)
        ev = round(((prob * odds) - 1.0) * 100, 2)
        
        # TIGHTENED FILTER: Strict threshold of EV >= +4.0%
        if ev >= min_ev_threshold:
            value_picks.append({
                **f,
                "implied_prob_str": f"{round(implied_prob * 100, 1)}%",
                "model_prob_str": f"{round(prob * 100, 1)}%",
                "ev_val": ev,
                "ev_str": f"+{ev}%",
                "edge_rating": "ULTRA VALUE" if ev >= 6.0 else "SOLID VALUE"
            })
    value_picks.sort(key=lambda x: x["ev_val"], reverse=True)
    return value_picks

SLATE_DATA = process_accumulator_slate(ACCUMULATOR_SLATE)
VALUE_PICKS_DATA = process_value_picks(GLOBAL_FIXTURE_POOL)

json_slate = json.dumps(SLATE_DATA)
json_value_picks = json.dumps(VALUE_PICKS_DATA)

HTML_CONTENT = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GEM V15.0 Engine & Value Finder</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }}
        .container {{ max-width: 1150px; margin: 0 auto; }}
        h1 {{ color: #38bdf8; text-align: center; margin-bottom: 20px; }}
        .tab-bar {{ display: flex; gap: 10px; margin-bottom: 20px; border-bottom: 2px solid #334155; padding-bottom: 5px; }}
        .tab-btn {{ background: #1e293b; color: #94a3b8; border: none; padding: 12px 24px; font-size: 15px; font-weight: bold; border-radius: 6px 6px 0 0; cursor: pointer; transition: 0.2s; }}
        .tab-btn.active {{ background: #38bdf8; color: #0f172a; }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
        .card {{ background: #1e293b; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3); }}
        .tier-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 15px; margin-bottom: 20px; }}
        .tier-card {{ background: #334155; padding: 15px; border-radius: 6px; border-left: 4px solid #38bdf8; }}
        .tier-card h3 {{ margin-top: 0; color: #38bdf8; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #475569; }}
        th {{ background: #334155; color: #94a3b8; }}
        input[type="number"] {{ background: #0f172a; border: 1px solid #475569; color: #fff; padding: 8px; border-radius: 4px; width: 100px; font-size: 16px; }}
        .ev-badge {{ background: #166534; color: #4ade80; padding: 4px 8px; border-radius: 4px; font-weight: bold; display: inline-block; }}
        .tier-badge {{ background: #1e3a8a; color: #93c5fd; padding: 3px 6px; border-radius: 4px; font-size: 11px; }}
        .rating-badge {{ background: #1e3a8a; color: #93c5fd; padding: 3px 6px; border-radius: 4px; font-weight: bold; font-size: 11px; }}
        .rating-badge.ultra {{ background: #166534; color: #4ade80; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>GEM V15.0 Quantitative Pipeline</h1>

        <div class="tab-bar">
            <button class="tab-btn active" onclick="switchTab('slateTab', this)">Active 9-Leg Slate</button>
            <button class="tab-btn" onclick="switchTab('valueTab', this)">🔥 Daily Pick Value (+EV Scanner)</button>
        </div>

        <div id="slateTab" class="tab-content active">
            <div class="card">
                <label><strong>Base Stake (£):</strong> </label>
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
                <h2>Active 9-Leg Slate</h2>
                <div id="slateContainer">Loading slate...</div>
            </div>
        </div>

        <div id="valueTab" class="tab-content">
            <div class="card">
                <h2>Global High-Value Picks (EV &ge; +4.0%)</h2>
                <p style="color: #94a3b8;">Strict value scanner filtering out low-margin noise. Displays only high-confidence statistical edges across global matches.</p>
                <div id="valueContainer">Loading value picks...</div>
            </div>
        </div>
    </div>

    <script>
        const slateData = {json_slate};
        const valueData = {json_value_picks};

        function switchTab(tabId, btn) {{
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            btn.classList.add('active');
        }}

        function renderSlateTable() {{
            let html = '<table><thead><tr><th>Leg</th><th>Date</th><th>Match</th><th>Selection</th><th>Odds</th><th>EV Edge</th><th>Tier Auto-Route</th></tr></thead><tbody>';
            slateData.forEach(f => {{
                html += `<tr>
                    <td>` + f.leg + `</td>
                    <td>` + f.date + `</td>
                    <td>` + f.match + `</td>
                    <td><strong>` + f.selection + `</strong></td>
                    <td>` + f.odds.toFixed(2) + `</td>
                    <td><span class="ev-badge">` + f.ev_str + `</span></td>
                    <td><span class="tier-badge">` + f.tier_assignment + `</span></td>
                </tr>`;
            }});
            html += '</tbody></table>';
            document.getElementById('slateContainer').innerHTML = html;
        }}

        function renderValueTable() {{
            let html = '<table><thead><tr><th>Date</th><th>League</th><th>Match</th><th>Selection</th><th>Bookie Odds</th><th>Bookie Prob</th><th>Model Prob</th><th>EV Edge</th><th>Edge Rating</th></tr></thead><tbody>';
            valueData.forEach(f => {{
                const ratingClass = f.ev_val >= 6.0 ? 'ultra' : '';
                html += `<tr>
                    <td>` + f.date + `</td>
                    <td>` + f.league + `</td>
                    <td>` + f.match + `</td>
                    <td><strong>` + f.selection + `</strong></td>
                    <td>` + f.odds.toFixed(2) + `</td>
                    <td>` + f.implied_prob_str + `</td>
                    <td>` + f.model_prob_str + `</td>
                    <td><span class="ev-badge">` + f.ev_str + `</span></td>
                    <td><span class="rating-badge ` + ratingClass + `">` + f.edge_rating + `</span></td>
                </tr>`;
            }});
            html += '</tbody></table>';
            document.getElementById('valueContainer').innerHTML = html;
        }}

        function calculateReturns() {{
            const stake = parseFloat(document.getElementById('baseStake').value) || 0;
            const calcOdds = (count) => slateData.slice(0, count).reduce((acc, item) => acc * item.odds, 1);

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

        renderSlateTable();
        renderValueTable();
        calculateReturns();
    </script>
</body>
</html>"""

@app.get("/api/slate")
def get_slate():
    return SLATE_DATA

@app.get("/api/value-picks")
def get_value_picks():
    return VALUE_PICKS_DATA

@app.get("/", response_class=HTMLResponse)
def read_root():
    return HTML_CONTENT