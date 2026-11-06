# -*- coding: utf-8 -*-
from flask import Flask, request
from datetime import datetime

app = Flask(__name__)

FIXTURE_FEED = {
"2026-11-06": [
{"h":"Borussia Dortmund","a":"VfB Stuttgart","l":"Bundesliga","t":"19:30 GMT","b":True,
"m":[{"n":"Over 1.5 Goals & Dortmund 1X","o":1.42,"p":0.77},
{"n":"BTTS Yes","o":1.72,"p":0.62},
{"n":"Dortmund Win","o":1.35,"p":0.78}]}
]
}

def edge(o, p):
    return round((p - 1 / o) * 100, 2)

def get_today_str():
    return datetime.utcnow().strftime("%Y-%m-%d")

def filter_active_fixtures():
    today = get_today_str()
    return {d: games for d, games in FIXTURE_FEED.items() if d >= today}

@app.route("/")
def main():
    tab = request.args.get("tab", "daily")
    today = get_today_str()
    fixtures = filter_active_fixtures()
    todays_games = fixtures.get(today, [])

    active = {}
    for t in ["daily","builder","ai","future","bankers","advanced"]:
        active[t] = "active" if tab == t else ""

    html_start = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>EDGEMETRIX V300</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0b0f19;color:#f1f5f9;font-family:sans-serif;padding:16px}
.wrap{max-width:720px;margin:0 auto}
h1{color:#38bdf8;text-align:center;margin-bottom:4px}
.subtitle{color:#94a3b8;font-size:14px;text-align:center;margin-bottom:12px}
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
.empty{color:#f87171;text-align:center;padding:30px}
</style>
</head>
<body>
<div class="wrap">
<h1>EDGEMETRIX V300 DASHBOARD</h1>
<p class="subtitle">Quantitative Football Analytics Engine</p>
<p class="date">Today: """ + today + """</p>
<div class="tabs">
<a class="tab """ + active["daily"] + """ href="/?tab=daily">Daily Picks</a>
<a class="tab """ + active["builder"] + """ href="/?tab=builder">Bet Builder</a>
<a class="tab """ + active["ai"] + """ href="/?tab=ai">AI Acca Generator</a>
<a class="tab """ + active["future"] + """ href="/?tab=future">Future</a>
<a class="tab """ + active["bankers"] + """ href="/?tab=bankers">Bankers</a>
<a class="tab """ + active["advanced"] + """ href="/?tab=advanced">Advanced</a>
</div>"""

    html_end = """</div></body></html>"""

    content = ""
    if tab == "daily":
        content = '<div class="card"><h2>Daily Picks</h2>'
        if not todays_games:
            content += '<p class="empty">No fixtures today</p>'
        else:
            for f in todays_games:
                content += '<div class="fix"><b>' + f["h"] + ' vs ' + f["a"] + '</b><br>'
                content += f["l"] + ' â€” ' + f["t"]
                for m in f["m"]:
                    e = edge(m["o"], m["p"])
                    content += '<br>' + m["n"] + ' @' + str(m["o"]) + ' | Edge +' + str(e) + '%'
                content += '</div>'
        content += '</div>'

    return html_start + content + html_end

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
