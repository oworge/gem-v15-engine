# -*- coding: utf-8 -*-
from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from datetime import datetime

app = FastAPI()

HTML_CONTENT = """<!DOCTYPE html>
<html>
<head>
    <title>GEM V15.0 + ScoreAI ENGINE</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="mobile-web-app-capable" content="yes">
    <link rel="manifest" href="/manifest.json">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #121212; color: #fff; padding: 15px; max-width: 800px; margin: auto; }
        .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #00ff88; padding-bottom: 10px; margin-bottom: 15px; }
        h1 { color: #00ff88; margin: 0; font-size: 22px; }
        .btn { background: #00ff88; color: #121212; border: none; padding: 10px 15px; font-weight: bold; border-radius: 6px; cursor: pointer; font-size: 14px; }
        .btn:active { background: #00cc6a; }
        .stake-box { background: #1e1e1e; padding: 12px; border-radius: 8px; margin-bottom: 15px; display: flex; align-items: center; justify-content: space-between; border: 1px solid #333; }
        .stake-box input { background: #121212; border: 1px solid #00ff88; color: #fff; padding: 8px; width: 90px; border-radius: 4px; font-size: 16px; text-align: right; font-weight: bold; }
        .acc-box { background: #1e1e1e; padding: 15px; margin-bottom: 15px; border-radius: 8px; border: 1px solid #00ff88; }
        .card { background: #1e1e1e; padding: 12px 15px; margin-bottom: 10px; border-radius: 8px; border-left: 4px solid #00ff88; display: flex; justify-content: space-between; align-items: center; }
        .badge { font-size: 10px; padding: 3px 6px; border-radius: 4px; font-weight: bold; text-transform: uppercase; margin-left: 5px; }
        .badge-upcoming { background: #333; color: #aaa; }
        .badge-scoreai { background: #00ff88; color: #121212; }
        .toast { position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background: #00ff88; color: #121212; padding: 10px 20px; border-radius: 20px; font-weight: bold; display: none; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>GEM V15.0 + ScoreAI</h1>
            <p style="margin:2px 0 0 0; font-size:12px; color:#aaa;">3-6-9 Tiered Engine with ScoreAI Modeling</p>
        </div>
        <button class="btn" onclick="copyBetSlip()">📋 Copy Slip</button>
    </div>

    <div class="stake-box">
        <span><b>Base Stake (£):</b></span>
        <input type="number" id="baseStake" value="10" min="1" oninput="recalculateReturns()">
    </div>

    <div id="acc-container"></div>

    <h3 style="margin-bottom:10px;">Active Slate (9 Legs + ScoreAI)</h3>
    <div id="fixtures-container">Loading slate...</div>

    <div id="toast" class="toast">Bet slip copied to clipboard!</div>

    <script>
        let globalData = null;

        async function fetchFixtures() {
            try {
                const response = await fetch('/api/fixtures?cb=' + new Date().getTime(), { cache: 'no-store' });
                globalData = await response.json();
                renderApp();
            } catch (err) {
                document.getElementById('fixtures-container').innerHTML = 'Error fetching slate.';
            }
        }

        function recalculateReturns() {
            const stakeInput = parseFloat(document.getElementById('baseStake').value) || 0;
            if (!globalData) return;

            const threeReturn = (stakeInput * globalData.accumulators.three_fold.odds).toFixed(2);
            const sixReturn = (stakeInput * globalData.accumulators.six_fold.odds).toFixed(2);
            const nineReturn = (stakeInput * globalData.accumulators.nine_fold.odds).toFixed(2);

            document.getElementById('acc-container').innerHTML = 
                '<div class="acc-box">' +
                    '<h3 style="color:#00ff88; margin-top:0; font-size:15px;">🎯 3-FOLD ACCUMULATOR (Legs 1-3)</h3>' +
                    '<p style="margin:4px 0; font-size:13px;">Odds: <b>' + globalData.accumulators.three_fold.odds + '</b> | Stake: <b>£' + stakeInput.toFixed(2) + '</b> ➔ Return: <b style="color:#00ff88;">£' + threeReturn + '</b></p>' +
                '</div>' +
                '<div class="acc-box">' +
                    '<h3 style="color:#00ff88; margin-top:0; font-size:15px;">⚡ 6-FOLD ACCUMULATOR (Legs 1-6)</h3>' +
                    '<p style="margin:4px 0; font-size:13px;">Odds: <b>' + globalData.accumulators.six_fold.odds + '</b> | Stake: <b>£' + stakeInput.toFixed(2) + '</b> ➔ Return: <b style="color:#00ff88;">£' + sixReturn + '</b></p>' +
                '</div>' +
                '<div class="acc-box">' +
                    '<h3 style="color:#00ff88; margin-top:0; font-size:15px;">🔥 9-FOLD ACCUMULATOR (Legs 1-9)</h3>' +
                    '<p style="margin:4px 0; font-size:13px;">Odds: <b>' + globalData.accumulators.nine_fold.odds + '</b> | Stake: <b>£' + stakeInput.toFixed(2) + '</b> ➔ Return: <b style="color:#00ff88;">£' + nineReturn + '</b></p>' +
                '</div>';
        }

        function renderApp() {
            recalculateReturns();
            const container = document.getElementById('fixtures-container');
            container.innerHTML = globalData.slate.map(item => 
                '<div class="card">' +
                    '<div>' +
                        '<div style="font-size:11px; color:#888; margin-bottom:2px;">LEG ' + item.leg + '</div>' +
                        '<b style="font-size:14px;">' + item.match + '</b><br/>' +
                        '<span style="font-size:13px; color:#00ff88;">' + item.selection + '</span> <span style="font-size:12px; color:#aaa;">(' + item.market + ')</span>' +
                    '</div>' +
                    '<div style="text-align:right;">' +
                        '<span class="badge badge-upcoming">' + item.status + '</span>' +
                        '<span class="badge badge-scoreai">AI: ' + item.scoreai_conf + '%</span>' +
                        '<div style="font-size:15px; font-weight:bold; margin-top:5px;">@ ' + item.odds + '</div>' +
                    '</div>' +
                '</div>'
            ).join('');
        }

        function copyBetSlip() {
            if (!globalData) return;
            const stakeInput = parseFloat(document.getElementById('baseStake').value) || 10;
            let text = "=== GEM V15.0 + SCOREAI SLIP ===\\n\\n";
            text += "🎯 3-Fold Odds: " + globalData.accumulators.three_fold.odds + " | Return: £" + (stakeInput * globalData.accumulators.three_fold.odds).toFixed(2) + "\\n";
            text += "⚡ 6-Fold Odds: " + globalData.accumulators.six_fold.odds + " | Return: £" + (stakeInput * globalData.accumulators.six_fold.odds).toFixed(2) + "\\n";
            text += "🔥 9-Fold Odds: " + globalData.accumulators.nine_fold.odds + " | Return: £" + (stakeInput * globalData.accumulators.nine_fold.odds).toFixed(2) + "\\n\\nSELECTIONS:\\n";
            globalData.slate.forEach(i => {
                text += "Leg " + i.leg + ": " + i.match + " -> " + i.selection + " (ScoreAI: " + i.scoreai_conf + "%) @ " + i.odds + "\\n";
            });
            navigator.clipboard.writeText(text).then(() => {
                const toast = document.getElementById('toast');
                toast.style.display = 'block';
                setTimeout(() => { toast.style.display = 'none'; }, 2000);
            });
        }

        fetchFixtures();
    </script>
</body>
</html>
"""

@app.get("/manifest.json")
async def manifest():
    return {"name": "GEM V15.0 ScoreAI", "short_name": "GEM+AI", "start_url": "/", "display": "standalone", "background_color": "#121212", "theme_color": "#00ff88", "icons": []}

@app.get("/", response_class=HTMLResponse)
async def read_index(response: Response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return HTML_CONTENT

@app.get("/api/fixtures")
async def get_fixtures(response: Response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    active_slate = [
        {"leg": 1, "match": "Chelsea vs Newcastle", "selection": "Chelsea Win", "market": "1X2", "odds": 1.75, "scoreai_conf": 84, "status": "UPCOMING"},
        {"leg": 2, "match": "Crystal Palace vs Liverpool", "selection": "Liverpool Win", "market": "1X2", "odds": 1.50, "scoreai_conf": 89, "status": "UPCOMING"},
        {"leg": 3, "match": "West Ham vs Manchester United", "selection": "Over 2.5 Goals", "market": "Total Goals", "odds": 1.70, "scoreai_conf": 79, "status": "UPCOMING"},
        {"leg": 4, "match": "Real Madrid vs Barcelona", "selection": "Over 1.5 Goals", "market": "Goals", "odds": 1.22, "scoreai_conf": 92, "status": "UPCOMING"},
        {"leg": 5, "match": "Inter Milan vs Juventus", "selection": "Inter Milan Win or Draw", "market": "Double Chance", "odds": 1.30, "scoreai_conf": 86, "status": "UPCOMING"},
        {"leg": 6, "match": "Monaco vs Lyon", "selection": "Both Teams to Score", "market": "BTTS", "odds": 1.65, "scoreai_conf": 81, "status": "UPCOMING"},
        {"leg": 7, "match": "Ajax vs Feyenoord", "selection": "Over 2.5 Goals", "market": "Total Goals", "odds": 1.60, "scoreai_conf": 78, "status": "UPCOMING"},
        {"leg": 8, "match": "Benfica vs Porto", "selection": "Benfica Win or Draw", "market": "Double Chance", "odds": 1.28, "scoreai_conf": 88, "status": "UPCOMING"},
        {"leg": 9, "match": "Sporting CP vs Braga", "selection": "Sporting CP Win", "market": "1X2", "odds": 1.55, "scoreai_conf": 85, "status": "UPCOMING"}
    ]
    return {
        "status": "success",
        "updated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "slate": active_slate,
        "accumulators": {
            "three_fold": {"legs": "1-3", "odds": 4.46},
            "six_fold": {"legs": "1-6", "odds": 8.15},
            "nine_fold": {"legs": "1-9", "odds": 36.42}
        }
    }
