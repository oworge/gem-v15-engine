import os

html_code = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Scorecast PRO</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #0b0f19; color: #f8fafc; font-family: system-ui, -apple-system, sans-serif; }
        .tab-btn { background: #1e293b; color: #94a3b8; border: none; padding: 10px 16px; font-size: 13px; font-weight: bold; border-radius: 8px; cursor: pointer; white-space: nowrap; }
        .tab-btn.active { background: #eab308; color: #0b0f19; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        table { width: 100%; border-collapse: collapse; font-size: 13px; margin-top: 10px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #1e293b; }
        th { background: #111827; color: #9ca3af; font-weight: 600; }
        .ev-badge { background: #065f46; color: #34d399; padding: 3px 8px; border-radius: 6px; font-weight: bold; font-size: 11px; }
        .badge-gold { background: #b45309; color: #fef3c7; padding: 3px 8px; border-radius: 6px; font-weight: bold; font-size: 11px; }
    </style>
</head>
<body class="bg-slate-950 min-h-screen pb-12">
    <div class="max-w-6xl mx-auto px-4 pt-6 flex justify-between items-center">
        <div class="px-3.5 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-semibold">
            AI ANALYSIS ENGINE ACTIVE
        </div>
        <div class="flex items-center gap-2">
            <span class="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block animate-pulse"></span>
            <span class="text-xs text-slate-300">10K Active Users</span>
        </div>
    </div>

    <div class="max-w-6xl mx-auto px-4 text-center mt-4">
        <h1 class="text-3xl font-extrabold text-white">
            AI Scorecast <span class="text-amber-400">PRO</span>
        </h1>
        <p class="text-sm text-slate-300 mt-1">Manage predictions with AI VIP analyses.</p>
    </div>

    <div class="max-w-6xl mx-auto px-4 mt-8">
        <div class="flex gap-2 bg-slate-900 p-2 rounded-xl border border-slate-800 overflow-x-auto">
            <button class="tab-btn active" onclick="switchTab('bTab', this)">AI Combo Banker (7)</button>
            <button class="tab-btn" onclick="switchTab('fTab', this)">3-6-9 Fold Slate</button>
            <button class="tab-btn" onclick="switchTab('bbTab', this)">Bet Builder</button>
            <button class="tab-btn" onclick="switchTab('gTab', this)">Goal Count (Over 2.5 Value)</button>
            <button class="tab-btn" onclick="switchTab('cTab', this)">Corner Predictions</button>
        </div>
    </div>

    <div id="bTab" class="tab-content active max-w-6xl mx-auto px-4 mt-6">
        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6">
            <h2 class="text-lg font-bold text-white mb-2">7 AI Automated Selected Bankers</h2>
            <div id="bCon" class="overflow-x-auto text-slate-400">Loading bankers...</div>
        </div>
    </div>

    <div id="fTab" class="tab-content max-w-6xl mx-auto px-4 mt-6">
        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6">
            <h2 class="text-lg font-bold text-white mb-2">3-6-9 Fold Accumulator Tiers</h2>
            <div id="fCon" class="overflow-x-auto text-slate-400">Loading accumulators...</div>
        </div>
    </div>

    <div id="bbTab" class="tab-content max-w-6xl mx-auto px-4 mt-6">
        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6">
            <h2 class="text-lg font-bold text-white mb-2">AI Recommended Bet Builders</h2>
            <div id="bbCon" class="overflow-x-auto text-slate-400">Loading bet builders...</div>
        </div>
    </div>

    <div id="gTab" class="tab-content max-w-6xl mx-auto px-4 mt-6">
        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6">
            <h2 class="text-lg font-bold text-white mb-2">Goal Count Predictions (Over 2.5 Value Finder)</h2>
            <div id="gCon" class="overflow-x-auto text-slate-400">Loading goal predictions...</div>
        </div>
    </div>

    <div id="cTab" class="tab-content max-w-6xl mx-auto px-4 mt-6">
        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6">
            <h2 class="text-lg font-bold text-white mb-2">Corner Count Predictions</h2>
            <div id="cCon" class="overflow-x-auto text-slate-400">Loading corner predictions...</div>
        </div>
    </div>

    <script>
        function switchTab(t, b) {
            var tabs = document.getElementsByClassName('tab-content');
            for(var i=0; i<tabs.length; i++) tabs[i].classList.remove('active');
            var btns = document.getElementsByClassName('tab-btn');
            for(var j=0; j<btns.length; j++) btns[j].classList.remove('active');
            document.getElementById(t).classList.add('active');
            if(b) b.classList.add('active');
        }

        function renderTable(headers, rows) {
            var html = '<table><thead><tr>';
            for(var i=0; i<headers.length; i++) html += '<th>' + headers[i] + '</th>';
            html += '</tr></thead><tbody>';
            for(var j=0; j<rows.length; j++) {
                html += '<tr>';
                for(var k=0; k<rows[j].length; k++) html += '<td>' + rows[j][k] + '</td>';
                html += '</tr>';
            }
            return html + '</tbody></table>';
        }

        function loadData() {
            Promise.all([
                fetch('/api/bankers').then(function(r){ return r.json(); }),
                fetch('/api/folds').then(function(r){ return r.json(); }),
                fetch('/api/bet-builders').then(function(r){ return r.json(); }),
                fetch('/api/goal-count').then(function(r){ return r.json(); }),
                fetch('/api/corners').then(function(r){ return r.json(); })
            ]).then(function(res) {
                var b = res[0], f = res[1], bb = res[2], g = res[3], c = res[4];

                var bRows = b.map(function(x){
                    return ['<span class="font-bold text-amber-400">#' + x.banker + '</span>', x.date, '<span class="font-semibold">' + x.match + '</span>', '<strong>' + x.selection + '</strong>', x.odds.toFixed(2), x.model_prob, '<span class="ev-badge">' + x.ev_edge + '</span>', '<span class="badge-gold">' + x.confidence + '</span>'];
                });
                document.getElementById('bCon').innerHTML = renderTable(['Banker #', 'Date', 'Match', 'Selection', 'Odds', 'Model Prob', 'EV Edge', 'Confidence'], bRows);

                var fRows = f.map(function(x){
                    return ['<span class="font-bold text-amber-400">' + x.tier + '</span>', '<span class="font-bold text-white">' + x.odds + '</span>', x.combined_prob, x.legs];
                });
                document.getElementById('fCon').innerHTML = renderTable(['Tier', 'Combined Odds', 'Model Prob', 'Included Legs'], fRows);

                var bbRows = bb.map(function(x){
                    return ['<span class="font-semibold">' + x.match + '</span>', '<strong class="text-amber-400">' + x.builder + '</strong>', '<span class="font-bold text-white">' + x.combined_odds.toFixed(2) + '</span>', '<span class="ev-badge">' + x.ev_edge + '</span>'];
                });
                document.getElementById('bbCon').innerHTML = renderTable(['Match', 'Bet Builder Combo', 'Combined Odds', 'EV Edge'], bbRows);

                var gRows = g.map(function(x){
                    return [x.date, x.league, '<span class="font-semibold">' + x.match + '</span>', '<strong class="text-amber-400">' + x.selection + '</strong>', x.odds.toFixed(2), x.xg_projected, x.model_prob, '<span class="ev-badge">' + x.ev_edge + '</span>'];
                });
                document.getElementById('gCon').innerHTML = renderTable(['Date', 'League', 'Match', 'Selection', 'Odds', 'Model xG', 'Model Prob', 'EV Edge'], gRows);

                var cRows = c.map(function(x){
                    return [x.date, '<span class="font-semibold">' + x.match + '</span>', '<strong class="text-amber-400">' + x.selection + '</strong>', x.odds.toFixed(2), x.avg_corners, x.model_prob, '<span class="ev-badge">' + x.ev_edge + '</span>'];
                });
                document.getElementById('cCon').innerHTML = renderTable(['Date', 'Match', 'Selection', 'Odds', 'Avg Corners', 'Model Prob', 'EV Edge'], cRows);
            });
        }
        window.onload = loadData;
    </script>
</body>
</html>"""

py_code = """from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI(title="AI Scorecast PRO")

COMBO_BANKERS = [
    {"banker": 1, "date": "2026-10-27", "match": "Sevilla vs. Osasuna", "selection": "Sevilla Win or Draw (1X)", "odds": 1.25, "model_prob": "84.0%", "ev_edge": "+5.00%", "confidence": "HIGH BANKER"},
    {"banker": 2, "date": "2026-10-27", "match": "Galatasaray vs. Fenerbahce", "selection": "Over 1.5 Match Goals", "odds": 1.30, "model_prob": "82.0%", "ev_edge": "+6.60%", "confidence": "HIGH BANKER"},
    {"banker": 3, "date": "2026-10-27", "match": "Santa Clara vs. Benfica", "selection": "Benfica Win", "odds": 1.36, "model_prob": "77.0%", "ev_edge": "+4.72%", "confidence": "SOLID BANKER"},
    {"banker": 4, "date": "2026-10-27", "match": "Fleetwood vs. Arsenal", "selection": "Arsenal Win", "odds": 1.18, "model_prob": "91.0%", "ev_edge": "+7.38%", "confidence": "HIGH BANKER"},
    {"banker": 5, "date": "2026-10-27", "match": "Sabah vs. Borussia Dortmund", "selection": "Over 2.5 Match Goals", "odds": 1.40, "model_prob": "76.0%", "ev_edge": "+6.40%", "confidence": "SOLID BANKER"},
    {"banker": 6, "date": "2026-10-27", "match": "PSG vs. Barcelona", "selection": "Over 1.5 Match Goals", "odds": 1.22, "model_prob": "85.0%", "ev_edge": "+5.25%", "confidence": "HIGH BANKER"},
    {"banker": 7, "date": "2026-10-28", "match": "Manchester City vs. Brighton", "selection": "Manchester City Win", "odds": 1.32, "model_prob": "80.0%", "ev_edge": "+5.60%", "confidence": "HIGH BANKER"}
]

GOAL_COUNT_VALUE = [
    {"date": "2026-10-27", "league": "Brazil Serie A U20", "match": "Cruzeiro U20 vs. Atletico Mineiro U20", "selection": "Over 2.5 Goals", "odds": 1.57, "model_prob": "75.0%", "xg_projected": "3.20", "ev_edge": "+17.75%"},
    {"date": "2026-10-27", "league": "Friendly", "match": "Sabah vs. Borussia Dortmund", "selection": "Over 2.5 Goals", "odds": 1.40, "model_prob": "76.0%", "xg_projected": "3.35", "ev_edge": "+6.40%"},
    {"date": "2026-10-27", "league": "UEFA Champions League", "match": "Real Madrid vs. Juventus", "selection": "Over 2.5 Goals", "odds": 1.68, "model_prob": "68.0%", "xg_projected": "2.95", "ev_edge": "+14.24%"},
    {"date": "2026-10-28", "league": "EFL Cup", "match": "Bournemouth vs. Aston Villa", "selection": "Over 2.5 Goals", "odds": 1.62, "model_prob": "70.0%", "xg_projected": "3.10", "ev_edge": "+13.40%"},
    {"date": "2026-10-28", "league": "EFL Cup", "match": "Manchester City vs. Brighton", "selection": "Over 2.5 Goals", "odds": 1.50, "model_prob": "74.0%", "xg_projected": "3.45", "ev_edge": "+11.00%"},
    {"date": "2026-10-28", "league": "EFL Cup", "match": "Liverpool vs. Chelsea", "selection": "Over 2.5 Goals", "odds": 1.55, "model_prob": "72.0%", "xg_projected": "3.25", "ev_edge": "+11.60%"}
]

CORNER_PREDICTIONS = [
    {"date": "2026-10-27", "match": "Sevilla vs. Osasuna", "selection": "Sevilla Over 4.5 Corners", "odds": 1.44, "model_prob": "78.0%", "avg_corners": "6.2", "ev_edge": "+12.32%"},
    {"date": "2026-10-27", "match": "Galatasaray vs. Fenerbahce", "selection": "Over 9.5 Match Corners", "odds": 1.72, "model_prob": "65.0%", "avg_corners": "11.4", "ev_edge": "+11.80%"},
    {"date": "2026-10-27", "match": "PSG vs. Barcelona", "selection": "PSG Over 5.5 Corners", "odds": 1.65, "model_prob": "67.0%", "avg_corners": "7.1", "ev_edge": "+10.55%"},
    {"date": "2026-10-28", "match": "Liverpool vs. Chelsea", "selection": "Over 9.5 Match Corners", "odds": 1.60, "model_prob": "69.0%", "avg_corners": "10.8", "ev_edge": "+10.40%"},
    {"date": "2026-10-28", "match": "Manchester City vs. Brighton", "selection": "Man City Over 6.5 Corners", "odds": 1.53, "model_prob": "72.0%", "avg_corners": "8.3", "ev_edge": "+10.16%"}
]

FOLDS_369 = [
    {"tier": "3-Fold Conservative", "odds": "2.21", "combined_prob": "45.2%", "legs": "Sevilla 1X, Galatasaray Over 1.5, Arsenal Win"},
    {"tier": "6-Fold Balanced", "odds": "5.62", "combined_prob": "22.8%", "legs": "Sevilla 1X, Galatasaray Over 1.5, Benfica Win, Arsenal Win, Dortmund Over 2.5, PSG Over 1.5"},
    {"tier": "9-Fold High Yield Slate", "odds": "14.28", "combined_prob": "10.4%", "legs": "Sevilla 1X, Galatasaray Over 1.5, Benfica Win, Arsenal Win, Dortmund Over 2.5, PSG Over 1.5, Man City Win, Cruzeiro U20 Over 2.5, Real Madrid Over 2.5"}
]

BET_BUILDERS = [
    {"match": "Sevilla vs. Osasuna", "builder": "Sevilla 1X + Over 4.5 Sevilla Corners + Under 4.5 Goals", "combined_odds": 2.10, "ev_edge": "+8.40%"},
    {"match": "PSG vs. Barcelona", "builder": "Over 1.5 Goals + PSG Over 5.5 Corners + Both Teams to Score", "combined_odds": 2.85, "ev_edge": "+11.20%"},
    {"match": "Liverpool vs. Chelsea", "builder": "Over 2.5 Goals + Over 9.5 Match Corners + Salah 1+ Shot on Target", "combined_odds": 3.10, "ev_edge": "+14.50%"}
]

@app.get("/api/bankers")
def get_bankers(): return COMBO_BANKERS

@app.get("/api/folds")
def get_folds(): return FOLDS_369

@app.get("/api/bet-builders")
def get_bet_builders(): return BET_BUILDERS

@app.get("/api/goal-count")
def get_goal_count(): return GOAL_COUNT_VALUE

@app.get("/api/corners")
def get_corners(): return CORNER_PREDICTIONS

@app.get("/")
def read_root(): return FileResponse("index.html")
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_code)

for file_name in ["main.py", "app.py", "server.py"]:
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(py_code)

print("Generator executed successfully.")