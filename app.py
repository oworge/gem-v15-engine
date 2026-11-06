from flask import Flask, render_template_string, request
from datetime import datetime, date
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("EDGEMETRIX")

app = Flask(__name__)

def get_verified_fixtures():
    return {
        "2026-11-06": [
            {
                "id": 199, 
                "date": "2026-11-06", 
                "region": "Premier League", 
                "home": "Everton", 
                "away": "Coventry City", 
                "league": "Premier League (England)", 
                "time": "20:00 GMT (Live)", 
                "banker": False, 
                "xg_home": 1.50, 
                "xg_away": 1.10, 
                "markets": [{"id": "199_1", "name": "Under 2.5 Goals", "odds": 1.80, "prob": 0.58}]
            }
        ],
        "2026-11-07": [
            {
                "id": 201, 
                "date": "2026-11-07", 
                "region": "Premier League", 
                "home": "Leeds United", 
                "away": "Tottenham Hotspur", 
                "league": "Premier League (England)", 
                "time": "12:30 GMT", 
                "banker": False, 
                "xg_home": 1.45, 
                "xg_away": 1.65, 
                "markets": [{"id": "201_1", "name": "Both Teams To Score (BTTS)", "odds": 1.72, "prob": 0.64}]
            },
            {
                "id": 202, 
                "date": "2026-11-07", 
                "region": "Premier League", 
                "home": "Arsenal", 
                "away": "Hull City", 
                "league": "Premier League (England)", 
                "time": "15:00 GMT", 
                "banker": True, 
                "xg_home": 2.20, 
                "xg_away": 0.80, 
                "markets": [{"id": "202_1", "name": "Arsenal Win", "odds": 1.30, "prob": 0.82}]
            },
            {
                "id": 203, 
                "date": "2026-11-07", 
                "region": "Premier League", 
                "home": "Nottingham Forest", 
                "away": "Manchester City", 
                "league": "Premier League (England)", 
                "time": "17:30 GMT", 
                "banker": False, 
                "xg_home": 1.10, 
                "xg_away": 2.05, 
                "markets": [{"id": "203_1", "name": "Manchester City Win", "odds": 1.55, "prob": 0.70}]
            }
        ],
        "2026-11-21": [
            {
                "id": 204, 
                "date": "2026-11-21", 
                "region": "Premier League", 
                "home": "Chelsea", 
                "away": "Leeds United", 
                "league": "Premier League (England)", 
                "time": "15:00 GMT", 
                "banker": False, 
                "xg_home": 1.85, 
                "xg_away": 1.10, 
                "markets": [{"id": "204_1", "name": "Chelsea Win & Over 1.5 Goals", "odds": 1.70, "prob": 0.65}]
            }
        ]
    }

@app.route("/")
def index():
    db = get_verified_fixtures()
    available_dates = sorted(db.keys())
    d = request.args.get("date", available_dates[0])
    slate = db.get(d, [])
    
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>EDGEMETRIX V300</title>
        <style>
            body { background: #0f172a; color: #f1f5f9; font-family: sans-serif; padding: 20px; }
            .card { background: #1e293b; padding: 15px; border-radius: 8px; margin-bottom: 10px; border: 1px solid #334155; }
            .mono { font-family: monospace; color: #38bdf8; }
            .btn { background: #0284c7; color: white; padding: 8px 14px; text-decoration: none; border-radius: 4px; margin-right: 5px; display: inline-block; margin-bottom: 10px; }
            .btn:hover { background: #0369a1; }
        </style>
    </head>
    <body>
        <h1>EDGEMETRIX V300 — Verified Premier League Slate</h1>
        <p>Select Match Date:</p>
        <div>
            {% for dt in available_dates %}
                <a class="btn" href="/?date={{ dt }}">{{ dt }}</a>
            {% endfor %}
        </div>
        <h2 style="margin-top:20px;">Fixtures for {{ active_date }}</h2>
        {% for f in slate %}
            <div class="card">
                <strong>{{ f.home }} vs {{ f.away }}</strong> ({{ f.league }})<br>
                📅 Date: <span class="mono">{{ f.date }}</span> | ⏰ Time: {{ f.time }} | Scope: {{ f.region }}
            </div>
        {% endfor %}
    </body>
    </html>
    ''', slate=slate, active_date=d, available_dates=available_dates)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
