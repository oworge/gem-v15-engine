# -*- coding: utf-8 -*-
from flask import Flask, request
from datetime import datetime

app = Flask(__name__)

FIXTURE_FEED = {
"2026-11-06": [
{"h":"Borussia Dortmund","a":"VfB Stuttgart","l":"Bundesliga","t":"19:30 GMT","b":True,
"m":[{"n":"Over 1.5 Goals & Dortmund 1X","o":1.42,"p":0.77},
{"n":"BTTS Yes","o":1.72,"p":0.62},
{"n":"Dortmund Win","o":1.35,"p":0.78"}]},
{"h":"Barcelona","a":"Atletico Madrid","l":"La Liga","t":"20:00 GMT","b":False,
"m":[{"n":"Double Chance: Draw or Atletico X2","o":1.50,"p":0.71},
{"n":"Over 1.5 Goals","o":1.30,"p":0.81"}]},
{"h":"Napoli","a":"Roma","l":"Serie A","t":"19:45 GMT","b":True,
"m":[{"n":"Napoli 1X & Over 1.5","o":1.48,"p":0.74},
{"n":"BTTS Yes","o":1.76,"p":0.64"}]}
],
"2026-11-07": [
{"h":"Man City","a":"Liverpool","l":"Premier League","t":"12:30 GMT","b":True,
"m":[{"n":"BTTS + Over 2.5","o":1.65,"p":0.72"}]}
],
"2026-11-08": [
{"h":"Arsenal","a":"Chelsea","l":"Premier League","t":"16:30 GMT","b":True,
"m":[{"n":"Arsenal Double Chance 1X","o":1.44,"p":0.76},
{"n":"Over 2.5 Goals","o":1.60,"p":0.71"}]},
{"h":"Bayern Munich","a":"RB Leipzig","l":"Bundesliga","t":"17:30 GMT","b":True,
"m":[{"n":"Bayern Win","o":1.32,"p":0.82},
{"n":"Over 3.5 Goals","o":1.55,"p":0.73"}]}
]
}

def edge(o, p):
    return round((p - 1 / o) * 100, 2)

def get_today_str():
    return datetime.utcnow().strftime("%Y-%m-%d")

def filter_active_fixtures(days=0):
    today = get_today_str()
    sorted_dates = sorted(FIXTURE_FEED.keys())
    result = {}
    for d in sorted_dates:
        if days == 0:
            if d >= today:
                result[d] = FIXTURE_FEED[d]
        else:
            if d >= today and d <= sorted_dates[min(sorted_dates.index(today)+days, len(sorted_dates)-1)]:
                result[d] = FIXTURE_FEED[d]
    return result

@app.route("/")
def main():
    tab = request.args.get("tab", "daily")
    today = get_today_str()
    fixtures = filter_active_fixtures()
    todays_games = fixtures.get(today, [])
    future_fixtures = filter_active_fixtures(days=2)

    active = {}
    for t in ["daily","builder","ai","future","bankers","advanced"]:
        active[t] = "active" if tab == t else ""

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
h1{color:#38bdf8;text-align:center;margin-bottom:4px;font-size:28px}
.subtitle{color:#94a3b8;font-size:14px;text-align:center;margin-bottom:12px}
.date{color:#4ade80;font-size:15px;text-align:center;margin-bottom:24px;font-weight:bold}
.tabs{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:24px;justify-content:center}
.tab{padding:12px 18px;border-radius:8px;background:#1e293b;color:#94a3b8;text-decoration:none;font-size:15px;border:none;cursor:pointer}
.tab.active{background:#0284c7;color:white}
.card{background:#1e293b;border-radius:12px;padding:24px;margin-bottom:20px}
h2{color:#e2e8f0;margin-bottom:20px;font-size:20px;border-bottom:1px solid #334155;padding-bottom:10px}
.fix{background:#0f172a;border-radius:8px;padding:18px;margin:12px 0;border-left:3px solid #38bdf8}
.fix.banker{border-left-color:#eab308}
.odd{color:#fbbf24;font-weight:bold}
.edg{color:#4ade80;font-weight:bold}
.empty{color:#f87171;text-align:center;padding:40px}
h3{color:#94a3b8;margin:20px 0 10px}
.market{margin:10px 0;padding:10px;background:#1e293b;border-radius:6px}
button{background:#16a34a;color:white;border:none;padding:14px;border-radius:8px;width:100%;font-weight:bold;margin-top:16px;font-size:16px;cursor:pointer}
</style>
</head>
<body>
<div class="wrap">
<h1>EDGEMETRIX V300 DASHBOARD</h1>
<p class="subtitle">Quantitative Football Analytics Engine</p>
<p class="date">Today: """ + today + """</p>
<div class="tabs">
<button class="tab """ + active["daily"] + """ onclick="window.location='?tab=daily'">Daily Picks</button>
<button class="tab """ + active["builder"] + """ onclick="window.location='?tab=builder'">Bet Builder</button>
<button class="tab """ + active["ai"] + """ onclick="window.location='?tab=ai'">AI Acca Generator</button>
<button class="tab """ + active["future"] + """ onclick="window.location='?tab=future'">Future (3-Day Value)</button>
<button class="tab """ + active["bankers"] + """ onclick="window.location='?tab=bankers'">Bankers Daily</button>
<button class="tab """ + active["advanced"] + """ onclick="window.location='?tab=advanced'">Acca Generator Tab</button>
</div>"""

    if tab == "daily":
        html += '<div class="card"><h2>Daily High-Confluence Value Picks</h2>'
        if not todays_games:
            html += '<p class="empty">No fixtures scheduled for today</p>'
        else:
            for f in todays_games:
                html += '<div class="fix"><div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px"><b style="font-size:18px">' + f["h"] + ' vs ' + f["a"] + '</b><span style="color:#94a3b8;font-size:14px">' + f["t"] + '</span></div>'
                html += '<div style="color:#94a3b8;font-size:14px;margin-bottom:14px">' + f["l"] + '</div>'
                for m in f["m"]:
                    e = edge(m["o"], m["p"])
                    html += '<div class="market"><b>' + m["n"] + '</b><br>Engine Prob: ' + str(int(m["p"]*100)) + '% | Edge: <span class="edg">+' + str(e) + '%</span></div>'
                html += '</div>'
        html += '</div>'

    elif tab == "builder":
        sel = request.args.getlist("sel")
        html += '<div class="card"><h2>Bet Builder</h2>'
        if sel:
            total_odds = 1.0
            html += '<h3>Your Selected Accumulator</h3>'
            for s in sel:
                parts = s.split("||")
                if len(parts) == 3:
                    total_odds *= float(parts[2])
                    html += '<div class="fix">' + parts[0] + '<br>' + parts[1] + ' <span class="odd">@' + parts[2] + '</span></div>'
            html += '<div style="padding:20px;background:#0369a1;border-radius:8px;margin-top:20px"><b style="font-size:18px">Combined Odds: ' + str(round(total_odds,2)) + '</b><br>Stake £20 → Return £' + str(round(20*total_odds,2)) + '</div>'
            html += '<br><a href="?tab=builder" style="color:#94a3b8">← Clear & Build New</a>'
        else:
            if not todays_games:
                html += '<p class="empty">No fixtures available today</p>'
            else:
                html += '<form method="GET"><input type="hidden" name="tab" value="builder">'
                for f in todays_games:
                    html += '<div class="fix"><b>' + f["h"] + ' vs ' + f["a"] + '</b><br><small style="color:#94a3b8">' + f["l"] + '</small>'
                    for m in f["m"]:
                        html += '<br><label style="cursor:pointer;padding:6px 0;display:block"><input type="checkbox" name="sel" value="' + f["h"] + '||' + m["n"] + '||' + str(m["o"]) + '"> ' + m["n"] + ' @' + str(m["o"]) + '</label>'
                    html += '</div>'
                html += '<button type="submit">Build Accumulator</button></form>'
        html += '</div>'

    elif tab == "ai":
        html += '<div class="card"><h2>AI Acca Generator</h2>'
        if not todays_games:
            html += '<p class="empty">No fixtures available today</p>'
        else:
            picks = []
            for f in todays_games:
                for m in f["m"]:
                    picks.append((-edge(m["o"], m["p"]), f["h"], f["a"], m["n"], m["o"]))
            picks.sort()
            top = picks[:3]
            if not top:
                html += '<p class="empty">No selections available</p>'
            else:
                total = 1.0
                html += '<p style="margin-bottom:20px">⚡ Top 3 highest-edge selections calculated automatically:</p>'
                for p in top:
                    total *= p[4]
                    html += '<div class="fix"><b>' + p[1] + ' vs ' + p[2] + '</b><br>' + p[3] + ' <span class="odd">@' + str(p[4]) + '</span><br>Edge: <span class="edg">+' + str(edge(p[4], 0.5)) + '%</span></div>'
                html += '<div style="padding:20px;background:#0369a1;border-radius:8px;margin-top:20px"><b style="font-size:18px">AI Recommended Accumulator</b><br>Combined Odds: ' + str(round(total,2)) + '<br>Stake £20 → Return £' + str(round(20*total,2)) + '</div>'
        html += '</div>'

    elif tab == "future":
        html += '<div class="card"><h2>Future (3-Day Value)</h2>'
        if not future_fixtures:
            html += '<p class="empty">No upcoming fixtures found</p>'
        else:
            for d in sorted(future_fixtures.keys()):
                label = "📅 Today — " + d if d == today else "📅 " + d
                html += '<h3>' + label + '</h3>'
                for f in future_fixtures[d]:
                    html += '<div class="fix"><b>' + f["h"] + ' vs ' + f["a"] + '</b><br>' + f["l"] + ' — ' + f["t"]
                    for m in f["m"]:
                        html += '<br>' + m["n"] + ' @' + str(m["o"])
                    html += '</div>'
        html += '</div>'

    elif tab == "bankers":
        html += '<div class="card"><h2>Bankers Daily</h2>'
        found = False
        for f in todays_games:
            if f.get("b", False):
                found = True
                html += '<div class="fix banker"><b>⭐ ' + f["h"] + ' vs ' + f["a"] + '</b><br>' + f["l"] + ' — ' + f["t"]
                for m in f["m"]:
                    if m["p"] >= 0.75:
                        html += '<br><b>' + m["n"] + '</b> @' + str(m["o"]) + ' | Confidence: ' + str(int(m["p"]*100)) + '%'
                html += '</div>'
        if not found:
            html += '<p class="empty">No banker selections today</p>'
        html += '</div>'

    elif tab == "advanced":
        html += '<div class="card"><h2>Acca Generator Tab</h2>'
        if len(todays_games) >= 3:
            html += '<p style="margin-bottom:20px">Generate accumulator from today fixtures:</p>'
            html += '<div style="background:#0369a1;padding:20px;border-radius:8px">'
            html += '<h3>Recommended 3-Leg Acca — ' + today + '</h3>'
            total_adv = 1.0
            for i, f in enumerate(todays_games[:3], 1):
                pick_m = f["m"][0]
                total_adv *= pick_m["o"]
                html += '<div style="margin:10px 0">' + str(i) + '. <b>' + f["h"] + ' vs ' + f["a"] + '</b><br>' + pick_m["n"] + ' @' + str(pick_m["o"]) + '</div>'
            html += '<div style="margin-top:15px;padding-top:15px;border-top:1px solid #38bdf8"><b>Combined Odds: ' + str(round(total_adv,2)) + '</b><br>Stake £20 → Return £' + str(round(20*total_adv,2)) + '</div></div>'
        else:
            html += '<p class="empty">Not enough fixtures for 3-leg accumulator</p>'
        html += '</div>'

    html += '</div></body></html>'
    return html

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
