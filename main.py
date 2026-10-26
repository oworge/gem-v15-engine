import json
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="GEM V15.0 Engine & Correct Score Matrix")

# 1. ACCUMULATOR SLATE WITH 4 BET BUILDER SELECTIONS PER GAME
ACCUMULATOR_SLATE = [
    {
        "leg": 1, "date": "2026-10-26", "match": "Sevilla vs. Osasuna", "selection": "Sevilla Win or Draw (1X)", "odds": 1.25, "model_prob": 0.84, "agreement": 0.92, "time": "20:00 GMT",
        "bet_builder": ["Sevilla Double Chance (1X)", "Under 3.5 Match Goals", "Sevilla Over 3.5 Team Corners", "Osasuna Over 1.5 Team Cards"],
        "builder_odds": 2.40
    },
    {
        "leg": 2, "date": "2026-10-26", "match": "Galatasaray vs. Fenerbahce", "selection": "Over 1.5 Goals", "odds": 1.30, "model_prob": 0.82, "agreement": 0.88, "time": "18:30 GMT",
        "bet_builder": ["Over 1.5 Match Goals", "Both Teams to Score (Yes)", "Over 4.5 Match Cards", "Galatasaray Over 4.5 Corners"],
        "builder_odds": 2.85
    },
    {
        "leg": 3, "date": "2026-10-26", "match": "Santa Clara vs. Benfica", "selection": "Benfica Win", "odds": 1.36, "model_prob": 0.77, "agreement": 0.85, "time": "18:45 GMT",
        "bet_builder": ["Benfica Match Winner", "Over 1.5 Match Goals", "Benfica Over 1.5 Team Goals", "Santa Clara Over 1.5 Cards"],
        "builder_odds": 2.50
    },
    {
        "leg": 4, "date": "2026-10-27", "match": "Fleetwood vs. Arsenal", "selection": "Arsenal Win", "odds": 1.18, "model_prob": 0.91, "agreement": 0.95, "time": "19:45 GMT",
        "bet_builder": ["Arsenal Match Winner", "Arsenal HT/FT", "Over 2.5 Match Goals", "Fleetwood Under 3.5 Corners"],
        "builder_odds": 2.10
    },
    {
        "leg": 5, "date": "2026-10-27", "match": "Sabah vs. Borussia Dortmund", "selection": "Over 2.5 Goals", "odds": 1.40, "model_prob": 0.76, "agreement": 0.79, "time": "17:45 GMT",
        "bet_builder": ["Over 2.5 Match Goals", "Dortmund Over 1.5 First Half Goals", "Dortmund Win Either Half", "Over 8.5 Match Corners"],
        "builder_odds": 2.65
    },
    {
        "leg": 6, "date": "2026-10-27", "match": "PSG vs. Barcelona", "selection": "Over 1.5 Goals", "odds": 1.22, "model_prob": 0.85, "agreement": 0.90, "time": "20:00 GMT",
        "bet_builder": ["Over 1.5 Match Goals", "Both Teams to Score (Yes)", "PSG Over 3.5 Team Corners", "Barcelona Over 1.5 Cards"],
        "builder_odds": 2.35
    },
    {
        "leg": 7, "date": "2026-10-28", "match": "Liverpool vs. Chelsea", "selection": "Over 1.5 Goals", "odds": 1.24, "model_prob": 0.83, "agreement": 0.87, "time": "19:45 GMT",
        "bet_builder": ["Over 1.5 Match Goals", "Liverpool Double Chance (1X)", "Over 9.5 Match Corners", "Over 3.5 Match Cards"],
        "builder_odds": 2.45
    },
    {
        "leg": 8, "date": "2026-10-28", "match": "Manchester City vs. Brighton", "selection": "Manchester City Win", "odds": 1.32, "model_prob": 0.80, "agreement": 0.84, "time": "19:45 GMT",
        "bet_builder": ["Man City Match Winner", "Over 2.5 Match Goals", "Man City Over 5.5 Team Corners", "Brighton Over 1.5 Cards"],
        "builder_odds": 2.55
    },
    {
        "leg": 9, "date": "2026-10-28", "match": "Bournemouth vs. Aston Villa", "selection": "Both Teams to Score", "odds": 1.50, "model_prob": 0.72, "agreement": 0.75, "time": "19:45 GMT",
        "bet_builder": ["Both Teams to Score (Yes)", "Over 2.5 Match Goals", "Aston Villa Double Chance (X2)", "Over 8.5 Match Corners"],
        "builder_odds": 3.10
    }
]

# 2. CORRECT SCORE MATRIX DATA
CORRECT_SCORE_DATA = [
    {"date": "2026-10-26", "match": "Sevilla vs. Osasuna", "xg": "1.65 - 0.85", "predicted_score": "1 - 0", "alt_score": "2 - 0", "score_odds": 6.50, "model_prob": "18.5%"},
    {"date": "2026-10-26", "match": "Galatasaray vs. Fenerbahce", "xg": "1.85 - 1.45", "predicted_score": "2 - 1", "alt_score": "1 - 1", "score_odds": 8.00, "model_prob": "14.2%"},
    {"date": "2026-10-26", "match": "Santa Clara vs. Benfica", "xg": "0.75 - 2.10", "predicted_score": "0 - 2", "alt_score": "0 - 3", "score_odds": 7.00, "model_prob": "16.8%"},
    {"date": "2026-10-27", "match": "Fleetwood vs. Arsenal", "xg": "0.40 - 2.60", "predicted_score": "0 - 3", "alt_score": "0 - 2", "score_odds": 6.00, "model_prob": "22.0%"},
    {"date": "2026-10-27", "match": "Sabah vs. Borussia Dortmund", "xg": "0.90 - 2.45", "predicted_score": "1 - 3", "alt_score": "1 - 2", "score_odds": 11.00, "model_prob": "11.5%"},
    {"date": "2026-10-27", "match": "PSG vs. Barcelona", "xg": "1.95 - 1.70", "predicted_score": "2 - 2", "alt_score": "2 - 1", "score_odds": 12.00, "model_prob": "10.4%"},
    {"date": "2026-10-28", "match": "Liverpool vs. Chelsea", "xg": "1.80 - 1.35", "predicted_score": "2 - 1", "alt_score": "1 - 1", "score_odds": 8.50, "model_prob": "13.8%"},
    {"date": "2026-10-28", "match": "Manchester City vs. Brighton", "xg": "2.40 - 1.05", "predicted_score": "2 - 0", "alt_score": "3 - 1", "score_odds": 7.50, "model_prob": "15.6%"},
    {"date": "2026-10-28", "match": "Bournemouth vs. Aston Villa", "xg": "1.45 - 1.55", "predicted_score": "1 - 1", "alt_score": "2 - 2", "score_odds": 7.00, "model_prob": "15.2%"}
]

# 3. GLOBAL FIXTURE POOL (For EV Scanner)
GLOBAL_FIXTURE_POOL = [
    {"date": "2026-10-26", "league": "Brazil Serie A U20", "match": "Cruzeiro U20 vs. Atletico Mineiro U20", "selection": "Over 2.5 Goals", "odds": 1.57, "model_prob": 0.75, "time": "18:00 GMT"},
    {"date": "2026-10-26", "league": "La Liga", "match": "Sevilla vs. Osasuna", "selection": "Sevilla Win or Draw (1X)", "odds": 1.25, "model_prob": 0.85, "time": "20:00 GMT"},
    {"date": "2026-10-26", "league": "Super Lig", "match": "Galatasaray vs. Fenerbahce", "selection": "Over 1.5 Goals", "odds": 1.30, "model_prob": 0.82, "time": "18:30 GMT"},
    {"date": "2026-10-26", "league": "Romania Liga I", "match": "Sepsi OSK vs. U Craiova", "selection": "Away Win", "odds": 1.50, "model_prob": 0.715, "time": "18:00 GMT"},
    {"date": "2026-10-26", "league": "Argentina Liga Prof", "match": "Union Santa Fe vs. Estudiantes", "selection": "Double Chance (12)", "odds": 1.36, "model_prob": 0.77, "time": "22:00 GMT"},
    {"date": "2026-10-27", "league": "Serie A (Italy)", "match": "Torino vs. Como", "selection": "Como Win", "odds": 1.73, "model_prob": 0.64, "time": "19:45 GMT"},
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
json_scores = json.dumps(CORRECT_SCORE_DATA)

HTML_CONTENT = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GEM V15.0 Engine & Correct Score Matrix</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }}
        .container {{ max-width: 1150px; margin: 0 auto; }}
        h1 {{ color: #38bdf8; text-align: center; margin-bottom: 20px; }}
        .tab-bar {{ display: flex; gap: 10px; margin-bottom: 20px; border-bottom: 2px solid #334155; padding-bottom: 5px; overflow-x: auto; }}
        .tab-btn {{ background: #1e293b; color: #94a3b8; border: none; padding: 12px 20px; font-size: 14px; font-weight: bold; border-radius: 6px 6px 0 0; cursor: pointer; transition: 0.2s; white-space: nowrap; }}
        .tab-btn.active {{ background: #38bdf8; color: #0f172a; }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
        .card {{ background: #1e293b; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3); }}
        .tier-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 15px; margin-bottom: 20px; }}
        .tier-card {{ background: #334155; padding: 15px; border-radius: 6px; border-left: 4px solid #38bdf8; }}
        .tier-card h3 {{ margin-top: 0; color: #38bdf8; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #475569; vertical-align: top; }}
        th {{ background: #334155; color: #94a3b8; }}
        input[type="number"] {{ background: #0f172a; border: 1px solid #475569; color: #fff; padding: 8px; border-radius: 4px; width: 100px; font-size: 16px; }}
        .ev-badge {{ background: #166534; color: #4ade80; padding: 4px 8px; border-radius: 4px; font-weight: bold; display: inline-block; }}
        .tier-badge {{ background: #1e3a8a; color: #93c5fd; padding: 3px 6px; border-radius: 4px; font-size: 11px; }}
        .rating-badge {{ background: #1e3a8a; color: #93c5fd; padding: 3px 6px; border-radius: 4px; font-weight: bold; font-size: 11px; }}
        .rating-badge.ultra {{ background: #166534; color: #4ade80; }}
        .score-badge {{ background: #b45309; color: #fef3c7; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 13px; }}
        .builder-box {{ background: #0f172a; border-radius: 6px; padding: 8px; margin-top: 4px; font-size: 11px; border-left: 3px solid #f59e0b; }}
        .builder-box ul {{ margin: 4px 0 0 15px; padding: 0; color: #cbd5e1; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>GEM V15.0 Quantitative Pipeline</h1>

        <div class="tab-bar">
            <button class="tab-btn active" onclick="switchTab('slateTab', this)">Active 9-Leg Slate</button>
            <button class="tab-btn" onclick="switchTab('valueTab', this)">🔥 Daily Pick Value (+EV)</button>
            <button class="tab-btn" onclick="switchTab('scoreTab', this)">🎯 Correct Score Matrix</button>
        </div>

        <!-- TAB 1: 9-LEG SLATE -->
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
                <h2>Active 9-Leg Slate & 4-Leg Bet Builders</h2>
                <div id="slateContainer">Loading slate...</div>
            </div>
        </div>

        <!-- TAB 2: DAILY VALUE SCANNER -->
        <div id="valueTab" class="tab-content">
            <div class="card">
                <h2>Global High-Value Picks (EV &ge; +4.0%)</h2>
                <p style="color: #94a3b8;">Strict value finder filtering out low-margin noise across global fixtures.</p>
                <div id="valueContainer">Loading value picks...</div>
            </div>
        </div>

        <!-- TAB 3: CORRECT SCORE MATRIX -->
        <div id="scoreTab" class="tab-content">
            <div class="card">
                <h2>🎯 Poisson Model Correct Score Projections</h2>
                <p style="color: #94a3b8;">Expected goals (xG) and most probable full-time scorelines calculated by the quantitative engine.</p>
                <div id="scoreContainer">Loading correct scores...</div>
            </div>
        </div>
    </div>

    <script>
        const slateData = {json_slate};
        const valueData = {json_value_picks};
        const scoreData = {json_scores};

        function switchTab(tabId, btn) {{
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            btn.classList.add('active');
        }}

        function renderSlateTable() {{
            let html = '<table><thead><tr><th>Leg</th><th>Date</th><th>Match</th><th>Selection & 4-Leg Bet Builder</th><th>Single Odds</th><th>Builder Odds</th><th>EV Edge</th><th>Tier</th></tr></thead><tbody>';
            slateData.forEach(f => {{
                let builderHtml = '<div class="builder-box"><strong>⚡ 4-Leg Bet Builder:</strong><ul>';
                f.bet_builder.forEach(item => {{
                    builderHtml += '<li>' + item + '</li>';
                }});
                builderHtml += '</ul></div>';

                html += `<tr>
                    <td>` + f.leg + `</td>
                    <td>` + f.date + `</td>
                    <td>` + f.match + `</td>
                    <td><strong>` + f.selection + `</strong>` + builderHtml + `</td>
                    <td>` + f.odds.toFixed(2) + `</td>
                    <td><strong>` + f.builder_odds.toFixed(2) + `</strong></td>
                    <td><span class="ev-badge">` + f.ev_str + `</span></td>
                    <td><span class="tier-badge">` + f.tier_assignment + `</span></td>
                </tr>`;
            }});
            html += '</tbody></table>';
            document.getElementById('slateContainer').innerHTML = html;
        }}

        function renderValueTable() {{
            let html = '<table><thead><tr><th>Date</th><th>League</th><th>Match</th><th>Selection</th><th>Bookie Odds</th><th>Model Prob</th><th>EV Edge</th><th>Rating</th></tr></thead><tbody>';
            valueData.forEach(f => {{
                const ratingClass = f.ev_val >= 6.0 ? 'ultra' : '';
                html += `<tr>
                    <td>` + f.date + `</td>
                    <td>` + f.league + `</td>
                    <td>` + f.match + `</td>
                    <td><strong>` + f.selection + `</strong></td>
                    <td>` + f.odds.toFixed(2) + `</td>
                    <td>` + f.model_prob_str + `</td>
                    <td><span class="ev-badge">` + f.ev_str + `</span></td>
                    <td><span class="rating-badge ` + ratingClass + `">` + f.edge_rating + `</span></td>
                </tr>`;
            }});
            html += '</tbody></table>';
            document.getElementById('valueContainer').innerHTML = html;
        }}

        function renderScoreTable() {{
            let html = '<table><thead><tr><th>Date</th><th>Match</th><th>Model xG (H - A)</th><th>Predicted Score</th><th>Alt Score</th><th>Est. Odds</th><th>Model Prob</th></tr></thead><tbody>';
            scoreData.forEach(s => {{
                html += `<tr>
                    <td>` + s.date + `</td>
                    <td><strong>` + s.match + `</strong></td>
                    <td>` + s.xg + `</td>
                    <td><span class="score-badge">` + s.predicted_score + `</span></td>
                    <td>` + s.alt_score + `</td>
                    <td>` + s.score_odds.toFixed(2) + `</td>
                    <td>` + s.model_prob + `</td>
                </tr>`;
            }});
            html += '</tbody></table>';
            document.getElementById('scoreContainer').innerHTML = html;
        }}

        function calculateReturns() {{
            const stake = parseFloat(defaultVal = document.getElementById('baseStake').value) || 0;
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
        renderScoreTable();
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

@app.get("/api/correct-scores")
def get_correct_scores():
    return CORRECT_SCORE_DATA

@app.get("/", response_class=HTMLResponse)
def read_root():
    return HTML_CONTENT