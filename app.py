# -*- coding: utf-8 -*-
from flask import Flask, request
from datetime import datetime

app = Flask(__name__)

# ===== FIXTURE DATA =====
FIXTURES = {
"2026-11-06": [
    {
        "home": "Borussia Dortmund",
        "away": "VfB Stuttgart",
        "league": "Bundesliga",
        "time": "19:30 GMT",
        "is_banker": True,
        "markets": [
            {"name": "Over 1.5 Goals & Dortmund 1X", "odds": 1.42, "prob": 0.77},
            {"name": "BTTS Yes", "odds": 1.72, "prob": 0.62},
            {"name": "Dortmund Win", "odds": 1.35, "prob": 0.78}
        ]
    },
    {
        "home": "Barcelona",
        "away": "Atletico Madrid",
        "league": "La Liga",
        "time": "20:00 GMT",
        "is_banker": False,
        "markets": [
            {"name": "Double Chance: Draw or Atletico X2", "odds": 1.50, "prob": 0.71},
            {"name": "Over 1.5 Goals", "odds": 1.30, "prob": 0.81}
        ]
    },
    {
        "home": "Napoli",
        "away": "Roma",
        "league": "Serie A",
        "time": "19:45 GMT",
        "is_banker": True,
        "markets": [
            {"name": "Napoli 1X & Over 1.5", "odds": 1.48, "prob": 0.74},
            {"name": "BTTS Yes", "odds": 1.76, "prob": 0.64}
        ]
    }
],
"2026-11-07": [
    {
        "home": "Man City",
        "away": "Liverpool",
        "league": "Premier League",
        "time": "12:30 GMT",
        "is_banker": True,
        "markets": [
            {"name": "BTTS + Over 2.5", "odds": 1.65, "prob": 0.72}
        ]
    }
],
"2026-11-08": [
    {
        "home": "Arsenal",
        "away": "Chelsea",
        "league": "Premier League",
        "time": "16:30 GMT",
        "is_banker": True,
        "markets": [
            {"name": "Arsenal Double Chance 1X", "odds": 1.44, "prob": 0.76},
            {"name": "Over 2.5 Goals", "odds": 1.60, "prob": 0.71}
        ]
    },
    {
        "home": "Bayern Munich",
        "away": "RB Leipzig",
        "league": "Bundesliga",
        "time": "17:30 GMT",
        "is_banker": True,
        "markets": [
            {"name": "Bayern Win", "odds": 1.32, "prob": 0.82},
            {"name": "Over 3.5 Goals", "odds": 1.55, "prob": 0.73}
        ]
    }
]
}

def edge(o, p):
    return round((p - 1 / o) * 100, 2)

today = datetime.utcnow().strftime("%Y-%m-%d")
todays_matches = FIXTURES.get(today, [])

@app.route("/")
def dashboard():
    tab = request.args.get("tab", "daily")
    
    # Active tab highlighting
    def active(t):
        return "active" if tab == t else ""
    
    # Start HTML
    html = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>EDGEMETRIX V300</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0b0f19;color:#f1f5f9;font-family:sans-serif;padding:16px}
.wrap{max-width:900px;margin:0 auto}
h1{color:#38bdf8;text-align:center;margin-bottom:4px;font-size:24px}
.sub{color:#94a3b8;text-align:center;margin-bottom:8px;font-size:14px}
.date{color:#4ade80;text-align:center;margin-bottom:20px;font-weight:bold}
.tabs{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:24px;justify-content:center}
.tab{padding:10px 14px;border-radius:8px;background:#1e293b;color:#94a3b8;border:none;cursor:pointer;font-size:14px}
.tab.active{background:#0284c7;color:white}
.card{background:#1e293b;border-radius:12px;padding:20px;margin-bottom:20px}
h2{color:#e2e8f0;margin-bottom:16px;font-size:18px;border-bottom:1px solid #334155;padding-bottom:8px}
.match{background:#0f172a;border-radius:8px;padding:16px;margin:12px 0;border-left:3px solid #38bdf8}
.match.banker{border-left-color:#eab308}
.odd{color:#fbbf24;font-weight:bold}
.edg{color:#4ade80;font-weight:bold}
.empty{color:#f87171;text-align:center;padding:30px}
h3{color:#94a3b8;margin:16px 0 8px}
button{background:#16a34a;color:white;border:none;padding:12px;border-radius:8px;width:100%;font-weight:bold;margin-top:12px;cursor:pointer}
label{display:block;margin:6px 0;cursor:pointer}
</style>
</head>
<body>
<div class="wrap">
<h1>EDGEMETRIX V300 DASHBOARD</h1>
<p class="sub">Quantitative Football Analytics Engine</p>
<p class="date">Today: """ + today + """</p>
<div class="tabs">
<button class="tab """ + active("daily") + """ onclick="location.href='?tab=daily'">Daily Picks</button>
<button class="tab """ + active("builder") + """ onclick="location.href='?tab=builder'">Bet Builder</button>
<button class="tab """ + active("ai") + """ onclick="location.href='?tab=ai'">AI Acca Generator</button>
<button class="tab """ + active("future") + """ onclick="location.href='?tab=future'">Future (3-Day)</button>
<button class="tab """ + active("bankers") + """ onclick="location.href='?tab=bankers'">Bankers</button>
<button class="tab """ + active("advanced") + """ onclick="location.href='?tab=advanced'">Acca Generator</button>
</div>"""

    # ========= DAILY PICKS =========
    if tab == "daily":
        html += '<div class="card"><h2>📊 Daily Picks</h2>'
        if not todays_matches:
            html += '<p class="empty">No fixtures today</p>'
        else:
            for m in todays_matches:
                html += '<div class="match">'
                html += '<b>' + m["home"] + ' vs ' + m["away"] + '</b><br>'
                html += '<span style="color:#94a3b8">' + m["league"] + ' — ' + m["time"] + '</span>'
                for mk in m["markets"]:
                    e = edge(mk["odds"], mk["prob"])
                    html += '<br><strong>' + mk["name"] + '</strong> @<span class="odd">' + str(mk["odds"]) + '</span> | Edge +<span class="edg">' + str(e) + '%</span>'
                html += '</div>'
        html += '</div>'

    # ========= BET BUILDER =========
    elif tab == "builder":
        sel = request.args.getlist("sel")
        html += '<div class="card"><h2>🔨 Bet Builder</h2>'
        if sel:
            total = 1.0
            html += '<h3>Your Selection</h3>'
            for s in sel:
                parts = s.split("||")
                if len(parts) == 3:
                    total *= float(parts[2])
                    html += '<div class="match">' + parts[0] + '<br>' + parts[1] + ' @<span class="odd">' + parts[2] + '</span></div>'
            html += '<div style="background:#0369a1;padding:16px;border-radius:8px;margin-top:16px"><b>Combined: ' + str(round(total,2)) + '</b><br>Stake £20 → £' + str(round(20*total,2)) + '</div>'
            html += '<p style="margin-top:12px"><a href="?tab=builder" style="color:#94a3b8">← Clear</a></p>'
        else:
            html += '<form method="GET"><input type="hidden" name="tab" value="builder">'
            if not todays_matches:
                html += '<p class="empty">No fixtures today</p>'
            else:
                for m in todays_matches:
                    html += '<div class="match"><b>' + m["home"] + ' vs ' + m["away"] + '</b><br><small style="color:#94a3b8">' + m["league"] + '</small>'
                    for mk in m["markets"]:
                        val = m["home"] + "||" + mk["name"] + "||" + str(mk["odds"])
                        html += '<br><label><input type="checkbox" name="sel" value="' + val + '"> ' + mk["name"] + ' @' + str(mk["odds"]) + '</label>'
                    html += '</div>'
            html += '<button type="submit">Build Acca</button></form>'
        html += '</div>'

    # ========= AI ACCA =========
    elif tab == "ai":
        html += '<div class="card"><h2>🤖 AI Acca Generator</h2>'
        if not todays_matches:
            html += '<p class="empty">No fixtures today</p>'
        else:
            ranked = []
            for m in todays_matches:
                for mk in m["markets"]:
                    ranked.append((-edge(mk["odds"], mk["prob"]), m["home"], m["away"], mk["name"], mk["odds"]))
            ranked.sort()
            top3 = ranked[:3]
            if top3:
                combined = 1.0
                html += '<p style="margin-bottom:16px">Top 3 by Edge:</p>'
                for idx, pick in enumerate(top3, 1):
                    combined *= pick[4]
                    html += '<div class="match">' + str(idx) + '. <b>' + pick[1] + ' vs ' + pick[2] + '</b><br>' + pick[3] + ' @<span class="odd">' + str(pick[4]) + '</span></div>'
                html += '<div style="background:#0369a1;padding:16px;border-radius:8px;margin-top:16px"><b>Combined: ' + str(round(combined,2)) + '</b><br>Stake £20 → £' + str(round(20*combined,2)) + '</div>'
            else:
                html += '<p class="empty">No selections</p>'
        html += '</div>'

    # ========= FUTURE =========
    elif tab == "future":
        html += '<div class="card"><h2>📅 Future (3-Day)</h2>'
        found = False
        for d in sorted(FIXTURES.keys()):
            label = "📅 Today — " + d if d == today else "📅 " + d
            html += '<h3>' + label + '</h3>'
            for m in FIXTURES[d]:
                found = True
                html += '<div class="match"><b>' + m["home"] + ' vs ' + m["away"] + '</b><br>' + m["league"] + ' — ' + m["time"]
                for mk in m["markets"]:
                    html += '<br>' + mk["name"] + ' @' + str(mk["odds"])
                html += '</div>'
        if not found:
            html += '<p class="empty">No fixtures found</p>'
        html += '</div>'

    # ========= BANKERS =========
    elif tab == "bankers":
        html += '<div class="card"><h2>⭐ Bankers Daily</h2>'
        found = False
        for m in todays_matches:
            if m.get("is_banker"):
                found = True
                html += '<div class="match banker"><b>⭐ ' + m["home"] + ' vs ' + m["away"] + '</b><br>' + m["league"] + ' — ' + m["time"]
                for mk in m["markets"]:
                    if mk["prob"] >= 0.75:
                        html += '<br><strong>' + mk["name"] + '</strong> @' + str(mk["odds"]) + ' — Conf ' + str(int(mk["prob"]*100)) + '%'
                html += '</div>'
        if not found:
            html += '<p class="empty">No bankers today</p>'
        html += '</div>'

    # ========= ADVANCED =========
    elif tab == "advanced":
        html += '<div class="card"><h2>🎯 Acca Generator</h2>'
        if len(todays_matches) >= 3:
            combined = 1.0
            html += '<p style="margin-bottom:16px">Today\'s 3-Leg Acca:</p>'
            for idx, m in enumerate(todays_matches[:3], 1):
                pick = m["markets"][0]
                combined *= pick["odds"]
                html += '<div class="match">' + str(idx) + '. <b>' + m["home"] + ' vs ' + m["away"] + '</b><br>' + pick["name"] + ' @' + str(pick["odds"]) + '</div>'
            html += '<div style="background:#0369a1;padding:16px;border-radius:8px;margin-top:16px"><b>Combined: ' + str(round(combined,2)) + '</b><br>Stake £20 → £' + str(round(20*combined,2)) + '</div>'
        else:
            html += '<p class="empty">Need 3+ fixtures for acca</p>'
        html += '</div>'

    # Fallback
    else:
        html += '<div class="card"><p class="empty">Tab not found</p></div>'

    html += '</div></body></html>'
    return html

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
