import json
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="AI Scorecast PRO - Quantitative Analytics Dashboard")

COMBO_BANKERS = [
    {"banker": 1, "date": "2026-10-26", "match": "Sevilla vs. Osasuna", "selection": "Sevilla Win or Draw (1X)", "odds": 1.25, "model_prob": "84.0%", "ev_edge": "+5.00%", "confidence": "HIGH BANKER"},
    {"banker": 2, "date": "2026-10-26", "match": "Galatasaray vs. Fenerbahce", "selection": "Over 1.5 Match Goals", "odds": 1.30, "model_prob": "82.0%", "ev_edge": "+6.60%", "confidence": "HIGH BANKER"},
    {"banker": 3, "date": "2026-10-26", "match": "Santa Clara vs. Benfica", "selection": "Benfica Win", "odds": 1.36, "model_prob": "77.0%", "ev_edge": "+4.72%", "confidence": "SOLID BANKER"},
    {"banker": 4, "date": "2026-10-27", "match": "Fleetwood vs. Arsenal", "selection": "Arsenal Win", "odds": 1.18, "model_prob": "91.0%", "ev_edge": "+7.38%", "confidence": "HIGH BANKER"},
    {"banker": 5, "date": "2026-10-27", "match": "Sabah vs. Borussia Dortmund", "selection": "Over 2.5 Match Goals", "odds": 1.40, "model_prob": "76.0%", "ev_edge": "+6.40%", "confidence": "SOLID BANKER"},
    {"banker": 6, "date": "2026-10-27", "match": "PSG vs. Barcelona", "selection": "Over 1.5 Match Goals", "odds": 1.22, "model_prob": "85.0%", "ev_edge": "+5.25%", "confidence": "HIGH BANKER"},
    {"banker": 7, "date": "2026-10-28", "match": "Manchester City vs. Brighton", "selection": "Manchester City Win", "odds": 1.32, "model_prob": "80.0%", "ev_edge": "+5.60%", "confidence": "HIGH BANKER"}
]

GOAL_COUNT_VALUE = [
    {"date": "2026-10-26", "league": "Brazil Serie A U20", "match": "Cruzeiro U20 vs. Atletico Mineiro U20", "selection": "Over 2.5 Goals", "odds": 1.57, "model_prob": "75.0%", "xg_projected": "3.20", "ev_edge": "+17.75%"},
    {"date": "2026-10-27", "league": "Friendly", "match": "Sabah vs. Borussia Dortmund", "selection": "Over 2.5 Goals", "odds": 1.40, "model_prob": "76.0%", "xg_projected": "3.35", "ev_edge": "+6.40%"},
    {"date": "2026-10-27", "league": "UEFA Champions League", "match": "Real Madrid vs. Juventus", "selection": "Over 2.5 Goals", "odds": 1.68, "model_prob": "68.0%", "xg_projected": "2.95", "ev_edge": "+14.24%"},
    {"date": "2026-10-28", "league": "EFL Cup", "match": "Bournemouth vs. Aston Villa", "selection": "Over 2.5 Goals", "odds": 1.62, "model_prob": "70.0%", "xg_projected": "3.10", "ev_edge": "+13.40%"},
    {"date": "2026-10-28", "league": "EFL Cup", "match": "Manchester City vs. Brighton", "selection": "Over 2.5 Goals", "odds": 1.50, "model_prob": "74.0%", "xg_projected": "3.45", "ev_edge": "+11.00%"},
    {"date": "2026-10-28", "league": "EFL Cup", "match": "Liverpool vs. Chelsea", "selection": "Over 2.5 Goals", "odds": 1.55, "model_prob": "72.0%", "xg_projected": "3.25", "ev_edge": "+11.60%"}
]

CORNER_PREDICTIONS = [
    {"date": "2026-10-26", "match": "Sevilla vs. Osasuna", "selection": "Sevilla Over 4.5 Corners", "odds": 1.44, "model_prob": "78.0%", "avg_corners": "6.2", "ev_edge": "+12.32%"},
    {"date": "2026-10-26", "match": "Galatasaray vs. Fenerbahce", "selection": "Over 9.5 Match Corners", "odds": 1.72, "model_prob": "65.0%", "avg_corners": "11.4", "ev_edge": "+11.80%"},
    {"date": "2026-10-27", "match": "PSG vs. Barcelona", "selection": "PSG Over 5.5 Corners", "odds": 1.65, "model_prob": "67.0%", "avg_corners": "7.1", "ev_edge": "+10.55%"},
    {"date": "2026-10-28", "match": "Liverpool vs. Chelsea", "selection": "Over 9.5 Match Corners", "odds": 1.60, "model_prob": "69.0%", "avg_corners": "10.8", "ev_edge": "+10.40%"},
    {"date": "2026-10-28", "match": "Manchester City vs. Brighton", "selection": "Man City Over 6.5 Corners", "odds": 1.53, "model_prob": "72.0%", "avg_corners": "8.3", "ev_edge": "+10.16%"}
]

b_json = json.dumps(COMBO_BANKERS)
g_json = json.dumps(GOAL_COUNT_VALUE)
c_json = json.dumps(CORNER_PREDICTIONS)

html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Scorecast PRO</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>
body {{ background:#0b0f19; color:#f8fafc; font-family:sans-serif; }}
.btn {{ background:#1e293b; color:#94a3b8; padding:10px 18px; font-size:13px; font-weight:bold; border-radius:8px; cursor:pointer; }}
.btn.active {{ background:#eab308; color:#0b0f19; }}
.tab {{ display:none; }}
.tab.active {{ display:block; }}
table {{ width:100%; border-collapse:collapse; font-size:13px; }}
th, td {{ padding:12px; text-align:left; border-bottom:1px solid #1e293b; }}
th {{ background:#111827; color:#9ca3af; }}
.ev {{ background:#065f46; color:#34d399; padding:3px 8px; border-radius:6px; font-weight:bold; }}
.gold {{ background:#b45309; color:#fef3c7; padding:3px 8px; border-radius:6px; font-weight:bold; font-size:11px; }}
</style>
</head>
<body class="bg-slate-950 min-h-screen pb-12">
<div class="max-w-6xl mx-auto px-4 pt-6 flex justify-between items-center">
    <div class="px-3.5 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-semibold">?? AI ANALYSIS ENGINE ACTIVE</div>
    <div class="flex items-center gap-2"><span class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span><span class="text-xs text-slate-300">10K Active Users</span></div>
</div>
<div class="max-w-6xl mx-auto px-4 text-center mt-4">
    <h1 class="text-3xl font-extrabold text-white">AI Scorecast <span class="text-amber-400">PRO</span></h1>
    <p class="text-sm text-slate-300 mt-1">Manage predictions with AI VIP analyses.</p>
</div>
<div class="max-w-6xl mx-auto px-4 mt-8">
    <div class="flex gap-2 bg-slate-900 p-2 rounded-xl border border-slate-800 overflow-x-auto">
        <button class="btn active" onclick="sw('bTab',this)">? AI Combo Banker (7 Bankers)</button>
        <button class="btn" onclick="sw('gTab',this)">? Goal Count Predictions (Over 2.5 Value)</button>
        <button class="btn" onclick="sw('cTab',this)">?? Corner Count Predictions</button>
    </div>
</div>
<div id="bTab" class="tab active max-w-6xl mx-auto px-4 mt-6"><div class="bg-slate-900 border border-slate-800 rounded-2xl p-6"><h2 class="text-lg font-bold text-white mb-4">7 AI Automated Selected Bankers</h2><div id="bCon"></div></div></div>
<div id="gTab" class="tab max-w-6xl mx-auto px-4 mt-6"><div class="bg-slate-900 border border-slate-800 rounded-2xl p-6"><h2 class="text-lg font-bold text-white mb-4">Goal Count Predictions (Over 2.5 Value Finder)</h2><div id="gCon"></div></div></div>
<div id="cTab" class="tab max-w-6xl mx-auto px-4 mt-6"><div class="bg-slate-900 border border-slate-800 rounded-2xl p-6"><h2 class="text-lg font-bold text-white mb-4">Corner Count Predictions</h2><div id="cCon"></div></div></div>
<script>
const bD = {b_json};
const gD = {g_json};
const cD = {c_json};
function sw(id, el) {{
    document.querySelectorAll('.tab').forEach(x => x.classList.remove('active'));
    document.querySelectorAll('.btn').forEach(x => x.classList.remove('active'));
    document.getElementById(id).classList.add('active');
    if(el) el.classList.add('active');
}}
function rB() {{
    let h = '<table><thead><tr><th>Banker #</th><th>Date</th><th>Match</th><th>Selection</th><th>Odds</th><th>Model Prob</th><th>EV Edge</th><th>Confidence</th></tr></thead><tbody>';
    bD.forEach(x => {{ h += <tr><td class="font-bold text-amber-400"># + x.banker + </td><td> + x.date + </td><td class="font-semibold"> + x.match + </td><td><strong> + x.selection + </strong></td><td> + x.odds.toFixed(2) + </td><td> + x.model_prob + </td><td><span class="ev"> + x.ev_edge + </span></td><td><span class="gold"> + x.confidence + </span></td></tr>; }});
    document.getElementById('bCon').innerHTML = h + '</tbody></table>';
}}
function rG() {{
    let h = '<table><thead><tr><th>Date</th><th>League</th><th>Match</th><th>Selection</th><th>Odds</th><th>Model xG</th><th>Model Prob</th><th>EV Edge</th></tr></thead><tbody>';
    gD.forEach(x => {{ h += <tr><td> + x.date + </td><td> + x.league + </td><td class="font-semibold"> + x.match + </td><td><strong class="text-amber-400"> + x.selection + </strong></td><td> + x.odds.toFixed(2) + </td><td> + x.xg_projected + </td><td> + x.model_prob + </td><td><span class="ev"> + x.ev_edge + </span></td></tr>; }});
    document.getElementById('gCon').innerHTML = h + '</tbody></table>';
}}
function rC() {{
    let h = '<table><thead><tr><th>Date</th><th>Match</th><th>Selection</th><th>Odds</th><th>Avg Corners</th><th>Model Prob</th><th>EV Edge</th></tr></thead><tbody>';
    cD.forEach(x => {{ h += <tr><td> + x.date + </td><td class="font-semibold"> + x.match + </td><td><strong class="text-amber-400"> + x.selection + </strong></td><td> + x.odds.toFixed(2) + </td><td> + x.avg_corners + </td><td> + x.model_prob + </td><td><span class="ev"> + x.ev_edge + </span></td></tr>; }});
    document.getElementById('cCon').innerHTML = h + '</tbody></table>';
}}
rB(); rG(); rC();
</script>
</body>
</html>"""

@app.get("/api/bankers")
def get_bankers(): return COMBO_BANKERS

@app.get("/api/goal-count")
def get_goal_count(): return GOAL_COUNT_VALUE

@app.get("/api/corners")
def get_corners(): return CORNER_PREDICTIONS

@app.get("/", response_class=HTMLResponse)
def read_root(): return html
