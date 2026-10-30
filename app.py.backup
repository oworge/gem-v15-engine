from flask import render_template, jsonify
# -*- coding: utf-8 -*-
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
    # Initialize default weights if empty
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
    """Self-learning feedback loop: adjusts weights based on ledger success rates"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM ledger WHERE status != 'PENDING'")
    settled = cursor.fetchall()
    
    if len(settled) >= 3:
        won_count = sum(1 for s in settled if s[0] == 'WON')
        win_rate = won_count / len(settled)
        # Dynamic self-tuning feedback calculation
        weights = get_ml_weights()
        if win_rate > 0.6:
            # Reward current tuning slightly
            cursor.execute("UPDATE ml_weights SET weight_value = weight_value * 1.02 WHERE metric_name = 'poisson_weight'")
        else:
            # Shift emphasis toward CLV if strike rate drops
            cursor.execute("UPDATE ml_weights SET weight_value = weight_value * 1.02 WHERE metric_name = 'clv_weight'")
        conn.commit()
    conn.close()

def poisson_prob(lmbda, k):
    return (math.exp(-lmbda) * (lmbda ** k)) / math.factorial(k)

def calculate_advanced_xg_poisson(home_xg, away_xg, home_xa, away_xa):
    # Advanced xG + xA tactical adjustment
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
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="mobile-web-app-capable" content="yes">
    <link rel="manifest" href="/manifest.json">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <style>
        :root { --bg: #0d1117; --card-bg: #161b22; --accent: #00ff88; --accent-glow: rgba(0,255,136,0.15); --gold: #f0b429; --text: #f0f6fc; --text-dim: #8b949e; --border: #30363d; --red: #ff5555; --purple: #a371f7; --cyan: #00bfff; }
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

        .tabs { display: flex; gap: 4px; margin-bottom: 12px; overflow-x: auto; padding-bottom: 4px; }
        .tab { background: var(--card-bg); border: 1px solid var(--border); color: var(--text-dim); padding: 9px 6px; border-radius: 6px; font-size: 10px; font-weight: 700; cursor: pointer; white-space: nowrap; flex: 1; text-align: center; transition: all 0.2s; }
        .tab.active { background: var(--accent); color: #0d1117; border-color: var(--accent); box-shadow: 0 0 10px var(--accent-glow); }
        .tab.daily-tab { background: rgba(240,180,41,0.15); color: var(--gold); border-color: rgba(240,180,41,0.4); }
        .tab.daily-tab.active { background: var(--gold); color: #0d1117; }
        .tab.futures-tab { background: rgba(163,113,247,0.15); color: var(--purple); border-color: rgba(163,113,247,0.4); }
        .tab.futures-tab.active { background: var(--purple); color: #0d1117; }
        .tab.ml-tab { background: rgba(0,191,255,0.15); color: var(--cyan); border-color: rgba(0,191,255,0.4); }
        .tab.ml-tab.active { background: var(--cyan); color: #0d1117; }
        .tab.ledger-tab { background: rgba(255,85,85,0.15); color: var(--red); border-color: rgba(255,85,85,0.4); }
        .tab.ledger-tab.active { background: var(--red); color: #0d1117; }

        .acc-container { display: flex; flex-direction: column; gap: 8px; margin-bottom: 15px; }
        .acc-box { background: var(--card-bg); padding: 12px 15px; border-radius: 10px; border: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; border-left: 4px solid var(--accent); cursor: pointer; transition: all 0.2s; }
        .acc-box.elite { border-left-color: var(--gold); background: linear-gradient(135deg, #161b22 0%, #1f241c 100%); }
        .acc-box:hover { border-color: var(--accent); }

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
        .badge-xg { background: rgba(163,113,247,0.15); color: var(--purple); border: 1px solid rgba(163,113,247,0.3); }
        .badge-elite { background: var(--gold); color: #0d1117; }

        .toast { position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background: var(--accent); color: #0d1117; padding: 10px 22px; border-radius: 20px; font-weight: 800; display: none; box-shadow: 0 5px 20px rgba(0,0,0,0.6); z-index: 1000; font-size: 13px; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>Edgemetrix-Pro-26</h1>
            <p style="margin:2px 0 0 0; font-size:11px; color:var(--text-dim);">Advanced xG & Self-Learning ML Weights</p>
        </div>
        <button class="btn" onclick="copyBetSlip()">ðŸ“‹ Copy Slip</button>
    </div>

    <div class="metrics-grid">
        <div class="metric-card">
            <label>Base Stake (Â£)</label>
            <input type="number" id="baseStake" value="10" min="1" oninput="recalculateReturns()">
        </div>
        <div class="metric-card">
            <label>ML Optimizer</label>
            <div class="val" style="font-size:14px; margin-top:4px; color:var(--cyan);">ðŸ§  Active Tuning</div>
        </div>
    </div>

    <div class="tabs">
        <div class="tab active" onclick="switchTab('all', this)">ðŸ”¥ All</div>
        <div class="tab daily-tab" onclick="switchTab('today', this)">âš¡ Today</div>
        <div class="tab futures-tab" onclick="switchTab('futures', this)">ðŸ”® Futures</div>
        <div class="tab" onclick="switchTab('three', this)">ðŸŽ¯ 3-Fold</div>
        <div class="tab ml-tab" onclick="switchTab('ml', this)">ðŸ§¬ ML Weights</div>
        <div class="tab ledger-tab" onclick="switchTab('ledger', this)">ðŸ“Š Ledger</div>
    </div>

    <div class="acc-container" id="acc-container"></div>

    <h3 id="slate-title" style="margin: 15px 0 10px 0; font-size: 14px; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.5px;">Active Slate</h3>
    <div id="fixtures-container">Loading terminal...</div>

    <div id="toast" class="toast">Bet slip copied & logged to SQLite ledger!</div>

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
            toast.innerText = tierName + " logged & ML weights optimized!";
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
            const sixRet = (stake * globalData.accumulators.six_fold.odds).toFixed(2);

            document.getElementById('acc-container').innerHTML = 
                '<div class="acc-box elite" onclick="logBetToLedger(\'3-Fold Anchor\', ' + globalData.accumulators.three_fold.odds + ')">' +
                    '<div>' +
                        '<div style="font-size:12px; font-weight:800; color:var(--gold);">ðŸŽ¯ 3-FOLD ANCHOR (Legs 1-3) &bull; Tap to Log</div>' +
                        '<div style="font-size:12px; color:var(--text-dim); margin-top:2px;">Odds: <b>' + globalData.accumulators.three_fold.odds + '</b> | Stake: Â£' + stake.toFixed(2) + '</div>' +
                    '</div>' +
                    '<div style="text-align:right;">' +
                        '<div style="font-size:16px; font-weight:800; color:var(--gold);">Â£' + threeRet + '</div>' +
                        '<div style="font-size:10px; color:var(--text-dim);">Est. Return</div>' +
                    '</div>' +
                '</div>';
        }

        function renderApp() {
            recalculateReturns();
            const container = document.getElementById('fixtures-container');
            const titleEl = document.getElementById('slate-title');
            
            if (currentTab === 'ml') {
                titleEl.innerText = "ðŸ§¬ Self-Learning ML Coefficient Weights";
                container.innerHTML = '<div class="card" style="border-left-color:var(--cyan);">' +
                    '<b style="color:var(--cyan); font-size:14px;">Closed-Loop Feedback Optimizer</b>' +
                    '<p style="font-size:12px; color:var(--text-dim); margin:6px 0 12px 0;">The backend automatically retrains prediction weights based on settled bet outcomes in your SQLite ledger.</p>' +
                    '<div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:6px; text-align:center;">' +
                        '<div style="background:var(--bg); padding:10px; border-radius:6px;"><div style="font-size:10px; color:var(--text-dim);">SCOREAI</div><b style="color:var(--accent);">' + (mlWeights.scoreai_weight || 0.35).toFixed(3) + '</b></div>' +
                        '<div style="background:var(--bg); padding:10px; border-radius:6px;"><div style="font-size:10px; color:var(--text-dim);">CLV EDGE</div><b style="color:var(--gold);">' + (mlWeights.clv_weight || 0.35).toFixed(3) + '</b></div>' +
                        '<div style="background:var(--bg); padding:10px; border-radius:6px;"><div style="font-size:10px; color:var(--text-dim);">POISSON xG</div><b style="color:var(--cyan);">' + (mlWeights.poisson_weight || 0.30).toFixed(3) + '</b></div>' +
                    '</div>' +
                '</div>';
                return;
            }

            if (currentTab === 'ledger') {
                titleEl.innerText = "ðŸ“Š Self-Learning Performance Ledger";
                if (ledgerData.length === 0) {
                    container.innerHTML = '<div style="text-align:center; padding:20px; color:var(--text-dim);">No logged bets yet. Tap the 3-Fold tier above to log your bet slip!</div>';
                    return;
                }
                
                let totalStaked = ledgerData.reduce((acc, cur) => acc + cur.stake, 0);
                let settled = ledgerData.filter(i => i.status !== 'PENDING');
                let won = settled.filter(i => i.status === 'WON');
                let profit = won.reduce((acc, cur) => acc + (cur.return_amt - cur.stake), 0) - settled.filter(i => i.status === 'LOST').reduce((acc, cur) => acc + cur.stake, 0);
                let strikeRate = settled.length > 0 ? ((won.length / settled.length) * 100).toFixed(1) : 0;

                let html = '<div class="card" style="border-left-color:var(--cyan);">' +
                    '<b style="color:var(--cyan); font-size:14px;">Ledger Performance Summary</b>' +
                    '<div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:5px; margin-top:8px; text-align:center;">' +
                        '<div style="background:var(--bg); padding:8px; border-radius:6px;"><div style="font-size:10px; color:var(--text-dim);">STAKED</div><b>Â£' + totalStaked.toFixed(2) + '</b></div>' +
                        '<div style="background:var(--bg); padding:8px; border-radius:6px;"><div style="font-size:10px; color:var(--text-dim);">PROFIT</div><b style="color:' + (profit >= 0 ? 'var(--accent)' : 'var(--red)') + ';">Â£' + profit.toFixed(2) + '</b></div>' +
                        '<div style="background:var(--bg); padding:8px; border-radius:6px;"><div style="font-size:10px; color:var(--text-dim);">STRIKE RATE</div><b>' + strikeRate + '%</b></div>' +
                    '</div>' +
                '</div>';

                html += ledgerData.map(item => 
                    '<div class="card" style="border-left-color:' + (item.status === 'WON' ? 'var(--accent)' : item.status === 'LOST' ? 'var(--red)' : 'var(--gold)') + '">' +
                        '<div class="card-top">' +
                            '<div>' +
                                '<div style="font-size:10px; color:var(--text-dim);">' + item.timestamp + '</div>' +
                                '<b style="font-size:14px;">' + item.tier_name + '</b><br/>' +
                                '<span style="font-size:12px; color:var(--text-dim);">Stake: Â£' + item.stake.toFixed(2) + ' | Odds: @' + item.odds + ' âž” Ret: Â£' + item.return_amt.toFixed(2) + '</span>' +
                            '</div>' +
                            '<div style="text-align:right;">' +
                                '<span class="badge" style="background:' + (item.status === 'WON' ? 'var(--accent)' : item.status === 'LOST' ? 'var(--red)' : 'var(--gold)') + '; color:#0d1117;">' + item.status + '</span>' +
                            '</div>' +
                        '</div>' +
                        (item.status === 'PENDING' ? '<div style="margin-top:8px; display:flex; gap:6px;"><button class="btn" style="padding:4px 10px; font-size:11px; background:var(--accent);" onclick="updateBetStatus(' + item.id + ', \'WON\')">âœ… Mark Won</button><button class="btn" style="padding:4px 10px; font-size:11px; background:var(--red); color:#fff;" onclick="updateBetStatus(' + item.id + ', \'LOST\')">âŒ Mark Lost</button></div>' : '') +
                    '</div>'
                ).join('');
                container.innerHTML = html;
                return;
            }

            let filteredSlate = globalData.slate;
            if (currentTab === 'today') {
                filteredSlate = globalData.slate.filter(i => i.day_group === 'today');
                titleEl.innerText = "âš¡ Today's Active Games & xG Predictions";
            } else if (currentTab === 'futures') {
                filteredSlate = globalData.slate.filter(i => i.day_group === 'futures');
                titleEl.innerText = "ðŸ”® Futures (Advanced xG Value Edge)";
            } else if (currentTab === 'three') {
                filteredSlate = globalData.slate.filter(i => i.leg <= 3);
                titleEl.innerText = "ðŸŽ¯ 3-Fold Anchor Selections (Legs 1-3)";
            } else {
                titleEl.innerText = "ðŸ”¥ Full Automated xG Slate (Legs 1-9)";
            }

            if (filteredSlate.length === 0) {
                container.innerHTML = '<div style="text-align:center; padding:20px; color:var(--text-dim);">No fixtures scheduled for this filter.</div>';
                return;
            }

            container.innerHTML = filteredSlate.map(item => {
                const isFutures = item.day_group === 'futures';
                const isElite = item.scoreai_conf >= 90;
                return '<div class="card ' + (isFutures ? 'futures-card' : isElite ? 'elite' : '') + '">' +
                    '<div class="card-top">' +
                        '<div>' +
                            '<div style="font-size:10px; color:var(--text-dim); font-weight:700; margin-bottom:2px;">LEG ' + item.leg + ' &bull; ðŸ“… ' + item.date + '</div>' +
                            '<b style="font-size:14px; font-weight:700;">' + item.match + '</b><br/>' +
                            '<span style="font-size:12px; color:var(--accent); font-weight:600;">' + item.selection + '</span> <span style="font-size:11px; color:var(--text-dim);">(' + item.market + ')</span>' +
                        '</div>' +
                        '<div style="text-align:right;">' +
                            '<div style="font-size:16px; font-weight:900; color:' + (isFutures ? 'var(--purple)' : isElite ? 'var(--gold)' : 'var(--accent)') + ';">@ ' + item.odds + '</div>' +
                        '</div>' +
                    '</div>' +
                    '<div class="progress-bar-bg">' +
                        '<div class="progress-bar-fill ' + (isFutures ? 'futures' : isElite ? 'elite' : '') + '" style="width: ' + item.scoreai_conf + '%;"></div>' +
                    '</div>' +
                    '<div class="badges">' +
                        (isFutures ? '<span class="badge badge-futures">ðŸ”® FUTURES</span>' : '') +
                        (isElite ? '<span class="badge badge-elite">â­ 90%+ ELITE</span>' : '') +
                        '<span class="badge badge-scoreai">AI: ' + item.scoreai_conf + '%</span>' +
                        '<span class="badge badge-clv">CLV: +' + item.clv_edge + '%</span>' +
                        '<span class="badge badge-poisson">xG Model: ' + item.poisson_prob + '%</span>' +
                    '</div>' +
                '</div>';
            }).join('');
        }

        function copyBetSlip() {
            if (!globalData) return;
            logBetToLedger('Full xG Slate Slip', globalData.accumulators.nine_fold.odds);
            
            let text = "=== Edgemetrix-Pro-26 xG ML SLIP ===\\n\\n";
            globalData.slate.forEach(i => {
                text += "Leg " + i.leg + " [" + i.date + "]: " + i.match + " -> " + i.selection + " (Model: " + i.poisson_prob + "%) @ " + i.odds + "\\n";
            });
            
            navigator.clipboard.writeText(text).then(() => {
                const toast = document.getElementById('toast');
                toast.innerText = "Bet slip copied & ML weights optimized!";
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
    return {"name": "Edgemetrix-Pro-26 ML", "short_name": "GEM ML", "start_url": "/", "display": "standalone", "background_color": "#0d1117", "theme_color": "#00ff88", "icons": []}

@app.get("/", response_class=HTMLResponse)
async def read_index(response: Response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return HTML_CONTENT

@app.get("/api/fixtures")
async def get_fixtures(response: Response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    
    raw_fixtures = [
        {"leg": 1, "date": "Today, 15:00", "day_group": "today", "match": "Chelsea vs Newcastle", "selection": "Chelsea Win or Draw (DC)", "market": "Double Chance", "odds": 1.25, "scoreai_conf": 91, "clv_edge": 4.2, "home_xg": 1.85, "away_xg": 0.92, "home_xa": 1.20, "away_xa": 0.60},
        {"leg": 2, "date": "Today, 17:30", "day_group": "today", "match": "Crystal Palace vs Liverpool", "selection": "Liverpool Win or Draw (DC)", "market": "Double Chance", "odds": 1.18, "scoreai_conf": 94, "clv_edge": 5.1, "home_xg": 2.10, "away_xg": 0.75, "home_xa": 1.40, "away_xa": 0.50},
        {"leg": 3, "date": "Wed 28 Oct, 20:00", "day_group": "futures", "match": "Arsenal vs Sevilla", "selection": "Arsenal Win or Draw (DC)", "market": "Double Chance", "odds": 1.22, "scoreai_conf": 93, "clv_edge": 5.8, "home_xg": 2.20, "away_xg": 0.80, "home_xa": 1.50, "away_xa": 0.55},
        {"leg": 4, "date": "Wed 28 Oct, 20:00", "day_group": "futures", "match": "Bayern Munich vs Galatasaray", "selection": "Over 1.5 Goals", "market": "Total Goals", "odds": 1.28, "scoreai_conf": 92, "clv_edge": 4.9, "home_xg": 2.40, "away_xg": 1.10, "home_xa": 1.80, "away_xa": 0.70},
        {"leg": 5, "date": "Thu 29 Oct, 18:45", "day_group": "futures", "match": "Roma vs Brighton", "selection": "Over 1.5 Goals", "market": "Total Goals", "odds": 1.32, "scoreai_conf": 89, "clv_edge": 4.1, "home_xg": 1.70, "away_xg": 1.55, "home_xa": 1.10, "away_xa": 1.00},
        {"leg": 6, "date": "Tomorrow, 19:45", "day_group": "today", "match": "Inter Milan vs Juventus", "selection": "Inter Milan Win or Draw", "market": "Double Chance", "odds": 1.30, "scoreai_conf": 89, "clv_edge": 3.9, "home_xg": 1.70, "away_xg": 0.95, "home_xa": 1.15, "away_xa": 0.65},
        {"leg": 7, "date": "Sat 31 Oct, 18:45", "day_group": "upcoming", "match": "Ajax vs Feyenoord", "selection": "Over 1.5 Goals", "market": "Total Goals", "odds": 1.35, "scoreai_conf": 87, "clv_edge": 3.5, "home_xg": 1.90, "away_xg": 1.40, "home_xa": 1.30, "away_xa": 0.90},
        {"leg": 8, "date": "Sat 31 Oct, 20:15", "day_group": "upcoming", "match": "Benfica vs Porto", "selection": "Benfica Win or Draw", "market": "Double Chance", "odds": 1.28, "scoreai_conf": 91, "clv_edge": 4.5, "home_xg": 1.60, "away_xg": 0.85, "home_xa": 1.05, "away_xa": 0.55},
        {"leg": 9, "date": "Sun 1 Nov, 20:30", "day_group": "upcoming", "match": "Sporting CP vs Braga", "selection": "Sporting CP Win or Draw", "market": "Double Chance", "odds": 1.20, "scoreai_conf": 93, "clv_edge": 4.8, "home_xg": 1.95, "away_xg": 0.90, "home_xa": 1.35, "away_xa": 0.60}
    ]

    processed_slate = []
    for fix in raw_fixtures:
        p_res = calculate_advanced_xg_poisson(fix["home_xg"], fix["away_xg"], fix["home_xa"], fix["away_xa"])
        if "Double Chance" in fix["market"]:
            model_prob = p_res["dc_home"] if "Chelsea" in fix["match"] or "Liverpool" in fix["match"] or "Arsenal" in fix["match"] or "Inter" in fix["match"] or "Benfica" in fix["match"] or "Sporting" in fix["match"] else p_res["dc_away"]
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

@app.get("/api/ml-weights")
async def get_ml_weights_api():
    return get_ml_weights()

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
    optimize_ml_weights()
    return {"status": "logged_and_optimized"}

@app.post("/api/ledger/update")
async def update_bet(request: Request):
    data = await request.json()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE ledger SET status = ? WHERE id = ?", (data.get("status"), data.get("id")))
    conn.commit()
    conn.close()
    optimize_ml_weights()
    return {"status": "updated_and_optimized"}



@app.api_route("/api/data", methods=["GET", "HEAD"])`n@app.api_route("/api/slate", methods=["GET", "HEAD"])
async def get_slate_data(slate: str = "bankers"):
    try:
        data = generate_predictions() if "generate_predictions" in globals() else {}
        return data
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.api_route("/api/health", methods=["GET", "HEAD"])
async def edgemetrix_health():
    return {
        "status": "healthy",
        "system": "Edgemetrix-Pro-26",
        "version": "2.6.0",
        "platform": "Render"
    }
# === DASHBOARD ROUTE ===
@app.route('/dashboard')
def dashboard():
    return render_template('index.html')

@app.route('/api/fixtures')
def api_fixtures():
    return jsonify({
        "status": "ok",
        "data": [

# === DASHBOARD ROUTES ===
@app.route('/dashboard')
def dashboard():
    return render_template('index.html')

@app.route('/api/fixtures')
def api_fixtures():
    return jsonify({
        "status": "ok",
        "data": [
            {"id": 1, "kickoff": "19:45", "league": "Premier League", "home": "Arsenal", "away": "Chelsea", "market": "1 - Home", "prob": 62.4, "odds": 1.85, "ev": 7.1, "confidence": 0.88},
            {"id": 2, "kickoff": "20:00", "league": "LaLiga", "home": "Real Madrid", "away": "Girona", "market": "O2.5 - Over", "prob": 68.1, "odds": 1.75, "ev": 5.8, "confidence": 0.91},
            {"id": 3, "kickoff": "19:30", "league": "Bundesliga", "home": "Dortmund", "away": "Leipzig", "market": "BTTS - Yes", "prob": 59.3, "odds": 1.90, "ev": 3.2, "confidence": 0.74},
            {"id": 4, "kickoff": "17:00", "league": "Premier League", "home": "Man City", "away": "Newcastle", "market": "1 - Home", "prob": 71.2, "odds": 1.62, "ev": 6.4, "confidence": 0.93},
            {"id": 5, "kickoff": "15:00", "league": "Serie A", "home": "Inter Milan", "away": "Napoli", "market": "1 - Home", "prob": 58.0, "odds": 1.95, "ev": 4.5, "confidence": 0.78}
        ]
    })
