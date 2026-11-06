from flask import Flask, request, os
from datetime import datetime

app = Flask(__name__)

FIXTURES = {
    "2026-11-06": [
        {
            "home": "Notts County",
            "away": "Chesterfield",
            "league": "League Two (England)",
            "time": "19:45 GMT",
            "is_banker": True,
            "markets": [
                {"name": "Over 1.5 Goals", "odds": 1.44, "prob": 0.76},
                {"name": "Over 2.5 Goals", "odds": 1.65, "prob": 0.69},
                {"name": "BTTS - Yes", "odds": 1.72, "prob": 0.63}
            ]
        },
        {
            "home": "Hammarby IF",
            "away": "IF Elfsborg",
            "league": "Allsvenskan (Sweden)",
            "time": "18:00 GMT",
            "is_banker": True,
            "markets": [
                {"name": "Hammarby Win", "odds": 1.65, "prob": 0.68},
                {"name": "1X & Over 1.5", "odds": 1.30, "prob": 0.83},
                {"name": "Over 2.5 Goals", "odds": 1.85, "prob": 0.57}
            ]
        },
        {
            "home": "Barnet",
            "away": "Oldham Athletic",
            "league": "National League (England)",
            "time": "19:30 GMT",
            "is_banker": True,
            "markets": [
                {"name": "Barnet 1X", "odds": 1.38, "prob": 0.79},
                {"name": "Over 1.5 Goals", "odds": 1.52, "prob": 0.72},
                {"name": "Barnet Win", "odds": 1.95, "prob": 0.55}
            ]
        },
        {
            "home": "Everton",
            "away": "Coventry City",
            "league": "Premier League (England)",
            "time": "19:45 GMT",
            "is_banker": True,
            "markets": [
                {"name": "Everton Win", "odds": 1.70, "prob": 0.65},
                {"name": "1X & Over 1.5", "odds": 1.32, "prob": 0.81},
                {"name": "BTTS - Yes", "odds": 1.95, "prob": 0.54}
            ]
        },
        {
            "home": "Sevilla",
            "away": "Deportivo Alaves",
            "league": "La Liga (Spain)",
            "time": "20:00 GMT",
            "is_banker": False,
            "markets": [
                {"name": "Sevilla Win", "odds": 1.90, "prob": 0.58},
                {"name": "Double Chance 1X", "odds": 1.38, "prob": 0.79},
                {"name": "Under 2.5 Goals", "odds": 1.62, "prob": 0.64}
            ]
        },
        {
            "home": "Birmingham City",
            "away": "Wrexham",
            "league": "League One (England)",
            "time": "19:45 GMT",
            "is_banker": False,
            "markets": [
                {"name": "BTTS - Yes", "odds": 1.75, "prob": 0.62},
                {"name": "Over 2.5 Goals", "odds": 1.88, "prob": 0.56},
                {"name": "BTTS & Over 2.5", "odds": 2.20, "prob": 0.48}
            ]
        },
        {
            "home": "Atalanta",
            "away": "Lazio",
            "league": "Serie A (Italy)",
            "time": "19:45 GMT",
            "is_banker": False,
            "markets": [
                {"name": "Over 2.5 Goals", "odds": 1.75, "prob": 0.62},
                {"name": "BTTS - Yes", "odds": 1.68, "prob": 0.64},
                {"name": "Atalanta Win", "odds": 1.85, "prob": 0.59}
            ]
        },
        {
            "home": "Vissel Kobe",
            "away": "Yokohama F. Marinos",
            "league": "J1 League (Japan)",
            "time": "11:00 GMT",
            "is_banker": True,
            "markets": [
                {"name": "1X & Over 1.5", "odds": 1.35, "prob": 0.78},
                {"name": "Over 2.5 Goals", "odds": 1.60, "prob": 0.68},
                {"name": "Home Win", "odds": 1.72, "prob": 0.63}
            ]
        },
        {
            "home": "LA Galaxy",
            "away": "Seattle Sounders",
            "league": "MLS (USA)",
            "time": "02:00 GMT",
            "is_banker": False,
            "markets": [
                {"name": "LA Galaxy Win", "odds": 2.05, "prob": 0.52},
                {"name": "Over 2.5 Goals", "odds": 1.72, "prob": 0.61},
                {"name": "BTTS - Yes", "odds": 1.80, "prob": 0.59}
            ]
        }
    ]
}

def edge(o, p):
    return round((p - 1 / o) * 100, 2)

today = datetime.utcnow().strftime("%Y-%m-%d")
todays_matches = FIXTURES.get(today, [])
SEP = "||"

@app.route("/")
def dashboard():
    tab = request.args.get("tab", "daily")
    
    def active(t):
        return "active" if tab == t else ""
    
    html_start = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>EDGEMETRIX V300</title>
<style>
:root{--bg:#0b101a;--card:#161d2f;--accent:#00d4ff;--gold:#ffc107;--green:#00e676;--red:#ff5252;--text:#e6eaf3;--muted:#8892a8}
*{margin:0;padding:0;box-sizing:border-box}
body{background:var(--bg);color:var(--text);font-family:'Segoe UI',system-ui,sans-serif;padding:16px;line-height:1.5}
.container{max-width:950px;margin:0 auto}
header{text-align:center;margin-bottom:24px}
h1{font-size:24px;color:var(--accent);margin-bottom:4px}
.subtitle{color:var(--muted);font-size:14px;margin-bottom:8px}
.date-badge{display:inline-block;background:#1a2938;color:var(--green);padding:6px 16px;border-radius:20px;font-weight:bold}
.tabs{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:24px;justify-content:center}
.tab-btn{padding:12px 16px;border-radius:10px;background:var(--card);color:var(--muted);border:none;cursor:pointer;font-size:14px;font-weight:500;transition:all .2s}
.tab-btn:hover{background:#1e2a42}
.tab-btn.active{background:var(--accent);color:#000;font-weight:bold}
.card{background:var(--card);border-radius:14px;padding:24px;margin-bottom:20px}
.card h2{font-size:18px;margin-bottom:20px;padding-bottom:10px;border-bottom:1px solid #2a3550;color:var(--accent)}
.match{background:#1e273f;border-radius:10px;padding:18px;margin:14px 0;border-left:4px solid var(--accent);transition:transform .15s}
.match:hover{transform:translateX(4px)}
.match.banker{border-left-color:var(--gold)}
.match-header{font-weight:bold;font-size:16px;margin-bottom:6px}
.match-meta{color:var(--muted);font-size:13px;margin-bottom:10px}
.market{padding:10px 14px;background:#25304d;border-radius:8px;margin:8px 0}
.odds{color:var(--gold);font-weight:bold}
.edge{color:var(--green);font-weight:bold}
.empty{text-align:center;color:var(--red);padding:40px 20px}
.form-btn{background:var(--accent);color:#000;border:none;padding:14px;border-radius:10px;font-weight:bold;font-size:16px;width:100%;margin-top:16px;cursor:pointer}
.form-btn:hover{background:#00b8e6}
.checkbox-item{padding:10px 0;cursor:pointer;display:block}
.selection-summary{background:#003344;padding:20px;border-radius:10px;margin-top:16px}
.clear-link{color:var(--muted);text-decoration:none;display:inline-block;margin-top:12px}
.clear-link:hover{color:var(--text)}
</style>
</head>
<body>
<div class="container">
<header>
<h1>⚽ EDGEMETRIX V300</h1>
<p class="subtitle">UK Pyramid & Global Value Feed</p>
<p class="date-badge">📅 ''' + today + '''</p>
</header>
<nav class="tabs">
<button class="tab-btn ''' + active("daily") + '''" onclick="location.href='?tab=daily'">Daily Picks</button>
<button class="tab-btn ''' + active("builder") + '''" onclick="location.href='?tab=builder'">Bet Builder</button>
<button class="tab-btn ''' + active("ai") + '''" onclick="location.href='?tab=ai'">AI Acca Generator</button>
<button class="tab-btn ''' + active("future") + '''" onclick="location.href='?tab=future'">Future (3-Day)</button>
<button class="tab-btn ''' + active("bankers") + '''" onclick="location.href='?tab=bankers'">Bankers</button>
<button class="tab-btn ''' + active("advanced") + '''" onclick="location.href='?tab=advanced'">Acca Generator</button>
</nav>
'''

    html_end = '</div></body></html>'
    html = html_start

    if tab == "daily":
        html += '<div class="card"><h2>📊 Daily Picks — Highest Edge Values</h2>'
        if not todays_matches:
            html += '<div class="empty">⚠️ No fixtures found for today</div>'
        else:
            for m in todays_matches:
                html += '<div class="match' + (" banker" if m.get("is_banker") else "") + '">'
                html += '<div class="match-header">' + m["home"] + " vs " + m["away"] + '</div>'
                html += '<div class="match-meta">' + m["league"] + " — " + m["time"] + '</div>'
                for mk in m["markets"]:
                    e = edge(mk["odds"], mk["prob"])
                    html += '<div class="market"><strong>' + mk["name"] + '</strong><br>Odds: <span class="odds">' + str(mk["odds"]) + '</span> | Prob: ' + str(int(mk["prob"]*100)) + '% | Edge: +<span class="edge">' + str(e) + '%</span></div>'
                html += '</div>'
        html += '</div>'

    elif tab == "builder":
        sel = request.args.getlist("sel")
        html += '<div class="card"><h2>🔨 Bet Builder</h2>'
        if sel:
            total_odds = 1.0
            html += '<h3 style="margin-bottom:12px">Your Selection</h3>'
            for s in sel:
                parts = s.split(SEP)
                if len(parts) == 3:
                    total_odds *= float(parts[2])
                    html += '<div class="market">' + parts[0] + '<br>' + parts[1] + ' @<span class="odds">' + parts[2] + '</span></div>'
            stake = 20
            returns = round(stake * total_odds, 2)
            html += '<div class="selection-summary"><strong>Combined Odds: ' + str(round(total_odds,2)) + '</strong><br>Stake £' + str(stake) + ' → Return £' + str(returns) + '</div>'
            html += '<a href="?tab=builder" class="clear-link">← Clear & Start Over</a>'
        else:
            html += '<form method="GET"><input type="hidden" name="tab" value="builder">'
            if not todays_matches:
                html += '<div class="empty">No fixtures available</div>'
            else:
                for m in todays_matches:
                    html += '<div class="match"><div class="match-header">' + m["home"] + " vs " + m["away"] + '</div><div class="match-meta">' + m["league"] + '</div>'
                    for mk in m["markets"]:
                        val = m["home"] + SEP + mk["name"] + SEP + str(mk["odds"])
                        html += '<label class="checkbox-item"><input type="checkbox" name="sel" value="' + val + '"> ' + mk["name"] + ' @' + str(mk["odds"]) + '</label>'
                    html += '</div>'
            html += '<button type="submit" class="form-btn">Build Accumulator Slip</button></form>'
        html += '</div>'

    elif tab == "ai":
        html += '<div class="card"><h2>🤖 AI Acca Generator — Top 3 by Edge</h2>'
        if not todays_matches:
            html += '<div class="empty">No fixtures available</div>'
        else:
            ranked = []
            for m in todays_matches:
                for mk in m["markets"]:
                    ranked.append((-edge(mk["odds"], mk["prob"]), m["home"], m["away"], mk["name"], mk["odds"]))
            ranked.sort()
            top3 = ranked[:3]
            if top3:
                combined = 1.0
                for idx, pick in enumerate(top3, 1):
                    combined *= pick[4]
                    html += '<div class="match"><div class="match-header">' + str(idx) + ". " + pick[1] + " vs " + pick[2] + '</div>'
                    html += '<div class="market">' + pick[3] + ' @<span class="odds">' + str(pick[4]) + '</span></div></div>'
                stake = 20
                returns = round(stake * combined, 2)
                html += '<div class="selection-summary"><strong>AI Recommended Accumulator</strong><br>Combined Odds: ' + str(round(combined,2)) + '<br>Stake £' + str(stake) + ' → Return £' + str(returns) + '</div>'
            else:
                html += '<div class="empty">No selections available</div>'
        html += '</div>'

    elif tab == "future":
        html += '<div class="card"><h2>📅 Future Fixtures — Early Value</h2>'
        for d in sorted(FIXTURES.keys()):
            label = "✅ Today — " + d if d == today else "📅 " + d
            html += '<h3 style="margin:16px 0 8px;color:var(--muted)">' + label + '</h3>'
            for m in FIXTURES[d]:
                html += '<div class="match"><div class="match-header">' + m["home"] + " vs " + m["away"] + '</div>'
                html += '<div class="match-meta">' + m["league"] + " — " + m["time"] + '</div>'
                for mk in m["markets"]:
                    html += '<div class="market">' + mk["name"] + ' @' + str(mk["odds"]) + '</div>'
                html += '</div>'
        html += '</div>'

    elif tab == "bankers":
        html += '<div class="card"><h2>⭐ Bankers — High Confidence (>=75%)</h2>'
        found = False
        for m in todays_matches:
            if m.get("is_banker"):
                found = True
                html += '<div class="match banker"><div class="match-header">⭐ ' + m["home"] + " vs " + m["away"] + '</div>'
                html += '<div class="match-meta">' + m["league"] + " — " + m["time"] + '</div>'
                for mk in m["markets"]:
                    if mk["prob"] >= 0.75:
                        html += '<div class="market"><strong>' + mk["name"] + '</strong> @' + str(mk["odds"]) + ' — Conf: ' + str(int(mk["prob"]*100)) + '%</div>'
                html += '</div>'
        if not found:
            html += '<div class="empty">No banker selections today</div>'
        html += '</div>'

    elif tab == "advanced":
        html += '<div class="card"><h2>🎯 3-Leg Acca Generator</h2>'
        if len(todays_matches) >= 3:
            combined = 1.0
            for idx, m in enumerate(todays_matches[:3], 1):
                pick = m["markets"][0]
                combined *= pick["odds"]
                html += '<div class="match"><div class="match-header">' + str(idx) + ". " + m["home"] + " vs " + m["away"] + '</div>'
                html += '<div class="market">' + pick["name"] + ' @' + str(pick["odds"]) + '</div></div>'
            stake = 20
            returns = round(stake * combined, 2)
            html += '<div class="selection-summary"><strong>Combined Odds: ' + str(round(combined,2)) + '</strong><br>Stake £' + str(stake) + ' → Return £' + str(returns) + '</div>'
        else:
            html += '<div class="empty">Need 3+ fixtures for 3-leg acca</div>'
        html += '</div>'

    else:
        html += '<div class="card"><div class="empty">Tab not recognized: ' + tab + '</div></div>'

    html += html_end
    return html

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=
