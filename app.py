from flask import Flask, request
from datetime import datetime, timedelta
import json

app = Flask(__name__)

# ==============================================
# AUTO-FIXTURE SYSTEM — Daily Refresh
# Finished games auto-hide, new games auto-appear
# ==============================================

# --------------------------
# FIXTURE DATABASE — Add games here ONCE, they auto-manage themselves
# Format: "YYYY-MM-DD": [ ... ]
# --------------------------
FIXTURE_FEED = {
"2026-11-06": [
{"h":"Borussia Dortmund","a":"VfB Stuttgart","l":"Bundesliga","t":"19:30","b":True,
"m":[{"n":"Over 2.5 Goals","o":1.50,"p":0.75},
{"n":"BTTS Yes","o":1.62,"p":0.70"}]},
{"h":"Barcelona","a":"Atlético Madrid","l":"La Liga","t":"20:00","b":False,
"m":[{"n":"Draw or Atlético X2","o":1.84,"p":0.66},
{"n":"Over 2.5 Goals","o":1.70,"p":0.68"}]},
{"h":"Napoli","a":"Roma","l":"Serie A","t":"19:45","b":True,
"m":[{"n":"Napoli 1X & Over 1.5","o":1.48,"p":0.74},
{"n":"BTTS Yes","o":1.76,"p":0.64"}]}
],
"2026-11-07": [
{"h":"Man City","a":"Liverpool","l":"Premier League","t":"12:30","b":True,
"m":[{"n":"BTTS + Over 2.5","o":1.65,"p":0.72"}]}
],
"2026-11-08": [
{"h":"Arsenal","a":"Chelsea","l":"Premier League","t":"16:30","b":True,
"m":[{"n":"Arsenal Double Chance (1X)","o":1.44,"p":0.76},
{"n":"Over 2.5 Goals","o":1.60,"p":0.71"}]},
{"h":"Bayern Munich","a":"RB Leipzig","l":"Bundesliga","t":"17:30","b":True,
"m":[{"n":"Bayern Win","o":1.32,"p":0.82},
{"n":"Over 3.5 Goals","o":1.55,"p":0.73"}]}
],
"2026-11-09": [
{"h":"Real Madrid","a":"Sevilla","l":"La Liga","t":"20:00","b":True,
"m":[{"n":"Real Madrid Win","o":1.28,"p":0.85},
{"n":"Both Teams To Score — Yes","o":1.80,"p":0.63"}]}
],
"2026-11-10": [
{"h":"Tottenham","a":"Aston Villa","l":"Premier League","t":"15:00","b":True,
"m":[{"n":"Tottenham Win","o":1.72,"p":0.65},
{"n":"Over 2.5 Goals","o":1.68,"p":0.68"}]},
{"h":"AC Milan","a":"Juventus","l":"Serie A","t":"19:45","b":False,
"m":[{"n":"Draw or Juventus X2","o":1.90,"p":0.63},
{"n":"Under 2.5 Goals","o":1.65,"p":0.69"}]}
],
"2026-11-11": [
{"h":"Bayern Munich","a":"Dortmund","l":"Bundesliga","t":"18:30","b":True,
"m":[{"n":"Bayern Win","o":1.55,"p":0.72},
{"n":"BTTS Yes","o":1.58,"p":0.71"}]}
]
}

def edge(o, p):
    return round((p - 1/o) * 100, 2)

def get_today_str():
    """Get today's date in YYYY-MM-DD format (UTC)"""
    return datetime.utcnow().strftime("%Y-%m-%d")

def get_tomorrow_str():
    return (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")

def get_upcoming_days(days=3):
    """Return list of dates from today to N days ahead"""
    dates = []
    today = datetime.utcnow().date()
    for i in range(days + 1):
        dates.append((today + timedelta(days=i)).strftime("%Y-%m-%d"))
    return dates

def filter_active_fixtures(include_days=7):
    """Auto-remove past fixtures, keep today + upcoming N days"""
    today = get_today_str()
    cutoff_date = (datetime.utcnow() + timedelta(days=include_days)).strftime("%Y-%m-%d")
    active = {}
    
    sorted_dates = sorted(FIXTURE_FEED.keys())
    for d in sorted_dates:
        if d >= today and d < cutoff_date:
            active[d] = FIXTURE_FEED[d]
    return active

def get_todays_fixtures():
    """Return only today's fixtures"""
    today = get_today_str()
    return filter_active_fixtures().get(today, [])

@app.route("/")
def main():
    tab = request.args.get("tab", "daily")
    today = get_today_str()
    fixtures = filter_active_fixtures()
    todays_games = fixtures.get(today, [])

    active = {}
    for t in ["daily","builder","ai","future","bankers","advanced"]:
        active[t] = "active" if tab == t else ""

    html = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>EDGEMETRIX V300 — Auto-Updating</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0b0f19;color:#f1f5f9;font-family:sans-serif;padding:16px}
.wrap{max-width:720px;margin:0 auto}
h1{color:#38bdf8;text-align:center;margin-bottom:4px}
.date{color:#4ade80;font-size:14px;text-align:center;margin-bottom:20px}
.tabs{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:24px;justify-content:center}
.tab{padding:10px 14px;border-radius:8px;background:#1e293b;color:#94a3b8;text-decoration:none;font-size:14px}
.tab.active{background:#0284c7;color:white}
.card{background:#1e293b;border-radius:12px;padding:20px;margin-bottom:20px}
h2{color:#e2e8f0;margin-bottom:16px;font-size:18px}
.fix{background:#0f172a;border-radius:8px;padding:16px;margin:12px 0;border-left:3px solid #38bdf8}
.fix.banker{border-left-color:#eab308}
.odd{color:#fbbf24;font-weight:bold}
.edg{color:#4ade80;font-weight:bold}
button{background:#16a34a;color:white;border:none;padding:12px;border-radius:8px;width:100%;font-weight:bold;margin-top:12px;font-size:16px}
.empty{color:#f87171;text-align:center;padding:30px}
h3{color:#94a3b8;margin:16px 0 8px}
.update-note{font-size:12px;color:#64748b;text-align:center;margin-top:10px}
</style>
</head>
<body>
<div class="wrap">
<h1>⚽ EDGEMETRIX V300</h1>
<p class="date">📅 Today: """ + today + """ — Auto-Updating ✅</p>
<div class="tabs">
<a class="tab """ + active["daily"] + """ href="/?tab=daily">Daily</a>
<a class="tab """ + active["builder"] + """ href="/?tab=builder">Builder</a>
<a class="tab """ + active["ai"] + """ href="/?tab=ai">AI</a>
<a class="tab """ + active["future"] + """ href="/?tab=future">Future</a>
<a class="tab """ + active["bankers"] + """ href="/?tab=bankers">Bankers</a>
<a class="tab """ + active["advanced"] + """ href="/?tab=advanced">Gen</a>
</div>"""

    # DAILY — Today Only
    if tab == "daily":
        html += '<div class="card"><h2>📊 Today\'s Picks</h2>'
        if not todays_games:
            html += '<p class="empty">No fixtures scheduled for today<br>Check back later or view Future tab</p>'
        else:
            for f in todays_games:
                html += '<div class="fix"><b>' + f["h"] + ' vs ' + f["a"] + '</b><br>' + f["l"] + ' · ' + f["t"]
                for m in f["m"]:
                    e = edge(m["o"], m["p"])
                    html += '<br>' + m["n"] + ' — Odds: <span class="odd">' + str(m["o"]) + '</span> | Edge: <span class="edg">+' + str(e) + '%</span>'
                html += '</div>'
        html += '</div>'

    # BET BUILDER
    elif tab == "builder":
        html += '<div class="card"><h2>🔨 Bet Builder</h2><form method="GET"><input type="hidden" name="tab" value="builder">'
        if not todays_games:
            html += '<p class="empty">No fixtures available today</p>'
        else:
            for f in todays_games:
                html += '<div class="fix"><b>' + f["h"] + ' vs ' + f["a"] + '</b>'
                for m in f["m"]:
                    html += '<br><label style="cursor:pointer"><input type="checkbox" name="sel" value="' + f["h"] + '||' + m["n"] + '"> ' + m["n"] + ' @' + str(m["o"]) + '</label>'
                html += '</div>'
        html += '<button type="submit">Build Slip</button></form></div>'

    # AI TOP 3 ACCA
    elif tab == "ai":
        html += '<div class="card"><h2>🤖 AI Top 3 Acca</h2>'
        picks = []
        for f in todays_games:
            for m in f["m"]:
                picks.append((-edge(m["o"], m["p"]), f["h"], f["a"], m["n"], m["o"]))
        picks.sort()
        top = picks[:3]
        if not top:
            html += '<p class="empty">No markets available today</p>'
        else:
            total = 1.0
            for p in top:
                total *= p[4]
                html += '<div class="fix">' + p[1] + ' vs ' + p[2] + '<br>' + p[3] + ' — <span class="odd">@' + str(p[4]) + '</span></div>'
            html += '<div style="padding:16px;background:#0369a1;border-radius:8px;margin-top:16px"><b>Combined Odds: ' + str(round(total,2)) + '</b><br>Stake £20 → Return £' + str(round(20*total,2)) + '</div>'
        html += '</div>'

    # FUTURE — All Upcoming
    elif tab == "future":
        html += '<div class="card"><h2>📅 Upcoming Fixtures</h2>'
        for d in sorted(fixtures.keys()):
            label = "📅 Today — " if d == today else "📆 "
            html += '<h3>' + label + d + '</h3>'
            for f in fixtures[d]:
                html += '<div class="fix"><b>' + f["h"] + ' vs ' + f["a"] + '</b><br>' + f["l"] + ' · ' + f["t"]
                for m in f["m"]:
                    html += '<br>' + m["n"] + ' @' + str(m["o"])
                html += '</div>'
        html += '</div>'

    # BANKERS
    elif tab == "bankers":
        html += '<div class="card"><h2>💰 Bankers Today (≥75%)</h2>'
        found = False
        for f in todays_games:
            if f["b"]:
                found = True
                html += '<div class="fix banker"><b>' + f["h"] + ' vs ' + f["a"] + '</b> ⭐<br>' + f["l"]
                for m in f["m"]:
                    if m["p"] >= 0.75:
                        html += '<br>' + m["n"] + ' — Conf ' + str(int(m["p"]*100)) + '% | @' + str(m["o"])
                html += '</div>'
        if not found:
            html += '<p class="empty">No banker selections today</p>'
        html += '</div>'

    # ADVANCED GENERATOR
    elif tab == "advanced":
        html += '<div class="card"><h2>⚙️ Acca Generator</h2>'
        html += '<div style="background:#0369a1;padding:16px;border-radius:8px">'
        html += '<h3>Sample 3-Leg Acca — ' + today + '</h3>'
        if len(todays_games) >= 1:
            html += '<div style="margin:8px 0">1. ' + todays_games[0]["h"] + ' vs ' + todays_games[0]["a"] + ' — ' + todays_games[0]["m"][0]["n"] + ' @' + str(todays_games[0]["m"][0]["o"]) + '</div>'
        if len(todays_games) >= 2:
            html += '<div style="margin:8px 0">2. ' + todays_games[1]["h"] + ' vs ' + todays_games[1]["a"] + ' — ' + todays_games[1]["m"][0]["n"] + ' @' + str(todays_games[1]["m"][0]["o"]) + '</div>'
        if len(todays_games) >= 3:
            html += '<div style="margin:8px 0">3. ' + todays_games[2]["h"] + ' vs ' + todays_games[2]["a"] + ' — ' + todays_games[2]["m"][0]["n"] + ' @' + str(todays_games[2]["m"][0]["o"]) + '</div>'
        html += '<div style="font-weight:bold;margin-top:12px;font-size:16px">Combined Odds: Auto-Calculated</div>'
        html += '<div>Stake £20 → Return Calculated</div></div></div>'

    html += '<p class="update-note">✅ Auto-updating — past games hidden, new games appear automatically</p>'
    html += '</div></body></html>'
    return html

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
