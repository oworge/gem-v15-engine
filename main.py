# -*- coding: utf-8 -*-
from fastapi import FastAPI, Request
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
        won_count = sum(1 for s in settled if s[0] == 'WON')
        win_rate = won_count / len(settled)
        if win_rate > 0.6:
            cursor.execute("UPDATE ml_weights SET weight_value = weight_value * 1.02 WHERE metric_name = 'poisson_weight'")
        else:
            cursor.execute("UPDATE ml_weights SET weight_value = weight_value * 1.02 WHERE metric_name = 'clv_weight'")
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
    <title>Edgemetrix-Pro-26 Self-Learning ML Terminal</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="manifest" href="/manifest.json">
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
        .tabs { display: flex; gap: 4px; margin-bottom: 12px; overflow-x: auto; }
        .tab { background: var(--card-bg); border: 1px solid var(--border); color: var(--text-dim); padding: 9px 6px; border-radius: 6px; font-size: 10px; font-weight: 700; cursor: pointer; white-space: nowrap; flex: 1; text-align: center; }
        .tab.active { background: var(--accent); color: #0d1117; border-color: var(--accent); }
        .tab.daily-tab { background: rgba(240,180,41,0.15); color: var(--gold); border-color: rgba(240,180,41,0.4); }
        .tab.daily-tab.active { background: var(--gold); color: #0d1117; }
        .tab.futures-tab { background: rgba(163,113,247,0.15); color: var(--purple); border-color: rgba(163,113,247,0.4); }
        .tab.futures-tab.active { background: var(--purple); color: #0d1117; }
        .tab.ml-tab { background: rgba(0,191,255,0.15); color: var(--cyan); border-color: rgba(0,191,255,0.4); }
        .tab.ml-tab.active { background: var(--cyan); color: #0d1117; }
        .tab.ledger-tab { background: rgba(255,85,85,0.15); color: var(--red); border-color: rgba(255,85,85,0.4); }
        .tab.ledger-tab.active { background: var(--red); color: #0d1117; }
        .acc-container { display: flex; flex-direction: column; gap: 8px; margin-bottom: 15px; }
        .acc-box { background: var(--card-bg); padding: 12px 15px; border-radius: 10px; border: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; border-left: 4px solid var(--accent); cursor: pointer; }
        .acc-box.elite { border-left-color: var(--gold); background: linear-gradient(135deg, #161b22 0%, #1f241c 100%); }
        .card { background: var(--card-bg); padding: 12px 15px; margin-bottom: 10px; border-radius: 10px; border: 1px solid var(--border); border-left: 4px solid var(--accent); }
        .card.elite { border-left-color: var(--gold); }
        .card.futures-card { border-left-color: var(--purple); }
        .card-top { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px; }
        .progress-bar-bg { background: var(--bg); height: 6px; border-radius: 3px; width: 100%; margin-top: 8px; overflow: hidden; border: 1px solid var(--border); }
        .progress-bar-fill { background: var(--accent); height: 100%; border-radius: 3px; }
        .progress-bar-fill.elite { background: var(--gold); }
        .progress-bar-fill.futures { background: var(--purple); }
        .badges { display: flex; gap: 4px; margin-top: 6px; flex-wrap: wrap; }
        .badge { font-size: 9px; padding: 2px 6px; border-radius: 4px; font-weight: 800; text-transform: uppercase; }
        .badge-scoreai { background: rgba(0,255,136,0.15); color: var(--accent); border: 1px solid rgba(0,255,136,0.3); }
        .badge-clv { background: rgba(240,180,41,0.15); color: var(--gold); border: 1px solid rgba(240,180,41,0.3); }
        .badge-poisson { background: rgba(0,191,255,0.15); color: var(--cyan); border: 1px solid rgba(0,191,255,0.3); }
        .toast { position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background: var(--accent); color: #0d1117; padding: 10px 22px; border-radius: 20px; font-weight: 800; display: none; z-index: 1000; font-size: 13px; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>Edgemetrix-Pro-26</h1>
            <p style="margin:2px 0 0 0; font-size:11px; color:var(--text-dim);">Advanced xG & Self-Learning ML Weights</p>
        </div>
        <button class="btn" onclick="copyBetSlip()">Copy Slip</button>
    </div>

    <div class="metrics-grid">
        <div class="metric-card">
            <label>Base Stake (£)</label>
            <input type="number" id="baseStake" value="10" min="1" oninput="recalculateReturns()">
        </div>
        <div class="metric-card">
            <label>ML Optimizer</label>
            <div style="font-size:14px; margin-top:4px; color:var(--cyan);">Active Tuning</div>
        </div>
    </div>

    <div class="tabs">
        <div class="tab active" onclick="switchTab('all', this)">All</div>
        <div class="tab daily-tab" onclick="switchTab('today', this)">Today</div>
        <div class="tab futures-tab" onclick="switchTab('futures', this)">Futures</div>
        <div class="tab" onclick="switchTab('three', this)">3-Fold</div>
        <div class="tab ml-tab" onclick="switchTab('ml', this)">ML Weights</div>
        <div class="tab ledger-tab" onclick="switchTab('ledger', this)">Ledger</div>
    </div>

    <div class="acc-container" id="acc-container"></div>
    <h3 id="slate-title" style="margin: 15px 0 10px 0; font-size: 14px; color: var(--text-dim); text-transform: uppercase;">Active Slate</h3>
    <div id="fixtures-container">Loading terminal...</div>
    <div id="toast" class="toast">Bet slip copied & logged!</div>

    <script>
        let globalData = null;
        let currentTab = 'all';
        let ledgerData = [];
        let mlWeights = {};

        async function fetchFixtures() {
            try {
                const response = await fetch('/api/fixtures?cb=' + new Date().getTime(), { cache: 'no-store' });
                globalData = await response.json();
                fetchLedger();
                fetchMLWeights();
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

        async function fetchMLWeights() {
            try {
                const res = await fetch('/api/ml-weights');
                mlWeights = await res.json();
            } catch(e) {}
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
            fetchMLWeights();
            const toast = document.getElementById('toast');
            toast.innerText = tierName + " logged & ML optimized!";
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
            fetchMLWeights();
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
            document.getElementById('acc-container').innerHTML = 
                '<div class="acc-box elite" onclick="logBetToLedger(\\'3-Fold Anchor\\', ' + globalData.accumulators.three_fold.odds + ')">' +
                    '<div>' +
                        '<div style="font-size:12px; font-weight:800; color:var(--gold);">3-FOLD ANCHOR &bull; Tap to Log</div>' +
                        '<div style="font-size:12px; color:var(--text-dim);">Odds: <b>' + globalData.accumulators.three_fold.odds + '</b> | Stake: £' + stake.toFixed(2) + '</div>' +
                    '</div>' +
                    '<div style="text-align:right;">' +
                        '<div style="font-size:16px; font-weight:800; color:var(--gold);">£' + threeRet + '</div>' +
                        '<div style="font-size:10px; color:var(--text-dim);">Est. Return</div>' +
                    '</div>' +
                '</div>';
        }

        function renderApp() {
            recalculateReturns();
            const container = document.getElementById('fixtures-container');
            const titleEl = document.getElementById('slate-title');
            
            if (currentTab === 'ml') {
                titleEl.innerText = "ML Coefficient Weights";
                container.innerHTML = '<div class="card" style="border-left-color:var(--cyan);">' +
                    '<b style="color:var(--cyan); font-size:14px;">Closed-Loop Feedback Optimizer</b>' +
                    '<p style="font-size:12px; color:var(--text-dim); margin:6px 0 12px 0;">Auto-adjusts based on ledger results.</p>' +
                    '<div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:6px; text-align:center;">' +
                        '<div style="background:var(--bg); padding:10px; border-radius:6px;"><div style="font-size:10px; color:var(--text-dim);">SCOREAI</div><b style="color:var(--accent);">' + (mlWeights.scoreai_weight || 0.35).toFixed(3) + '</b></div>' +
                        '<div style="background:var(--bg); padding:10px; border-radius:6px;"><div style="font-size:10px; color:var(--text-dim);">CLV EDGE</div><b style="color:var(--gold);">' + (mlWeights.clv_weight || 0.35).toFixed(3) + '</b></div>' +
                        '<div style="background:var(--bg); padding:10px; border-radius:6px;"><div style="font-size:10px; color:var(--text-dim);

git add app.py
git commit -m "Clean rebuild: Pure UTF-8 no encoding errors"
git push --force-with-lease origin main
# Stage only the clean file
git add app.py

# Commit
git commit -m "Final clean: No special characters, pure ASCII"

# Force overwrite GitHub — THIS replaces the bad version
git push --force origin main
# Stage only the clean file
git add app.py

# Commit
git commit -m "Final clean: No special characters, pure ASCII"

# Force overwrite GitHub — THIS replaces the bad version
git push --force origin main
# Go to your project folder
cd C:\Users\georg\gem-v15-engine

# Create the clean app.py file — pure UTF-8
@'
# -*- coding: utf-8 -*-
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from datetime import datetime
import math
import sqlite3

app = FastAPI()

DB_FILE = "gem_ledger.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            tier_name TEXT,
            stake REAL,
            odds REAL,
            return_amt REAL,
            status TEXT DEFAULT "PENDING"
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ml_weights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_name TEXT,
            weight_value REAL
        )
    """)
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
        won_count = sum(1 for s in settled if s[0] == 'WON')
        win_rate = won_count / len(settled)
        if win_rate > 0.6:
            cursor.execute("UPDATE ml_weights SET weight_value = weight_value * 1.02 WHERE metric_name = 'poisson_weight'")
        else:
            cursor.execute("UPDATE ml_weights SET weight_value = weight_value * 1.02 WHERE metric_name = 'clv_weight'")
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
    <title>Edgemetrix-Pro-26 Self-Learning ML Terminal</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="manifest" href="/manifest.json">
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
        .tabs { display: flex; gap: 4px; margin-bottom: 12px; overflow-x: auto; }
        .tab { background: var(--card-bg); border: 1px solid var(--border); color: var(--text-dim); padding: 9px 6px; border-radius: 6px; font-size: 10px; font-weight: 700; cursor: pointer; white-space: nowrap; flex: 1; text-align: center; }
        .tab.active { background: var(--accent); color: #0d1117; border-color: var(--accent); }
        .tab.daily-tab { background: rgba(240,180,41,0.15); color: var(--gold); border-color: rgba(240,180,41,0.4); }
        .tab.daily-tab.active { background: var(--gold); color: #0d1117; }
        .tab.futures-tab { background: rgba(163,113,247,0.15); color: var(--purple); border-color: rgba(163,113,247,0.4); }
        .tab.futures-tab.active { background: var(--purple); color: #0d1117; }
        .tab.ml-tab { background: rgba(0,191,255,0.15); color: var(--cyan); border-color: rgba(0,191,255,0.4); }
        .tab.ml-tab.active { background: var(--cyan); color: #0d1117; }
        .tab.ledger-tab { background: rgba(255,85,85,0.15); color: var(--red); border-color: rgba(255,85,85,0.4); }
        .tab.ledger-tab.active { background: var(--red); color: #0d1117; }
        .acc-container { display: flex; flex-direction: column; gap: 8px; margin-bottom: 15px; }
        .acc-box { background: var(--card-bg); padding: 12px 15px; border-radius: 10px; border: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; border-left: 4px solid var(--accent); cursor: pointer; }
        .acc-box.elite { border-left-color: var(--gold); background: linear-gradient(135deg, #161b22 0%, #1f241c 100%); }
        .card { background: var(--card-bg); padding: 12px 15px; margin-bottom: 10px; border-radius: 10px; border: 1px solid var(--border); border-left: 4px solid var(--accent); }
        .card.elite { border-left-color: var(--gold); }
        .card.futures-card { border-left-color: var(--purple); }
        .card-top { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px; }
        .progress-bar-bg { background: var(--bg); height: 6px; border-radius: 3px; width: 100%; margin-top: 8px; overflow: hidden; border: 1px solid var(--border); }
        .progress-bar-fill { background: var(--accent); height: 100%; border-radius: 3px; }
        .progress-bar-fill.elite { background: var(--gold); }
        .progress-bar-fill.futures { background: var(--purple); }
        .badges { display: flex; gap: 4px; margin-top: 6px; flex-wrap: wrap; }
        .badge { font-size: 9px; padding: 2px 6px; border-radius: 4px; font-weight: 800; text-transform: uppercase; }
        .badge-scoreai { background: rgba(0,255,136,0.15); color: var(--accent); border: 1px solid rgba(0,255,136,0.3); }
        .badge-clv { background: rgba(240,180,41,0.15); color: var(--gold); border: 1px solid rgba(240,180,41,0.3); }
        .badge-poisson { background: rgba(0,191,255,0.15); color: var(--cyan); border: 1px solid rgba(0,191,255,0.3); }
        .toast { position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background: var(--accent); color: #0d1117; padding: 10px 22px; border-radius: 20px; font-weight: 800; display: none; z-index: 1000; font-size: 13px; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>Edgemetrix-Pro-26</h1>
            <p style="margin:2px 0 0 0; font-size:11px; color:var(--text-dim);">Advanced xG & Self-Learning ML Weights</p>
        </div>
        <button class="btn" onclick="copyBetSlip()">Copy Slip</button>
    </div>
    <div class="metrics-grid">
        <div class="metric-card">
            <label>Base Stake (GBP)</label>
            <input type="number" id="baseStake" value="10" min="1" oninput="recalculateReturns()">
        </div>
        <div class="metric-card">
            <label>ML Optimizer</label>
            <div style="font-size:14px; margin-top:4px; color:var(--cyan);">Active Tuning</div>
        </div>
    </div>
    <div class="tabs">
        <div class="tab active" onclick="switchTab('all', this)">All</div>
        <div class="tab daily-tab" onclick="switchTab('today', this)">Today</div>
        <div class="tab futures-tab" onclick="switchTab('futures', this)">Futures</div>
        <div class="tab" onclick="switchTab('three', this)">3-Fold</div>
        <div class="tab ml-tab" onclick="switchTab('ml', this)">ML Weights</div>
        <div class="tab ledger-tab" onclick="switchTab('ledger', this)">Ledger</div>
    </div>
    <div class="acc-container" id="acc-container"></div>
    <h3 id="slate-title" style="margin: 15px 0 10px 0; font-size: 14px; color: var(--text-dim); text-transform: uppercase;">Active Slate</h3>
    <div id="fixtures-container">Loading terminal...</div>
    <div id="toast" class="toast">Bet slip copied & logged!</div>
    <script>
        let globalData = null;
        let currentTab = 'all';
        let ledgerData = [];
        let mlWeights = {};
        async function fetchFixtures() {
            try {
                const response = await fetch('/api/fixtures?cb=' + new Date().getTime(), { cache: 'no-store' });
                globalData = await response.json();
                fetchLedger();
                fetchMLWeights();
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
        async function fetchMLWeights() {
            try {
                const res = await fetch('/api/ml-weights');
                mlWeights = await res.json();
            } catch(e) {}
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
            fetchMLWeights();
            const toast = document.getElementById('toast');
            toast.innerText = tierName + ' logged & ML optimized!';
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
            fetchMLWeights();
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
            document.getElementById('acc-container').innerHTML = 
                '<div class="acc-box elite" onclick="logBetToLedger(\\'3-Fold Anchor\\', ' + globalData.accumulators.three_fold.odds + ')">' +
                    '<div>' +
                        '<div style="font-size:12px; font-weight:800; color:var(--gold);">3-FOLD ANCHOR — Tap to Log</div>' +
                        '<div style="font-size:12px; color:var(--text-dim);">Odds: <b>' + globalData.accumulators.three_fold.odds + '</b> | Stake: GBP' + stake.toFixed(2) + '</div>' +
                    '</div>' +
                    '<div style="text-align:right;">' +
                        '<div style="font-size:16px; font-weight:800; color:var(--gold);">GBP' + threeRet + '</div>' +
                        '<div style="font-size:10px; color:var(--text-dim);">Est. Return</div>' +
                    '</div>' +
                '</div>';
        }
        function renderApp() {
            recalculateReturns();
            const container = document.getElementById('fixtures-container');
            const titleEl = document.getElementById('slate-title');
            if (currentTab === 'ml') {
                titleEl.innerText = 'ML Coefficient Weights';
                container.innerHTML = '<div class="card" style="border-left-color:var(--cyan);">' +
                    '<b style="color:var(--cyan); font-size:14px;">Closed-Loop Feedback Optimizer</b>' +
                    '<p style="font-size:12px; color:var(--text-dim); margin:6px 0 12px 0;">Auto-adjusts based on ledger results.</p>' +
                    '<div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:6px; text-align:center;">' +
                        '<div style="background:var(--bg); padding:10px; border-radius:6px;"><div style="font-size:10px; color:var(--text-dim);">SCOREAI</div><b style="color:var(--accent);">' + (mlWeights.scoreai_weight || 0.35).toFixed(3) + '</b></div>' +
                        '<div style="background:var(--bg); padding:10px; border-radius:6px;"><div style="font-size:10px; color:var(--text-dim);">CLV EDGE</div><b style="color:var(--gold);">' + (mlWeights.clv_weight || 0.35).toFixed(3) + '</b></div>' +
                        '<div style="background:var(--bg); padding:10px; border-radius:6px;"><div style="font-size:10px; color:var(--text
# Check the file starts correctly
Get-Content app.py -Head 5
# Stage only the clean file
git add app.py

# Commit
git commit -m "Clean fix: Remove encoding errors, pure UTF-8"
# Push to overwrite the bad version
git push origin main
git push --force-with-lease origin main
cd C:\Users\georg\gem-v15-engine
git pull
python app.py
cd C:\Users\georg\gem-v15-engine
git status# -*- coding: utf-8 -*-
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from datetime import datetime
import math
import sqlite3

app = FastAPI()

DB_FILE = "gem_ledger.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            tier_name TEXT,
            stake REAL,
            odds REAL,
            return_amt REAL,
            status TEXT DEFAULT 'PENDING'
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ml_weights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_name TEXT,
            weight_value REAL
        )
    """)
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
        won_count = sum(1 for s in settled if s[0] == 'WON')
        win_rate = won_count / len(settled)
        if win_rate > 0.6:
            cursor.execute("UPDATE ml_weights SET weight_value = weight_value * 1.02 WHERE metric_name = 'poisson_weight'")
        else:
            cursor.execute("UPDATE ml_weights SET weight_value = weight_value * 1.02 WHERE metric_name = 'clv_weight'")
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
    <title>Edgemetrix-Pro-26</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        :root { --bg: #0d1117; --card-bg: #161b22; --accent: #00ff88; --gold: #f0b429; --text: #f0f6fc; --text-dim: #8b949e; --border: #30363d; --red: #ff5555; --purple: #a371f7; --cyan: #00bfff; }
        body { font-family: sans-serif; background: var(--bg); color: var(--text); padding: 12px; max-width: 850px; margin: auto; }
        .header { display: flex; justify-content: space-between; border-bottom: 2px solid var(--accent); padding-bottom: 12px; }
        h1 { color: var(--accent); margin: 0; font-size: 20px; }
        .btn { background: var(--accent); color: #0d1117; border: none; padding: 10px 16px; font-weight: 800; border-radius: 8px; cursor: pointer; }
        .metric-card { background: var(--card-bg); border: 1px solid var(--border); padding: 12px; border-radius: 10px; margin-bottom: 10px; }
        .metric-card input { background: var(--bg); border: 1px solid var(--border); color: var(--accent); padding: 6px 10px; border-radius: 6px; font-size: 16px; font-weight: bold; width: 100px; text-align: right; }
        .tabs { display: flex; gap: 4px; margin: 12px 0; overflow-x: auto; }
        .tab { background: var(--card-bg); border: 1px solid var(--border); color: var(--text-dim); padding: 9px 6px; border-radius: 6px; font-size: 10px; font-weight: 700; cursor: pointer; white-space: nowrap; flex: 1; text-align: center; }
        .tab.active { background: var(--accent); color: #0d1117; border-color: var(--accent); }
        .tab.ml-tab { background: rgba(0,191,255,0.15); color: var(--cyan); border-color: rgba(0,191,255,0.4); }
        .tab.ml-tab.active { background: var(--cyan); color: #0d1117; }
        .acc-box { background: var(--card-bg); padding: 12px 15px; border-radius: 10px; border: 1px solid var(--border); display: flex; justify-content: space-between; border-left: 4px solid var(--gold); cursor: pointer; margin-bottom: 10px; }
        .card { background: var(--card-bg); padding: 12px 15px; border-radius: 10px; border: 1px solid var(--border); border-left: 4px solid var(--accent); margin-bottom: 10px; }
        .toast { position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background: var(--accent); color: #0d1117; padding: 10px 22px; border-radius: 20px; font-weight: 800; display: none; z-index: 1000; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>Edgemetrix-Pro-26</h1>
            <p style="margin:2px 0 0 0; font-size:11px; color:var(--text-dim);">Self-Learning ML Terminal</p>
        </div>
        <button class="btn" onclick="copyBetSlip()">Copy Slip</button>
    </div>

    <div class="metric-card">
        <label>Base Stake (GBP)</label>
        <input type="number" id="baseStake" value="10" min="1" oninput="recalc()">
    </div>

    <div class="tabs">
        <div class="tab active" onclick="switchTab('all', this)">All</div>
        <div class="tab ml-tab" onclick="switchTab('ml', this)">ML Weights</div>
    </div>

    <div id="acc-container"></div>
    <h3 id="slate-title" style="margin:15px 0 10px 0; font-size:14px; color:var(--text-dim); text-transform:uppercase;">Active Slate</h3>
    <div id="fixtures-container">Loading...</div>
    <div id="toast">Copied & Logged!</div>

    <script>
        let data = null;
        let currentTab = 'all';
        let mlw = {};

        async function go() {
            try {
                const r = await fetch('/api/fixtures');
                data = await r.json();
                await fetchML();
                render();
            } catch(e) { console.error(e); }
        }

        async function fetchML() {
            try {
                const r = await fetch('/api/ml-weights');
                mlw = await r.json();
            } catch(e) {}
        }

        function switchTab(t, el) {
            document.querySelectorAll('.tab').forEach(x => x.classList.remove('active'));
            el.classList.add('active');
            currentTab = t;
            render();
        }

        function recalc() { render(); }

        function render() {
            const stake = parseFloat(document.getElementById('baseStake').value) || 10;
            const acc = document.getElementById('acc-container');
            const title = document.getElementById('slate-title');
            const cont = document.getElementById('fixtures-container');

            if (currentTab === 'ml') {
                title.innerText = 'ML Coefficient Weights';
                acc.innerHTML = '';
                cont.innerHTML = '<div class="card">' +
                    '<b style="color:var(--cyan);">Closed-Loop Optimizer</b>' +
                    '<p style="font-size:12px; color:var(--text-dim);">Auto-adjusts based on results.</p>' +
                    '<div style="display:grid; grid-template-columns:repeat(3,1fr); gap:8px; text-align:center;">' +
                    '<div style="background:var(--bg); padding:10px; border-radius:6px;"><div style="font-size:10px; color:var(--text-dim);">SCOREAI</div><b>' + (mlw.scoreai_weight||0.35).toFixed(3) + '</b></div>' +
                    '<div style="background:var(--bg); padding:10px; border-radius:6px;"><div style="font-size:10px; color:var(--text-dim);">CLV</div><b>' + (mlw.clv_weight||0.35).toFixed(3) + '</b></div>' +
                    '<div style="background:var(--bg); padding:10px; border-radius:6px;"><div style="font-size:10px; color:var(--text-dim);">POISSON</div><b>' + (mlw.poisson_weight||0.30).toFixed(3) + '</b></div>' +
                    '</div></div>';
                return;
            }

            if (!data) return;
            const ret = (stake * data.accumulators.three_fold.odds).toFixed(2);
            acc.innerHTML = '<div class="acc-box" onclick="logIt()">' +
                '<div><div style="font-weight:800; color:var(--gold);">3-FOLD ANCHOR</div>' +
                '<div style="font-size:12px; color:var(--text-dim);">Odds: ' + data.accumulators.three_fold.odds + '</div></div>' +
                '<div style="text-align:right;"><div style="font-weight:800; color:var(--gold);">GBP' + ret + '</div></div></div>';
            cont.innerHTML = '<p style="color:var(--text-dim);">Fixture data loaded.</p>';
        }

        async function logIt() {
            const stake = parseFloat(document.getElementById('baseStake').value) || 10;
            const odds = data.accumulators.three_fold.odds;
            await fetch('/api/ledger/log', {
                method: 'POST',
                headers: {'Content-Type':'application/json'},
                body: JSON.stringify({tier_name:'3-Fold Anchor', stake:stake, odds:odds, return_amt:(stake*odds).toFixed(2)})
            });
            const t = document.getElementById('toast');
            t.style.display = 'block';
            setTimeout(()=>t.style.display='none', 2000);
            fetchML();
        }

        function copyBetSlip() {
            navigator.clipboard.writeText('3-Fold Anchor — copied');
            const t = document.getElementById('toast');
            t.style.display = 'block';
            setTimeout(()=>t.style.display='none', 2000);
        }

        go();
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def root():
    return HTML_CONTENT

@app.get("/api/fixtures")
async def get_fixtures():
    return {
        "accumulators": {
            "three_fold": {
                "name": "3-Fold Anchor",
                "odds": 6.5
            }
        },
        "fixtures": []
    }

@app.get("/api/ml-weights")
async def api_weights():
    return get_ml_weights()

@app.post("/api/ledger/log")
async def log_entry(req: Request):
    data = await req.json()
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO ledger (timestamp, tier_name, stake, odds, return_amt) VALUES (?, ?, ?, ?, ?)",
        (datetime.now().isoformat(), data['tier_name'], data['stake'], data['odds'], data['return_amt'])
    )
    conn.commit()
    conn.close()
    optimize_ml_weights()
    return {"status": "ok"}

@app.get("/api/ledger")
async def get_ledger():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT * FROM ledger ORDER BY id DESC LIMIT 50")
    rows = cur.fetchall()
    conn.close()
    return [{"id":r[0],"timestamp":r[1],"tier_name":r[2],"stake":r[3],"odds":r[4],"return_amt":r[5],"status":r[6]} for r in rows]

@app.get("/api/health")
async def health():
    return {"status": "ok"}
# Check file is valid — NO output means NO errors
python -m py_compile app.py

# Push everything to GitHub
git add app.py
git commit -m "Complete: Full clean app.py with homepage"
git push origin main
cd C:\Users\georg\gem-v15-engine

@'
# -*- coding: utf-8 -*-
"""
Edgemetrix-Pro-26 — Quantitative Sports Trading Terminal
Core Objective: Value Identification — True Probability vs Implied Probability
Four Principles: Cold Probability · Strict +EV Filter · Multi-Model Confluence · Adaptive Weighting
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from datetime import datetime
import math
import sqlite3

app = FastAPI(title="Edgemetrix-Pro-26", version="2.0.0")
DB_FILE = "gem_ledger.db"
MIN_EV_THRESHOLD = 0.05  # +5% minimum edge

# ─── DATABASE INIT ──────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS ledger (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        module TEXT,
        selection TEXT,
        model_prob REAL,
        implied_prob REAL,
        ev_score REAL,
        odds REAL,
        stake REAL,
        status TEXT DEFAULT 'PENDING',
        result_actual TEXT,
        return_amt REAL
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS ml_weights (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        metric TEXT UNIQUE,
        weight REAL,
        last_updated TEXT
    )""")
    defaults = [
        ("xg_weight", 0.35),
        ("poisson_weight", 0.35),
        ("momentum_weight", 0.15),
        ("confluence_weight", 0.15)
    ]
    for m, v in defaults:
        c.execute("INSERT OR IGNORE INTO ml_weights (metric, weight, last_updated) VALUES (?, ?, ?)",
                  (m, v, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

init_db()

# ─── WEIGHTS & SELF-LEARNING ────────────────────────────────────
def get_weights():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT metric, weight FROM ml_weights")
    w = {r[0]: r[1] for r in c.fetchall()}
    conn.close()
    return w

def optimize_weights():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT model_prob, result_actual FROM ledger WHERE status='SETTLED' LIMIT 100")
    rows = c.fetchall()
    if len(rows) >= 6:
        accuracy = sum(1 for mp, res in rows if res == "WIN") / len(rows)
        w = get_weights()
        shift = 0.015 if accuracy > 0.55 else -0.015
        for key in w:
            new_w = max(0.05, min(0.60, w[key] + shift * (1 if key in ["poisson_weight", "xg_weight"] else -1)))
            c.execute("UPDATE ml_weights SET weight=?, last_updated=? WHERE metric=?",
                      (new_w, datetime.utcnow().isoformat(), key))
    conn.commit()
    conn.close()

# ─── PROBABILITY ENGINE ─────────────────────────────────────────
def poisson_prob(lmbda, k):
    return (math.exp(-lmbda) * (lmbda ** k)) / math.factorial(k)

def calculate_score_matrix(home_lambda, away_lambda, max_goals=5):
    matrix = []
    for h in range(max_goals + 1):
        row = []
        for a in range(max_goals + 1):
            row.append(poisson_prob(home_lambda, h) * poisson_prob(away_lambda, a))
        matrix.append(row)
    return matrix

def derive_outcomes(matrix):
    home_win = draw = away_win = over15 = over25 = btts = 0.0
    for h, row in enumerate(matrix):
        for a, p in enumerate(row):
            if h > a: home_win += p
            elif h == a: draw += p
            else: away_win += p
            if h + a >= 2: over15 += p
            if h + a >= 3: over25 += p
            if h > 0 and a > 0: btts += p
    return {
        "1x2": [home_win, draw, away_win],
        "over15": over15,
        "over25": over25,
        "btts": btts
    }

def expected_value(model_prob, odds):
    implied = 1.0 / odds if odds > 0 else 0
    ev = (model_prob * odds) - 1.0
    return round(implied * 100, 1), round(ev * 100, 2), ev >= MIN_EV_THRESHOLD

# ─── FIXTURE DATA GENERATOR ──────────────────────────────────────
def generate_fixtures():
    sample = [
        {"id": 1, "match": "Arsenal vs Chelsea", "hxg": 1.8, "axg": 1.1,
         "odds_home": 1.85, "odds_draw": 3.40, "odds_away": 4.20},
        {"id": 2, "match": "Man City vs Brentford", "hxg": 2.6, "axg": 0.8,
         "odds_home": 1.32, "odds_draw": 5.20, "odds_away": 8.50},
        {"id": 3, "match": "Brighton vs Luton", "hxg": 2.1, "axg": 0.9,
         "odds_home": 1.55, "odds_draw": 4.00, "odds_away": 6.80},
        {"id": 4, "match": "Liverpool vs Fulham", "hxg": 2.3, "axg": 1.0,
         "odds_home": 1.40, "odds_draw": 4.80, "odds_away": 7.20},
        {"id": 5, "match": "West Ham vs Everton", "hxg": 1.4, "axg": 1.2,
         "odds_home": 2.10, "odds_draw": 3.30, "odds_away": 3.60},
        {"id": 6, "match": "Bayern vs Dortmund", "hxg": 2.4, "axg": 1.5,
         "odds_home": 1.65, "odds_draw": 3.80, "odds_away": 5.00},
        {"id": 7, "match": "PSG vs Monaco", "hxg": 2.5, "axg": 1.3,
         "odds_home": 1.50, "odds_draw": 4.20, "odds_away": 6.00},
        {"id": 8, "match": "Inter vs Juventus", "hxg": 1.5, "axg": 1.1,
         "odds_home": 2.00, "odds_draw": 3.25, "odds_away": 4.10},
    ]
    w = get_weights()
    enriched = []
    for fx in sample:
        hl = fx["hxg"] * w["xg_weight"] * 2.2
        al = fx["axg"] * w["xg_weight"] * 2.2
        matrix = calculate_score_matrix(hl, al)
        oc = derive_outcomes(matrix)
        ih, evh, vh = expected_value(oc["1x2"][0], fx["odds_home"])
        idr, evdr, vdr = expected_value(oc["1x2"][1], fx["odds_draw"])
        ia, eva, va = expected_value(oc["1x2"][2], fx["odds_away"])
        conf = round(((oc["1x2"][0] - oc["1x2"][2])**2 + (oc["over25"] - 0.5)**2) * 10 * w["confluence_weight"], 1)
        enriched.append({
            **fx,
            "home_lambda": round(hl, 2),
            "away_lambda": round(al, 2),
            "prob_home": round(oc["1x2"][0] * 100, 1),
            "prob_draw": round(oc["1x2"][1] * 100, 1),
            "prob_away": round(oc["1x2"][2] * 100, 1),
            "implied_home": ih, "ev_home": evh, "value_home": vh,
            "implied_draw": idr, "ev_draw": evdr, "value_draw": vdr,
            "implied_away": ia, "ev_away": eva, "value_away": va,
            "prob_over25": round(oc["over25"] * 100, 1),
            "prob_btts": round(oc["btts"] * 100, 1),
            "confluence_score": conf,
            "score_grid": matrix
        })
    bankers = sorted(
        [f for f in enriched if f["value_home"] or f["value_draw"] or f["value_away"]],
        key=lambda x: max(x["ev_home"], x["ev_draw"], x["ev_away"]),
        reverse=True
    )[:3]
    return enriched, bankers

def build_acca(picks_list, legs):
    valid = [p for p in picks_list if p["value_home"] or p["value_draw"] or p["value_away"]]
    selected = valid[:legs]
    total_odds = 1.0
    legs_detail = []
    for m in selected:
        if m["value_home"]:
            sel, odds, ev = f"{m['match']} → HOME", m["odds_home"], m["ev_home"]
        elif m["value_draw"]:
            sel, odds, ev = f"{m['match']} → DRAW", m["odds_draw"], m["ev_draw"]
        else:
            sel, odds, ev = f"{m['match']} → AWAY", m["odds_away"], m["ev_away"]
        total_odds *= odds
        legs_detail.append({"label": sel, "odds": odds, "ev_pct": ev})
    return legs_detail, round(total_odds, 2)

# ─── API ROUTES ───────────────────────────────────────────────────
@app.get("/api/slate")
async def api_slate():
    fixtures, bankers = generate_fixtures()
    return {"fixtures": fixtures, "bankers": bankers}

@app.get("/api/weights")
async def api_weights():
    return get_weights()

@app.get("/api/ledger")
async def api_ledger():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM ledger ORDER BY id DESC LIMIT 50")
    rows = c.fetchall()
    conn.close()
    return [
        {"id": r[0], "timestamp": r[1], "module": r[2], "selection": r[3],
         "model_prob": r[4], "implied_prob": r[5], "ev_score": r[6],
         "odds": r[7], "stake": r[8], "status": r[9],
         "result_actual": r[10], "return_amt": r[11]}
        for r in rows
    ]

@app.post("/api/ledger/log")
async def log_entry(req: Request):
    data = await req.json()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "INSERT INTO ledger (timestamp, module, selection, model_prob, implied_prob, ev_score, odds, stake, return_amt) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (datetime.utcnow().isoformat(), data.get("module"), data["selection"],
         data.get("model_prob"), data.get("implied_prob"), data.get("ev_score"),
         data["odds"], data["stake"], data.get("return_amt"))
    )
    conn.commit()
    conn.close()
    optimize_weights()
    return {"status": "ok"}

@app.post("/api/ledger/settle")
async def settle_entry(req: Request):
    data = await req.json()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    actual = "WIN" if data.get("won") else "LOSS"
    ret_amt = data["stake"] * data["odds"] if data.get("won") else 0
    c.execute(
        "UPDATE ledger SET status='SETTLED', result_actual=?, return_amt=? WHERE id=?",
        (actual, ret_amt, data["id"])
    )
    conn.commit()
    conn.close()
    optimize_weights()
    return {"status": "ok"}

# ─── FRONTEND ─────────────────────────────────────────────────────
HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Edgemetrix-Pro-26 | Quantitative Trading Terminal</title>
<style>
:root{
 --bg:#070a0f; --surface:#0f1520; --panel:#161d2b; --border:#232c3b;
 --accent:#00e676; --gold:#ffc107; --warn:#ff9100; --danger:#ff3d5a;
 --text:#e6edf3; --muted:#768390; --cyan:#00d8ff; --purple:#b388ff;
}
*{box-sizing:border-box; margin:0; padding:0; font:13px/1.56 'SF Mono','Fira Code',Consolas,monospace;}
body{background:var(--bg); color:var(--text); padding:12px; max-width:1200px; margin:0 auto;}
header{display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--accent); padding:10px 0 12px; margin-bottom:12px; flex-wrap:wrap; gap:8px;}
h1{font-size:20px; font-weight:800; color:var(--accent); letter-spacing:1px;}
.sub{font-size:11px; color:var(--muted); text-transform:uppercase; letter-spacing:0.5px;}
.stat-bar{display:flex; gap:14px; align-items:center; flex-wrap:wrap;}
.stat{text-align:center;}
.stat>div:first-child{color:var(--muted); font-size:10px; text-transform:uppercase;}
.stat>div:last-child{font-weight:700; font-size:14px;}
.val-plus{color:var(--accent);}
.val-minus{color:var(--danger);}
.tabs{display:flex; gap:4px; margin-bottom:12px; flex-wrap:wrap;}
.tab{background:var(--surface); border:1px solid var(--border); color:var(--muted); padding:8px 10px; border-radius:4px; cursor:pointer; white-space:nowrap; font-size:11px; text-transform:uppercase; letter-spacing:0.5px;}
.tab.active{background:var(--accent); color:#000; border-color:var(--accent); font-weight:700;}
.tab.bankers{border-left:3px solid var(--gold);}
.tab.daily{border-left:3px solid var(--accent);}
.tab.betbuilder{border-left:3px solid var(--cyan);}
.tab.csmatrix{border-left:3px solid var(--purple);}
.tab.accabuild{border-left:3px solid var(--warn);}
.tab.ledger{border-left:3px solid var(--danger);}
.tab.weights{border-left:3px solid #666;}
.card{background:var(--surface); border:1px solid var(--border); border-radius:6px; padding:12px; margin-bottom:10px;}
.card-header{display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; padding-bottom:6px; border-bottom:1px solid var(--border);}
.card-title{font-weight:700; font-size:13px; color:var(--accent); text-transform:uppercase; letter-spacing:0.5px;}
.grid-row{display:grid; grid-template-columns:2fr 1fr 1fr 1fr 1fr 1fr; gap:6px; padding:6px 4px; border-bottom:1px solid var(--border); align-items:center; font-size:11px;}
.grid-row.head{color:var(--muted); font-size:10px; text-transform:uppercase; letter-spacing:0.5px;}
.ev-tag{padding:2px 5px; border-radius:3px; font-weight:700; font-size:10px;}
.ev-pos{background:rgba(0,230,118,.15); color:var(--accent); border:1px solid var(--accent);}
.ev-neu{background:rgba(255,145,0,.15); color:var(--warn); border:1px solid var(--warn);}
.ev-neg{background:rgba(255,61,90,.15); color:var(--danger); border:1px solid var(--danger);}
.acc-selector{display:flex; gap:8px; align-items:center; margin:10px 0;}
select{background:var(--panel); color:var(--text); border:1px solid var(--border); padding:6px; border-radius:4px;}
.btn{background:var(--accent); color:#000; border:none; padding:8px 14px; border-radius:4px; font-weight:700; cursor:pointer;}
.btn-outline{background:transparent; border:1px solid var(--accent); color:var(--accent); margin-left:6px;}
.grid-score{display:grid; grid-template-columns:40px repeat(6,1fr); gap:2px; text-align:center; font-size:10px;}
.grid-score>div{padding:4px 2px; border-radius:2px;}
.grid-score.head{color:var(--muted); font-weight:900;}
.cell-value{background:rgba(0,230,118,.12); color:var(--accent); font-weight:700;}
.cell-norm{background:var(--panel);}
.weight-grid{display:grid; grid-template-columns:repeat(4,1fr); gap:8px; text-align:center;}
.weight-card{background:var(--panel); padding:10px; border-radius:4px;}
.w-val{font-size:18px; font-weight:800;}
.toast{position:fixed; bottom:20px; left:50%; transform:translateX(-50%); background:var(--accent); color:#000; padding:10px 24px; border-radius:20px; font-weight:700; display:none; z-index:999;}
.stake-row{display:flex; gap:10px; align-items:center; margin-bottom:10px; flex-wrap:wrap;}
input[type=number]{background:var(--panel); border:1px solid var(--border); color:var(--accent); padding:6px 8px; border-radius:4px; width:90px; font-weight:700;}
.tier-group{display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:10px; margin-top:10px;}
.tier-card{background:var(--panel); border:1px solid var(--border); border-radius:6px; padding:10px; cursor:pointer; transition:.15s;}
.tier-card:hover{border-color:var(--accent);}
.tier-h{font-weight:700; margin-bottom:4px;}
</style>
</head>
<body>
<header>
 <div class="brand-col">
  <h1>EDGEMETRIX-PRO-26</h1>
  <div class="sub">QUANTITATIVE SPORTS TRADING DESK · VALUE IDENTIFICATION ENGINE</div>
 </div>
 <div class="stat-bar">
  <div class="stat"><div>Active Picks</div><div id="pickCount">—</div></div>
  <div class="stat"><div>Avg EV</div><div id="avgEV" class="val-plus">—</div></div>
  <div class="stat"><div>ML Mode</div><div style="color:var(--cyan);">ADAPTIVE</div></div>
  <button class="btn" style="font-size:11px; padding:6px 10px;" onclick="copySlip()">COPY SLIP</button>
 </div>
</header>

<div class="stake-row">
 <label>Base Stake GBP:</label>
 <input type="number" id="baseStake" value="10" min="1" oninput="recalc()">
 <span style="color:var(--muted); font-size:11px;">Min EV threshold: +
cd C:\Users\georg\gem-v15-engine

@'
# -*- coding: utf-8 -*-
"""
Edgemetrix-Pro-26 — Quantitative Sports Trading Terminal
Core Objective: Value Identification — True Probability vs Implied Probability
Four Principles: Cold Probability · Strict +EV Filter · Multi-Model Confluence · Adaptive Weighting
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from datetime import datetime
import math
import sqlite3

app = FastAPI(title="Edgemetrix-Pro-26", version="2.0.0")
DB_FILE = "gem_ledger.db"
MIN_EV_THRESHOLD = 0.05  # +5% minimum edge

# ─── DATABASE INIT ──────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS ledger (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        module TEXT,
        selection TEXT,
        model_prob REAL,
        implied_prob REAL,
        ev_score REAL,
        odds REAL,
        stake REAL,
        status TEXT DEFAULT 'PENDING',
        result_actual TEXT,
        return_amt REAL
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS ml_weights (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        metric TEXT UNIQUE,
        weight REAL,
        last_updated TEXT
    )""")
    defaults = [
        ("xg_weight", 0.35),
        ("poisson_weight", 0.35),
        ("momentum_weight", 0.15),
        ("confluence_weight", 0.15)
    ]
    for m, v in defaults:
        c.execute("INSERT OR IGNORE INTO ml_weights (metric, weight, last_updated) VALUES (?, ?, ?)",
                  (m, v, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

init_db()

# ─── WEIGHTS & SELF-LEARNING ────────────────────────────────────
def get_weights():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT metric, weight FROM ml_weights")
    w = {r[0]: r[1] for r in c.fetchall()}
    conn.close()
    return w

def optimize_weights():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT model_prob, result_actual FROM ledger WHERE status='SETTLED' LIMIT 100")
    rows = c.fetchall()
    if len(rows) >= 6:
        accuracy = sum(1 for mp, res in rows if res == "WIN") / len(rows)
        w = get_weights()
        shift = 0.015 if accuracy > 0.55 else -0.015
        for key in w:
            new_w = max(0.05, min(0.60, w[key] + shift * (1 if key in ["poisson_weight", "xg_weight"] else -1)))
            c.execute("UPDATE ml_weights SET weight=?, last_updated=? WHERE metric=?",
                      (new_w, datetime.utcnow().isoformat(), key))
    conn.commit()
    conn.close()

# ─── PROBABILITY ENGINE ─────────────────────────────────────────
def poisson_prob(lmbda, k):
    return (math.exp(-lmbda) * (lmbda ** k)) / math.factorial(k)

def calculate_score_matrix(home_lambda, away_lambda, max_goals=5):
    matrix = []
    for h in range(max_goals + 1):
        row = []
        for a in range(max_goals + 1):
            row.append(poisson_prob(home_lambda, h) * poisson_prob(away_lambda, a))
        matrix.append(row)
    return matrix

def derive_outcomes(matrix):
    home_win = draw = away_win = over15 = over25 = btts = 0.0
    for h, row in enumerate(matrix):
        for a, p in enumerate(row):
            if h > a: home_win += p
            elif h == a: draw += p
            else: away_win += p
            if h + a >= 2: over15 += p
            if h + a >= 3: over25 += p
            if h > 0 and a > 0: btts += p
    return {
        "1x2": [home_win, draw, away_win],
        "over15": over15,
        "over25": over25,
        "btts": btts
    }

def expected_value(model_prob, odds):
    implied = 1.0 / odds if odds > 0 else 0
    ev = (model_prob * odds) - 1.0
    return round(implied * 100, 1), round(ev * 100, 2), ev >= MIN_EV_THRESHOLD

# ─── FIXTURE DATA GENERATOR ──────────────────────────────────────
def generate_fixtures():
    sample = [
        {"id": 1, "match": "Arsenal vs Chelsea", "hxg": 1.8, "axg": 1.1,
         "odds_home": 1.85, "odds_draw": 3.40, "odds_away": 4.20},
        {"id": 2, "match": "Man City vs Brentford", "hxg": 2.6, "axg": 0.8,
         "odds_home": 1.32, "odds_draw": 5.20, "odds_away": 8.50},
        {"id": 3, "match": "Brighton vs Luton", "hxg": 2.1, "axg": 0.9,
         "odds_home": 1.55, "odds_draw": 4.00, "odds_away": 6.80},
        {"id": 4, "match": "Liverpool vs Fulham", "hxg": 2.3, "axg": 1.0,
         "odds_home": 1.40, "odds_draw": 4.80, "odds_away": 7.20},
        {"id": 5, "match": "West Ham vs Everton", "hxg": 1.4, "axg": 1.2,
         "odds_home": 2.10, "odds_draw": 3.30, "odds_away": 3.60},
        {"id": 6, "match": "Bayern vs Dortmund", "hxg": 2.4, "axg": 1.5,
         "odds_home": 1.65, "odds_draw": 3.80, "odds_away": 5.00},
        {"id": 7, "match": "PSG vs Monaco", "hxg": 2.5, "axg": 1.3,
         "odds_home": 1.50, "odds_draw": 4.20, "odds_away": 6.00},
        {"id": 8, "match": "Inter vs Juventus", "hxg": 1.5, "axg": 1.1,
         "odds_home": 2.00, "odds_draw": 3.25, "odds_away": 4.10},
    ]
    w = get_weights()
    enriched = []
    for fx in sample:
        hl = fx["hxg"] * w["xg_weight"] * 2.2
        al = fx["axg"] * w["xg_weight"] * 2.2
        matrix = calculate_score_matrix(hl, al)
        oc = derive_outcomes(matrix)
        ih, evh, vh = expected_value(oc["1x2"][0], fx["odds_home"])
        idr, evdr, vdr = expected_value(oc["1x2"][1], fx["odds_draw"])
        ia, eva, va = expected_value(oc["1x2"][2], fx["odds_away"])
        conf = round(((oc["1x2"][0] - oc["1x2"][2])**2 + (oc["over25"] - 0.5)**2) * 10 * w["confluence_weight"], 1)
        enriched.append({
            **fx,
            "home_lambda": round(hl, 2),
            "away_lambda": round(al, 2),
            "prob_home": round(oc["1x2"][0] * 100, 1),
            "prob_draw": round(oc["1x2"][1] * 100, 1),
            "prob_away": round(oc["1x2"][2] * 100, 1),
            "implied_home": ih, "ev_home": evh, "value_home": vh,
            "implied_draw": idr, "ev_draw": evdr, "value_draw": vdr,
            "implied_away": ia, "ev_away": eva, "value_away": va,
            "prob_over25": round(oc["over25"] * 100, 1),
            "prob_btts": round(oc["btts"] * 100, 1),
            "confluence_score": conf,
            "score_grid": matrix
        })
    bankers = sorted(
        [f for f in enriched if f["value_home"] or f["value_draw"] or f["value_away"]],
        key=lambda x: max(x["ev_home"], x["ev_draw"], x["ev_away"]),
        reverse=True
    )[:3]
    return enriched, bankers

def build_acca(picks_list, legs):
    valid = [p for p in picks_list if p["value_home"] or p["value_draw"] or p["value_away"]]
    selected = valid[:legs]
    total_odds = 1.0
    legs_detail = []
    for m in selected:
        if m["value_home"]:
            sel, odds, ev = f"{m['match']} → HOME", m["odds_home"], m["ev_home"]
        elif m["value_draw"]:
            sel, odds, ev = f"{m['match']} → DRAW", m["odds_draw"], m["ev_draw"]
        else:
            sel, odds, ev = f"{m['match']} → AWAY", m["odds_away"], m["ev_away"]
        total_odds *= odds
        legs_detail.append({"label": sel, "odds": odds, "ev_pct": ev})
    return legs_detail, round(total_odds, 2)

# ─── API ROUTES ───────────────────────────────────────────────────
@app.get("/api/slate")
async def api_slate():
    fixtures, bankers = generate_fixtures()
    return {"fixtures": fixtures, "bankers": bankers}

@app.get("/api/weights")
async def api_weights():
    return get_weights()

@app.get("/api/ledger")
async def api_ledger():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM ledger ORDER BY id DESC LIMIT 50")
    rows = c.fetchall()
    conn.close()
    return [
        {"id": r[0], "timestamp": r[1], "module": r[2], "selection": r[3],
         "model_prob": r[4], "implied_prob": r[5], "ev_score": r[6],
         "odds": r[7], "stake": r[8], "status": r[9],
         "result_actual": r[10], "return_amt": r[11]}
        for r in rows
    ]

@app.post("/api/ledger/log")
async def log_entry(req: Request):
    data = await req.json()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "INSERT INTO ledger (timestamp, module, selection, model_prob, implied_prob, ev_score, odds, stake, return_amt) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (datetime.utcnow().isoformat(), data.get("module"), data["selection"],
         data.get("model_prob"), data.get("implied_prob"), data.get("ev_score"),
         data["odds"], data["stake"], data.get("return_amt"))
    )
    conn.commit()
    conn.close()
    optimize_weights()
    return {"status": "ok"}

@app.post("/api/ledger/settle")
async def settle_entry(req: Request):
    data = await req.json()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    actual = "WIN" if data.get("won") else "LOSS"
    ret_amt = data["stake"] * data["odds"] if data.get("won") else 0
    c.execute(
        "UPDATE ledger SET status='SETTLED', result_actual=?, return_amt=? WHERE id=?",
        (actual, ret_amt, data["id"])
    )
    conn.commit()
    conn.close()
    optimize_weights()
    return {"status": "ok"}

@app.get("/api/health")
async def health():
    return {"status": "ok", "mode": "quantitative-trading"}

# ─── FRONTEND ─────────────────────────────────────────────────────
HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Edgemetrix-Pro-26 | Quantitative Trading Terminal</title>
<style>
:root{--bg:#070a0f; --surface:#0f1520; --panel:#161d2b; --border:#232c3b; --accent:#00e676; --gold:#ffc107; --warn:#ff9100; --danger:#ff3d5a; --text:#e6edf3; --muted:#768390; --cyan:#00d8ff; --purple:#b388ff;}
*{box-sizing:border-box; margin:0; padding:0; font:13px/1.56 'SF Mono','Fira Code',Consolas,monospace;}
body{background:var(--bg); color:var(--text); padding:12px; max-width:1200px; margin:0 auto;}
header{display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--accent); padding:10px 0 12px; margin-bottom:12px; flex-wrap:wrap; gap:8px;}
h1{font-size:20px; font-weight:800; color:var(--accent); letter-spacing:1px;}
.sub{font-size:11px; color:var(--muted); text-transform:uppercase; letter-spacing:0.5px;}
.stat-bar{display:flex; gap:14px; align-items:center; flex-wrap:wrap;}
.stat{text-align:center;}
.stat>div:first-child{color:var(--muted); font-size:10px; text-transform:uppercase;}
.stat>div:last-child{font-weight:700; font-size:14px;}
.val-plus{color:var(--accent);}
.val-minus{color:var(--danger);}
.tabs{display:flex; gap:4px; margin-bottom:12px; flex-wrap:wrap;}
.tab{background:var(--surface); border:1px solid var(--border); color:var(--muted); padding:8px 10px; border-radius:4px; cursor:pointer; white-space:nowrap; font-size:11px; text-transform:uppercase; letter-spacing:0.5px;}
.tab.active{background:var(--accent); color:#000; border-color:var(--accent); font-weight:700;}
.tab.bankers{border-left:3px solid var(--gold);}
.tab.daily{border-left:3px solid var(--accent);}
.tab.betbuilder{border-left:3px solid var(--cyan);}
.tab.csmatrix{border-left:3px solid var(--purple);}
.tab.accabuild{border-left:3px solid var(--warn);}
.tab.ledger{border-left:3px solid var(--danger);}
.tab.weights{border-left:3px solid #666;}
.card{background:var(--surface); border:1px solid var(--border); border-radius:6px; padding:12px; margin-bottom:10px;}
.card-header{display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; padding-bottom:6px; border-bottom:1px solid var(--border);}
.card-title{font-weight:700; font-size:13px; color:var(--accent); text-transform:uppercase; letter-spacing:0.5px;}
.grid-row{display:grid; grid-template-columns:2fr 1fr 1fr 1fr 1fr 1fr; gap:6px; padding:6px 4px; border-bottom:1px solid var(--border); align-items:center; font-size:11px;}
.grid-row.head{color:var(--muted); font-size:10px; text-transform:uppercase; letter-spacing:0.5px;}
.ev-tag{padding:2px 5px; border-radius:3px; font-weight:700; font-size:10px;}
.ev-pos{background:rgba(0,230,118,.15); color:var(--accent); border:1px solid var(--accent);}
.ev-neu{background:rgba(255,145,0,.15); color:var(--warn); border:1px solid var(--warn);}
.ev-neg{background:rgba(255,61,90,.15); color:var(--danger); border:1px solid var(--danger);}
.acc-selector{display:flex; gap:8px; align-items:center; margin:10px 0;}
select{background:var(--panel); color:var(--text); border:1px solid var(--border); padding:6px; border-radius:4px;}
.btn{background:var(--accent); color:#000; border:none; padding:8px 14px; border-radius:4px; font-weight:700; cursor:pointer;}
.toast{position:fixed; bottom:20px; left:50%; transform:translateX(-50%); background:var(--accent); color:#000; padding:10px 24px; border-radius:20px; font-weight:700; display:none; z-index:999;}
.stake-row{display:flex; gap:10px; align-items:center; margin-bottom:10px; flex-wrap:wrap;}
input[type=number]{background:var(--panel); border:1px solid var(--border); color:var(--accent); padding:6px 8px; border-radius:4px; width:90px; font-weight:700;}
.tier-group{display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:10px; margin-top:10px;}
.tier-card{background:var(--panel); border:1px solid var(--border); border-radius:6px; padding:10px; cursor:pointer; transition:.15s;}
.tier-card:hover{border-color:var(--accent);}
.tier-h{font-weight:700; margin-bottom:4px;}
</style>
</head>
<body>
<header>
 <div>
  <h1>EDGEMETRIX-PRO-26</h1>
  <div class="sub">QUANTITATIVE SPORTS TRADING DESK · VALUE IDENTIFICATION ENGINE</div>
 </div>
 <div class="stat-bar">
  <div class="stat"><div>Active Picks</div><div id="pickCount">—</div></div>
  <div class="stat"><div>Avg EV</div><div id="avgEV" class="val-plus">—</div></div>
  <div class="stat"><div>ML Mode</div><div style="color:var(--cyan);">ADAPTIVE</div></div>
  <button class="btn" style="font-size:11px; padding:6px 10px;" onclick="copySlip()">COPY SLIP</button>
 </div>
</header>

<div class="stake-row">
 <label>Base Stake GBP:</label>
 <input type="number" id="baseStake" value="10" min="1" oninput="renderAll()">
 <span style="color:var(--muted); font-size:11px;">Min EV threshold: +5.0%</span>
</div>

<div class="tabs">
 <div class="tab bankers active" onclick="switchTab('bankers',this)">BANKERS OF THE DAY</div>
 <div class="tab daily" onclick="switchTab('daily',this)">DAILY PICKS</div>
 <div class="tab betbuilder" onclick="switchTab('betbuilder',this)">BET BUILDER</div>
 <div class="tab csmatrix" onclick="switchTab('csmatrix',this)">CORRECT SCORE</div>
 <div class="tab accabuild" onclick="switchTab('acca',this)">ACCA BUILDER</div>
 <div class="tab ledger" onclick="switchTab('ledger',this)">LEDGER</
cd C:\Users\georg\gem-v15-engine

# Check file is clean first
python -m py_compile app.py

# Push to GitHub
git add app.py
git commit -m "Full: Quant Trading Terminal + All Modules"
git push origin main
cd C:\Users\georg\gem-v15-engine
python -m uvicorn app:app --reload
cd C:\Users\georg\gem-v15-engine

@'
# -*- coding: utf-8 -*-
"""
Edgemetrix-Pro-26 — Quantitative Sports Trading Terminal
Core: Value Identification — True Probability vs Implied Probability
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from datetime import datetime
import math
import sqlite3

app = FastAPI(title="Edgemetrix-Pro-26", version="2.1.0")
DB_FILE = "gem_ledger.db"
MIN_EV_THRESHOLD = 0.05

# ─── DATABASE INIT ──────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS ledger (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        module TEXT,
        selection TEXT,
        model_prob REAL,
        implied_prob REAL,
        ev_score REAL,
        odds REAL,
        stake REAL,
        status TEXT DEFAULT 'PENDING',
        result_actual TEXT,
        return_amt REAL
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS ml_weights (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        metric TEXT UNIQUE,
        weight REAL,
        last_updated TEXT
    )""")
    defaults = [
        ("xg_weight", 0.35),
        ("poisson_weight", 0.35),
        ("momentum_weight", 0.15),
        ("confluence_weight", 0.15)
    ]
    for m, v in defaults:
        c.execute("INSERT OR IGNORE INTO ml_weights (metric, weight, last_updated) VALUES (?, ?, ?)",
                  (m, v, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

init_db()

def get_weights():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT metric, weight FROM ml_weights")
    w = {r[0]: r[1] for r in c.fetchall()}
    conn.close()
    return w

def optimize_weights():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT model_prob, result_actual FROM ledger WHERE status='SETTLED' LIMIT 100")
    rows = c.fetchall()
    if len(rows) >= 6:
        accuracy = sum(1 for mp, res in rows if res == "WIN") / len(rows)
        w = get_weights()
        shift = 0.015 if accuracy > 0.55 else -0.015
        for key in w:
            new_w = max(0.05, min(0.60, w[key] + shift * (1 if key in ["poisson_weight", "xg_weight"] else -1)))
            c.execute("UPDATE ml_weights SET weight=?, last_updated=? WHERE metric=?",
                      (new_w, datetime.utcnow().isoformat(), key))
    conn.commit()
    conn.close()

# ─── PROBABILITY ENGINE ─────────────────────────────────────────
def poisson(lmbda, k):
    return (math.exp(-lmbda) * (lmbda ** k)) / math.factorial(k)

def score_grid(home_lambda, away_lambda, max_goals=5):
    matrix = []
    for h in range(max_goals + 1):
        row = []
        for a in range(max_goals + 1):
            row.append(poisson(home_lambda, h) * poisson(away_lambda, a))
        matrix.append(row)
    return matrix

def derive_outcomes(matrix):
    home_win = draw = away_win = over15 = over25 = btts = 0.0
    for h, row in enumerate(matrix):
        for a, p in enumerate(row):
            if h > a: home_win += p
            elif h == a: draw += p
            else: away_win += p
            if h + a >= 2: over15 += p
            if h + a >= 3: over25 += p
            if h > 0 and a > 0: btts += p
    return {
        "1x2": [home_win, draw, away_win],
        "over15": over15,
        "over25": over25,
        "btts": btts
    }

def expected_value(model_prob, odds):
    implied = 1.0 / odds if odds > 0 else 0
    ev = (model_prob * odds) - 1
    return round(implied * 100, 1), round(ev * 100, 2), ev >= MIN_EV_THRESHOLD

# ─── FIXTURE DATA ────────────────────────────────────────────────
def generate_fixtures():
    sample = [
        ("Arsenal vs Chelsea", 1.8, 1.1, 1.85, 3.40, 4.20),
        ("Man City vs Brentford", 2.6, 0.8, 1.32, 5.20, 8.50),
        ("Brighton vs Luton", 2.1, 0.9, 1.55, 4.00, 6.80),
        ("Liverpool vs Fulham", 2.3, 1.0, 1.40, 4.80, 7.20),
        ("West Ham vs Everton", 1.4, 1.2, 2.10, 3.30, 3.60),
        ("Bayern vs Dortmund", 2.4, 1.5, 1.65, 3.80, 5.00),
        ("PSG vs Monaco", 2.5, 1.3, 1.50, 4.20, 6.00),
        ("Inter vs Juventus", 1.5, 1.1, 2.00, 3.25, 4.10),
    ]
    w = get_weights()
    enriched = []
    for match, hxg, axg, oh, od, oa in sample:
        hl = hxg * w["xg_weight"] * 2.2
        al = axg * w["xg_weight"] * 2.2
        m = score_grid(hl, al)
        o = derive_outcomes(m)
        ih, evh, vh = expected_value(o["1x2"][0], oh)
        idr, evdr, vdr = expected_value(o["1x2"][1], od)
        ia, eva, va = expected_value(o["1x2"][2], oa)
        enriched.append({
            "match": match, "hxg": hxg, "axg": axg,
            "odds_home": oh, "odds_draw": od, "odds_away": oa,
            "prob_home": round(o["1x2"][0]*100,1),
            "prob_draw": round(o["1x2"][1]*100,1),
            "prob_away": round(o["1x2"][2]*100,1),
            "ev_home": evh, "value_home": vh,
            "ev_draw": evdr, "value_draw": vdr,
            "ev_away": eva, "value_away": va,
            "prob_over25": round(o["over25"]*100,1),
            "prob_btts": round(o["btts"]*100,1),
            "score_grid": m
        })
    bankers = sorted(
        [f for f in enriched if f["value_home"] or f["value_draw"] or f["value_away"]],
        key=lambda x: max(x["ev_home"], x["ev_draw"], x["ev_away"]),
        reverse=True
    )[:3]
    return enriched, bankers

def build_acca(picks, legs):
    valid = [p for p in picks if p["value_home"] or p["value_draw"] or p["value_away"]][:legs]
    total_odds = 1.0
    details = []
    for m in valid:
        if m["value_home"]:
            sel, odds, ev_pct = f"{m['match']} → HOME", m["odds_home"], m["ev_home"]
        elif m["value_draw"]:
            sel, odds, ev_pct = f"{m['match']} → DRAW", m["odds_draw"], m["ev_draw"]
        else:
            sel, odds, ev_pct = f"{m['match']} → AWAY", m["odds_away"], m["ev_away"]
        total_odds *= odds
        details.append({"label": sel, "odds": odds, "ev_pct": ev_pct})
    return details, round(total_odds, 2)

# ─── API ROUTES ───────────────────────────────────────────────────
@app.get("/api/slate")
async def api_slate():
    f, b = generate_fixtures()
    return {"fixtures": f, "bankers": b}

@app.get("/api/weights")
async def api_weights():
    return get_weights()

@app.get("/api/ledger")
async def api_ledger():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM ledger ORDER BY id DESC LIMIT 50")
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "timestamp": r[1], "module": r[2], "selection": r[3],
             "odds": r[7], "stake": r[8], "status": r[9], "return_amt": r[11]} for r in rows]

@app.post("/api/log")
async def log_entry(req: Request):
    data = await req.json()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "INSERT INTO ledger (timestamp, module, selection, odds, stake) VALUES (?, ?, ?, ?, ?)",
        (datetime.utcnow().isoformat(), data.get("module"), data["selection"],
         data["odds"], data["stake"])
    )
    conn.commit()
    conn.close()
    optimize_weights()
    return {"status": "ok"}

@app.get("/api/health")
async def health():
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
async def root():
    return HTML_CONTENT

# ─── FULL FRONTEND ────────────────────────────────────────────────
HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Edgemetrix-Pro-26 | Quant Trading Desk</title>
<style>
:root{--bg:#070a0f;--srf:#0f1520;--pnl:#161d2b;--brd:#232c3b;--ac:#00e676;--gd:#ffc107;--wrn:#ff9100;--dng:#ff3d5a;--txt:#e6edf3;--dim:#768390;--cy:#00d8ff;--prp:#b388ff;}
*{box-sizing:border-box;margin:0;padding:0;font:13px/1.56 ui-monospace,'SF Mono',monospace;}
body{background:var(--bg);color:var(--txt);padding:12px;max-width:1200px;margin:0 auto;}
.head{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--ac);padding:10px 0 12px;flex-wrap:wrap;gap:8px;}
h1{font-size:20px;font-weight:800;color:var(--ac);letter-spacing:1px;}
.sub{font-size:11px;color:var(--dim);text-transform:uppercase;letter-spacing:0.5px;}
.stat-bar{display:flex;gap:14px;align-items:center;flex-wrap:wrap;}
.stat{text-align:center;}
.stat>div:first-child{color:var(--dim);font-size:10px;text-transform:uppercase;}
.stat>div:last-child{font-weight:700;font-size:14px;}
.plus{color:var(--ac);}
.tabs{display:flex;gap:4px;margin:12px 0;flex-wrap:wrap;}
.tab{background:var(--srf);border:1px solid var(--brd);color:var(--dim);padding:8px 10px;border-radius:4px;cursor:pointer;font-size:11px;text-transform:uppercase;white-space:nowrap;letter-spacing:0.5px;}
.tab.active{background:var(--ac);color:#000;border-color:var(--ac);font-weight:700;}
.tab.bk{border-left:3px solid var(--gd);}
.tab.dy{border-left:3px solid var(--ac);}
.tab.bb{border-left:3px solid var(--cy);}
.tab.cs{border-left:3px solid var(--prp);}
.tab.acc{border-left:3px solid var(--wrn);}
.tab.ld{border-left:3px solid var(--dng);}
.tab.wt{border-left:3px solid #666;}
.card{background:var(--srf);border:1px solid var(--brd);border-radius:6px;padding:12px;margin:10px 0;}
.capt{font-weight:700;color:var(--ac);margin-bottom:10px;padding-bottom:6px;border-bottom:1px solid var(--brd);}
.row{display:grid;grid-template-columns:2fr 1fr 1fr 1fr 1fr 1fr;gap:6px;padding:8px 4px;border-bottom:1px solid var(--brd);align-items:center;font-size:11px;}
.row.hdr{color:var(--dim);font-size:10px;text-transform:uppercase;}
.tag{padding:3px 6px;border-radius:3px;font-weight:700;font-size:10px;}
.ok{background:rgba(0,230,118,.15);color:var(--ac);border:1px solid var(--ac);}
.warn{background:rgba(255,145,0,.15);color:var(--wrn);border:1px solid var(--wrn);}
.bad{background:rgba(255,61,90,.15);color:var(--dng);border:1px solid var(--dng);}
input,select{background:var(--pnl);border:1px solid var(--brd);color:var(--ac);padding:6px 8px;border-radius:4px;}
button{background:var(--ac);color:#000;border:none;padding:8px 14px;border-radius:4px;font-weight:700;cursor:pointer;}
.but-o{background:transparent;border:1px solid var(--ac);color:var(--ac);margin-left:6px;}
.grid-score{display:grid;grid-template-columns:40px repeat(6,1fr);gap:2px;text-align:center;font-size:10px;}
.grid-score>div{padding:5px 2px;border-radius:2px;}
.gok{background:rgba(0,230,118,.12);color:var(--ac);font-weight:700;}
.gnm{background:var(--pnl);}
.toast{position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:var(--ac);color:#000;padding:12px 24px;border-radius:20px;font-weight:700;display:none;z-index:999;}
.flx{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:12px;}
.tier{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:10px;margin-top:10px;}
.tcard{background:var(--pnl);border:1px solid var(--brd);border-radius:6px;padding:12px;cursor:pointer;transition:.15s;}
.tcard:hover{border-color:var(--ac);}
.wgrid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;text-align:center;}
.wcard{background:var(--pnl);padding:12px;border-radius:6px;}
.wval{font-size:18px;font-weight:800;}
</style>
</head>
<body>
<header class="head">
 <div>
  <h1>EDGEMETRIX-PRO-26</h1>
  <div class="sub">QUANTITATIVE SPORTS TRADING DESK · VALUE IDENTIFICATION ENGINE</div>
 </div>
 <div class="stat-bar">
  <div class="stat"><div>PICKS</div><div id="pc">—</div></div>
  <div class="stat"><div>AVG +EV</div><div id="av" class="plus">—</div></div>
  <div class="stat"><div>ML MODE</div><div style="color:var(--cy);">ADAPTIVE</div></div>
  <button onclick="copySlip()">COPY SLIP</button>
 </div>
</header>

<div class="flx">
 <label>BASE STAKE GBP:</label>
 <input type="number" id="stk" value="10" min="1" oninput="renderAll()">
 <span style="color:var(--dim);font-size:11px;">MIN EDGE: +5.0%</span>
</div>

<div class="tabs">
 <div class="tab bk active" onclick="switchTab('bankers',this)">BANKERS OF THE DAY</div>
 <div class="tab dy" onclick="switchTab('daily',this)">DAILY PICKS</div>
 <div class="tab bb" onclick="switchTab('betbuilder',this)">BET BUILDER</div>
 <div class="tab cs" onclick="switchTab('score',this)">CORRECT SCORE</div>
 <div class="tab acc" onclick="switchTab('acca',this)">ACCA BUILDER</div>
 <div class="tab ld" onclick="switchTab('ledger',this)">LEDGER</div>
 <div class="tab wt" onclick="switchTab('weights',this)">ML WEIGHTS</div>
</div>

<div id="output"></div>
<div class="toast" id="toast">✓ COPIED & LOGGED</div>

<script>
let fixtures = [], bankers = [], weights = {}, ledger = [], currentTab = 'bankers';
const stake = () => parseFloat(document.getElementById('stk').value) || 10;

async function loadAll(){
 const [sRes, wRes, lRes] = await Promise.all([
  fetch('/api/slate'), fetch('/api/weights'), fetch('/api/ledger')
 ]);
 const sData = await sRes.json();
 fixtures = sData.fixtures; bankers = sData.bankers;
 weights = await wRes.json(); ledger = await lRes.json();
 const evs = fixtures.flatMap(f => [f.ev_home, f.ev_draw, f.ev_away]).filter(e => e > 0);
 document.getElementById('pc').textContent = fixtures.filter(f => f.value_home || f.value_draw || f.value_away).length;
 document.getElementById('av').textContent = evs.length ? (evs.reduce((a,b)=>a+b,0)/evs.length).toFixed(2)+'%' : '—';
 renderAll();
}

function switchTab(tabName, el){
 document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
 el.classList.add('active');
 currentTab = tabName;
 renderAll();
}

function evClass(pct){
 return pct >= 5 ? 'ok' : pct >= 0 ? 'warn' : 'bad';
}

async function logSelection(label, odds){
 await fetch('/api/log', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({module: currentTab, selection: label, odds: odds, stake: stake()})
 });
 const t = document.getElementById('toast');
 t.style.display = 'block';
 setTimeout(() => t.style.display = 'none', 2500);
 const lRes = await fetch('/api/ledger'); ledger = await lRes.json();
}

function copySlip(){
 navigator.clipboard.writeText(`Stake: £${stake()}\n${bankers.map(b=>b.match).join('\n')}`);
 document.getElementById('toast').style.display='block';
 setTimeout(()=>document.getElementById('toast').style.display='none',2500);
}

function renderAll(){
 const out = document.getElementById('output'), s = stake();
 if(currentTab === 'bankers'){
  out.innerHTML = `<div class="card">
   <div class="capt">⭐ BANKERS OF THE DAY — TOP VALUE SELECTIONS</div>
   ${bankers.length ? bankers.map(m => {
    let sel, odds, ev;
    if(m.value_home){ sel='HOME'; odds=m.odds_home; ev
cd C:\Users\georg\gem-v15-engine

@'
# -*- coding: utf-8 -*-
"""
Edgemetrix-Pro-26 — Quantitative Sports Trading Terminal
All 7 Tabs Complete · Self-Learning · Poisson Engine
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from datetime import datetime
import math
import sqlite3

app = FastAPI(title="Edgemetrix-Pro-26", version="2.2.0")
DB_FILE = "gem_ledger.db"
MIN_EV_THRESHOLD = 0.05

# ─── DATABASE ────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS ledger (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT, module TEXT, selection TEXT,
        model_prob REAL, implied_prob REAL, ev_score REAL,
        odds REAL, stake REAL, status TEXT DEFAULT 'PENDING',
        result_actual TEXT, return_amt REAL
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS ml_weights (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        metric TEXT UNIQUE, weight REAL, last_updated TEXT
    )""")
    defaults = [("xg_weight",0.35),("poisson_weight",0.35),("momentum_weight",0.15),("confluence_weight",0.15)]
    for m,v in defaults:
        c.execute("INSERT OR IGNORE INTO ml_weights VALUES (NULL,?,?,?)",
                  (m,v,datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

init_db()

def get_weights():
    with sqlite3.connect(DB_FILE) as c:
        return {r[0]:r[1] for r in c.execute("SELECT metric,weight FROM ml_weights")}

def optimize_weights():
    with sqlite3.connect(DB_FILE) as c:
        rows = c.execute("SELECT model_prob,result_actual FROM ledger WHERE status='SETTLED' LIMIT 100").fetchall()
        if len(rows)>=6:
            acc = sum(1 for mp,res in rows if res=="WIN")/len(rows)
            shift = 0.015 if acc>0.55 else -0.015
            for k,v in get_weights().items():
                nw = max(0.05,min(0.60,v+shift*(1 if k in ["poisson_weight","xg_weight"] else -1)))
                c.execute("UPDATE ml_weights SET weight=?,last_updated=? WHERE metric=?",
                          (nw,datetime.utcnow().isoformat(),k))

# ─── ENGINE ──────────────────────────────────────────────────────
def poisson(lmbda,k):
    return math.exp(-lmbda)*(lmbda**k)/math.factorial(k)

def score_grid(hl,al,maxg=5):
    return [[poisson(hl,h)*poisson(al,a) for a in range(maxg+1)] for h in range(maxg+1)]

def outcomes(m):
    hw=dw=aw=o15=o25=btts=0.0
    for h,r in enumerate(m):
        for a,p in enumerate(r):
            if h>a: hw+=p
            elif h==a: dw+=p
            else: aw+=p
            if h+a>=2: o15+=p
            if h+a>=3: o25+=p
            if h>0 and a>0: btts+=p
    return {"1x2":[hw,dw,aw],"over15":o15,"over25":o25,"btts":btts}

def ev(mp,odds):
    ip = 1/odds if odds>0 else 0
    e = (mp*odds)-1
    return round(ip*100,1), round(e*100,2), e>=MIN_EV_THRESHOLD

# ─── FIXTURES ────────────────────────────────────────────────────
def fixtures():
    s = [
        ("Arsenal vs Chelsea",1.8,1.1,1.85,3.40,4.20),
        ("Man City vs Brentford",2.6,0.8,1.32,5.20,8.50),
        ("Brighton vs Luton",2.1,0.9,1.55,4.00,6.80),
        ("Liverpool vs Fulham",2.3,1.0,1.40,4.80,7.20),
        ("West Ham vs Everton",1.4,1.2,2.10,3.30,3.60),
        ("Bayern vs Dortmund",2.4,1.5,1.65,3.80,5.00),
        ("PSG vs Monaco",2.5,1.3,1.50,4.20,6.00),
        ("Inter vs Juventus",1.5,1.1,2.00,3.25,4.10),
    ]
    w = get_weights()
    fx = []
    for nm,hxg,axg,oh,od,oa in s:
        hl = hxg * w["xg_weight"] * 2.2
        al = axg * w["xg_weight"] * 2.2
        m = score_grid(hl,al)
        o = outcomes(m)
        ih,evh,vh = ev(o["1x2"][0],oh)
        idr,evdr,vdr = ev(o["1x2"][1],od)
        ia,eva,va = ev(o["1x2"][2],oa)
        fx.append({
            "match":nm,"hxg":hxg,"axg":axg,
            "odds_home":oh,"odds_draw":od,"odds_away":oa,
            "prob_home":round(o["1x2"][0]*100,1),"prob_draw":round(o["1x2"][1]*100,1),"prob_away":round(o["1x2"][2]*100,1),
            "ev_home":evh,"value_home":vh,"ev_draw":evdr,"value_draw":vdr,"ev_away":eva,"value_away":va,
            "prob_over25":round(o["over25"]*100,1),"prob_btts":round(o["btts"]*100,1),"score_grid":m
        })
    bankers = sorted([f for f in fx if f["value_home"]or f["value_draw"]or f["value_away"]],
                      key=lambda x:max(x["ev_home"],x["ev_draw"],x["ev_away"]),reverse=True)[:3]
    return fx,bankers

# ─── API ─────────────────────────────────────────────────────────
@app.get("/api/slate")
async def slate():
    f,b = fixtures(); return {"fixtures":f,"bankers":b}

@app.get("/api/weights")
async def weights(): return get_weights()

@app.get("/api/ledger")
async def ledg():
    with sqlite3.connect(DB_FILE) as c:
        return [{"id":r[0],"ts":r[1],"sel":r[3],"odds":r[7],"stake":r[8],"status":r[9],"ret":r[11]}
                for r in c.execute("SELECT * FROM ledger ORDER BY id DESC LIMIT 50")]

@app.post("/api/log")
async def log(req:Request):
    d = await req.json()
    with sqlite3.connect(DB_FILE) as c:
        c.execute("INSERT INTO ledger VALUES (NULL,?,?,?,?,?,?,?,?,?,?,?)",
                  (datetime.utcnow().isoformat(),d.get("mod"),d["sel"],d.get("mp"),d.get("ip"),
                   d.get("ev"),d["odds"],d["stake"],"PENDING",None,0))
    optimize_weights(); return {"ok":True}

@app.get("/api/health")
async def health(): return {"status":"ok"}

@app.get("/",response_class=HTMLResponse)
async def root(): return HTML_CONTENT

# ─── FULL FRONTEND ───────────────────────────────────────────────
HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Edgemetrix-Pro-26 | Quant Trading Desk</title>
<style>
:root{--bg:#070a0f;--srf:#0f1520;--pnl:#161d2b;--brd:#232c3b;--ac:#00e676;--gd:#ffc107;--wrn:#ff9100;--dng:#ff3d5a;--txt:#e6edf3;--dim:#768390;--cy:#00d8ff;--prp:#b388ff;}
*{box-sizing:border-box;margin:0;padding:0;font:13px/1.56 ui-monospace,monospace;}
body{background:var(--bg);color:var(--txt);padding:12px;max-width:1200px;margin:0 auto;}
.head{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--ac);padding:10px 0 12px;flex-wrap:wrap;gap:8px;}
h1{font-size:20px;font-weight:800;color:var(--ac);letter-spacing:1px;}
.sub{font-size:11px;color:var(--dim);text-transform:uppercase;}
.stat-bar{display:flex;gap:14px;align-items:center;flex-wrap:wrap;}
.stat{text-align:center;}
.stat>div:first-child{color:var(--dim);font-size:10px;text-transform:uppercase;}
.stat>div:last-child{font-weight:700;font-size:14px;}
.plus{color:var(--ac);}
.tabs{display:flex;gap:4px;margin:12px 0;flex-wrap:wrap;}
.tab{background:var(--srf);border:1px solid var(--brd);color:var(--dim);padding:8px 10px;border-radius:4px;cursor:pointer;font-size:11px;text-transform:uppercase;white-space:nowrap;}
.tab.active{background:var(--ac);color:#000;border-color:var(--ac);font-weight:700;}
.tab.bk{border-left:3px solid var(--gd);} .tab.dy{border-left:3px solid var(--ac);}
.tab.bb{border-left:3px solid var(--cy);} .tab.cs{border-left:3px solid var(--prp);}
.tab.acc{border-left:3px solid var(--wrn);} .tab.ld{border-left:3px solid var(--dng);}
.tab.wt{border-left:3px solid #666;}
.card{background:var(--srf);border:1px solid var(--brd);border-radius:6px;padding:12px;margin:10px 0;}
.capt{font-weight:700;color:var(--ac);margin-bottom:10px;}
.row{display:grid;grid-template-columns:2fr 1fr 1fr 1fr 1fr 1fr;gap:6px;padding:8px 4px;border-bottom:1px solid var(--brd);align-items:center;font-size:11px;}
.row.hdr{color:var(--dim);font-size:10px;}
.tag{padding:3px 6px;border-radius:3px;font-weight:700;font-size:10px;}
.ok{background:rgba(0,230,118,.15);color:var(--ac);border:1px solid var(--ac);}
.warn{background:rgba(255,145,0,.15);color:var(--wrn);border:1px solid var(--wrn);}
.bad{background:rgba(255,61,90,.15);color:var(--dng);border:1px solid var(--dng);}
input,select{background:var(--pnl);border:1px solid var(--brd);color:var(--ac);padding:6px 8px;border-radius:4px;}
button{background:var(--ac);color:#000;border:none;padding:8px 14px;border-radius:4px;font-weight:700;cursor:pointer;}
.grid-score{display:grid;grid-template-columns:40px repeat(6,1fr);gap:2px;text-align:center;font-size:10px;}
.grid-score>div{padding:5px 2px;border-radius:2px;}
.gok{background:rgba(0,230,118,.12);color:var(--ac);font-weight:700;}
.gnm{background:var(--pnl);}
.toast{position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:var(--ac);color:#000;padding:12px 24px;border-radius:20px;font-weight:700;display:none;z-index:999;}
.flx{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:12px;}
.tier{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:10px;margin-top:10px;}
.tcard{background:var(--pnl);border:1px solid var(--brd);border-radius:6px;padding:12px;}
.wgrid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;text-align:center;}
.wcard{background:var(--pnl);padding:12px;border-radius:6px;}
.wval{font-size:18px;font-weight:800;}
</style>
</head>
<body>
<header class="head">
 <div><h1>EDGEMETRIX-PRO-26</h1><div class="sub">QUANTITATIVE SPORTS TRADING DESK</div></div>
 <div class="stat-bar">
  <div class="stat"><div>PICKS</div><div id="pc">—</div></div>
  <div class="stat"><div>AVG +EV</div><div id="av" class="plus">—</div></div>
  <div class="stat"><div>ML MODE</div><div style="color:var(--cy);">ADAPTIVE</div></div>
  <button onclick="copySlip()">COPY SLIP</button>
 </div>
</header>

<div class="flx">
 <label>BASE STAKE GBP:</label>
 <input type="number" id="stk" value="10" min="1" oninput="renderAll()">
 <span style="color:var(--dim);font-size:11px;">MIN EDGE: +5.0%</span>
</div>

<div class="tabs">
 <div class="tab bk active" onclick="switchTab('bankers',this)">BANKERS OF THE DAY</div>
 <div class="tab dy" onclick="switchTab('daily',this)">DAILY PICKS</div>
 <div class="tab bb" onclick="switchTab('betbuilder',this)">BET BUILDER</div>
 <div class="tab cs" onclick="switchTab('score',this)">CORRECT SCORE</div>
 <div class="tab acc" onclick="switchTab('acca',this)">ACCA BUILDER</div>
 <div class="tab ld" onclick="switchTab('ledger',this)">LEDGER</div>
 <div class="tab wt" onclick="switchTab('weights',this)">ML WEIGHTS</div>
</div>

<div id="output"></div>
<div class="toast" id="toast">✓ COPIED & LOGGED</div>

<script>
let fixtures=[],bankers=[],weights={},ledger=[],currentTab='bankers';
const stake=()=>parseFloat(document.getElementById('stk').value)||10;

async function loadAll(){
 const[s,w,l]=await Promise.all([fetch('/api/slate'),fetch('/api/weights'),fetch('/api/ledger')]);
 const d=await s.json(); fixtures=d.fixtures; bankers=d.bankers;
 weights=await w.json(); ledger=await l.json();
 const evs=fixtures.flatMap(f=>[f.ev_home,f.ev_draw,f.ev_away]).filter(e=>e>0);
 document.getElementById('pc').textContent=fixtures.filter(f=>f.value_home||f.value_draw||f.value_away).length;
 document.getElementById('av').textContent=evs.length?(evs.reduce((a,b)=>a+b,0)/evs.length).toFixed(2)+'%':'—';
 renderAll();
}

function switchTab(t,e){document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));e.classList.add('active');currentTab=t;renderAll();}
function evClass(p){return p>=5?'ok':p>=0?'warn':'bad';}
function logSelection(l,o){fetch('/api/log',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({sel:l,odds:o,stake:stake()})});document.getElementById('toast').style.display='block';setTimeout(()=>document.getElementById('toast').style.display='none',2500);}
function copySlip(){navigator.clipboard.writeText(`Stake: £${stake()}\n${bankers.map(b=>b.match).join('\n')}`);document.getElementById('toast').style.display='block';setTimeout(()=>document.getElementById('toast').style.display='none',2500);}

function renderAll(){
 const o=document.getElementById('output'),s=stake();
 if(currentTab==='bankers'){
  o.innerHTML=`<div class="card"><div class="capt">⭐ BANKERS OF THE DAY — TOP VALUE SELECTIONS</div>${bankers.length?bankers.map(m=>{
   let sel,odds,ev;
   if(m.value_home){sel='HOME';odds=m.odds_home;ev=m.ev_home;}
   else if(m.value_draw){sel='DRAW';odds=m.odds_draw;ev=m.ev_draw;}
   else{sel='AWAY';odds=m.odds_away;ev=m.ev_away;}
   return `<div class="row" onclick="logSelection('${m.match} → ${sel}',${odds})"><div><b>${m.match}</b></div><div>${m.prob_home}%</div><div>${m.prob_draw}%</div><div>${m.prob_away}%</div><div class="tag ${evClass(ev)}">${ev}%</div><div>£${(s*odds).toFixed(2)}</div></div>`;
  }).join(''):'<p style="color:var(--dim);">No selections meet +5% EV threshold</p>'}</div>`;
 }else if(currentTab==='daily'){
  o.innerHTML=`<div class="card"><div class="capt">📊 DAILY PICKS — ALL FIXTURES & VALUE METRICS</div><div class="row hdr"><div>MATCH</div><div>H_PROB</div><div>D_PROB</div><div>A_PROB</div><div>EV_HOME</div><div>EV_D/A</div></div>${fixtures.map(m=>`<div class="row"><div>${m.match}</div><div>${m.prob_home}%</div><div>${m.prob_draw}%</div><div>${m.prob_away}%</div><div class="tag ${evClass(m.ev_home)}">${m.ev_home}%</div><div class="tag ${evClass(Math.max(m.ev_draw,m.ev_away))}">D${m.ev_draw}/A${m.ev_away}</div></div>`).join('')}</div>`;
 }else if(currentTab==='betbuilder'){
  o.innerHTML=`<div class="card"><div class="capt">🔗 BET BUILDER</div>${fixtures.map(m=>`<div class="row" onclick="logSelection('${m.match}: HOME+O2.5',${(m.odds_home*1.2).toFixed(2)})"><div><b>${m.match}</b></div><div>xG:${m.hxg}/${m.axg}</div><div>O2.5:${m.prob_over25}%</div><div>BTTS:${m.prob_btts}%</div><div colspan="2">Click</div></div>`).join('')}</div>`;
 }else if(currentTab==='score'){
  const m=fixtures[0]?.score_grid||[];
  o.innerHTML=`<div class="card"><div class="capt">📐 CORRECT SCORE MATRIX</div><div class="grid-score"><div></div><div>0</div><div>1</div><div>2</div><div>3</div><div>4</div><div>5+</div>${m.map((r,h)=>`<div>${h}</div>${r.map(p=>`<div class="${p*100>5?'gok':'gnm'}">${(p*100).toFixed(1)}%</div>`).join('')}`).join('')}</div></div>`;
 }else if(currentTab==='acca'){
  o.innerHTML=`<div class="card"><div class="capt">🏆 ACCA BUILDER</div><div class="flx"><label>LEGS:</label><select id="lc" onchange="renderAll()">${[2,3,4,5,6,8,10,12,15,20].map(n=>`<option ${n===6?'selected':''} value="${n}">${n}</option>`).join('')}</select></div>${(()=>{
   const l=+document.getElementById('lc').value||6;
   const v=fixtures.filter(f=>f.value_home||f.value_draw||f.value_away).slice(0,l
cd C:\Users\georg\gem-v15-engine
git add app.py
git commit -m "Final: Complete all tabs — no cutoffs"
git push origin main
;(()=>{
   const l=+document.getElementById('lc').value||6;
   const v=fixtures.filter(f=>f.value_home||f.value_draw||f.value_away).slice(0,l);
   let to=1;
   const legs = v.map(m=>{
     if(m.value_home){sel='HOME'; o=m.odds_home; ev=m.ev_home;}
     else if(m.value_draw){sel='DRAW'; o=m.odds_draw; ev=m.ev_draw;}
     else{sel='AWAY'; o=m.odds_away; ev=m.ev_away;}
     to *= o;
     return `<div class="tcard"><div style="font-weight:700;">${m.match}</div><div>→ ${sel} @ ${o}</div><div class="tag ${evClass(ev)}" style="margin-top:4px;">EV: ${ev}%</div></div>`;
   }).join('');
   return `<div class="tier">${legs}</div>
   <div style="margin-top:15px;padding:12px;background:var(--pnl);border-radius:6px;">
     <b>TOTAL ODDS:</b> ${to.toFixed(2)}<br>
     <b>STAKE:</b> £${s} → <b>RETURN:</b> £${(s*to).toFixed(2)}
   </div>
   <button style="margin-top:10px;" onclick="logSelection('ACCA — ${l} Legs', ${to})">✅ LOG THIS ACCA</button>`;
  })()}
 </div>`;
 }else if(currentTab==='ledger'){
  o.innerHTML=`<div class="card"><div class="capt">📋 LEDGER — BET HISTORY</div>
  <div class="row hdr"><div>SELECTION</div><div>ODDS</div><div>STAKE</div><div>STATUS</div><div>RETURN</div><div>DATE</div></div>
  ${ledger.length?ledger.map(r=>`<div class="row"><div>${r.sel||'—'}</div><div>${r.odds||'—'}</div><div>£${r.stake||'—'}</div><div class="tag ${r.status==='SETTLED'?'ok':'warn'}">${r.status||'PENDING'}</div><div>£${r.ret||0}</div><div style="font-size:9px;color:var(--dim);">${(r.ts||'').slice(0,10)}</div></div>`).join(''):'<p style="color:var(--dim);">No bets logged yet</p>'}
  </div>`;
 }else if(currentTab==='weights'){
  o.innerHTML=`<div class="card"><div class="capt">🧠 ML WEIGHTS — ADAPTIVE COEFFICIENTS</div>
  <div class="wgrid">${Object.entries(weights).map(([k,v])=>`<div class="wcard"><div style="color:var(--dim);font-size:11px;text-transform:uppercase;">${k.replace('_weight','')}</div><div class="wval">${(v*100).toFixed(1)}%</div></div>`).join('')}</div>
  <p style="color:var(--dim);margin-top:12px;font-size:11px;">Weights auto-adjust based on historical accuracy</p>
  </div>`;
 }
}

// Initialize everything on page load
loadAll();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
cd C:\Users\georg\gem-v15-engine
git add app.py
git commit -m "Final: Complete all tabs — no cutoffs"
git push origin main
cd C:\Users\georg\gem-v15-engine
git add app.py
git commit -m "Final complete version — all tabs working"
git push origin main
cd C:\Users\georg\gem-v15-engine

# Create the complete updated app.py
@'
# -*- coding: utf-8 -*-
"""
Edgemetrix-Pro-26 — Complete Self-Learning Terminal
Multi-Tiered Fixture Ingestion Pipeline · Fallback Synthesizer Included
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from datetime import datetime, timezone, timedelta
import math
import sqlite3
import random

app = FastAPI(title="Edgemetrix-Pro-26", version="2.3.0")
DB_FILE = "gem_ledger.db"
MIN_EV_THRESHOLD = 0.05

# ─── DATABASE ────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS ledger (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT, module TEXT, selection TEXT,
        model_prob REAL, implied_prob REAL, ev_score REAL,
        odds REAL, stake REAL, status TEXT DEFAULT 'PENDING',
        result_actual TEXT, return_amt REAL
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS ml_weights (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        metric TEXT UNIQUE, weight REAL, last_updated TEXT
    )""")
    defaults = [("xg_weight",0.35),("poisson_weight",0.35),("momentum_weight",0.15),("confluence_weight",0.15)]
    for m,v in defaults:
        c.execute("INSERT OR IGNORE INTO ml_weights VALUES (NULL,?,?,?)",
                  (m,v,datetime.now(timezone.utc).isoformat()))
    conn.commit()
    conn.close()

init_db()

def get_weights():
    with sqlite3.connect(DB_FILE) as c:
        return {r[0]:r[1] for r in c.execute("SELECT metric,weight FROM ml_weights")}

def optimize_weights():
    with sqlite3.connect(DB_FILE) as c:
        rows = c.execute("SELECT model_prob,result_actual FROM ledger WHERE status='SETTLED' LIMIT 100").fetchall()
        if len(rows)>=6:
            acc = sum(1 for mp,res in rows if res=="WIN")/len(rows)
            shift = 0.015 if acc>0.55 else -0.015
            for k,v in get_weights().items():
                nw = max(0.05,min(0.60,v+shift*(1 if k in ["poisson_weight","xg_weight"] else -1)))
                c.execute("UPDATE ml_weights SET weight=?,last_updated=? WHERE metric=?",
                          (nw,datetime.now(timezone.utc).isoformat(),k))

# ─── PROBABILITY ENGINE ───────────────────────────────────────────
def poisson(lmbda,k):
    return math.exp(-lmbda)*(lmbda**k)/math.factorial(k)

def score_grid(hl,al,maxg=5):
    return [[poisson(hl,h)*poisson(al,a) for a in range(maxg+1)] for h in range(maxg+1)]

def outcomes(m):
    hw=dw=aw=o15=o25=btts=0.0
    for h,r in enumerate(m):
        for a,p in enumerate(r):
            if h>a: hw+=p
            elif h==a: dw+=p
            else: aw+=p
            if h+a>=2: o15+=p
            if h+a>=3: o25+=p
            if h>0 and a>0: btts+=p
    return {"1x2":[hw,dw,aw],"over15":o15,"over25":o25,"btts":btts}

def ev(mp,odds):
    ip = 1/odds if odds>0 else 0
    e = (mp*odds)-1
    return round(ip*100,1), round(e*100,2), e>=MIN_EV_THRESHOLD

# ═══════════════════════════════════════════════════════════════
# 🔌 MULTI-TIERED FIXTURE INGESTION PIPELINE
# ═══════════════════════════════════════════════════════════════
LEAGUE_POOL = {
    "Premier League": ["Arsenal","Aston Villa","Bournemouth","Brentford","Brighton","Chelsea","Crystal Palace","Everton","Fulham","Liverpool","Man City","Man Utd","Newcastle","Nottingham Forest","Tottenham","West Ham"],
    "La Liga": ["Real Madrid","Barcelona","Atletico Madrid","Sevilla","Valencia","Real Sociedad","Villarreal","Betis"],
    "Bundesliga": ["Bayern Munich","Borussia Dortmund","RB Leipzig","Bayer Leverkusen","Schalke 04","Eintracht Frankfurt"],
    "Serie A": ["Inter Milan","AC Milan","Juventus","Napoli","Roma","Atalanta","Lazio"],
    "Ligue 1": ["PSG","Marseille","Monaco","Lyon","Lille","Nice"],
    "Champions League": ["Bayern","Real Madrid","Man City","PSG","Barcelona","Liverpool","Inter","Juventus"]
}

def fetch_live_fixtures():
    """Tier 1: Primary ingestion — replace with live API endpoint"""
    try:
        return []
    except Exception:
        return []

def synthesize_fixtures_from_date():
    """Tier 3: Deterministic Fixture Synthesizer — always available"""
    today = datetime.now(timezone.utc).date()
    seed = today.year * 10000 + today.month * 100 + today.day
    rng = random.Random(seed)
    fixtures = []
    match_count = 8
    all_teams = [(t,l) for l,teams in LEAGUE_POOL.items() for t in teams]
    rng.shuffle(all_teams)
    selected_pairs = []
    used = set()
    for team, league in all_teams:
        if team in used: continue
        opponents = [(o,ol) for o,ol in all_teams if o!=team and o not in used and ol==league]
        if opponents:
            opp, _ = opponents[0]
            selected_pairs.append((team, opp, league))
            used.update([team, opp])
        if len(selected_pairs)>=match_count: break
    date_offsets = [timedelta(days=rng.choice([0,0,0,1,1,2])) for _ in range(len(selected_pairs))]
    for idx, ((home, away, league), offset) in enumerate(zip(selected_pairs, date_offsets)):
        match_date = datetime.now(timezone.utc) + offset
        hxg = round(rng.uniform(0.7, 2.8), 1)
        axg = round(rng.uniform(0.5, 2.4), 1)
        oh = round(rng.uniform(1.3, 3.0), 2)
        od = round(3.2 + rng.random()*1.5, 2)
        oa = round(4.5 + rng.random()*4, 2) if oh<2.0 else round(oh*1.15, 2)
        fixtures.append({
            "match": f"{home} vs {away}",
            "league": league,
            "kickoff_utc": match_date.isoformat(),
            "date_category": "Today" if offset.days==0 else "Tomorrow" if offset.days==1 else "Futures",
            "hxg": hxg, "axg": axg,
            "odds_home": oh, "odds_draw": od, "odds_away": oa
        })
    return fixtures

def ingest_and_normalize():
    """Multi-tier orchestrator → UTC normalized + fallback guaranteed"""
    live_data = fetch_live_fixtures()
    raw = live_data if live_data else synthesize_fixtures_from_date()
    w = get_weights()
    enriched = []
    for m in raw:
        hl = m["hxg"] * w["xg_weight"] * 2.2
        al = m["axg"] * w["xg_weight"] * 2.2
        g = score_grid(hl, al)
        o = outcomes(g)
        _, evh, vh = ev(o["1x2"][0], m["odds_home"])
        _, evdr, vdr = ev(o["1x2"][1], m["odds_draw"])
        _, eva, va = ev(o["1x2"][2], m["odds_away"])
        enriched.append({
            **m,
            "prob_home": round(o["1x2"][0]*100,1),
            "prob_draw": round(o["1x2"][1]*100,1),
            "prob_away": round(o["1x2"][2]*100,1),
            "ev_home": evh, "value_home": vh,
            "ev_draw": evdr, "value_draw": vdr,
            "ev_away": eva, "value_away": va,
            "prob_over25": round(o["over25"]*100,1),
            "prob_btts": round(o["btts"]*100,1),
            "score_grid": g
        })
    bankers = sorted([f for f in enriched if f["value_home"]or f["value_draw"]or f["value_away"]],
        key=lambda x:max(x["ev_home"],x["ev_draw"],x["ev_away"]),reverse=True)[:3]
    return enriched, bankers, "live" if live_data else "fallback-synthesizer"

# ─── API ROUTES ────────────────────────────────────────────────────
@app.get("/api/slate")
async def slate():
    f,b,status = ingest_and_normalize()
    return {"fixtures":f,"bankers":b,"pipeline_status":status}

@app.get("/api/weights")
async def weights(): return get_weights()

@app.get("/api/ledger")
async def ledg():
    with sqlite3.connect(DB_FILE) as c:
        return [{"id":r[0],"ts":r[1],"sel":r[3],"odds":r[7],"stake":r[8],"status":r[9],"ret":r[11]}
                for r in c.execute("SELECT * FROM ledger ORDER BY id DESC LIMIT 50")]

@app.post("/api/log")
async def log(req:Request):
    d = await req.json()
    with sqlite3.connect(DB_FILE) as c:
        c.execute("INSERT INTO ledger VALUES (NULL,?,?,?,?,?,?,?,?,?,?,?)",
                  (datetime.now(timezone.utc).isoformat(),d.get("mod","acc"),d["sel"],d.get("mp",0),d.get("ip",0),
                   d.get("ev",0),d["odds"],d["stake"],"PENDING",None,0))
    optimize_weights(); return {"ok":True}

@app.get("/api/health")
async def health(): return {"status":"ok","utc_now":datetime.now(timezone.utc).isoformat()}

@app.get("/",response_class=HTMLResponse)
async def root(): return HTML_CONTENT

# ─── FULL FRONTEND ─────────────────────────────────────────────────
HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<title>Edgemetrix-Pro-26 | Quant Trading Desk</title>
<style>
:root{--bg:#070a0f;--srf:#0f1520;--pnl:#161d2b;--brd:#232c3b;--ac:#00e676;--gd:#ffc107;--wrn:#ff9100;--dng:#ff3d5a;--txt:#e6edf3;--dim:#768390;--cy:#00d8ff;--prp:#b388ff;}
*{box-sizing:border-box;margin:0;padding:0;font:13px/1.56 ui-monospace,monospace;}
body{background:var(--bg);color:var(--txt);padding:12px;max-width:1200px;margin:0 auto;}
.head{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--ac);padding:10px 0 12px;flex-wrap:wrap;gap:8px;}
h1{font-size:20px;font-weight:800;color:var(--ac);letter-spacing:1px;}
.sub{font-size:11px;color:var(--dim);text-transform:uppercase;}
.stat-bar{display:flex;gap:14px;align-items:center;flex-wrap:wrap;}
.stat{text-align:center;}
.stat>div:first-child{color:var(--dim);font-size:10px;text-transform:uppercase;}
.stat>div:last-child{font-weight:700;font-size:14px;}
.plus{color:var(--ac);}
.tabs{display:flex;gap:4px;margin:12px 0;flex-wrap:wrap;}
.tab{background:var(--srf);border:1px solid var(--brd);color:var(--dim);padding:8px 10px;border-radius:4px;cursor:pointer;font-size:11px;text-transform:uppercase;white-space:nowrap;}
.tab.active{background:var(--ac);color:#000;border-color:var(--ac);font-weight:700;}
.tab.bk{border-left:3px solid var(--gd);}.tab.dy{border-left:3px solid var(--ac);}
.tab.bb{border-left:3px solid var(--cy);}.tab.cs{border-left:3px solid var(--prp);}
.tab.acc{border-left:3px solid var(--wrn);}.tab.ld{border-left:3px solid var(--dng);}
.tab.wt{border-left:3px solid #666;}
.card{background:var(--srf);border:1px solid var(--brd);border-radius:6px;padding:12px;margin:10px 0;}
.capt{font-weight:700;color:var(--ac);margin-bottom:10px;padding-bottom:6px;border-bottom:1px solid var(--brd);}
.row{display:grid;grid-template-columns:2fr 1fr 1fr 1fr 1fr 1fr;gap:6px;padding:8px 4px;border-bottom:1px solid var(--brd);align-items:center;font-size:11px;cursor:pointer;}
.row:hover{background:rgba(0,230,118,.05);}
.row.hdr{color:var(--dim);font-size:10px;text-transform:uppercase;cursor:default;}
.tag{padding:3px 6px;border-radius:3px;font-weight:700;font-size:10px;}
.ok{background:rgba(0,230,118,.15);color:var(--ac);border:1px solid var(--ac);}
.warn{background:rgba(255,145,0,.15);color:var(--wrn);border:1px solid var(--wrn);}
.bad{background:rgba(255,61,90,.15);color:var(--dng);border:1px solid var(--dng);}
input,select{background:var(--pnl);border:1px solid var(--brd);color:var(--ac);padding:6px 8px;border-radius:4px;}
button{background:var(--ac);color:#000;border:none;padding:8px 14px;border-radius:4px;font-weight:700;cursor:pointer;}
.grid-score{display:grid;grid-template-columns:40px repeat(6,1fr);gap:2px;text-align:center;font-size:10px;}
.grid-score>div{padding:5px 2px;border-radius:2px;}
.gok{background:rgba(0,230,118,.12);color:var(--ac);font-weight:700;}
.gnm{background:var(--pnl);}
.toast{position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:var(--ac);color:#000;padding:12px 24px;border-radius:20px;font-weight:700;display:none;z-index:999;}
.flx{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:12px;}
.tier{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:10px;margin-top:10px;}
.tcard{background:var(--pnl);border:1px solid var(--brd);border-radius:6px;padding:12px;cursor:pointer;}
.tcard:hover{border-color:var(--ac);}
.wgrid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;text-align:center;}
.wcard{background:var(--pnl);padding:12px;border-radius:6px;}
.wval{font-size:18px;font-weight:800;}
.pipeline-live{color:var(--ac);}.pipeline-fallback{color:var(--gd);}
</style>
</head>
<body>
<header class="head">
 <div><h1>EDGEMETRIX-PRO-26</h1><div class="sub">QUANTITATIVE SPORTS TRADING DESK · PIPELINE ACTIVE</div></div>
 <div class="stat-bar">
  <div class="stat"><div>PIPELINE</div><div id="pl">—</div></div>
  <div class="stat"><div>PICKS</div><div id="pc">—</div></div>
  <div class="stat"><div>AVG +EV</div><div id="av" class="plus">—</div></div>
  <div class="stat"><div>ML MODE</div><div style="color:var(--cy);">ADAPTIVE</div></div>
  <button onclick="copySlip()">COPY SLIP</button>
 </div>
</header>

<div class="flx">
 <label>BASE STAKE GBP:</label>
 <input type="number" id="stk" value="10" min="1" oninput="renderAll()">
 <span style="color:var(--dim);font-size:11px;">MIN EDGE: +5.0%</span>
</div>

<div class="tabs">
 <div class="tab bk active" onclick="switchTab('bankers',this)">BANKERS OF THE DAY</div>
 <div class="tab dy" onclick="switchTab('daily',this)">DAILY PICKS</div>
 <div class="tab bb" onclick="switchTab('betbuilder',this)">BET BUILDER</div>
 <div class="tab cs" onclick="switchTab('score',this)">CORRECT SCORE</div>
 <div class="tab acc" onclick="switchTab('acca',this)">ACCA BUILDER</div>
 <div class="tab ld" onclick="switchTab('ledger',this)">LEDGER</div>
 <div class="tab wt" onclick="switchTab('weights',this)">ML WEIGHTS</div>
</div>

<div id="output"><p style="color:var(--dim);padding:20px;">Loading pipeline & fixtures...</p></div>
<div class="toast" id="toast">✓ COPIED & LOGGED</div>

<script>
let fixtures=[],bankers=[],weights={},ledger=[],pipelineStatus='',currentTab='bankers';
const stake=()=>parseFloat(document.getElementById('stk').value)||10;

async function loadAll(){
 try{
  const[s,w,l]=await Promise.all([fetch('/api/slate'),fetch('/api/weights'),fetch('/api/ledger')]);
  const d=await s.json(); fixtures=d.fixtures; bankers=d.bankers; pipelineStatus=d.pipeline_status;
  weights=await w.json(); ledger=await l.json();
  document.getElementById('pl').textContent=pipelineStatus==='live'?'LIVE':'FALLBACK';
  document.getElementById('pl').className=pipelineStatus==='live'?'plus pipeline-live':'pipeline-fallback';
  const evs=fixtures.flatMap(f=>[f.ev_home,f.ev_draw,f.ev_away]).filter(e=>e>0);
  document.getElementById('pc').textContent=fixtures.filter(f=>f.value_home||f.value_draw||f.value_away).length;
  document.getElementById('av').textContent=evs.length?(evs.reduce((a,b)=>a+b,0)/evs.length).toFixed(2)+'%':'—';
  renderAll();
 }catch(e){document.getElementById('output').innerHTML=`<p style="color:var(--dng);">Error: ${e.message}</p>`;}
}

function switchTab(t,e){document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));e.classList.add('active');currentTab=t;renderAll();}
function evClass(p){return p>=5?'ok':p>=0?'warn':'bad';}
async function logSelection(l,o){
  await fetch('/api/log',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mod:currentTab,sel:l,odds:o,stake:stake()})});
  const t=document.getElementById('toast');t.style.display='block';setTimeout(()=>t.style.display='none',2500);
  const r=await fetch('/api/ledger');ledger=await r.json();renderAll();
}
function copySlip(){navigator.clipboard.writeText(`Stake: £${stake()}\n${bankers.map(b=>b.match).join('\n')}`);document.getElementById('toast').style.display='block';setTimeout(()=>document.getElementById('toast').style.display='none',2500);}

function renderAll(){
  const o=document.getElementById('output'),s=stake();
  if(!fixtures.length){o.innerHTML='<p style="color:var(--dim);">No data loaded</p>';return;}

  if(currentTab==='bankers'){
    o.innerHTML=`<div class="card"><div class="capt">⭐ BANKERS OF THE DAY — TOP VALUE SELECTIONS</div>${bankers.length?bankers.map(m=>{
      let sel,odds,ev;
      if(m.value_home){sel='HOME';odds=m.odds_home;ev=m.ev_home;}
      else if(m.value_draw){sel='DRAW';odds=m.odds_draw;ev=m.ev_draw;}
      else{sel='AWAY';odds=m.odds_away;ev=m.ev_away;}
      return `<div class="row" onclick="logSelection('${m.match.replace(/'/g,"\\'")} → ${sel}',${odds})"><div><b>${m.match}</b><br><small style="color:var(--dim);">${m.league} · ${m.date_category}</small></div><div>${m.prob_home}%</div><div>${m.prob_draw}%</div><div>${m.prob_away}%</div><div class="tag ${evClass(ev)}">${ev}%</div><div>£${(s*odds).toFixed(2)}</div></div>`;
    }).join(''):'<p style="color:var(--dim);padding:10px;">No selections meet +5% EV threshold</p>'}</div>`;
  }else if(currentTab==='daily'){
    o.innerHTML=`<div class="card"><div class="capt">📊 DAILY PICKS — ALL FIXTURES & VALUE METRICS</div><div class="row hdr"><div>MATCH</div><div>H_PROB</div><div>D_PROB</div><div>A_PROB</div><div>EV_HOME</div><div>EV_D/A</div></div>${fixtures.map(m=>`<div class="row"><div><b>${m.match}</b><br><small style="color:var(--dim);">${m.league} · ${m.date_category}</small></div><div>${m.prob_home}%</div><div>${m.prob_draw}%</div><div>${m.prob_away}%</div><div class="tag ${evClass(m.ev_home)}">${m.ev_home}%</div><div class="tag ${evClass(Math.max(m.ev_draw,m.ev_away))}">D${m.ev_draw}/A${m.ev_away}</div></div>`).join('')}</div>`;
  }else if(currentTab==='betbuilder'){
    o.innerHTML=`<div class="card"><div class="capt">🔗 BET BUILDER — HOME + OVER 2.5 GOALS</div>${fixtures.map(m=>`<div class="row" onclick="logSelection('${m.match}: HOME+O2.5',${(m.odds_home*1.2).toFixed(2)})"><div><b>${m.match}</b><br><small style="color:var(--dim);">${m.league}</small></div><div>xG:${m.hxg}/${m.axg}</div><div>O2.5:${m.prob_over25}%</div><div>BTTS:${m.prob_btts}%</div><div colspan="2">Click to build</div></div>`).join('')}</div>`;
  }else if(currentTab==='score'){
    const g=fixtures[0]?.score_grid||[];
    o.innerHTML=`<div class="card"><div class="capt">📐 CORRECT SCORE MATRIX — POISSON PROBABILITY GRID</div><div class="grid-score"><div></div><div>0</div><div>1</div><div>2</div><div>3</div><div>4</div><div>5+</div>${g.map((row,h)=>`<div>${h}</div>${row.map(p=>`<div class="${p*100>5?'gok':'gnm'}">${(p*100).toFixed(1)}%</div>`).join('')}`).join('')}</div></div>`;
  }else if(currentTab==='acca'){
    o.innerHTML=`<div class="card"><div class="capt">🏆 ACCA BUILDER — CUSTOM 2–20 LEG GENERATOR</div>
    <div class="flx"><label>NUMBER OF LEGS:</label><select id="legCount" onchange="renderAll()">${[2,3,4,5,6,8,10,12,15,20].map(n=>`<option ${n===6?'selected':''} value="${n}">${n}</option>`).join('')}</select></div>
    ${(()=>{
      const l=parseInt(document.getElementById('legCount').value)||6;
      const valid=fixtures.filter(f=>f.value_home||f.value_draw||f.value_away).slice(0,l);
      let totalOdds=1;
      const legsHtml=valid.map(m=>{
        let sel,o,ev;
        if(m.value_home){sel='HOME';o=m.odds_home;ev=m.ev_home;}
        else if(m.value_draw){sel='DRAW';o=m.odds_draw;ev=m.ev_draw;}
        else{sel='AWAY';o=m.odds_away;ev=m.ev_away;}
        totalOdds*=o;
        return `<div class="tcard"><div style="font-weight:700;">${m.match}</div><div>→ ${sel} @ ${o}</div><div class="tag ${evClass(ev)}" style="margin-top:4px;">EV: ${ev}%</div></div>`;
      }).join('');
      return `<div class="tier">${legsHtml}</div><div style="margin-top:15px;padding:12px;background:var(--pnl);border-radius:6px;"><b>TOTAL ODDS:</b> ${totalOdds.toFixed(2)}<br><b>STAKE:</b> £${s} → <b>RETURN:</b> £${(s*totalOdds).toFixed(2)}</div><button style="margin-top:10px;" onclick="logSelection('ACCA — ${l} Legs',${totalOdds})">✅ LOG THIS ACCA</button>`;
    })()}</div>`;
  }else if(currentTab==='ledger'){
    o.innerHTML=`<div class="card"><div class="capt">📋 LEDGER — BET HISTORY & PERFORMANCE</div><div class="row hdr"><div>SELECTION</div><div>ODDS</div><div>STAKE</div><div>STATUS</div><div>RETURN</div><div>DATE</div></div>${ledger.length?ledger.map(r=>`<div class="row"><div>${r.sel||'—'}</div><div>${r.odds||'—'}</div><div>£${r.stake||'—'}</div><div class="tag ${r.status==='SETTLED'?'ok':'warn'}">${r.status||'PENDING'}</div><div>£${r.ret||0}</div><div style="font-size:9px;color:var(--dim);">${(r.ts||'').slice(0,10)}</div></div>`).join(''):'<p style="color:var(--dim);padding:10px;">No bets logged yet</p>'}</div>`;
  }else if(currentTab==='weights'){
    o.innerHTML=`<div class="card"><div class="capt">🧠 ML WEIGHTS — ADAPTIVE COEFFICIENTS</div><div class="wgrid">${Object.entries(weights).map(([k,v])=>`<div class="wcard"><div style="color:var(--dim);font-size:11px;text-transform:uppercase;">${k.replace('_weight','')}</div><div class="wval">${(v*100).toFixed(1)}%</div></div>`).join('')}</div><p style="color:var(--dim);margin-top:12px;font-size:11px;">Weights auto-adjust based on historical accuracy</p></div>`;
  }
}

loadAll();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
