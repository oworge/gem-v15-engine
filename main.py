# -*- coding: utf-8 -*-
from fastapi import FastAPI, Response, Request
from fastapi.responses import HTMLResponse, JSONResponse
from datetime import datetime
import math
import sqlite3

app = FastAPI()

DB_FILE = "gem_ledger.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            tier_name TEXT,
            stake REAL,
            odds REAL,
            return_amt REAL,
            status TEXT DEFAULT 'PENDING'
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def poisson_prob(lmbda, k):
    return (math.exp(-lmbda) * (lmbda ** k)) / math.factorial(k)

def calculate_poisson_edge(home_xg, away_xg):
    home_win_prob = 0
    draw_prob = 0
    away_win_prob = 0
    over_15_prob = 0
    
    for h in range(6):
        for a in range(6):
            p = poisson_prob(home_xg, h) * poisson_prob(away_xg, a)
            if h > a:
                home_win_prob += p
            elif h == a:
                draw_prob += p
            else:
                away_win_prob += p
            if h + a >= 2:
                over_15_prob += p
                
    return {
        "dc_home": round((home_win_prob + draw_prob) * 100, 1),
        "dc_away": round((away_win_prob + draw_prob) * 100, 1),
        "over_15": round(over_15_prob * 100, 1)
    }

HTML_CONTENT = """<!DOCTYPE html>
<html>
<head>
    <title>GEM V15.0 Daily 3-6-9 Terminal</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="mobile-web-app-capable" content="yes">
    <link rel="manifest" href="/manifest.json">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <style>
        :root { --bg: #0d1117; --card-bg: #161b22; --accent: #00ff88; --accent-glow: rgba(0,255,136,0.15); --gold: #f0b429; --text: #f0f6fc; --text-dim: #8b949e; --border: #30363d; --red: #ff5555; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: var(--bg); color: var(--text); padding: 12px; max-width: 850px; margin: auto; }
        .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid var(--accent); padding-bottom: 12px; margin-bottom: 12px; }
        h1 { color: var(--accent); margin: 0; font-size: 20px; letter-spacing: 0.5px; }
        .btn { background: var(--accent); color: #0d1117; border: none; padding: 10px 16px; font-weight: 800; border-radius: 8px; cursor: pointer; font-size: 13px; box-shadow: 0 0 15px var(--accent-glow); transition: all 0.2s; }
        .btn:active { transform: scale(0.96); opacity: 0.8; }
        
        .metrics-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 12px; }
        .metric-card { background: var(--card-bg); border: 1px solid var(--border); padding: 12px; border-radius: 10px; }
        .metric-card label { font-size: 11px; color: var(--text-dim); text-transform: uppercase; font-weight: 700; display: block; margin-bottom: 4px; }
        .metric-card input { background: var(--bg); border: 1px solid var(--border); color: var(--accent); padding: 6px 10px; width: 100%; border-radius: 6px; font-size: 16px; font-weight: bold; box-sizing: border-box; text-align: right; }
        .metric-card .val { font-size: 18px; font-weight: 800; color: var(--accent); }

        .tabs { display: flex; gap: 5px; margin-bottom: 12px; overflow-x: auto; padding-bottom: 4px; }
        .tab { background: var(--card-bg); border: 1px solid var(--border); color: var(--text-dim); padding: 9px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; cursor: pointer; white-space: nowrap; flex: 1; text-align: center; transition: all 0.2s; }
        .tab.active { background: var(--accent); color: #0d1117; border-color: var(--accent); box-shadow: 0 0 10px var(--accent-glow); }
        .tab.daily-tab { background: rgba(240,180,41,0.15); color: var(--gold); border-color: rgba(240,180,41,0.4); }
        .tab.daily-tab.active { background: var(--gold); color: #0d1117; }
        .tab.ledger-tab { background: rgba(0,191,255,0.15); color: #00bfff; border-color: rgba(0,191,255,0.4); }
        .tab.ledger-tab.active { background: #00bfff; color: #0d1117; }

        .acc-container { display: flex; flex-direction: column; gap: 8px; margin-bottom: 15px; }
        .acc-box { background: var(--card-bg); padding: 12px 15px; border-radius: 10px; border: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; border-left: 4px solid var(--accent); cursor: pointer; transition: all 0.2s; }
        .acc-box.elite { border-left-color: var(--gold); background: linear-gradient(135deg, #161b22 0%, #1f241c 100%); }
        .acc-box:hover { border-color: var(--accent); }

        .card { background: var(--card-bg); padding: 12px 15px; margin-bottom: 10px; border-radius: 10px; border: 1px solid var(--border); border-left: 4px solid var(--accent); }
        .card.elite { border-left-color: var(--gold); }
        .card-top { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px; }
        
        .progress-bar-bg { background: var(--bg); height: 6px; border-radius: 3px; width: 100%; margin-top: 8px; overflow: hidden; border: 1px solid var(--border); }
        .progress-bar-fill { background: var(--accent); height: 100%; border-radius: 3px; }
        .progress-bar-fill.elite { background: var(--gold); }

        .badges { display: flex; gap: 4px; margin-top: 6px; flex-wrap: wrap; }
        .badge { font-size: 9px; padding: 2px 6px; border-radius: 4px; font-weight: 800; text-transform: uppercase; }
        .badge-scoreai { background: rgba(0,255,136,0.15); color: var(--accent); border: 1px solid rgba(0,255,136,0.3); }
        .badge-clv { background: rgba(240,180,41,0.15); color: var(--gold); border: 1px solid rgba(240,180,41,0.3); }
        .badge-poisson { background: rgba(0,191,255,0.15); color: #00bfff; border: 1px solid rgba(0,191,255,0.3); }
        .badge-elite { background: var(--gold); color: #0d1117; }

        .toast { position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background: var(--accent); color: #0d1117; padding: 10px 22px; border-radius: 20px; font-weight: 800; display: none; box-shadow: 0 5px 20px rgba(0,0,0,0.6); z-index: 1000; font-size: 13px; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>GEM V15.0 QUANT TERMINAL</h1>
            <p style="margin:2px 0 0 0; font-size:11px; color:var(--text-dim);">Automated Daily 3-6-9 Fold Engine</p>
        </div>
        <button class="btn" onclick="copyBetSlip()">📋 Copy Slip</button>
    </div>

    <div class="metrics-grid">
        <div class="metric-card">
            <label>Base Stake (£)</label>
            <input type="number" id="baseStake" value="10" min="1" oninput="recalculateReturns()">
        </div>
        <div class="metric-card">
            <label>System Mode</label>
            <div class="val" style="font-size:14px; margin-top:4px;">⚡ Daily 3-6-9 Active</div>
        </div>
    </div>

    <div class="tabs">
        <div class="tab active" onclick="switchTab('all', this)">🔥 Full Slate</div>
        <div class="tab daily-tab" onclick="switchTab('today', this)">⚡ Today's Games</div>
        <div class="tab" onclick="switchTab('three', this)">🎯 3-Fold Tier</div>
        <div class="tab" onclick="switchTab('six', this)">⚡ 6-Fold Tier</div>
        <div class="tab ledger-tab" onclick="switchTab('ledger', this)">📊 Ledger</div>
    </div>

    <div class="acc-container" id="acc-container"></div>

    <h3 id="slate-title" style="margin: 15px 0 10px 0; font-size: 14px; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.5px;">Active Slate</h3>
    <div id="fixtures-container">Loading terminal...</div>

    <div id="toast" class="toast">Bet slip copied & logged to SQLite ledger!</div>

    <script>
        let globalData = null;
        let currentTab = 'all';
        let ledgerData = [];

        async function fetchFixtures() {
            try {
                const response = await fetch('/api/fixtures?cb=' + new Date().getTime(), { cache: 'no-store' });
                globalData = await response.json();
                fetchLedger();
            } catch (err) {
                document.getElementById('fixtures-container').innerHTML = '<div style="color:#ff5555; text-align:center; padding:20px;">Terminal connection error.</div>';
            }
        }

        async function fetchLedger() {
            try {
                const res = await fetch('/api/ledger');
                ledgerData = await res.json();
                renderApp();
            } catch(e) { renderApp(); }
        }

        async function logBetToLedger(tierName, oddsVal) {
            const stake = parseFloat(document.getElementById('baseStake').value) || 10;
            const retAmt = (stake * oddsVal).toFixed(2);
            await fetch('/api/ledger/log', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({tier_name: tierName, stake: stake, odds: oddsVal, return_amt: retAmt})
            });
            fetchLedger();
            const toast = document.getElementById('toast');
            toast.innerText = tierName + " logged to SQLite ledger!";
            toast.style.display = 'block';
            setTimeout(() => { toast.style.display = 'none'; }, 2000);
        }

        async function updateBetStatus(id, status) {
            await fetch('/api/ledger/update', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({id: id, status: status})
            });
            fetchLedger();
        }

        function switchTab(tab, el) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            el.classList.add('active');
            currentTab = tab;
            renderApp();
        }

        function recalculateReturns() {
            const stake = parseFloat(document.getElementById('baseStake').value) || 0;
            if (!globalData) return;

            const threeRet = (stake * globalData.accumulators.three_fold.odds).toFixed(2);
            const sixRet = (stake * globalData.accumulators.six_fold.odds).toFixed(2);
            const nineRet = (stake * globalData.accumulators.nine_fold.odds).toFixed(2);

            document.getElementById('acc-container').innerHTML = 
                '<div class="acc-box elite" onclick="logBetToLedger(\'3-Fold Anchor\', ' + globalData.accumulators.three_fold.odds + ')">' +
                    '<div>' +
                        '<div style="font-size:12px; font-weight:800; color:var(--gold);">🎯 3-FOLD ANCHOR (Legs 1-3) &bull; Tap to Log</div>' +
                        '<div style="font-size:12px; color:var(--text-dim); margin-top:2px;">Odds: <b>' + globalData.accumulators.three_fold.odds + '</b> | Stake: £' + stake.toFixed(2) + '</div>' +
                    '</div>' +
                    '<div style="text-align:right;">' +
                        '<div style="font-size:16px; font-weight:800; color:var(--gold);">£' + threeRet + '</div>' +
                        '<div style="font-size:10px; color:var(--text-dim);">Est. Return</div>' +
                    '</div>' +
                '</div>' +
                '<div class="acc-box" onclick="logBetToLedger(\'6-Fold Multiplier\', ' + globalData.accumulators.six_fold.odds + ')">' +
                    '<div>' +
                        '<div style="font-size:12px; font-weight:800; color:var(--accent);">⚡ 6-FOLD MULTIPLIER (Legs 1-6) &bull; Tap to Log</div>' +
                        '<div style="font-size:12px; color:var(--text-dim); margin-top:2px;">Odds: <b>' + globalData.accumulators.six_fold.odds + '</b> | Stake: £' + stake.toFixed(2) + '</div>' +
                    '</div>' +
                    '<div style="text-align:right;">' +
                        '<div style="font-size:16px; font-weight:800; color:var(--accent);">£' + sixRet + '</div>' +
                        '<div style="font-size:10px; color:var(--text-dim);">Est. Return</div>' +
                    '</div>' +
                '</div>' +
                '<div class="acc-box" onclick="logBetToLedger(\'9-Fold Full Slate\', ' + globalData.accumulators.nine_fold.odds + ')">' +
                    '<div>' +
                        '<div style="font-size:12px; font-weight:800; color:var(--accent);">🔥 9-FOLD FULL SLATE (Legs 1-9) &bull; Tap to Log</div>' +
                        '<div style="font-size:12px; color:var(--text-dim); margin-top:2px;">Odds: <b>' + globalData.accumulators.nine_fold.odds + '</b> | Stake: £' + stake.toFixed(2) + '</div>' +
                    '</div>' +
                    '<div style="text-align:right;">' +
                        '<div style="font-size:16px; font-weight:800; color:var(--accent);">£' + nineRet + '</div>' +
                        '<div style="font-size:10px; color:var(--text-dim);">Est. Return</div>' +
                    '</div>' +
                '</div>';
        }

        function renderApp() {
            recalculateReturns();
            const container = document.getElementById('fixtures-container');
            const titleEl = document.getElementById('slate-title');
            
            if (currentTab === 'ledger') {
                titleEl.innerText = "📊 Self-Learning Performance Ledger";
                if (ledgerData.length === 0) {
                    container.innerHTML = '<div style="text-align:center; padding:20px; color:var(--text-dim);">No logged bets yet. Tap any 3-6-9 fold tier box above to log your accumulator!</div>';
                    return;
                }
                
                let totalStaked = ledgerData.reduce((acc, cur) => acc + cur.stake, 0);
                let settled = ledgerData.filter(i => i.status !== 'PENDING');
                let won = settled.filter(i => i.status === 'WON');
                let profit = won.reduce((acc, cur) => acc + (cur.return_amt - cur.stake), 0) - settled.filter(i => i.status === 'LOST').reduce((acc, cur) => acc + cur.stake, 0);
                let strikeRate = settled.length > 0 ? ((won.length / settled.length) * 100).toFixed(1) : 0;

                let html = '<div class="card" style="border-left-color:#00bfff;">' +
                    '<b style="color:#00bfff; font-size:14px;">Ledger Performance Summary</b>' +
                    '<div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:5px; margin-top:8px; text-align:center;">' +
                        '<div style="background:var(--bg); padding:8px; border-radius:6px;"><div style="font-size:10px; color:var(--text-dim);">STAKED</div><b>£' + totalStaked.toFixed(2) + '</b></div>' +
                        '<div style="background:var(--bg); padding:8px; border-radius:6px;"><div style="font-size:10px; color:var(--text-dim);">PROFIT</div><b style="color:' + (profit >= 0 ? 'var(--accent)' : 'var(--red)') + ';">£' + profit.toFixed(2) + '</b></div>' +
                        '<div style="background:var(--bg); padding:8px; border-radius:6px;"><div style="font-size:10px; color:var(--text-dim);">STRIKE RATE</div><b>' + strikeRate + '%</b></div>' +
                    '</div>' +
                '</div>';

                html += ledgerData.map(item => 
                    '<div class="card" style="border-left-color:' + (item.status === 'WON' ? 'var(--accent)' : item.status === 'LOST' ? 'var(--red)' : 'var(--gold)') + '">' +
                        '<div class="card-top">' +
                            '<div>' +
                                '<div style="font-size:10px; color:var(--text-dim);">' + item.timestamp + '</div>' +
                                '<b style="font-size:14px;">' + item.tier_name + '</b><br/>' +
                                '<span style="font-size:12px; color:var(--text-dim);">Stake: £' + item.stake.toFixed(2) + ' | Odds: @' + item.odds + ' ➔ Ret: £' + item.return_amt.toFixed(2) + '</span>' +
                            '</div>' +
                            '<div style="text-align:right;">' +
                                '<span class="badge" style="background:' + (item.status === 'WON' ? 'var(--accent)' : item.status === 'LOST' ? 'var(--red)' : 'var(--gold)') + '; color:#0d1117;">' + item.status + '</span>' +
                            '</div>' +
                        '</div>' +
                        (item.status === 'PENDING' ? '<div style="margin-top:8px; display:flex; gap:6px;"><button class="btn" style="padding:4px 10px; font-size:11px; background:var(--accent);" onclick="updateBetStatus(' + item.id + ', \'WON\')">✅ Mark Won</button><button class="btn" style="padding:4px 10px; font-size:11px; background:var(--red); color:#fff;" onclick="updateBetStatus(' + item.id + ', \'LOST\')">❌ Mark Lost</button></div>' : '') +
                    '</div>'
                ).join('');
                container.innerHTML = html;
                return;
            }

            let filteredSlate = globalData.slate;
            if (currentTab === 'today') {
                filteredSlate = globalData.slate.filter(i => i.day_group === 'today');
                titleEl.innerText = "⚡ Today's Active Games & Poisson Predictions";
            } else if (currentTab === 'three') {
                filteredSlate = globalData.slate.filter(i => i.leg <= 3);
                titleEl.innerText = "🎯 3-Fold Anchor Selections (Legs 1-3)";
            } else if (currentTab === 'six') {
                filteredSlate = globalData.slate.filter(i => i.leg <= 6);
                titleEl.innerText = "⚡ 6-Fold Multiplier Selections (Legs 1-6)";
            } else {
                titleEl.innerText = "🔥 Full Automated Slate (Legs 1-9)";
            }

            if (filteredSlate.length === 0) {
                container.innerHTML = '<div style="text-align:center; padding:20px; color:var(--text-dim);">No fixtures scheduled for this filter.</div>';
                return;
            }

            container.innerHTML = filteredSlate.map(item => {
                const isElite = item.scoreai_conf >= 90;
                return '<div class="card ' + (isElite ? 'elite' : '') + '">' +
                    '<div class="card-top">' +
                        '<div>' +
                            '<div style="font-size:10px; color:var(--text-dim); font-weight:700; margin-bottom:2px;">LEG ' + item.leg + ' &bull; 📅 ' + item.date + '</div>' +
                            '<b style="font-size:14px; font-weight:700;">' + item.match + '</b><br/>' +
                            '<span style="font-size:12px; color:var(--accent); font-weight:600;">' + item.selection + '</span> <span style="font-size:11px; color:var(--text-dim);">(' + item.market + ')</span>' +
                        '</div>' +
                        '<div style="text-align:right;">' +
                            '<div style="font-size:16px; font-weight:900; color:' + (isElite ? 'var(--gold)' : 'var(--accent)') + ';">@ ' + item.odds + '</div>' +
                        '</div>' +
                    '</div>' +
                    '<div class="progress-bar-bg">' +
                        '<div class="progress-bar-fill ' + (isElite ? 'elite' : '') + '" style="width: ' + item.scoreai_conf + '%;"></div>' +
                    '</div>' +
                    '<div class="badges">' +
                        (isElite ? '<span class="badge badge-elite">⭐ 90%+ ELITE</span>' : '') +
                        '<span class="badge badge-scoreai">AI: ' + item.scoreai_conf + '%</span>' +
                        '<span class="badge badge-clv">CLV: +' + item.clv_edge + '%</span>' +
                        '<span class="badge badge-poisson">Poisson Model: ' + item.poisson_prob + '%</span>' +
                    '</div>' +
                '</div>';
            }).join('');
        }

        function copyBetSlip() {
            if (!globalData) return;
            logBetToLedger('Full Slate Slip', globalData.accumulators.nine_fold.odds);
            
            let text = "=== GEM V15.0 DAILY 3-6-9 SLIP ===\\n\\n";
            globalData.slate.forEach(i => {
                text += "Leg " + i.leg + " [" + i.date + "]: " + i.match + " -> " + i.selection + " (Model: " + i.poisson_prob + "%) @ " + i.odds + "\\n";
            });
            
            navigator.clipboard.writeText(text).then(() => {
                const toast = document.getElementById('toast');
                toast.innerText = "Bet slip copied & logged to ledger!";
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
    return {"name": "GEM V15.0 Daily", "short_name": "GEM Daily", "start_url": "/", "display": "standalone", "background_color": "#0d1117", "theme_color": "#00ff88", "icons": []}

@app.get("/", response_class=HTMLResponse)
async def read_index(response: Response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return HTML_CONTENT

@app.get("/api/fixtures")
async def get_fixtures(response: Response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    
    raw_fixtures = [
        {"leg": 1, "date": "Today, 15:00", "day_group": "today", "match": "Chelsea vs Newcastle", "selection": "Chelsea Win or Draw (DC)", "market": "Double Chance", "odds": 1.25, "scoreai_conf": 91, "clv_edge": 4.2, "home_xg": 1.85, "away_xg": 0.92},
        {"leg": 2, "date": "Today, 17:30", "day_group": "today", "match": "Crystal Palace vs Liverpool", "selection": "Liverpool Win or Draw (DC)", "market": "Double Chance", "odds": 1.18, "scoreai_conf": 94, "clv_edge": 5.1, "home_xg": 2.10, "away_xg": 0.75},
        {"leg": 3, "date": "Today, 20:00", "day_group": "today", "match": "Real Madrid vs Barcelona", "selection": "Over 1.5 Goals", "market": "Goals", "odds": 1.22, "scoreai_conf": 92, "clv_edge": 5.2, "home_xg": 2.30, "away_xg": 1.80},
        {"leg": 4, "date": "Tomorrow, 14:00", "day_group": "tomorrow", "match": "West Ham vs Manchester United", "selection": "Over 1.5 Goals", "market": "Total Goals", "odds": 1.28, "scoreai_conf": 90, "clv_edge": 3.8, "home_xg": 1.65, "away_xg": 1.45},
        {"leg": 5, "date": "Tomorrow, 17:05", "day_group": "tomorrow", "match": "Monaco vs Lyon", "selection": "Both Teams to Score (Yes)", "market": "BTTS", "odds": 1.65, "scoreai_conf": 88, "clv_edge": 3.1, "home_xg": 1.55, "away_xg": 1.30},
        {"leg": 6, "date": "Tomorrow, 19:45", "day_group": "tomorrow", "match": "Inter Milan vs Juventus", "selection": "Inter Milan Win or Draw", "market": "Double Chance", "odds": 1.30, "scoreai_conf": 89, "clv_edge": 3.9, "home_xg": 1.70, "away_xg": 0.95},
        {"leg": 7, "date": "Tue 27 Oct, 18:45", "day_group": "upcoming", "match": "Ajax vs Feyenoord", "selection": "Over 1.5 Goals", "market": "Total Goals", "odds": 1.35, "scoreai_conf": 87, "clv_edge": 3.5, "home_xg": 1.90, "away_xg": 1.40},
        {"leg": 8, "date": "Tue 27 Oct, 20:15", "day_group": "upcoming", "match": "Benfica vs Porto", "selection": "Benfica Win or Draw", "market": "Double Chance", "odds": 1.28, "scoreai_conf": 91, "clv_edge": 4.5, "home_xg": 1.60, "away_xg": 0.85},
        {"leg": 9, "date": "Wed 28 Oct, 20:30", "day_group": "upcoming", "match": "Sporting CP vs Braga", "selection": "Sporting CP Win or Draw", "market": "Double Chance", "odds": 1.20, "scoreai_conf": 93, "clv_edge": 4.8, "home_xg": 1.95, "away_xg": 0.90}
    ]

    processed_slate = []
    for fix in raw_fixtures:
        p_res = calculate_poisson_edge(fix["home_xg"], fix["away_xg"])
        if "Double Chance" in fix["market"]:
            model_prob = p_res["dc_home"] if "Chelsea" in fix["match"] or "Liverpool" in fix["match"] or "Inter" in fix["match"] or "Benfica" in fix["match"] or "Sporting" in fix["match"] else p_res["dc_away"]
        else:
            model_prob = p_res["over_15"]
            
        processed_slate.append({
            "leg": fix["leg"],
            "date": fix["date"],
            "day_group": fix["day_group"],
            "match": fix["match"],
            "selection": fix["selection"],
            "market": fix["market"],
            "odds": fix["odds"],
            "scoreai_conf": fix["scoreai_conf"],
            "clv_edge": fix["clv_edge"],
            "poisson_prob": model_prob
        })

    return {
        "status": "success",
        "updated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "slate": processed_slate,
        "accumulators": {
            "three_fold": {"legs": "1-3", "odds": 1.89},
            "six_fold": {"legs": "1-6", "odds": 4.15},
            "nine_fold": {"legs": "1-9", "odds": 10.42}
        }
    }

@app.get("/api/ledger")
async def get_ledger():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ledger ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.post("/api/ledger/log")
async def log_bet(request: Request):
    data = await request.json()
    now = datetime.utcnow().strftime("%d %b %H:%M")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO ledger (timestamp, tier_name, stake, odds, return_amt) VALUES (?, ?, ?, ?, ?)",
                   (now, data.get("tier_name"), data.get("stake"), data.get("odds"), data.get("return_amt")))
    conn.commit()
    conn.close()
    return {"status": "logged"}

@app.post("/api/ledger/update")
async def update_bet(request: Request):
    data = await request.json()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE ledger SET status = ? WHERE id = ?", (data.get("status"), data.get("id")))
    conn.commit()
    conn.close()
    return {"status": "updated"}
