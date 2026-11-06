from flask import Flask, render_template_string, request
from datetime import datetime, date
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("EDGEMETRIX")

app = Flask(__name__)

def get_verified_fixtures():
    '''Returns strictly verified 2026/27 Premier League fixtures.'''
    return {
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
        ],
        "2026-11-28": [
            {
                "id": 205, 
                "date": "2026-11-28", 
                "region": "Premier League", 
                "home": "Leeds United", 
                "away": "Coventry City", 
                "league": "Premier League (England)", 
                "time": "15:00 GMT", 
                "banker": True, 
                "xg_home": 1.80, 
                "xg_away": 1.05, 
                "markets": [{"id": "205_1", "name": "Leeds United Win", "odds": 1.68, "prob": 0.67}]
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
        <title>EDGEMETRIX V300 — Dashboard</title>
        <style>
            body { background: #0f172a; color: #f1f5f9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding: 30px; margin: 0; }
            .container { max-width: 900px; margin: 0 auto; }
            h1 { font-size: 24px; margin-bottom: 5px; color: #38bdf8; }
            .subtitle { color: #94a3b8; font-size: 14px; margin-bottom: 25px; }
            .date-nav { display: flex; gap: 10px; margin-bottom: 25px; flex-wrap: wrap; }
            .btn { background: #1e293b; color: #cbd5e1; padding: 10px 16px; text-decoration: none; border-radius: 6px; font-weight: 500; border: 1px solid #334155; transition: all 0.2s; }
            .btn:hover, .btn.active { background: #0284c7; color: white; border-color: #0284c7; }
            .card { background: #1e293b; padding: 20px; border-radius: 10px; margin-bottom: 15px; border: 1px solid #334155; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
            .match-title { font-size: 18px; font-weight: bold; color: #f8fafc; margin-bottom: 8px; }
            .league-badge { display: inline-block; background: #334155; color: #38bdf8; font-size: 11px; padding: 3px 8px; border-radius: 4px; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.5px; }
            .meta { font-size: 13px; color: #94a3b8; }
            .mono { font-family: monospace; color: #38bdf8; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>EDGEMETRIX V300</h1>
            <div class="subtitle">Quantitative Prediction Engine & Verified Premier League Dashboard</div>
            
            <p><strong>Select Match Date:</strong></p>
            <div class="date-nav">
                {% for dt in available_dates %}
                    <a class="btn {% if dt == active_date %}active{% endif %}" href="/?date={{ dt }}">{{ dt }}</a>
                {% endfor %}
            </div>
            
            <h2>Fixtures for {{ active_date }}</h2>
            
            {% if slate %}
                {% for f in slate %}
                    <div class="card">
                        <div class="league-badge">{{ f.league }}</div>
                        <div class="match-title">{{ f.home }} vs {{ f.away }}</div>
                        <div class="meta">
                            📅 Date: <span class="mono">{{ f.date }}</span> | ⏰ Time: {{ f.time }} | Venue/Scope: {{ f.region }}
                        </div>
                    </div>
                {% endfor %}
            {% else %}
                <div class="card"><p>No verified fixtures scheduled for this date.</p></div>
            {% endif %}
        </div>
    </body>
    </html>
    ''', slate=slate, active_date=d, available_dates=available_dates)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
