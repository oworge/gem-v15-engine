from flask import Flask, request
from datetime import datetime
import math
import os
import requests

app = Flask(__name__)

def fetch_live_fixtures():
    api_key = os.environ.get("FOOTBALL_API_KEY", "")
    today = datetime.utcnow().strftime("%Y-%m-%d")
    
    if not api_key:
        print("⚠️ No API key — using sample data")
        return get_sample_fixtures()
    
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "api-football-v1.p.rapidapi.com"
    }
    
    try:
        url = f"https://api-football-v1.p.rapidapi.com/v3/fixtures?date={today}"
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"⚠️ API status: {response.status_code}")
            return get_sample_fixtures()
        
        data = response.json()
        fixtures = data.get("response", [])
        
        if not fixtures:
            print("⚠️ No fixtures today")
            return get_sample_fixtures()
        
        matches = []
        for fx in fixtures[:12]:
            home = fx["teams"]["home"]["name"]
            away = fx["teams"]["away"]["name"]
            league = fx["league"]["name"] + " (" + fx["league"]["country"] + ")"
            kickoff = datetime.fromisoformat(fx["fixture"]["date"].replace("Z", "+00:00"))
            gmt_time = kickoff.strftime("%H:%M GMT")
            
            matches.append({
                "id": f"fx-{fx['fixture']['id']}",
                "home": home,
                "away": away,
                "league": league,
                "time": gmt_time,
                "confidence": 75,
                "markets": [
                    {"name": f"{home} Win", "odds": 0.0, "prob": 0.50, "ev": 0.0},
                    {"name": "Over 2.5 Goals", "odds": 0.0, "prob": 0.50, "ev": 0.0},
                    {"name": "BTTS — Yes", "odds": 0.0, "prob": 0.50, "ev": 0.0}
                ],
                "btts_prob": 0.50,
                "btts_odds": 0.0,
                "clv_score": 75,
                "tactical_rating": "📊 Live Data",
                "correct_score": ["1-1", "2-1", "1-2"],
                "tactical_notes": "🔄 Live fixtures loaded"
            })
        
        print(f"✅ Loaded {len(matches)} fixtures")
        return matches
        
    except Exception as e:
        print(f"⚠️ API error: {e}")
        return get_sample_fixtures()


def get_sample_fixtures():
    return [
        {
            "id":"demo-1","home":"Arsenal","away":"Nottingham Forest",
            "league":"Premier League (England)","time":"19:45 GMT","confidence":74,
            "markets":[
                {"name":"Arsenal Win","odds":1.44,"prob":0.74,"ev":8.7},
                {"name":"Over 2.5 Goals","odds":1.63,"prob":0.67,"ev":6.0},
                {"name":"BTTS — Yes","odds":1.75,"prob":0.62,"ev":8.5}
            ],
            "btts_prob":0.62,"btts_odds":1.75,"clv_score":88,
            "tactical_rating":"⭐ Demo Data",
            "correct_score":["2-0","2-1","1-1"],
            "tactical_notes":"📡 Add FOOTBALL_API_KEY for live fixtures"
        },
        {
            "id":"demo-2","home":"Bayern Munich","away":"Eintracht Frankfurt",
            "league":"Bundesliga (Germany)","time":"19:30 GMT","confidence":83,
            "markets":[
                {"name":"Bayern Win","odds":1.36,"prob":0.83,"ev":9.2},
                {"name":"Over 3.5 Goals","odds":2.05,"prob":0.61,"ev":12.5},
                {"name":"BTTS — Yes","odds":1.68,"prob":0.65,"ev":8.6}
            ],
            "btts_prob":0.65,"btts_odds":1.68,"clv_score":94,
            "tactical_rating":"⭐ Demo Data",
            "correct_score":["3-1","4-1","3-0"],
            "tactical_notes":"📡 Add FOOTBALL_API_KEY for live fixtures"
        }
    ]


MATCHES = fetch_live_fixtures()


@app.route("/")
def dashboard():
    tab = request.args.get("tab", "daily")
    def active(t): return "active" if tab == t else ""
    
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>EDGEMETRIX — GLOBAL</title>
<style>
:root{--bg:#0f172a;--card:#1e293b;--border:rgba(148,163,184,.12);--accent:#38bdf8;--gold:#fbbf24;--green:#22c55e;--t1:#f1f5f9;--t2:#94a3b8;--t3:#64748b}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:system-ui,sans-serif;background:var(--bg);color:var(--t1);padding:24px 16px}
.g{max-width:1200px;margin:0 auto}
.h{display:flex;justify-content:space-between;flex-wrap:wrap;gap:15px;margin-bottom:25px}
.h1{font-size:24px;font-weight:800;color:var(--gold)}
.dt{background:rgba(34,197,94,.1);color:var(--green);padding:8px 16px;border-radius:20px;font-size:13px}
.tabs{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:25px;border-bottom:1px solid var(--border);padding-bottom:8px}
.b{padding:10px 16px;background:0;border:0;color:var(--t2);font-size:14px;font-weight:600;cursor:pointer;border-radius:8px 8px 0 0;text-decoration:none}
.b.active{background:var(--gold);color:#78350f;font-weight:700}
.c{background:var(--card);border-radius:12px;padding:24px;margin-bottom:15px;border:1px solid var(--border)}
.ct{font-size:18px;font-weight:700;color:var(--accent);margin-bottom:15px}
.mc{background:linear-gradient(135deg,rgba(30,41,59,.6),rgba(15,23,42,.9));border-radius:10px;padding:20px;margin-bottom:12px;border:1px solid var(--border)}
.tt{font-size:16px;font-weight:600;margin-bottom:6px}
.mm{color:var(--t3);font-size:13px;margin-bottom:10px}
.mr{display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:10px;padding:8px 0;border-bottom:1px solid rgba(255,255,255,.05)}
.n{font-weight:500;font-size:14px}
.o{color:var(--gold);font-weight:600;text-align:right;font-family:monospace}
.su{margin-top:15px;padding:12px;background:rgba(56,189,248,.1);border-radius:8px;color:var(--accent)}
.cl{color:var(--accent);text-decoration:none;margin-top:10px;display:inline-block;font-size:14px}
.btn{background:var(--gold);color:#78350f;border:0;padding:10px 20px;border-radius:8px;font-weight:700;cursor:pointer;font-size:14px;margin-top:10px}
.empty{text-align:center;color:var(--t3);padding:40px}
</style>
</head>
<body>
<div class="g">
<div class="h">
<div class="h1">⚽ EDGEMETRIX — GLOBAL</div>
<div class="dt">''' + datetime.utcnow().strftime("%A, %d %B %Y") + '''</div>
</div>
<div class="tabs">
<a href="?tab=daily" class="b ''' + active("daily") + '''">🔥 Daily Picks</a>
<a href="?tab=btts" class="b ''' + active("btts") + '''">✅ BTTS</a>
<a href="?tab=acca" class="b ''' + active("acca") + '''">🎯 Acca Generator</a>
<a href="?tab=builder" class="b ''' + active("builder") + '''">🔨 Bet Builder</a>
<a href="?tab=clv" class="b ''' + active("clv") + '''">📊 True CLV</a>
<a href="?tab=score" class="b ''' + active("score") + '''">🔢 Correct Scores</a>
<a href="?tab=tactical" class="b ''' + active("tactical") + '''">🧠 Tactical Health</a>
</div>
'''
    
    if tab == "daily":
        html += '<div class="c"><div class="ct">🔥 Daily Picks — Top Value Selections</div>'
        for m in MATCHES:
            html += '<div class="mc"><div class="tt">' + m["home"] + ' vs ' + m["away"] + '</div><div class="mm">' + m["league"] + ' — ' + m["time"] + '</div>'
            for mk in m["markets"]:
                if mk["ev"] > 0:
                    html += '<div class="mr"><div class="n">' + mk["name"] + '</div><div class="o">' + str(mk["odds"]) + '</div><div class="o">' + str(round(mk["prob"]*100)) + '%</div><div class="o">+' + str(mk["ev"]) + '%</div></div>'
            html += '<div style="margin-top:8px;font-size:13px;color:var(--t3)">' + m["tactical_notes"] + '</div></div>'
        html += '</div>'
    
    elif tab == "btts":
        html += '<div class="c"><div class="ct">✅ Both Teams To Score</div>'
        for m in MATCHES:
            html += '<div class="mc"><div class="tt">' + m["home"] + ' vs ' + m["away"] + '</div>'
            html += '<div class="mr"><div class="n">BTTS — Yes</div><div class="o">' + str(m["btts_odds"]) + '</div><div class="o">' + str(round(m["btts_prob"]*100)) + '%</div><div class="o">' + m["tactical_rating"] + '</div></div></div>'
        html += '</div>'
    
    elif tab == "acca":
        html += '<div class="c"><div class="ct">🎯 Acca Generator — Top 3 Value</div>'
        ranked = []
        for m in MATCHES:
            for mk in m["markets"]:
                ranked.append((-mk["ev"], m["home"], m["away"], mk["name"], mk["odds"]))
        ranked.sort()
        top3 = ranked[:3] if len(ranked)>=3 else []
        if top3:
            total_odds = 1.0
            stake = 20
            html += '<div style="margin-bottom:15px">'
            for idx, pick in enumerate(top3, 1):
                total_odds *= pick[4]
                html += '<div class="mr"><div class="n">' + str(idx) + '. ' + pick[1] + ' vs ' + pick[2] + ' — ' + pick[3] + '</div><div class="o">' + str(pick[4]) + '</div></div>'
            returns = round(stake * total_odds, 2)
            html += '<div class="su"><strong>Combined Odds: ' + str(round(total_odds,2)) + '</strong><br>Stake £' + str(stake) + ' → Return £' + str(returns) + '</div></div>'
        else:
            html += '<div class="empty">Need 3+ fixtures for Acca</div>'
        html += '</div>'
    
    elif tab == "clv":
        html += '<div class="c"><div class="ct">📊 True CLV — Closing Line Value</div><span style="color:var(--t3);font-size:12px">Higher = Better Value</span>'
        for m in MATCHES:
            cl = m["clv_score"]
            st = "exc" if cl >=90 else ("good" if cl >=80 else "")
            html += '<div class="mc"><div style="display:flex;justify-content:space-between;align-items:center"><div class="tt">' + m["home"] + ' vs ' + m["away"] + '</div><span style="color:' + ("#22c55e" if cl>=90 else "#fbbf24" if cl>=80 else "#94a3b8") + ';font-weight:700">CLV ' + str(cl) + '%</span></div></div>'
        html += '</div>'
    
    elif tab == "score":
        html += '<div class="c"><div class="ct">🔢 Predicted Correct Scores</div>'
        for m in MATCHES:
            html += '<div class="mc"><div class="tt">' + m["home"] + ' vs ' + m["away"] + '</div><div class="mm">' + m["league"] + '</div>'
            html += '<div style="display:flex;gap:10px;margin-top:8px">'
            for s in m["correct_score"]:
                html += '<span style="background:rgba(56,189,248,.15);color:var(--accent);padding:6px 12px;border-radius:6px;font-weight:600">' + s + '</span>'
            html += '</div></div>'
        html += '</div>'
    
    elif tab == "tactical":
        html += '<div class="c"><div class="ct">🧠 Tactical Health & Analysis</div>'
        for m in MATCHES:
            html += '<div class="mc"><div class="tt">' + m["home"] + ' vs ' + m["away"] + '</div>'
            html += '<div style="margin-top:8px"><strong>Rating:</strong> ' + m["tactical_rating"] + '</div>'
            html += '<div style="margin-top:4px;color:var(--t3);font-size:14px">' + m["tactical_notes"] + '</div></div>'
        html += '</div>'
    
    else:
        html += '<div class="c"><div class="empty">Tab not recognized</div></div>'
    
    html += '</div></body></html>'
    return html


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
