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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ml_weights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_name TEXT,
            weight_value REAL
        )
    ''')
    cursor.execute("SELECT COUNT(*) FROM ml_weights")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO ml_weights (metric_name, weight_value) VALUES ('scoreai_weight', 0.35)")
        cursor.execute("INSERT INTO ml_weights (metric_name, weight_value) VALUES ('clv_weight', 0.35)")
        cursor.execute("INSERT INTO ml_weights (metric_name, weight_value) VALUES ('poisson_weight', 0.30)")
    conn.commit()
    conn.close()

init_db()

def get_ml_weights():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT metric_name, weight_value FROM ml_weights")
    rows = cursor.fetchall()
    conn.close()
    return {row[0]: row[1] for row in rows}

def optimize_ml_weights():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM ledger WHERE status != 'PENDING'")
    settled = cursor.fetchall()
    if len(settled) >= 3:
        cursor.execute("UPDATE ml_weights SET weight_value = weight_value * 1.02 WHERE metric_name = 'poisson_weight'")
        conn.commit()
    conn.close()

def poisson_prob(lmbda, k):
    return (math.exp(-lmbda) * (lmbda ** k)) / math.factorial(k)

def calculate_advanced_xg_poisson(home_xg, away_xg, home_xa, away_xa):
    adjusted_home_lmbda = home_xg * 0.85 + home_xa * 0.15
    adjusted_away_lmbda = away_xg * 0.85 + away_xa * 0.15
    
    home_win_prob = 0
    draw_prob = 0
    away_win_prob = 0
    over_15_prob = 0
    
    for h in range(6):
        for a in range(6):
            p = poisson_prob(adjusted_home_lmbda, h) * poisson_prob(adjusted_away_lmbda, a)
            if h > a: home_win_prob += p
            elif h == a: draw_prob += p
            else: away_win_prob += p
            if h + a >= 2: over_15_prob += p
                
    return {
        "dc_home": round((home_win_prob + draw_prob) * 100, 1),
        "dc_away": round((away_win_prob + draw_prob) * 100, 1),
        "over_15": round(over_15_prob * 100, 1)
    }

HTML_CONTENT = """<!DOCTYPE html>
<html>
<head>
    <title>GEM V15.0 Terminal</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <style>
        :root { --bg: #0d1117; --card-bg: #161b22; --accent: #00ff88; --gold: #f0b429; --text: #f0f6fc; --text-dim: #8b949e; --border: #30363d; --red: #ff5555; --purple: #a371f7; --cyan: #00bfff; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: var(--bg); color: var(--text); padding: 12px; max-width: 850px; margin: auto; }
        .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid var(--accent); padding-bottom: 12px; margin-bottom: 12px; }
        h1 { color: var(--accent); margin: 0; font-size: 20px; }
        .btn { background: var(--accent); color: #0d1117; border: none; padding: 10px 16px; font-weight: 800; border-radius: 8px; cursor: pointer; font-size: 13px; }
        .metrics-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 12px; }
        .metric-card { background: var(--card-bg); border: 1px solid var(--border); padding: 12px; border-radius: 10px; }
        .metric-card label { font-size: 11px; color: var(--text-dim); text-transform: uppercase; font-weight: 700; display: block; margin-bottom: 4px; }
        .metric-card input { background: var(--bg); border: 1px solid var(--border); color: var(--accent); padding: 6px 10px; width: 100%; border-radius: 6px; font-size: 16px; font-weight: bold; box-sizing: border-box; text-align: right; }
        .tabs { display: flex; gap: 4px; margin-bottom: 12px; overflow-x: auto; padding-bottom: 4px; }
        .tab { background: var(--card-bg); border: 1px solid var(--border); color: var(--text-dim); padding: 9px 8px; border-radius: 6px; font-size: 11px; font-weight: 700; cursor: pointer; flex: 1; text-align: center; }
        .tab.active { background: var(--accent); color: #0d1117; border-color: var(--accent); }
        .acc-box { background: var(--card-bg); padding: 12px 15px; border-radius: 10px; border: 1px solid var(--border); border-left: 4px solid var(--gold); display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; cursor: pointer; }
        .card { background: var(--card-bg); padding: 12px 15px; margin-bottom: 10px; border-radius: 10px; border: 1px solid var(--border); border-left: 4px solid var(--accent); }
        .card-top { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px; }
        .progress-bar-bg { background: var(--bg); height: 6px; border-radius: 3px; width: 100%; margin-top: 8px; overflow: hidden; border: 1px solid var(--border); }
        .progress-bar-fill { background: var(--accent); height: 100%; border-radius: 3px; }
        .badges { display: flex; gap: 4px; margin-top: 6px; flex-wrap: wrap; }
        .badge { font-size: 9px; padding: 2px 6px; border-radius: 4px; font-weight: 800; text-transform: uppercase; }
        .badge-ai { background: rgba(0,255,136,0.15); color: var(--accent); border: 1px solid rgba(0,255,136,0.3); }
        .toast { position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background: var(--accent); color: #0d1117; padding: 10px 22px; border-radius: 20px; font-weight: 800; display: none; z-index: 1000; font-size: 13px; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>GEM V15.0 TERMINAL</h1>
            <p style="margin:2px 0 0 0; font-size:11px; color:var(--text-dim);">Quantitative Dashboard</p>
        </div>
        <button class="btn" onclick="copyBetSlip()">📋 Copy Slip</button>
    </div>

    <div class="metrics-grid">
        <div class="metric-card">
            <label>Base Stake (£)</label>
            <input type="number" id="baseStake" value="10" min="1" oninput="renderApp()">
        </div>
        <div class="metric-card">
            <label>System Status</label>
            <div style="font-size:14px; margin-top:6px; color:var(--accent); font-weight:800;">🟢 Online (Paid)</div>
        </div>
    </div>

    <div class="tabs">
        <div class="tab active" onclick="switchTab('all', this)">🔥 All</div>
        <div class="tab" onclick="switchTab('today', this)">⚡ Today</div>
        <div class="tab" onclick="switchTab('futures', this)">🔮 Futures</div>
        <div class="tab" onclick="switchTab('ledger', this)">📊 Ledger</div>
    </div>

    <div id="acc-container"></div>
    <h3 id="slate-title" style="margin: 15px 0 10px 0; font-size: 14px; color: var(--text-dim); text-transform: uppercase;">Active Slate</h3>
    <div id="fixtures-container">Loading terminal...</div>
    <div id="toast" class="toast">Action completed!</div>

    <script>
        let globalData = null;
        let currentTab = 'all';
        let ledgerData = [];

        async function init() {
            try {
                const res = await fetch('/api/fixtures?cb=' + Date.now());
                globalData = await res.json();
                const ledRes = await fetch('/api/ledger');
                ledgerData = await ledRes.json();
                renderApp();
            } catch (err) {
                document.getElementById('fixtures-container').innerHTML = '<div style="color:var(--red); text-align:center; padding:20px;">Error loading terminal data.</div>';
            }
        }

        async function logBet(tierName, oddsVal) {
            const stake = parseFloat(document.getElementById('baseStake').value) || 10;
            const retAmt = (stake * oddsVal).toFixed(2);
            await fetch('/api/ledger/log', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({tier_name: tierName, stake: stake, odds: oddsVal, return_amt: retAmt})
            });
            const ledRes = await fetch('/api/ledger');
            ledgerData = await ledRes.json();
            renderApp();
            showToast(tierName + " logged to ledger!");
        }

        function switchTab(tab, el) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            el.classList.add('active');
            currentTab = tab;
            renderApp();
        }

        function showToast(msg) {
            const t = document.getElementById('toast');
            t.innerText = msg;
            t.style.display = 'block';
            setTimeout(() => { t.style.display = 'none'; }, 2000);
        }

        function renderApp() {
            if (!globalData) return;
            const stake = parseFloat(document.getElementById('baseStake').value) || 10;
            const threeOdds = globalData.accumulators.three_fold.odds;
            const threeRet = (stake * threeOdds).toFixed(2);

            document.getElementById('acc-container').innerHTML = 
                '<div class="acc-box" onclick="logBet(\\'3-Fold Anchor\\', ' + threeOdds + ')">' +
                    '<div>' +
                        '<div style="font-size:12px; font-weight:800; color:var(--gold);">🎯 3-FOLD ANCHOR &bull; Tap to Log</div>' +
                        '<div style="font-size:12px; color:var(--text-dim); margin-top:2px;">Odds: <b>' + threeOdds + '</b> | Stake: £' + stake.toFixed(2) + '</div>' +
                    '</div>' +
                    '<div style="text-align:right;">' +
                        '<div style="font-size:16px; font-weight:800; color:var(--gold);">£' + threeRet + '</div>' +
                        '<div style="font-size:10px; color:var(--text-dim);">Est. Return</div>' +
                    '</div>' +
                '</div>';

            const container = document.getElementById('fixtures-container');
            const titleEl = document.getElementById('slate-title');

            if (currentTab === 'ledger') {
                titleEl.innerText = "📊 Performance Ledger";
                if (ledgerData.length === 0) {
                    container.innerHTML = '<div style="text-align:center; padding:20px; color:var(--text-dim);">No bets logged yet. Tap the 3-Fold Anchor above to log a bet!</div>';
                    return;
                }
                container.innerHTML = ledgerData.map(i => 
                    '<div class="card">' +
                        '<div class="card-top"><div><b>' + i.tier_name + '</b><br/><span style="font-size:12px; color:var(--text-dim);">Stake: £' + i.stake + ' | Odds: @' + i.odds + ' ➔ Ret: £' + i.return_amt + '</span></div>' +
                        '<span class="badge" style="background:var(--gold); color:#0d1117;">' + i.status + '</span></div>' +
                    '</div>'
                ).join('');
                return;
            }

            let slate = globalData.slate;
            if (currentTab === 'today') {
                slate = slate.filter(i => i.day_group === 'today');
                titleEl.innerText = "⚡ Today's Games";
            } else if (currentTab === 'futures') {
                slate = slate.filter(i => i.day_group === 'futures');
                titleEl.innerText = "🔮 Futures Value";
            } else {
                titleEl.innerText = "🔥 Full Slate";
            }

            container.innerHTML = slate.map(i => 
                '<div class="card">' +
                    '<div class="card-top">' +
                        '<div>' +
                            '<div style="font-size:10px; color:var(--text-dim); font-weight:700; margin-bottom:2px;">LEG ' + i.leg + ' &bull; ' + i.date + '</div>' +
                            '<b style="font-size:14px;">' + i.match + '</b><br/>' +
                            '<span style="font-size:12px; color:var(--accent); font-weight:600;">' + i.selection + '</span>' +
                        '</div>' +
                        '<div style="font-size:16px; font-weight:900; color:var(--accent);">@ ' + i.odds + '</div>' +
                    '</div>' +
                    '<div class="progress-bar-bg"><div class="progress-bar-fill" style="width: ' + i.scoreai_conf + '%;"></div></div>' +
                    '<div class="badges"><span class="badge badge-ai">AI: ' + i.scoreai_conf + '%</span><span class="badge badge-ai">Model: ' + i.poisson_prob + '%</span></div>' +
                '</div>'
            ).join('');
        }

        function copyBetSlip() {
            if (!globalData) return;
            logBet('Full Slate Slip', globalData.accumulators.nine_fold.odds);
        }

        init();
    </script>
</body>
</html>
"""

@app.get("/")
async def read_index(response: Response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return HTML_CONTENT

@app.get("/api/fixtures")
async def get_fixtures(response: Response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return {
        "status": "success",
        "slate": [
            {"leg": 1, "date": "Today, 15:00", "day_group": "today", "match": "Chelsea vs Newcastle", "selection": "Chelsea Win or Draw", "odds": 1.25, "scoreai_conf": 91, "poisson_prob": 88.5},
            {"leg": 2, "date": "Today, 17:30", "day_group": "today", "match": "Crystal Palace vs Liverpool", "selection": "Liverpool Win or Draw", "odds": 1.18, "scoreai_conf": 94, "poisson_prob": 92.0},
            {"leg": 3, "date": "Wed 28 Oct, 20:00", "day_group": "futures", "match": "Arsenal vs Sevilla", "selection": "Arsenal Win or Draw", "odds": 1.22, "scoreai_conf": 93, "poisson_prob": 89.4}
        ],
        "accumulators": {
            "three_fold": {"legs": "1-3", "odds": 1.80},
            "nine_fold": {"legs": "1-3", "odds": 3.50}
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

cd C:\Users\georg\gem-v15-engine

Set-Content -Path main.py -Value @"
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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ml_weights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_name TEXT,
            weight_value REAL
        )
    ''')
    cursor.execute("SELECT COUNT(*) FROM ml_weights")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO ml_weights (metric_name, weight_value) VALUES ('scoreai_weight', 0.35)")
        cursor.execute("INSERT INTO ml_weights (metric_name, weight_value) VALUES ('clv_weight', 0.35)")
        cursor.execute("INSERT INTO ml_weights (metric_name, weight_value) VALUES ('poisson_weight', 0.30)")
    conn.commit()
    conn.close()

init_db()

HTML_CONTENT = """<!DOCTYPE html>
<html>
<head>
    <title>GEM V15.0 Terminal</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <style>
        :root { --bg: #0d1117; --card-bg: #161b22; --accent: #00ff88; --gold: #f0b429; --text: #f0f6fc; --text-dim: #8b949e; --border: #30363d; --red: #ff5555; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: var(--bg); color: var(--text); padding: 12px; max-width: 850px; margin: auto; }
        .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid var(--accent); padding-bottom: 12px; margin-bottom: 12px; }
        h1 { color: var(--accent); margin: 0; font-size: 20px; }
        .btn { background: var(--accent); color: #0d1117; border: none; padding: 10px 16px; font-weight: 800; border-radius: 8px; cursor: pointer; font-size: 13px; }
        .metrics-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 12px; }
        .metric-card { background: var(--card-bg); border: 1px solid var(--border); padding: 12px; border-radius: 10px; }
        .metric-card label { font-size: 11px; color: var(--text-dim); text-transform: uppercase; font-weight: 700; display: block; margin-bottom: 4px; }
        .metric-card input { background: var(--bg); border: 1px solid var(--border); color: var(--accent); padding: 6px 10px; width: 100%; border-radius: 6px; font-size: 16px; font-weight: bold; box-sizing: border-box; text-align: right; }
        .tabs { display: flex; gap: 4px; margin-bottom: 12px; overflow-x: auto; padding-bottom: 4px; }
        .tab { background: var(--card-bg); border: 1px solid var(--border); color: var(--text-dim); padding: 9px 8px; border-radius: 6px; font-size: 11px; font-weight: 700; cursor: pointer; flex: 1; text-align: center; }
        .tab.active { background: var(--accent); color: #0d1117; border-color: var(--accent); }
        .acc-box { background: var(--card-bg); padding: 12px 15px; border-radius: 10px; border: 1px solid var(--border); border-left: 4px solid var(--gold); display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; cursor: pointer; }
        .card { background: var(--card-bg); padding: 12px 15px; margin-bottom: 10px; border-radius: 10px; border: 1px solid var(--border); border-left: 4px solid var(--accent); }
        .card-top { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px; }
        .progress-bar-bg { background: var(--bg); height: 6px; border-radius: 3px; width: 100%; margin-top: 8px; overflow: hidden; border: 1px solid var(--border); }
        .progress-bar-fill { background: var(--accent); height: 100%; border-radius: 3px; }
        .badges { display: flex; gap: 4px; margin-top: 6px; flex-wrap: wrap; }
        .badge { font-size: 9px; padding: 2px 6px; border-radius: 4px; font-weight: 800; text-transform: uppercase; }
        .badge-ai { background: rgba(0,255,136,0.15); color: var(--accent); border: 1px solid rgba(0,255,136,0.3); }
        .toast { position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background: var(--accent); color: #0d1117; padding: 10px 22px; border-radius: 20px; font-weight: 800; display: none; z-index: 1000; font-size: 13px; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>GEM V15.0 TERMINAL</h1>
            <p style="margin:2px 0 0 0; font-size:11px; color:var(--text-dim);">Quantitative Dashboard</p>
        </div>
        <button class="btn" onclick="copyBetSlip()">📋 Copy Slip</button>
    </div>

    <div class="metrics-grid">
        <div class="metric-card">
            <label>Base Stake (£)</label>
            <input type="number" id="baseStake" value="10" min="1" oninput="renderApp()">
        </div>
        <div class="metric-card">
            <label>System Status</label>
            <div style="font-size:14px; margin-top:6px; color:var(--accent); font-weight:800;">🟢 Online (Paid)</div>
        </div>
    </div>

    <div class="tabs">
        <div class="tab active" onclick="switchTab('all', this)">🔥 All</div>
        <div class="tab" onclick="switchTab('today', this)">⚡ Today</div>
        <div class="tab" onclick="switchTab('futures', this)">🔮 Futures</div>
        <div class="tab" onclick="switchTab('ledger', this)">📊 Ledger</div>
    </div>

    <div id="acc-container"></div>
    <h3 id="slate-title" style="margin: 15px 0 10px 0; font-size: 14px; color: var(--text-dim); text-transform: uppercase;">Active Slate</h3>
    <div id="fixtures-container">Loading terminal...</div>
    <div id="toast" class="toast">Action completed!</div>

    <script>
        let globalData = null;
        let currentTab = 'all';
        let ledgerData = [];

        async function init() {
            try {
                const res = await fetch('/api/fixtures?cb=' + Date.now());
                globalData = await res.json();
                const ledRes = await fetch('/api/ledger');
                ledgerData = await ledRes.json();
                renderApp();
            } catch (err) {
                document.getElementById('fixtures-container').innerHTML = <div style="color:var(--red); text-align:center; padding:20px;">Error loading terminal data.</div>;
            }
        }

        async function logBet(tierName, oddsVal) {
            const stake = parseFloat(document.getElementById('baseStake').value) || 10;
            const retAmt = (stake * oddsVal).toFixed(2);
            await fetch('/api/ledger/log', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({tier_name: tierName, stake: stake, odds: oddsVal, return_amt: retAmt})
            });
            const ledRes = await fetch('/api/ledger');
            ledgerData = await ledRes.json();
            renderApp();
            showToast(tierName + " logged to ledger!");
        }

        function switchTab(tab, el) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            el.classList.add('active');
            currentTab = tab;
            renderApp();
        }

        function showToast(msg) {
            const t = document.getElementById('toast');
            t.innerText = msg;
            t.style.display = 'block';
            setTimeout(() => { t.style.display = 'none'; }, 2000);
        }

        function renderApp() {
            if (!globalData) return;
            const stake = parseFloat(document.getElementById('baseStake').value) || 10;
            const threeOdds = globalData.accumulators.three_fold.odds;
            const threeRet = (stake * threeOdds).toFixed(2);

            document.getElementById('acc-container').innerHTML = 
                <div class="acc-box" onclick="logBet('3-Fold Anchor', )">
                    <div>
                        <div style="font-size:12px; font-weight:800; color:var(--gold);">🎯 3-FOLD ANCHOR &bull; Tap to Log</div>
                        <div style="font-size:12px; color:var(--text-dim); margin-top:2px;">Odds: <b></b> | Stake: £</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-size:16px; font-weight:800; color:var(--gold);">£</div>
                        <div style="font-size:10px; color:var(--text-dim);">Est. Return</div>
                    </div>
                </div>
            ;

            const container = document.getElementById('fixtures-container');
            const titleEl = document.getElementById('slate-title');

            if (currentTab === 'ledger') {
                titleEl.innerText = "📊 Performance Ledger";
                if (ledgerData.length === 0) {
                    container.innerHTML = <div style="text-align:center; padding:20px; color:var(--text-dim);">No bets logged yet. Tap the 3-Fold Anchor above to log a bet!</div>;
                    return;
                }
                container.innerHTML = ledgerData.map(i => 
                    <div class="card">
                        <div class="card-top">
                            <div>
                                <b></b><br/>
                                <span style="font-size:12px; color:var(--text-dim);">Stake: £ | Odds: @ &➔ Ret: £</span>
                            </div>
                            <span class="badge" style="background:var(--gold); color:#0d1117;"></span>
                        </div>
                    </div>
                ).join('');
                return;
            }

            let slate = globalData.slate;
            if (currentTab === 'today') {
                slate = slate.filter(i => i.day_group === 'today');
                titleEl.innerText = "⚡ Today's Games";
            } else if (currentTab === 'futures') {
                slate = slate.filter(i => i.day_group === 'futures');
                titleEl.innerText = "🔮 Futures Value";
            } else {
                titleEl.innerText = "🔥 Full Slate";
            }

            container.innerHTML = slate.map(i => 
                <div class="card">
                    <div class="card-top">
                        <div>
                            <div style="font-size:10px; color:var(--text-dim); font-weight:700; margin-bottom:2px;">LEG  &bull; </div>
                            <b style="font-size:14px;"></b><br/>
                            <span style="font-size:12px; color:var(--accent); font-weight:600;"></span>
                        </div>
                        <div style="font-size:16px; font-weight:900; color:var(--accent);">@ </div>
                    </div>
                    <div class="progress-bar-bg"><div class="progress-bar-fill" style="width: %;"></div></div>
                    <div class="badges">
                        <span class="badge badge-ai">AI: %</span>
                        <span class="badge badge-ai">Model: %</span>
                    </div>
                </div>
            ).join('');
        }

        function copyBetSlip() {
            if (!globalData) return;
            logBet('Full Slate Slip', globalData.accumulators.nine_fold.odds);
        }

        init();
    </script>
</body>
</html>
"""

@app.get("/")
async def read_index(response: Response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return HTML_CONTENT

@app.get("/api/fixtures")
async def get_fixtures(response: Response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return {
        "status": "success",
        "slate": [
            {"leg": 1, "date": "Today, 15:00", "day_group": "today", "match": "Chelsea vs Newcastle", "selection": "Chelsea Win or Draw", "odds": 1.25, "scoreai_conf": 91, "poisson_prob": 88.5},
            {"leg": 2, "date": "Today, 17:30", "day_group": "today", "match": "Crystal Palace vs Liverpool", "selection": "Liverpool Win or Draw", "odds": 1.18, "scoreai_conf": 94, "poisson_prob": 92.0},
            {"leg": 3, "date": "Wed 28 Oct, 20:00", "day_group": "futures", "match": "Arsenal vs Sevilla", "selection": "Arsenal Win or Draw", "odds": 1.22, "scoreai_conf": 93, "poisson_prob": 89.4}
        ],
        "accumulators": {
            "three_fold": {"legs": "1-3", "odds": 1.80},
            "nine_fold": {"legs": "1-3", "odds": 3.50}
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
