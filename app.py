from flask import Flask, render_template_string, request
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
                "time": "20:00 GMT (Live)", "banker": False, "xg_home": 1.50, "xg_away": 1.10, 
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
        ],
        "2026-11-28": [
            {
                "id": 205, "date": "2026-11-28", "region": "Premier League", 
                "home": "Leeds United", "away": "Coventry City", "league": "Premier League (England)", 
                "time": "15:00 GMT", "banker": True, "xg_home": 1.80, "xg_away": 1.05, 
                "markets": [{"name": "Leeds United Win", "odds": 1.68, "prob": 0.67}]
            }
        ]
    }

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>EDGEMETRIX V300 Quantitative Engine</title>
    <style>
        body { background: #07090e; color: #f1f5f9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 25px; }
        .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1e293b; padding-bottom: 15px; margin-bottom: 20px; }
        h1 { font-size: 24px; color: #38bdf8; margin: 0; letter-spacing: 0.5px; }
        .nav-tabs { display: flex; gap: 8px; margin-bottom: 25px; border-bottom: 1px solid #1e293b; padding-bottom: 12px; flex-wrap: wrap; }
        .tab-btn { background: #1e293b; color: #94a3b8; padding: 9px 16px; text-decoration: none; border-radius: 6px; font-size: 13px; font-weight: 600; border: 1px solid #334155; transition: all 0.2s; }
        .tab-btn.active, .tab-btn:hover { background: #0284c7; color: white; border-color: #0284c7; }
        .date-bar { display: flex; gap: 8px; margin-bottom: 25px; align-items: center; flex-wrap: wrap; }
        .date-btn { background: #0f172a; color: #cbd5e1; padding: 7px 14px; text-decoration: none; border-radius: 6px; font-size: 13px; border: 1px solid #334155; font-weight: 500; }
        .date-btn.active { background: #334155; color: #38bdf8; border-color: #38bdf8; }
        .card { background: #111827; border: 1px solid #1f2937; border-radius: 10px; padding: 20px; margin-bottom: 15px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
        .match-header { display: flex; justify-content: space-between; font-weight: bold; font-size: 18px; margin-bottom: 8px; color: #fff; }
        .badge { background: #1e3a8a; color: #93c5fd; font-size: 11px; padding: 3px 10px; border-radius: 4px; font-weight: 600; }
        .metrics { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 15px; background: #030712; padding: 12px; border-radius: 8px; font-size: 13px; border: 1px solid #1e293b; }
        .metric-box { color: #94a3b8; }
        .metric-val { color: #38bdf8; font-weight: bold; }
        h2 { color: #f8fafc; font-size: 18px; margin-top: 0; margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>EDGEMETRIX V300</h1>
        <span style="color: #64748b; font-size: 13px;">Engine Status: Online | Mode: Verified Premier League</span>
    </div>

    <!-- 6 Navigation Tabs -->
    <div class="nav-tabs">
        <a class="tab-btn {% if tab == 'slate' or not tab %}active{% endif %}" href="/?date={{ d }}&tab=slate">Match Slate</a>
        <a class="tab-btn {% if tab == 'predictions' %}active{% endif %}" href="/?date={{ d }}&tab=predictions">Predictions & xG</a>
        <a class="tab-btn {% if tab == 'markets' %}active{% endif %}" href="/?date={{ d }}&tab=markets">Value Markets</a>
        <a class="tab-btn {% if tab == 'banker' %}active{% endif %}" href="/?date={{ d }}&tab=banker">Banker Builder</a>
        <a class="tab-btn {% if tab == 'tactical' %}active{% endif %}" href="/?date={{ d }}&tab=tactical">Tactical Health</a>
        <a class="tab-btn {% if tab == 'clv' %}active{% endif %}" href="/?date={{ d }}&tab=clv">CLV Audit</a>
    </div>

    <!-- Date Bar -->
    <div class="date-bar">
        <span style="font-size:13px; color:#94a3b8; font-weight:500; margin-right:5px;">Match Date:</span>
        {% for dt in dates %}
            <a class="date-btn {% if dt == d %}active{% endif %}" href="/?date={{ dt }}&tab={{ tab }}">{{ dt }}</a>
        {% endfor %}
    </div>

    <!-- Dynamic Content per Tab -->
    {% if tab == 'slate' or tab == 'predictions' or tab == 'markets' or not tab %}
        <h2>Matchday Slate & Quantitative Models ({{ d }})</h2>
        {% if slate %}
            {% for f in slate %}
                <div class="card">
                    <div class="match-header">
                        <span>{{ f.home }} vs {{ f.away }}</span>
                        <span class="badge">{{ f.league }}</span>
                    </div>
                    <div style="font-size: 13px; color: #94a3b8; margin-bottom: 4px;">
                        📅 Date: <span style="color: #38bdf8; font-family: monospace;">{{ f.date }}</span> | ⏰ Time: {{ f.time }} | Venue: {{ f.region }}
                    </div>
                    <div class="metrics">
                        <div class="metric-box">Home Expected Goals (xG): <span class="metric-val">{{ f.xg_home }}</span></div>
                        <div class="metric-box">Away Expected Goals (xG): <span class="metric-val">{{ f.xg_away }}</span></div>
                        <div class="metric-box">Primary Market: <span class="metric-val">{% if f.markets %}{{ f.markets[0].name }} (@{{ f.markets[0].odds }}){% else %}N/A{% endif %}</span></div>
                    </div>
                </div>
            {% endfor %}
        {% else %}
            <div class="card"><p style="color: #94a3b8; margin: 0;">No fixtures available for this date.</p></div>
        {% endif %}
    {% elif tab == 'banker' %}
        <h2>Banker Accumulator Builder</h2>
        <div class="card"><p style="color: #94a3b8; margin: 0;">Configuring high-probability accumulator legs and double-chance safety buffers based on verified Premier League confluence parameters.</p></div>
    {% elif tab == 'tactical' %}
        <h2>Tactical Health Module</h2>
        <div class="card"><p style="color: #94a3b8; margin: 0;">Evaluating squad fatigue indices, tactical formations, and pressing intensity vectors across top-flight fixtures.</p></div>
    {% elif tab == 'clv' %}
        <h2>Closing Line Value (CLV) Audit</h2>
        <div class="card"><p style="color: #94a3b8; margin: 0;">Tracking market steam, opening vs. closing price differentials, and beat rates across active model bets.</p></div>
    {% endif %}
</body>
</html>
"""

@app.route("/")
def index():
    db = get_engine_data()
    dates = sorted(db.keys())
    d = request.args.get("date", dates[0])
    if d not in db:
        d = dates[0]
    tab = request.args.get("tab", "slate")
    slate = db.get(d, [])
    return render_template_string(TEMPLATE, dates=dates, d=d, tab=tab, slate=slate)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
