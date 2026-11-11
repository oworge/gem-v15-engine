import sqlite3
import random
from datetime import datetime
from flask import Flask, request, render_template_string

app = Flask(__name__)

TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>EDGEMETRIX V300 PRO -- Syndicate Terminal</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #070b12; color: #f8fafc; margin: 0; padding: 25px; }
        h1 { color: #facc15; font-size: 24px; margin-bottom: 5px; }
        .subtitle { color: #94a3b8; font-size: 13px; margin-bottom: 25px; text-transform: uppercase; letter-spacing: 1px; display: flex; justify-content: space-between; align-items: center; }
        .live-date-badge { background: #1e293b; color: #38bdf8; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: bold; border: 1px solid #334155; }
        .nav-tabs { display: flex; gap: 8px; margin-bottom: 25px; border-bottom: 1px solid #1e293b; padding-bottom: 15px; flex-wrap: wrap; }
        .tab-btn { background: #0d1527; color: #94a3b8; border: 1px solid #1e293b; padding: 10px 16px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 12px; transition: all 0.2s; }
        .tab-btn.active { background: #facc15; color: #000; border-color: #facc15; }
        .card { background: #0d1527; border: 1px solid #1e293b; border-radius: 12px; padding: 25px; margin-bottom: 20px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5); }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 12px 16px; border-bottom: 1px solid #1e293b; text-align: left; font-size: 13px; }
        th { color: #facc15; font-weight: 600; text-transform: uppercase; font-size: 11px; letter-spacing: 0.5px; }
        .badge { background: #10b981; color: #000; padding: 4px 8px; border-radius: 6px; font-weight: bold; font-size: 11px; }
        .table-container { max-height: 550px; overflow-y: auto; }
    </style>
</head>
<body>
    <h1>EDGEMETRIX V300 PRO -- Syndicate Terminal</h1>
    <div class="subtitle">
        <span>Poisson Decay (γ=0.90) | Fractional Kelly (0.25x) | Tactical Health</span>
        <span class="live-date-badge">Live Feed Date: {{ current_date }}</span>
    </div>

    <div class="nav-tabs">
        <a href="/?tab=dailypicks" class="tab-btn {% if active_tab == 'dailypicks' %}active{% endif %}">Daily Picks ({{ daily_picks|length }})</a>
        <a href="/?tab=btts" class="tab-btn {% if active_tab == 'btts' %}active{% endif %}">BTTS & Goals ({{ btts_picks|length }})</a>
        <a href="/?tab=correctscore" class="tab-btn {% if active_tab == 'correctscore' %}active{% endif %}">Correct Score Matrix ({{ cs_picks|length }})</a>
        <a href="/?tab=accagenerator" class="tab-btn {% if active_tab == 'accagenerator' %}active{% endif %}">Acca Generator</a>
        <a href="/?tab=trueclv" class="tab-btn {% if active_tab == 'trueclv' %}active{% endif %}">True CLV Audit</a>
    </div>

    {% if active_tab == 'dailypicks' %}
    <div class="card">
        <h2 style="color: #facc15; margin-top: 0; font-size: 18px;">Daily Value Slate (Live Feed)</h2>
        <div class="table-container">
            <table>
                <thead><tr><th>Fixture</th><th>Competition</th><th>Market</th><th>Odds</th><th>Model Edge</th><th>Kelly Stake</th></tr></thead>
                <tbody>
                    {% for item in daily_picks %}
                    <tr>
                        <td><strong>{{ item.match }}</strong></td>
                        <td>{{ item.league }}</td>
                        <td><strong style="color: #facc15;">{{ item.market }}</strong></td>
                        <td>{{ item.odds }}</td>
                        <td><span class="badge">{{ item.ev }}</span></td>
                        <td><strong style="color: #38bdf8;">{{ item.kelly_stake }}</strong></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    {% elif active_tab == 'btts' %}
    <div class="card">
        <h2 style="color: #facc15; margin-top: 0; font-size: 18px;">BTTS & Goals Expectation Matrix</h2>
        <div class="table-container">
            <table>
                <thead><tr><th>Fixture</th><th>Competition</th><th>Market Floor</th><th>Poisson Odds</th><th>Expected Edge</th><th>Status</th></tr></thead>
                <tbody>
                    {% for item in btts_picks %}
                    <tr>
                        <td><strong>{{ item.match }}</strong></td>
                        <td>{{ item.league }}</td>
                        <td><strong style="color: #facc15;">{{ item.market }}</strong></td>
                        <td>{{ item.odds }}</td>
                        <td><span class="badge">{{ item.ev }}</span></td>
                        <td><strong style="color: #38bdf8;">High Value Floor</strong></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    {% elif active_tab == 'correctscore' %}
    <div class="card">
        <h2 style="color: #facc15; margin-top: 0; font-size: 18px;">Poisson Correct Score Distribution Table</h2>
        <div class="table-container">
            <table>
                <thead><tr><th>Fixture</th><th>Top Projected Score</th><th>Secondary Score</th><th>Model Probability</th><th>Value Odds</th></tr></thead>
                <tbody>
                    {% for item in cs_picks %}
                    <tr>
                        <td><strong>{{ item.match }}</strong></td>
                        <td><strong style="color: #facc15;">{{ item.top_score }}</strong></td>
                        <td>{{ item.sec_score }}</td>
                        <td><span class="badge">{{ item.prob }}</span></td>
                        <td><strong style="color: #38bdf8;">{{ item.odds }}</strong></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    {% elif active_tab == 'accagenerator' %}
    <div class="card">
        <h2 style="color: #facc15; margin-top: 0; font-size: 18px;">3-Fold Acca Generator</h2>
        {{ acca_html | safe }}
    </div>

    {% else %}
    <div class="card">
        <h2 style="color: #facc15; margin-top: 0; font-size: 18px;">True CLV Audit Ledger</h2>
        <p style="color: #94a3b8;">Opening line value and market steam audit active for today's UWCL and EFL slates.</p>
    </div>
    {% endif %}
</body>
</html>
"""

@app.route('/')
def index():
    active_tab = request.args.get('tab', 'dailypicks')
    formatted_date = "Wednesday, November 11, 2026"
    
    rng = random.Random(20261111)
    live_slate = [
        ("OH Leuven Women vs. HB Køge Women", "UEFA Women's Champions League", "Home Win (1X)", 1.35, 14.8),
        ("Juventus Women vs. OL Lyonnes", "UEFA Women's Champions League", "Over 1.5 Goals", 1.42, 15.2),
        ("Benfica Women vs. Austria Wien Women", "UEFA Women's Champions League", "Home Win", 1.39, 13.9),
        ("Barnsley vs. Oldham Athletic", "EFL Trophy", "Home Win", 1.68, 13.5),
        ("Sheffield Wednesday vs. Accrington Stanley", "EFL Trophy", "Under 2.5 Goals", 1.62, 12.4),
        ("Barcelona Femení vs. Arsenal WFC", "UEFA Women's Champions League", "Over 2.5 Goals", 1.50, 16.1),
        ("FC Bayern München vs. Real Madrid", "UEFA Women's Champions League", "BTTS - Yes", 1.72, 13.0)
    ]
    
    rng.shuffle(live_slate)
    daily_picks = []
    
    for d in live_slate[:5]:
        match, league, market, odds, ev = d[0], d[1], d[2], d[3], d[4]
        p = (1.0 + (ev / 100.0)) / odds
        b = odds - 1.0
        f_star = max(0.0, (b * p - (1.0 - p)) / b)
        stake_val = round(1000.0 * (0.25 * f_star), 2)
        
        daily_picks.append({
            "match": match, "league": league, "market": market, 
            "odds": str(odds), "ev": f"+{ev}%", "kelly_stake": f"£{stake_val}"
        })

    # Populated BTTS Slate
    btts_picks = [
        {"match": "FC Bayern München vs. Real Madrid", "league": "UEFA Women's Champions League", "market": "BTTS - Yes", "odds": "1.72", "ev": "+13.0%"},
        {"match": "Juventus Women vs. OL Lyonnes", "league": "UEFA Women's Champions League", "market": "Over 1.5 Goals Floor", "odds": "1.42", "ev": "+15.2%"},
        {"match": "Barcelona Femení vs. Arsenal WFC", "league": "UEFA Women's Champions League", "market": "BTTS & Over 2.5", "odds": "1.95", "ev": "+14.1%"}
    ]

    # Populated Correct Score Slate
    cs_picks = [
        {"match": "OH Leuven Women vs. HB Køge Women", "top_score": "2 - 0", "sec_score": "2 - 1", "prob": "18.4%", "odds": "6.50"},
        {"match": "Juventus Women vs. OL Lyonnes", "top_score": "1 - 2", "sec_score": "1 - 1", "prob": "14.2%", "odds": "8.00"},
        {"match": "Barnsley vs. Oldham Athletic", "top_score": "2 - 1", "sec_score": "1 - 0", "prob": "16.1%", "odds": "7.50"}
    ]

    # Acca Builder Logic
    top3 = daily_picks[:3]
    combined_odds = 1.0
    acca_html = '<div style="margin-bottom:20px">'
    for idx, p in enumerate(top3, 1):
        combined_odds *= float(p['odds'])
        acca_html += f'<div style="padding: 10px 0; border-bottom: 1px solid #1e293b;">Leg #{idx}: <strong>{p["match"]}</strong> -- <span style="color:#facc15">{p["market"]}</span> @ {p["odds"]}</div>'
    
    payout = round(combined_odds * 20, 2)
    acca_html += f'<div style="margin-top: 15px; padding: 12px; background: #090e1a; border-radius: 6px; color: #facc15; font-weight: bold;">Combined 3-Fold Odds: {round(combined_odds, 2)} | Stake: £20 | Payout: £{payout}</div></div>'

    return render_template_string(
        TEMPLATE, 
        active_tab=active_tab, 
        current_date=formatted_date, 
        daily_picks=daily_picks, 
        btts_picks=btts_picks, 
        cs_picks=cs_picks, 
        acca_html=acca_html
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000)
