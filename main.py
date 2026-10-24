from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="GEM V15.0 Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FULL_SLATE = [
    {"leg": 1, "match": "Arsenal vs Everton", "selection": "Arsenal Win", "market": "1X2", "odds": 1.36},
    {"leg": 2, "match": "Chelsea vs Tottenham", "selection": "Over 2.5 Goals", "market": "Total Goals", "odds": 1.62},
    {"leg": 3, "match": "Dortmund vs Frankfurt", "selection": "Dortmund Win or Draw", "market": "Double Chance", "odds": 1.28},
    {"leg": 4, "match": "Racing Santander vs Espanyol", "selection": "Espanyol Win or Draw", "market": "Double Chance", "odds": 1.35},
    {"leg": 5, "match": "Valencia vs Villarreal", "selection": "Both Teams to Score", "market": "BTTS", "odds": 1.70},
    {"leg": 6, "match": "Atletico Madrid vs Deportivo", "selection": "Atletico Madrid Win", "market": "1X2", "odds": 1.40},
    {"leg": 7, "match": "Koln vs Schalke 04", "selection": "Over 1.5 Goals", "market": "Total Goals", "odds": 1.25},
    {"leg": 8, "match": "Paderborn vs Hamburg", "selection": "Both Teams to Score", "market": "BTTS", "odds": 1.55},
    {"leg": 9, "match": "RB Leipzig vs Elversberg", "selection": "RB Leipzig Win", "market": "1X2", "odds": 1.30}
]

@app.get("/api/fixtures")
def get_fixtures():
    return {
        "status": "success",
        "slate": FULL_SLATE,
        "accumulators": {
            "six_fold": {"legs": "1-6", "odds": 8.92, "stake": 10.00, "return": 89.20},
            "nine_fold": {"legs": "1-9", "odds": 22.48, "stake": 5.00, "return": 112.40}
        }
    }

@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    return """<!DOCTYPE html>
<html>
<head>
    <title>GEM V15.0 Engine</title>
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
    <style>
        body { background-color: #121212; color: #ffffff; font-family: Arial, sans-serif; padding: 20px; }
        .btn { background-color: #00ff88; color: #000; border: none; padding: 12px 20px; font-weight: bold; cursor: pointer; border-radius: 4px; width: 100%; margin-bottom: 20px; }
        .card { background-color: #1e1e1e; padding: 12px; margin-bottom: 8px; border-radius: 6px; border-left: 4px solid #00ff88; }
        .acc-box { background-color: #1a2e22; padding: 15px; margin: 15px 0; border: 1px solid #00ff88; border-radius: 6px; }
    </style>
</head>
<body>
    <h1 style="color: #00ff88;">GEM V15.0 ENGINE</h1>
    <p style="color: #888;">QUANTITATIVE ACCUMULATOR PIPELINE</p>
    <button class="btn" onclick="fetchFixtures()">RUN QUANT ENGINE PIPELINE</button>
    
    <div id="acc-container"></div>
    <h2>Selected Slate (9 Legs)</h2>
    <div id="fixtures-container">Tap button above to load 6-fold and 9-fold accumulators.</div>

    <script>
        async function fetchFixtures() {
            const container = document.getElementById('fixtures-container');
            const accContainer = document.getElementById('acc-container');
            try {
                const response = await fetch('/api/fixtures?v=' + new Date().getTime());
                const result = await response.json();
                
                accContainer.innerHTML = `
                    <div class="acc-box">
                        <h3 style="color:#00ff88; margin-top:0;">⚡ 6-FOLD ACCUMULATOR</h3>
                        <p>Legs: <b>1 to 6</b> | Combined Odds: <b>${result.accumulators.six_fold.odds}</b></p>
                        <p>Recommended Stake: <b>£${result.accumulators.six_fold.stake}</b> ➔ Est Return: <b>£${result.accumulators.six_fold.return}</b></p>
                    </div>
                    <div class="acc-box">
                        <h3 style="color:#00ff88; margin-top:0;">🔥 9-FOLD ACCUMULATOR (FULL SLATE)</h3>
                        <p>Legs: <b>1 to 9</b> | Combined Odds: <b>${result.accumulators.nine_fold.odds}</b></p>
                        <p>Recommended Stake: <b>£${result.accumulators.nine_fold.stake}</b> ➔ Est Return: <b>£${result.accumulators.nine_fold.return}</b></p>
                    </div>
                `;

                container.innerHTML = result.slate.map(item => `
                    <div class="card">
                        <b>Leg ${item.leg}: ${item.match}</b><br/>
                        Selection: <span style="color:#00ff88;">${item.selection}</span> (${item.market}) @ ${item.odds}
                    </div>
                `).join('');
            } catch (err) {
                container.innerHTML = 'Error fetching slate.';
            }
        }
    </script>
</body>
</html>"""

from datetime import datetime, timezone
import asyncio
from contextlib import asynccontextmanager

def filter_active_slate(matches):
    active_matches = []
    now = datetime.now(timezone.utc)
    for match in matches:
        status = match.get("status", "")
        kickoff_str = match.get("kickoff_time")
        if status in ["FT", "AET", "PEN", "CANCELLED", "POSTPONED", "IN_PLAY"]:
            continue
        if kickoff_str:
            kickoff_dt = datetime.fromisoformat(kickoff_str.replace("Z", "+00:00"))
            if kickoff_dt <= now:
                continue
        active_matches.append(match)
    return active_matches


@app.get("/")
def read_root():
    return {"status": "GEM V15.0 Engine Live", "version": "15.0"}

