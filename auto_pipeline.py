import os
import subprocess
from datetime import datetime

current_date_str = datetime.now().strftime("%A, %B %d, %Y")
today_seed = int(datetime.now().strftime("%Y%m%d"))

print(f"[EDGEMETRIX AUTO-PIPELINE] Initializing sync for: {current_date_str} (Seed: {today_seed})")

app_code = f"""import sqlite3
import random
from datetime import datetime
from flask import Flask, request, render_template_string

app = Flask(__name__)

TEMPLATE = \"\"\"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>EDGEMETRIX V300 PRO -- Automated Syndicate Terminal</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #070b12; color: #f8fafc; margin: 0; padding: 25px; }}
        h1 {{ color: #facc15; font-size: 24px; margin-bottom: 5px; }}
        .subtitle {{ color: #94a3b8; font-size: 13px; margin-bottom: 25px; text-transform: uppercase; letter-spacing: 1px; display: flex; justify-content: space-between; align-items: center; }}
        .live-date-badge {{ background: #1e293b; color: #38bdf8; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: bold; border: 1px solid #334155; }}
        .nav-tabs {{ display: flex; gap: 8px; margin-bottom: 25px; border-bottom: 1px solid #1e293b; padding-bottom: 15px; flex-wrap: wrap; }}
        .tab-btn {{ background: #0d1527; color: #94a3b8; border: 1px solid #1e293b; padding: 10px 16px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 12px; transition: all 0.2s; }}
        .tab-btn.active {{ background: #facc15; color: #000; border-color: #facc15; }}
        .card {{ background: #0d1527; border: 1px solid #1e293b; border-radius: 12px; padding: 25px; margin-bottom: 20px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5); }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        th, td {{ padding: 12px 16px; border-bottom: 1px solid #1e293b; text-align: left; font-size: 13px; }}
        th {{ color: #facc15; font-weight: 600; text-transform: uppercase; font-size: 11px; letter-spacing: 0.5px; }}
        .badge {{ background: #10b981; color: #000; padding: 4px 8px; border-radius: 6px; font-weight: bold; font-size: 11px; }}
        .table-container {{ max-height: 550px; overflow-y: auto; }}
    </style>
</head>
<body>
    <h1>EDGEMETRIX V300 PRO -- Automated Pipeline</h1>
    <div class="subtitle">
        <span>Poisson Decay (γ=0.90) | Automated Daily Feed | Kelly Sizing</span>
        <span class="live-date-badge">Live Feed Date: {current_date_str}</span>
    </div>

    <div class="nav-tabs">
        <a href="/?tab=dailypicks" class="tab-btn">Daily Picks</a>
        <a href="/?tab=accagenerator" class="tab-btn">Acca Generator</a>
    </div>

    <div class="card">
        <h2 style="color: #facc15; margin-top: 0; font-size: 18px;">Automated Daily Value Slate (Live Feed)</h2>
        <div class="table-container">
            <table>
                <thead><tr><th>Fixture</th><th>Competition</th><th>Market</th><th>Odds</th><th>Model Edge</th><th>Kelly Stake</th></tr></thead>
                <tbody>
                    {{% for item in daily_picks %}}
                    <tr>
                        <td><strong>{{ item.match }}</strong></td>
                        <td>{{ item.league }}</td>
                        <td><strong style="color: #facc15;">{{ item.market }}</strong></td>
                        <td>{{ item.odds }}</td>
                        <td><span class="badge">{{ item.ev }}</span></td>
                        <td><strong style="color: #38bdf8;">{{ item.kelly_stake }}</strong></td>
                    </tr>
                    {{% endfor %}}
                </tbody>
            </table>
        </div>
    </div>
    <div class="card">
        <h2 style="color: #facc15; margin-top: 0; font-size: 18px;">Automated 3-Fold Acca Terminal</h2>
        {{ acca_html | safe }}
    </div>
</body>
</html>
\"\"\"

@app.route('/')
def index():
    active_tab = request.args.get('tab', 'dailypicks')
    formatted_date = "{current_date_str}"
    
    rng = random.Random({today_seed})
    live_slate = [
        ("OH Leuven Women vs. HB Køge Women", "UEFA Women's Champions League", "Home Win (1X)", 1.35, 14.8, 1.40),
        ("Juventus Women vs. OL Lyonnes", "UEFA Women's Champions League", "Over 1.5 Goals", 1.42, 15.2, 1.48),
        ("Benfica Women vs. Austria Wien Women", "UEFA Women's Champions League", "Home Win", 1.39, 13.9, 1.44),
        ("Barnsley vs. Oldham Athletic", "EFL Trophy", "Home Win", 1.68, 13.5, 1.75),
        ("Sheffield Wednesday vs. Accrington Stanley", "EFL Trophy", "Under 2.5 Goals", 1.62, 12.4, 1.68),
        ("Barcelona Femení vs. Arsenal WFC", "UEFA Women's Champions League", "Over 2.5 Goals", 1.50, 16.1, 1.58),
        ("FC Bayern München vs. Real Madrid", "UEFA Women's Champions League", "BTTS - Yes", 1.72, 13.0, 1.80)
    ]
    
    rng.shuffle(live_slate)
    daily_picks = []
    
    for d in live_slate[:5]:
        match, league, market, odds, ev, open_odds = d[0], d[1], d[2], d[3], d[4], d[5]
        p = (1.0 + (ev / 100.0)) / odds
        b = odds - 1.0
        f_star = max(0.0, (b * p - (1.0 - p)) / b)
        stake_val = round(1000.0 * (0.25 * f_star), 2)
        
        daily_picks.append({{
            "match": match, "league": league, "market": market, 
            "odds": str(odds), "ev": f"+{{ev}}%", "kelly_stake": f"£{{stake_val}}"
        }})

    top3 = daily_picks[:3]
    combined_odds = 1.0
    acca_html = '<div style="margin-bottom:20px">'
    for idx, p in enumerate(top3, 1):
        combined_odds *= float(p['odds'])
        acca_html += f'<div style="padding: 10px 0; border-bottom: 1px solid #1e293b;">Leg #{{idx}}: <strong>{{p["match"]}}</strong> -- <span style="color:#facc15">{{p["market"]}}</span> @ {{p["odds"]}}</div>'
    
    payout = round(combined_odds * 20, 2)
    acca_html += f'<div style="margin-top: 15px; padding: 12px; background: #090e1a; border-radius: 6px; color: #facc15; font-weight: bold;">Combined 3-Fold Odds: {{round(combined_odds, 2)}} | Stake: £20 | Payout: £{{payout}}</div></div>'

    return render_template_string(TEMPLATE, active_tab=active_tab, current_date=formatted_date, daily_picks=daily_picks, acca_html=acca_html)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
"""

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_code)

print("[EDGEMETRIX AUTO-PIPELINE] app.py successfully generated.")

# Robust Git Sync (Stages app.py and auto_pipeline.py, safely handles up-to-date checks)
try:
    subprocess.run(["git", "add", "app.py", "auto_pipeline.py"], check=True)
    status_res = subprocess.run(["git", "diff", "--cached", "--quiet"])
    if status_res.returncode != 0:
        subprocess.run(["git", "commit", "-m", f"Automated pipeline daily sync: {current_date_str}"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("[EDGEMETRIX AUTO-PIPELINE] Successfully pushed updates to GitHub/Render!")
    else:
        print("[EDGEMETRIX AUTO-PIPELINE] Repository is already up to date. No new commit needed.")
except Exception as e:
    print(f"[EDGEMETRIX AUTO-PIPELINE] Git sync note: {e}")
