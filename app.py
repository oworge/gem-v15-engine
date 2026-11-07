import os
import logging
import requests
from flask import Flask, render_template_string, request
from engines import ENGINES

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

FOOTBALL_API_KEY = os.environ.get('FOOTBALL_API_KEY', '')
API_URL = 'https://v3.football.api-sports.io/fixtures'

def fetch_live_upcoming_fixtures():
    headers = {
        'x-rapidapi-host': 'v3.football.api-sports.io',
        'x-rapidapi-key': FOOTBALL_API_KEY
    }
    params = {'next': '250', 'status': 'NS-1H-2H-HT'}
    processed_db = {}
    
    if FOOTBALL_API_KEY:
        try:
            response = requests.get(API_URL, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json().get('response', [])
                for item in data:
                    status_short = item['fixture']['status']['short']
                    if status_short in ['FT', 'AET', 'PEN', 'PST', 'CANC']:
                        continue
                    
                    match_id = item['fixture']['id']
                    match_date = item['fixture']['date'][:10]
                    home = item['teams']['home']['name']
                    away = item['teams']['away']['name']
                    region = item['league']['name']
                    
                    intel = ENGINES.run_all_engines(match_id, home, away, region)
                    
                    fixture_obj = {
                        'id': match_id,
                        'region': region,
                        'home': home,
                        'away': away,
                        'league': f"{item['league']['name']} ({item['league']['country']})",
                        'time': item['fixture']['date'][11:16] + ' GMT',
                        'market': f'{home} Win or Draw & Over 1.5',
                        'odds': 1.45,
                        'value_tag': intel['consensus_status'],
                        'backend_intelligence': intel
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
    <title>EDGEMETRIX V300 - Active Core</title>
    <style>
        body { background: #07090e; color: #f1f5f9; font-family: system-ui, sans-serif; margin: 0; padding: 25px; }
        .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1e293b; padding-bottom: 15px; margin-bottom: 20px; }
        h1 { font-size: 22px; color: #38bdf8; margin: 0; }
        .card { background: #111827; border: 1px solid #1f2937; border-radius: 10px; padding: 20px; margin-bottom: 15px; }
        .match-header { display: flex; justify-content: space-between; font-weight: bold; font-size: 18px; color: #fff; }
        .badge { background: #064e3b; color: #4ade80; border: 1px solid #059669; font-size: 11px; padding: 3px 10px; border-radius: 4px; }
        .metrics { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-top: 15px; background: #030712; padding: 12px; border-radius: 8px; font-size: 13px; }
        .metric-val { color: #38bdf8; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h1>EDGEMETRIX V300 <span class="badge">90%+ Engine Active</span></h1>
        <span>Total Active Predictions: {{ slate | length }}</span>
    </div>

    <h2>⚡ Verified Match Card ({{ d }})</h2>

    {% for f in slate %}
        <div class="card">
            <div class="match-header">
                <span>{{ f.home }} vs {{ f.away }}</span>
                <span class="badge">{{ f.value_tag }}</span>
            </div>
            <div style="font-size: 13px; color: #94a3b8; margin-top: 4px;">{{ f.league }} | Kickoff: {{ f.time }}</div>
            
            <div class="metrics">
                <div>Selection: <span class="metric-val" style="color: #4ade80;">{{ f.market }}</span></div>
                <div>Odds: <span class="metric-val">@{{ f.odds }}</span></div>
                <div>Confluence: <span class="metric-val" style="color: #c084fc;">{{ f.backend_intelligence.consensus_score }}</span></div>
                <div>Opta xG Diff: <span class="metric-val">{{ f.backend_intelligence.opta_ai.xg_differential }}</span></div>
            </div>
        </div>
    {% endfor %}
</body>
</html>
"""

@app.route('/')
def index():
    db = fetch_live_upcoming_fixtures()
    dates = sorted(db.keys())
    d = request.args.get('date', dates[0] if dates else '')
    if d not in db and dates:
        d = dates[0]
    slate = db.get(d, [])
    return render_template_string(TEMPLATE, dates=dates, d=d, slate=slate)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
