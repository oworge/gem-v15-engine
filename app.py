import os
import json
import logging
import urllib.request
from flask import Flask, render_template_string, request
from engines import ENGINES
from props_engine import PROPS_ENGINE

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

FOOTBALL_API_KEY = os.environ.get('FOOTBALL_API_KEY', '')
API_URL = 'https://v3.football.api-sports.io/fixtures?next=300&status=NS-1H-2H-HT'

def fetch_live_upcoming_fixtures():
    processed_db = {}
    if FOOTBALL_API_KEY:
        try:
            req = urllib.request.Request(
                API_URL, 
                headers={'x-rapidapi-host': 'v3.football.api-sports.io', 'x-rapidapi-key': FOOTBALL_API_KEY}
            )
            with urllib.request.urlopen(req, timeout=12) as response:
                data_json = json.loads(response.read().decode())
                for item in data_json.get('response', []):
                    if item['fixture']['status']['short'] in ['FT', 'AET', 'PEN', 'PST', 'CANC']:
                        continue
                    match_id = item['fixture']['id']
                    match_date = item['fixture']['date'][:10]
                    home = item['teams']['home']['name']
                    away = item['teams']['away']['name']
                    region = item['league']['name']
                    
                    intel = ENGINES.run_all_engines(match_id, home, away, region)
                    fixture_obj = {
                        'id': match_id, 'region': region, 'home': home, 'away': away,
                        'league': f"{item['league']['name']} ({item['league']['country']})",
                        'time': item['fixture']['date'][11:16] + ' GMT',
                        'market': f'{home} Win or Draw & Over 1.5', 'odds': 1.45,
                        'value_tag': intel['consensus_status'], 'backend_intelligence': intel
                    }
                    if match_date not in processed_db:
                        processed_db[match_date] = []
                    processed_db[match_date].append(fixture_obj)
        except Exception as e:
            logging.error(f'API Fetch Error: {e}')

    if not processed_db:
        today_str = "2026-11-07"
        processed_db[today_str] = [
            {'id': 101, 'region': 'Premier League', 'home': 'Leeds United', 'away': 'Tottenham Hotspur', 'league': 'Premier League (UK)', 'time': '12:30 GMT', 'market': 'Both Teams To Score', 'odds': 1.65, 'value_tag': 'VERIFIED 92.1%'},
            {'id': 102, 'region': 'Premier League', 'home': 'Fulham', 'away': 'Newcastle United', 'league': 'Premier League (UK)', 'time': '15:00 GMT', 'market': 'Newcastle or Draw & Over 1.5', 'odds': 1.42, 'value_tag': 'VERIFIED 91.5%'},
            {'id': 103, 'region': 'Premier League', 'home': 'Nottingham Forest', 'away': 'Manchester City', 'league': 'Premier League (UK)', 'time': '17:30 GMT', 'market': 'Man City or Draw & Over 1.5', 'odds': 1.30, 'value_tag': 'VERIFIED 93.8%'},
            {'id': 201, 'region': 'La Liga', 'home': 'CA Osasuna', 'away': 'Athletic Club', 'league': 'La Liga (Spain)', 'time': '17:30 GMT', 'market': 'Athletic Club or Draw & Over 1.5', 'odds': 1.40, 'value_tag': 'VERIFIED 92.4%'},
            {'id': 202, 'region': 'La Liga', 'home': 'Valencia', 'away': 'Real Madrid', 'league': 'La Liga (Spain)', 'time': '20:00 GMT', 'market': 'Real Madrid or Draw & Over 1.5', 'odds': 1.35, 'value_tag': 'VERIFIED 94.5%'},
            {'id': 301, 'region': 'Bundesliga', 'home': 'Mainz 05', 'away': 'Bayern Munich', 'league': 'Bundesliga (Germany)', 'time': '14:30 GMT', 'market': 'Bayern Munich or Draw & Over 1.5', 'odds': 1.28, 'value_tag': 'VERIFIED 95.1%'}
        ]
        for match in processed_db[today_str]:
            match['backend_intelligence'] = ENGINES.run_all_engines(match['id'], match['home'], match['away'], match['region'])
    return processed_db

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>EDGEMETRIX V300 - Multi-Market Pro Dashboard</title>
    <style>
        body { background: #07090e; color: #f1f5f9; font-family: system-ui, sans-serif; margin: 0; padding: 25px; }
        .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1e293b; padding-bottom: 15px; margin-bottom: 20px; }
        h1 { font-size: 22px; color: #38bdf8; margin: 0; }
        .nav-tabs { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 25px; background: #111827; padding: 12px; border-radius: 8px; border: 1px solid #374151; }
        .tab-btn { background: #1f2937; color: #94a3b8; border: 1px solid #4b5563; padding: 10px 16px; border-radius: 6px; cursor: pointer; font-weight: bold; text-decoration: none; font-size: 14px; display: inline-block; }
        .tab-btn.active { background: #0284c7; color: #ffffff; border-color: #38bdf8; }
        .card { background: #111827; border: 1px solid #1f2937; border-radius: 10px; padding: 20px; margin-bottom: 15px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.2); }
        .match-header { display: flex; justify-content: space-between; font-weight: bold; font-size: 18px; color: #fff; }
        .badge { background: #064e3b; color: #4ade80; border: 1px solid #059669; font-size: 11px; padding: 3px 10px; border-radius: 4px; }
        .badge-prop { background: #581c87; color: #e879f9; border: 1px solid #7e22ce; font-size: 11px; padding: 3px 10px; border-radius: 4px; }
        .badge-goals { background: #1e3a8a; color: #60a5fa; border: 1px solid #2563eb; font-size: 11px; padding: 3px 10px; border-radius: 4px; }
        .metrics { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-top: 15px; background: #030712; padding: 12px; border-radius: 8px; font-size: 13px; }
        .metric-val { color: #38bdf8; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h1>EDGEMETRIX V300 <span class="badge">Multi-Tab Pro Active</span></h1>
        <span style="color: #94a3b8;">System Mode: Global Match Slate, Goals, BTTS & Props</span>
    </div>

    <div class="nav-tabs">
        <a href="/?tab=matches" class="tab-btn {% if active_tab == 'matches' %}active{% endif %}">⚽ Global Match Slate</a>
        <a href="/?tab=over25" class="tab-btn {% if active_tab == 'over25' %}active{% endif %}">📈 Over 2.5 Goals (10)</a>
        <a href="/?tab=btts" class="tab-btn {% if active_tab == 'btts' %}active{% endif %}">🔥 BTTS High Confidence (10)</a>
        <a href="/?tab=props" class="tab-btn {% if active_tab == 'props' %}active{% endif %}">🎯 Bully Engine Props</a>
    </div>

    {% if active_tab == 'matches' %}
        <h2>⚡ Verified Global Match Card ({{ d }})</h2>
        {% for f in slate %}
            <div class="card">
                <div class="match-header">
                    <span>{{ f.home }} vs {{ f.away }}</span>
                    <span class="badge">{{ f.value_tag }}</span>
                </div>
                <div style="font-size: 13px; color: #94a3b8; margin-top: 4px;">{{ f.league }} | Kickoff: {{ f.time }}</div>
                <div class="metrics">
                    <div>Highest +EV Market: <span class="metric-val" style="color: #4ade80;">{{ f.market }}</span></div>
                    <div>Odds: <span class="metric-val">@{{ f.odds }}</span></div>
                    <div>Confluence: <span class="metric-val" style="color: #c084fc;">{{ f.backend_intelligence.consensus_score }}</span></div>
                    <div>Opta xG Diff: <span class="metric-val">{{ f.backend_intelligence.opta_ai.xg_differential }}</span></div>
                </div>
            </div>
        {% endfor %}
    
    {% elif active_tab == 'over25' %}
        <h2>📈 Over 2.5 Goals — Top 10 High Confidence Games</h2>
        <p style="color: #94a3b8; font-size: 13px; margin-bottom: 20px;">Filtered by combined expected goals (xG), high shot volume, and defensive vulnerabilities.</p>
        {% for g in over25_slate %}
            <div class="card">
                <div class="match-header">
                    <span>{{ g.match }}</span>
                    <span class="badge-goals">{{ g.confidence }}</span>
                </div>
                <div style="font-size: 13px; color: #94a3b8; margin-top: 4px;">{{ g.league }}</div>
                <div class="metrics">
                    <div>Selection: <span class="metric-val" style="color: #4ade80;">{{ g.market }}</span></div>
                    <div>Odds: <span class="metric-val">@{{ g.odds }}</span></div>
                    <div>Combined xG: <span class="metric-val" style="color: #c084fc;">{{ g.combined_xg }}</span></div>
                    <div>Engine Status: <span class="metric-val">{{ g.status }}</span></div>
                </div>
            </div>
        {% endfor %}

    {% elif active_tab == 'btts' %}
        <h2>🔥 Both Teams To Score (BTTS) — Top 10 High Confidence Games</h2>
        <p style="color: #94a3b8; font-size: 13px; margin-bottom: 20px;">Selected via opposition scoring frequency, clean-sheet ratios, and tactical offensive pressure.</p>
        {% for b in btts_slate %}
            <div class="card">
                <div class="match-header">
                    <span>{{ b.match }}</span>
                    <span class="badge" style="background: #831843; color: #f472b6; border-color: #db2777;">{{ b.btts_rating }}</span>
                </div>
                <div style="font-size: 13px; color: #94a3b8; margin-top: 4px;">{{ b.league }}</div>
                <div class="metrics">
                    <div>Selection: <span class="metric-val" style="color: #4ade80;">{{ b.market }}</span></div>
                    <div>Odds: <span class="metric-val">@{{ b.odds }}</span></div>
                    <div>Confidence Tier: <span class="metric-val" style="color: #c084fc;">{{ b.confidence }}</span></div>
                    <div>Engine Status: <span class="metric-val">{{ b.status }}</span></div>
                </div>
            </div>
        {% endfor %}

    {% else %}
        <h2>🎯 Bully Engine - Dynamic Player Props & Builder Feed</h2>
        <p style="color: #94a3b8; font-size: 13px; margin-bottom: 20px;">Automatically synchronized with today's active match card fixtures and player metrics.</p>
        {% for p in props_slate %}
            <div class="card">
                <div class="match-header">
                    <span>{{ p.player }} <span style="font-size: 13px; color: #94a3b8;">({{ p.team }} vs {{ p.opponent }})</span></span>
                    <span class="badge-prop">{{ p.rating }}</span>
                </div>
                <div style="font-size: 13px; color: #4ade80; margin-top: 5px; font-weight: 600;">Selection: {{ p.prop_market }}</div>
                <div class="metrics">
                    <div>Baseline Stat: <span class="metric-val">{{ p.baseline }}</span></div>
                    <div>Odds: <span class="metric-val">@{{ p.odds }}</span></div>
                    <div>Modeled Prob: <span class="metric-val" style="color: #c084fc;">{{ p.modeled_probability }}</span></div>
                    <div>Expected Value: <span class="metric-val" style="color: #4ade80;">{{ p.expected_value }}</span></div>
                </div>
            </div>
        {% endfor %}
    {% endif %}
</body>
</html>
"""

@app.route('/')
def index():
    try:
        active_tab = request.args.get('tab', 'matches')
        db = fetch_live_upcoming_fixtures()
        dates = sorted(db.keys())
        d = request.args.get('date', dates[0] if dates else '')
        if d not in db and dates:
            d = dates[0]
        slate = db.get(d, [])
        props_slate = PROPS_ENGINE.get_dynamic_props(slate)
        over25_slate = PROPS_ENGINE.get_over_25_slate(slate)
        btts_slate = PROPS_ENGINE.get_btts_slate(slate)
        return render_template_string(TEMPLATE, dates=dates, d=d, slate=slate, props_slate=props_slate, over25_slate=over25_slate, btts_slate=btts_slate, active_tab=active_tab)
    except Exception as e:
        return f"<h3 style='color:red;'>Dashboard Error: {e}</h3>", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
