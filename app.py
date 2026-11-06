from flask import Flask, render_template_string, request
from datetime import datetime, date, timedelta
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("EDGEMETRIX")

app = Flask(__name__)

def get_verified_fixtures():
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
                "id": 101, 
                "date": "2026-11-07", 
                "region": "UK Pyramid", 
                "home": "Birmingham City", 
                "away": "Wrexham", 
                "league": "League One (England)", 
                "time": "15:00 GMT", 
                "banker": False, 
                "xg_home": 1.70, 
                "xg_away": 1.35, 
                "markets": [{"id": "101_1", "name": "Both Teams To Score (BTTS)", "odds": 1.75, "prob": 0.62}]
            }
        ],
        "2026-11-21": [
            {
                "id": 202, 
                "date": "2026-11-21", 
                "region": "Premier League", 
                "home": "Chelsea", 
                "away": "Leeds United", 
                "league": "Premier League (England)", 
                "time": "15:00 GMT", 
                "banker": False, 
                "xg_home": 1.85, 
                "xg_away": 1.10, 
                "markets": [{"id": "202_1", "name": "Chelsea Win & Over 1.5 Goals", "odds": 1.70, "prob": 0.65}]
            }
        ],
        "2026-11-28": [
            {
                "id": 203, 
                "date": "2026-11-28", 
                "region": "Premier League", 
                "home": "Leeds United", 
                "away": "Coventry City", 
                "league": "Premier League (England)", 
                "time": "15:00 GMT", 
                "banker": True, 
                "xg_home": 1.80, 
                "xg_away": 1.05, 
                "markets": [{"id": "203_1", "name": "Leeds United Win", "odds": 1.68, "prob": 0.67}]
            }
        ]
    }

@app.route("/")
def index():
    db = get_verified_fixtures()
    available_dates = sorted(db.keys())
    d = request.args.get("date", available_dates[0])
    slate = db.get(d, [])
    
    html = '''<!DOCTYPE html><html><head><title>EDGEMETRIX V300</title><style>
    body { background: #0f172a; color: #f1f5f9; font-family: sans-serif; padding: 20px; }
    .card { background: #1e293b; padding: 15px; border-radius: 8px; margin-bottom: 10px; border: 1px solid #334155; }
    .mono { font-family: monospace; color: #38bdf8; }
    .btn { background: #0284c7; color: white; padding: 8px 14px; text-decoration: none; border-radius: 4px; margin-right: 5px; display: inline-block; margin-bottom: 10px; }
    </style></head><body>'''
    
    html += "<h1>EDGEMETRIX V300 — Verified Premier League Slate</h1><p>Select Match Date:</p><div>"
    for dt in available_dates:
        html += f'<a class="btn" href="/?date={dt}">{dt}</a>'
    html += f"</div><h2 style='margin-top:20px;'>Fixtures for {d}</h2>"

    for f in slate:
        html += f'''<div class="card">
            <strong>{f["home"]} vs {f["away"]}</strong> ({f["league"]})<br>
            📅 Date: <span class="mono">{f["date"]}</span> | ⏰ Time: {f["time"]} | Scope: {f["region"]}
        </div>'''
    html += "</body></html>"
    return render_template_string(html)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
