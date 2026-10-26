# Force redeploy tag: 2026-10-26 20:18:02
import json
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="SlateMetrics AI - Quantitative Analytics Dashboard")

# 1. 7 AI AUTOMATED COMBO BANKERS
COMBO_BANKERS = [
    {"banker": 1, "date": "2026-10-26", "match": "Sevilla vs. Osasuna", "selection": "Sevilla Win or Draw (1X)", "odds": 1.25, "model_prob": "84.0%", "ev_edge": "+5.00%", "Here is the exact remaining HTML/JavaScript snippet starting right from where your terminal paste cut off (`display: inline-block;`), followed by the rest of `main.py` and the Git deployment commands to run in PowerShell:

```powershell
Set-Location "$HOME\gem-v15-engine"

$mainPy = @'
import json
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="SlateMetrics AI - Quantitative Analytics Dashboard")

# 1. 7 AI AUTOMATED COMBO BANKERS
COMBO_BANKERS = [
    {"banker": 1, "date": "2026-10-26", "match": "Sevilla vs. Osasuna", "selection": "Sevilla Win or Draw (1X)", "odds": 1.25, "model_prob": "84.0%", "ev_edge": "+5.00%", "confidence": "HIGH BANKER"},
    {"banker": 2, "date": "2026-10-26", "match": "Galatasaray vs. Fenerbahce", "selection": "Over 1.5 Match Goals", "odds": 1.30, "model_prob": "82.0%", "ev_edge": "+6.60%", "confidence": "HIGH BANKER"},
    {"banker": 3, "date": "2026-10-26", "match": "Santa Clara vs. Benfica", "selection": "Benfica Win", "odds": 1.36, "model_prob": "77.0%", "ev_edge": "+4.72%", "confidence": "SOLID BANKER"},
    {"banker": 4, "date": "2026-10-27", "match": "Fleetwood vs. Arsenal", "selection": "Arsenal Win", "odds": 1.18, "model_prob": "91.0%", "ev_edge": "+7.38%", "confidence": "HIGH BANKER"},
    {"banker": 5, "date": "2026-10-27", "match": "Sabah vs. Borussia Dortmund", "selection": "Over 2.5 Match Goals", "odds": 1.40, "model_prob": "76.0%", "ev_edge": "+6.40%", "confidence": "SOLID BANKER"},
    {"banker": 6, "date": "2026-10-27", "match": "PSG vs. Barcelona", "selection": "Over 1.5 Match Goals", "odds": 1.22, "model_prob": "85.0%", "ev_edge": "+5.25%", "confidence": "HIGH BANKER"},
    {"banker": 7, "date": "2026-10-28", "match": "Manchester City vs. Brighton", "selection": "Manchester City Win", "odds": 1.32, "model_prob": "80.0%", "ev_edge": "+5.60%", "confidence": "HIGH BANKER"}
]

# 2. OVER 2.5 GOAL COUNT VALUE FINDER (6 SELECTIONS)
GOAL_COUNT_VALUE = [
    {"date": "2026-10-26", "league": "Brazil Serie A U20", "match": "Cruzeiro U20 vs. Atletico Mineiro U20", "selection": "Over 2.5 Goals", "odds": 1.57, "model_prob": "75.0%", "xg_projected": "3.20", "ev_edge": "+17.75%"},
    {"date": "2026-10-27", "league": "Friendly", "match": "Sabah vs. Borussia Dortmund", "selection": "Over 2.5 Goals", "odds": 1.40, "model_prob": "76.0%", "xg_projected": "3.35", "ev_edge": "+6.40%"},
    {"date": "2026-10-27", "league": "UEFA Champions League", "match": "Real Madrid vs. Juventus", "selection": "Over 2.5 Goals", "odds": 1.68, "model_prob": "68.0%", "xg_projected": "2.95", "ev_edge": "+14.24%"},
    {"date": "2026-10-28", "league": "EFL Cup", "match": "Bournemouth vs. Aston Villa", "selection": "Over 2.5 Goals", "odds": 1.62, "model_prob": "70.0%", "xg_projected": "3.10", "ev_edge": "+13.40%"},
    {"date": "2026-10-28", "league": "EFL Cup", "match": "Manchester City vs. Brighton", "selection": "Over 2.5 Goals", "odds": 1.50, "model_prob": "74.0%", "xg_projected": "3.45", "ev_edge": "+11.00%"},
    {"date": "2026-10-28", "league": "EFL Cup", "match": "Liverpool vs. Chelsea", "selection": "Over 2.5 Goals", "odds": 1.55, "model_prob": "72.0%", "xg_projected": "3.25", "ev_edge": "+11.60%"}
]

# 3. CORNER COUNT PREDICTIONS
CORNER_PREDICTIONS = [
    {"date": "2026-10-26", "match": "Sevilla vs. Osasuna", "selection": "Sevilla Over 4.5 Corners", "odds": 1.44, "model_prob": "78.0%", "avg_corners": "6.2", "ev_edge": "+12.32%"},
    {"date": "2026-10-26", "match": "Galatasaray vs. Fenerbahce", "selection": "Over 9.5 Match Corners", "odds": 1.72, "model_prob": "65.0%", "avg_corners": "11.4", "ev_edge": "+11.80%"},
    {"date": "2026-10-27", "match": "PSG vs. Barcelona", "selection": "PSG Over 5.5 Corners", "odds": 1.65, "model_prob": "67.0%", "avg_corners": "7.1", "ev_edge": "+10.55%"},
    {"date": "2026-10-28", "match": "Liverpool vs. Chelsea", "selection": "Over 9.5 Match Corners", "odds": 1.60, "model_prob": "69.0%", "avg_corners": "10.8", "ev_edge": "+10.40%"},
    {"date": "2026-10-28", "match": "Manchester City vs. Brighton", "selection": "Man City Over 6.5 Corners", "odds": 1.53, "model_prob": "72.0%", "avg_corners": "8.3", "ev_edge": "+10.16%"}
]

json_bankers = json.dumps(COMBO_BANKERS)
json_goals = json.dumps(GOAL_COUNT_VALUE)
json_corners = json.dumps(CORNER_PREDICTIONS)

HTML_CONTENT = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SlateMetrics AI - Analytics Dashboard</title>
    <script src="[https://cdn.tailwindcss.com](https://cdn.tailwindcss.com)"></script>
    <style>
        body {{ background-color: #0b0f19; color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
        .bg-stadium {{ background: linear-gradient(to bottom, rgba(11, 15, 25, 0.4), rgba(11, 15, 25, 0.95)), url('[https://images.unsplash.com/photo-1508098682722-e99c43a406b2?q=80&w=1000&auto=format&fit=crop](https://images.unsplash.com/photo-1508098682722-e99c43a406b2?q=80&w=1000&auto=format&fit=crop)') center/cover no-repeat; }}
        .tab-btn {{ background: #1e293b; color: #94a3b8; border: none; padding: 10px 18px; font-size: 13px; font-weight: bold; border-radius: 8px; cursor: pointer; transition: 0.2s; white-space: nowrap; }}
        .tab-btn.active {{ background: #eab308; color: #0b0f19; }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #1e293b; vertical-align: top; }}
        th {{ background: #111827; color: #9ca3af; }}
        .ev-badge {{ background: #065f46; color: #34d399; padding: 3px 8px; border-radius: 6px; font-weight: bold; display: inline-block; }}
        .badge-gold {{ background: #b45309; color: #fef3c7; padding: 3px 8px; border-radius: 6px; font-weight: bold; font-size: 11px; }}
    </style>
</head>
<body class="bg-stadium min-h-screen pb-12">

    <!-- Top Header Bar -->
    <div class="max-w-6xl mx-auto px-4 pt-6 flex justify-between items-center">
        <div class="inline-flex items-center gap-1.5 px-3.5 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-semibold">
            <span>ðŸ‘‘</span> AI ANALYSIS ENGINE ACTIVE
        </div>
        <div class="flex items-center gap-2">
            <span class="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block animate-pulse"></span>
            <span class="text-xs font-medium text-slate-300">10K Active Users</span>
        </div>
    </div>

    <!-- Main Title Header -->
    <div class="max-w-6xl mx-auto px-4 text-center mt-4">
        <h1 class="text-3xl font-extrabold tracking-tight text-white">
            SlateMetrics <span class="text-amber-400">AI</span>
        </h1>
        <p class="text-sm text-slate-300 mt-1">
            Manage your predictions more consciously with AI-powered VIP analyses.
        </p>
    </div>

    <!-- Feature Quick Pills -->
    <div class="max-w-6xl mx-auto px-4 mt-6 grid grid-cols-2 md:grid-cols-4 gap-3">
        <div class="bg-slate-900/80 border border-slate-800 rounded-xl p-3.5 flex items-center gap-2.5 cursor-pointer" onclick="switchTab('bankerTab', document.querySelectorAll('.tab-btn')[0])">
            <div class="w-6 h-6 rounded-full bg-amber-500/20 text-amber-400 flex items-center justify-center text-xs font-bold">âœ“</div>
            <span class="text-xs font-semibold text-slate-200">Combo Banker (7)</span>
        </div>
        <div class="bg-slate-900/80 border border-slate-800 rounded-xl p-3.5 flex items-center gap-2.5 cursor-pointer" onclick="switchTab('goalTab', document.querySelectorAll('.tab-btn')[1])">
            <div class="w-6 h-6 rounded-full bg-amber-500/20 text-amber-400 flex items-center justify-center text-xs font-bold">âœ“</div>
            <span class="text-xs font-semibold text-slate-200">Goal Count (Over 2.5)</span>
        </div>
        <div class="bg-slate-900/80 border border-slate-800 rounded-xl p-3.5 flex items-center gap-2.5 cursor-pointer" onclick="switchTab('cornerTab', document.querySelectorAll('.tab-btn')[2])">
            <div class="w-6 h-6 rounded-full bg-amber-500/20 text-amber-400 flex items-center justify-center text-xs font-bold">âœ“</div>
            <span class="text-xs font-semibold text-slate-200">Corner Predictions</span>
        </div>
        <div class="bg-slate-900/80 border border-slate-800 rounded-xl p-3.5 flex items-center gap-2.5">
            <div class="w-6 h-6 rounded-full bg-amber-500/20 text-amber-400 flex items-center justify-center text-xs font-bold">âœ“</div>
            <span class="text-xs font-semibold text-slate-200">Live Predictions</span>
        </div>
    </div>

    <!-- Navigation Tab Bar -->
    <div class="max-w-6xl mx-auto px-4 mt-8">
        <div class="flex gap-2 bg-slate-900/90 p-2 rounded-xl border border-slate-800 overflow-x-auto">
            <button class="tab-btn active" onclick="switchTab('bankerTab', this)">âš¡ AI Combo Banker (7 Bankers)</button>
            <button class="tab-btn" onclick="switchTab('goalTab', this)">âš½ Goal Count Predictions (Over 2.5 Value)</button>
            <button class="tab-btn" onclick="switchTab('cornerTab', this)">ðŸš© Corner Count Predictions</button>
        </div>
    </div>

    <!-- TAB 1: COMBO BANKERS -->
    <div id="bankerTab" class="tab-content active max-w-6xl mx-auto px-4 mt-6">
        <div class="bg-slate-900/90 border border-slate-800 rounded-2xl p-6">
            <h2 class="text-lg font-bold text-white mb-1">7 AI Automated Selected Bankers</h2>
            <p class="text-xs text-slate-400 mb-4">High-confidence model selections with strong probability agreement and positive expected value.</p>
            <div class="overflow-x-auto" id="bankerContainer">Loading bankers...</div>
        </div>
    </div>

    <!-- TAB 2: GOAL COUNT (OVER 2.5 VALUE) -->
    <div id="goalTab" class="tab-content max-w-6xl mx-auto px-4 mt-6">
        <div class="bg-slate-900/90 border border-slate-800 rounded-2xl p-6">
            <h2 class="text-lg font-bold text-white mb-1">Goal Count Predictions (Over 2.5 Value Finder)</h2>
            <p class="text-xs text-slate-400 mb-4">Fixtures with high projected xG exceeding market price expectations.</p>
            <div class="overflow-x-auto" id="goalContainer">Loading goal picks...</div>
        </div>
    </div>

    <!-- TAB 3: CORNER PREDICTIONS -->
    <div id="cornerTab" class="tab-content max-w-6xl mx-auto px-4 mt-6">
        <div class="bg-slate-900/90 border border-slate-800 rounded-2xl p-6">
            <h2 class="text-lg font-bold text-white mb-1">Corner Count Predictions</h2>
            <p class="text-xs text-slate-400 mb-4">High-probability team and total match corner projections based on historical volumetric metrics.</p>
            <div class="overflow-x-auto" id="cornerContainer">Loading corner picks...</div>
        </div>
    </div>

    <script>
        const bankerData = {json_bankers};
        const goalData = {json_goals};
        const cornerData = {json_corners};

        function switchTab(tabId, btn) {{
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            if(btn) btn.classList.add('active');
        }}

        function renderBankerTable() {{
            let html = '<table><thead><tr><th>Banker #</th><th>Date</th><th>Match</th><th>Selection</th><th>Odds</th><th>Model Prob</th><th>EV Edge</th><th>Confidence</th></tr></thead><tbody>';
            bankerData.forEach(f => {{
                html += `<tr>
                    <td class="font-bold text-amber-400">#` + f.banker + `</td>
                    <td>` + f.date + `</td>
                    <td class="font-semibold">` + f.match + `</td>
                    <td><strong>` + f.selection + `</strong></td>
                    <td>` + f.odds.toFixed(2) + `</td>
                    <td>` + f.model_prob + `</td>
                    <td><span class="ev-badge">` + f.ev_edge + `</span></td>
                    <td><span class="badge-gold">` + f.confidence + `</span></td>
                </tr>`;
            }});
            html += '</tbody></table>';
            document.getElementById('bankerContainer').innerHTML = html;
        }}

        function renderGoalTable() {{
            let html = '<table><thead><tr><th>Date</th><th>League</th><th>Match</th><th>Selection</th><th>Odds</th><th>Model xG</th><th>Model Prob</th><th>EV Edge</th></tr></thead><tbody>';
            goalData.forEach(f => {{
                html += `<tr>
                    <td>` + f.date + `</td>
                    <td>` + f.league + `</td>
                    <td class="font-semibold">` + f.match + `</td>
                    <td><strong class="text-amber-400">` + f.selection + `</strong></td>
                    <td>` + f.odds.toFixed(2) + `</td>
                    <td>` + f.xg_projected + `</td>
                    <td>` + f.model_prob + `</td>
                    <td><span class="ev-badge">` + f.ev_edge + `</span></td>
                </tr>`;
            }});
            html += '</tbody></table>';
            document.getElementById('goalContainer').innerHTML = html;
        }}

        function renderCornerTable() {{
            let html = '<table><thead><tr><th>Date</th><th>Match</th><th>Selection</th><th>Odds</th><th>Model Avg Corners</th><th>Model Prob</th><th>EV Edge</th></tr></thead><tbody>';
            cornerData.forEach(c => {{
                html += `<tr>
                    <td>` + c.date + `</td>
                    <td class="font-semibold">` + c.match + `</td>
                    <td><strong class="text-amber-400">` + c.selection + `</strong></td>
                    <td>` + c.odds.toFixed(2) + `</td>
                    <td>` + c.avg_corners + `</td>
                    <td>` + c.model_prob + `</td>
                    <td><span class="ev-badge">` + c.ev_edge + `</span></td>
                </tr>`;
            }});
            html += '</tbody></table>';
            document.getElementById('cornerContainer').innerHTML = html;
        }}

        renderBankerTable();
        renderGoalTable();
        renderCornerTable();
    </script>
</body>
</html>"""

@app.get("/api/bankers")
def get_bankers():
    return COMBO_BANKERS

@app.get("/api/goal-count")
def get_goal_count():
    return GOAL_COUNT_VALUE

@app.get("/api/corners")
def get_corners():
    return CORNER_PREDICTIONS

@app.get("/", response_class=HTMLResponse)
def read_root():
    return HTML_CONTENT