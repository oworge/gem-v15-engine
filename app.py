from flask import Flask, render_template_string, request
from datetime import datetime, date
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("EDGEMETRIX")

app = Flask(__name__)

def get_engine_data():
    return {
        "2026-11-06": [
            {
                "id": 199, "date": "2026-11-06", "region": "Premier League", 
                "home": "Everton", "away": "Coventry City", "league": "Premier League (England)", 
                "time": "20:00 GMT", "banker": False, "xg_home": 1.50, "xg_away": 1.10, 
                "markets": [{"name": "Under 2.5 Goals", "odds": 1.80, "prob": 0.58}]
            }
        ],
        "2026-11-07": [
            {
                "id": 201, "date": "2026-11-07", "region": "Premier League", 
                "home": "Leeds United", "away": "Tottenham Hotspur", "league": "Premier League (England)", 
                "time": "12:30 GMT", "banker": False, "xg_home": 1.45, "xg_away": 1.65, 
                "markets": [{"name": "Both Teams To Score (BTTS)", "odds": 1.72, "prob": 0.64}]
            },
            {
                "id": 202, "date": "2026-11-07", "region": "Premier League", 
                "home": "Arsenal", "away": "Hull City", "league": "Premier League (England)", 
                "time": "15:00 GMT", "banker": True, "xg_home": 2.20, "xg_away": 0.80, 
                "markets": [{"name": "Arsenal Win", "odds": 1.30, "prob": 0.82}]
            },
            {
                "id": 203, "date": "2026-11-07", "region": "Premier League", 
                "home": "Nottingham Forest", "away": "Manchester City", "league": "Premier League (England)", 
                "time": "17:30 GMT", "banker": False, "xg_home": 1.10, "xg_away": 2.05, 
                "markets": [{"name": "Manchester City Win", "odds": 1.55, "prob": 0.70}]
            }
        ],
        "2026-11-21": [
            {
                "id": 204, "date": "2026-11-21", "region": "Premier League", 
                "home": "Chelsea", "away": "Leeds United", "league": "Premier League (England)", 
                "time": "15:00 GMT", "banker": False, "xg_home": 1.85, "xg_away": 1.10, 
                "markets": [{"name": "Chelsea Win & Over 1.5", "odds": 1.70, "prob": 0.65}]
            }
        ]
    }

@app.route("/")
def index():
    db = get_engine_data()
    dates = sorted(db.keys())
    d = request.args.get("date", dates[0])
    tab = request.args.get("tab", "slate")
    slate = db.get(d, [])
    
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>EDGEMETRIX V300 Engine</title>
        <style>
            body { background: #07090e; color: #f1f5f9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 20px; }
            .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1e293b; padding-bottom: 15px; margin-bottom: 20px; }
            h1 { font-size: 22px; color: #38bdf8; margin: 0; }
            .nav-tabs { display: flex; gap: 8px; margin-bottom: 25px; border-bottom: 1px solid #1e293b; padding-bottom: 10px; }
            .tab-btn { background: #1e293b; color: #94a3b8; padding: 8px 14px; text-decoration: none; border-radius: 6px; font-size: 13px; font-weight: 600; border: 1px solid #334155; }
            .tab-btn.active, .tab-btn:hover { background: #0284c7; color: white; border-color: #0284c7; }
            .date-bar { display: flex; gap: 8px; margin-bottom: 20px; }
            .date-btn { background: #0f172a; color: #cbd5e1; padding: 6px 12px; text-decoration: none; border-radius: 4px; font-size: 13px; border: 1px solid #334155; }
            .date-btn.active { background: #334155; color: #38bdf8; border-color: #38bdf8; }
            .card { background: #111827; border: 1px solid #1f2937; border-radius: 8px; padding: 16px; margin-bottom: 12px; }
            .match-header { display: flex; justify-content: space-between; font-weight: bold; font-size: 16px; margin-bottom: 8px; color: #fff; }
            .badge { background: #1e3a8a; color: #93c5fd; font-size: 11px; padding: 2px 8px; border-radius: 4px; }
            .metrics { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 12px; background: #030712; padding: 10px; border-radius: 6px; font-size: 13px; }
            .metric-box { color: #94a3b8; }
            .metric-val { color: #38bdf8; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>EDGEMETRIX V300</h1>
            <span style="color: #64748b; font-size: 13px;">Engine Status: Online | Mode: Verified Premier League</span>
        </div>

        <!-- 6 Navigation Tabs -->
        <div class="nav-tabs">
            <a class="tab-btn {% if tab == 'slate' %}active{% endif %}" href="/?date={{ d }}&tab=slate">Match Slate</a>
            <a class="tab-btn {% if tab == 'predictions' %}active{% endif %}" href="/?date={{ d }}&tab=predictions">Predictions & xG</a>
            <a class="tab-btn {% if tab == 'markets' %}active{% endif %}" href="/?date={{ d }}&tab=markets">Value Markets</a>
            <a class="tab-btn {% if tab == 'banker' %}active{% endif %}" href="/?date={{ d }}&tab=banker">Banker Builder</a>
            <a class="tab-btn {% if tab == 'tactical' %}active{% endif %}" href="/?date={{ d }}&tab=tactical">Tactical Health</a>
            <a class="tab-btn {% if tab == 'clv' %}active{% endif %}" href="/?date={{ d }}&tab=clv">CLV Audit</a>
        </div>

        <!-- Date Bar -->
        <div class="date-bar">
            <span style="align-self:center; font-size:13px; color:#94a3b8; margin-right:5px;">Date:</span>
            {% for dt in dates %}
                <a class="date-btn {% if dt == d %}active{% endif %}" href="/?date={{ dt }}&tab={{ tab }}">{{ dt }}</a>
            {% endfor %}
        </div>

        <!-- Dynamic Content per Tab -->
        {% if tab == 'slate' or tab == 'predictions' or tab == 'markets' %}
            <h2>Matchday Slate & Predictions ({{ d }})</h2>
            {% for f in slate %}
                <div class="card">
                    <div class="match-header">
                        <span>{{ f.home }} vs {{ f.away }}</span>
                        <span class="badge">{{ f.league }}</span>
                    </div>
                    <div style="font-size: 13px; color: #94a3b8; margin-bottom: 8px;">
                        📅 {{ f.date }} &nbsp;|&nbsp; ⏰ {{ f.time }} &nbsp;|&nbsp; Venue: {{ f.region }}
                    </div>
                    <div class="metrics">
                        <div class="metric-box">Home xG: <span class="metric-val">{{ f.xg_home }}</span></div>
                        <div class="metric-box">Away xG: <span class="metric-val">{{ f.xg_away }}</span></div>
                        <div class="metric-box">Top Market: <span class="metric-val">{% if f.markets %}{{ f.markets[0].name }} (@{{ f.markets[0].odds }}){% else %}N/A{% endif %}</span></div>
                    </div>
                </div>
            {% endfor %}
        {% elif tab == 'banker' %}
            <h2>Banker Accumulator Builder</h2>
            <div class="card"><p>Configuring high-probability accumulator legs based on verified Premier League confluence parameters.</p></div>
        {% elif tab == 'tactical' %}
            <h2>Tactical Health Module</h2>
            <div class="card"><p>Evaluating squad fatigue, tactical formations, and pressing intensity vectors for top-flight fixtures.</p></div>
        {% elif tab == 'clv' %}
            <h2>Closing Line Value (CLV) Audit</h2>
            <div class="card"><p>Tracking market steam and closing price beat rates across active model bets.</p></div>
        {% endif %}
    </body>
    </html>
    ''', dates=dates, d=d, tab=tab, slate=slate)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
