from flask import Flask

app = Flask(__name__)

FIXTURES = {
    "2026-11-05": [
        {"home": "AC Milan", "away": "Ferencváros", "league": "UEFA Europa League", "time": "17:45 GMT", "banker": True,
         "markets": [
             {"name": "Over 1.5 Goals & Milan 1X", "odds": 1.42, "prob": 0.77},
             {"name": "BTTS — Yes", "odds": 1.72, "prob": 0.62},
             {"name": "AC Milan Win", "odds": 1.35, "prob": 0.78}
         ]},
        {"home": "Bayer Leverkusen", "away": "Marseille", "league": "UEFA Europa League", "time": "20:00 GMT", "banker": True,
         "markets": [
             {"name": "Over 1.5 Goals", "odds": 1.35, "prob": 0.80},
             {"name": "Leverkusen Win", "odds": 1.42, "prob": 0.76}
         ]}
    ],
    "2026-11-06": [
        {"home": "Borussia Dortmund", "away": "VfB Stuttgart", "league": "Bundesliga", "time": "19:30 GMT", "banker": True,
         "markets": [{"name": "Over 2.5 Goals", "odds": 1.50, "prob": 0.75}]}
    ],
    "2026-11-07": [
        {"home": "Manchester City", "away": "Liverpool", "league": "Premier League", "time": "12:30 GMT", "banker": True,
         "markets": [{"name": "BTTS & Over 2.5", "odds": 1.65, "prob": 0.72}]}
    ]
}

def calc_edge(odds, prob):
    return round((prob - (1 / odds)) * 100, 2)

@app.route("/")
def index():
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EDGEMETRIX V300</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{background:#0b0f19;color:#f1f5f9;font-family:sans-serif;padding:16px}
        .wrap{max-width:760px;margin:0 auto}
        .hdr{text-align:center;margin-bottom:24px}
        h1{color:#38bdf8;font-size:24px}
        .stat{color:#4ade80;font-size:14px;margin-top:6px}
        .tabs{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:20px;border-bottom:1px solid #1e293b;padding-bottom:8px}
        .tab{padding:10px 14px;border-radius:8px;text-decoration:none;font-size:13px;font-weight:600;background:#1e293b;color:#94a3b8;border:1px solid transparent}
        .tab.active{background:#0284c7;color:white;border-color:#38bdf8}
        .card{background:#1e293b;border-radius:12px;padding:20px;margin-bottom:16px;border:1px solid #334155}
        .card h2{color:#e2e8f0;font-size:17px;margin-bottom:16px;padding-bottom:8px;border-bottom:1px solid #334155}
        .match{background:#0f172a;border-radius:10px;padding:14px;margin-bottom:12px;border-left:3px solid #38bdf8}
        .match.banker{border-left-color:#eab308}
        .m-head{display:flex;justify-content:space-between;flex-wrap:wrap;gap:4px;margin-bottom:4px}
        .teams{font-weight:700}
        .m-time{color:#94a3b8;font-size:12px}
        .league{color:#94a3b8;font-size:12px;margin-bottom:10px}
        .mkt{background:#1e293b;border-radius:8px;padding:10px;margin:6px 0;border:1px solid #334155}
        .mkt-nm{font-weight:600;font-size:14px;margin-bottom:4px}
        .odds{color:#fbbf24;font-weight:600}
        .edge{color:#4ade80;font-weight:700}
        .banker-tag{display:inline-block;background:#eab308;color:#0f172a;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:bold;margin-left:8px}
        .empty{color:#f87171;text-align:center;padding:20px}
    </style>
</head>
<body>
<div class="wrap">
    <div class="hdr">
        <h1>⚽ EDGEMETRIX V300</h1>
        <p class="stat">● ONLINE — Flask & Render Active</p>
    </div>
    <nav class="tabs">
        <a class="tab active" href="/">Daily Picks</a>
        <a class="tab" href="/ai">AI Acca Generator</a>
        <a class="tab" href="/future">Future Fixtures</a>
        <a class="tab" href="/bankers">Bankers Daily</a>
    </nav>
"""
    # Daily Tab
    html += '<div class="card"><h2>📊 Daily High-Confluence Value Picks</h2>'
    fixtures_today = FIXTURES.get("2026-11-05", [])
    if not fixtures_today:
        html += '<p class="empty">No fixtures found for today</p>'
    else:
        for fx in fixtures_today:
            html += f'<div class="match"><div class="m-head"><span class="teams">{fx["home"]} vs {fx["away"]}</span><span class="m-time">{fx["time"]}</span></div>'
            html += f'<div class="league">{fx["league"]}</div>'
            for mk in fx["markets"]:
                e = calc_edge(mk["odds"], mk["prob"])
                html += f'<div class="mkt"><div class="mkt-nm">{mk["name"]}</div><div>Odds: <span class="odds">{mk["odds"]}</span> | Prob: {mk["prob"]*100:.1f}% | Edge: <span class="edge">+{e}%</span></div></div>'
            html += "</div>"
    html += "</div>"

    # AI Tab
    html += '<div class="card"><h2>🤖 AI High-Edge 3-Fold Generator</h2>'
    all_mkts = []
    for fx in FIXTURES.get("2026-11-05", []):
        for mk in fx["markets"]:
            all_mkts.append((-calc_edge(mk["odds"], mk["prob"]), fx["home"], fx["away"], mk["name"], mk["odds"]))
    all_mkts.sort()
    top3 = all_mkts[:3]
    if top3:
        comb_odds = 1.0
        html += '<div style="background:#0369a1;border-radius:10px;padding:16px;margin-top:10px;border:1px solid #38bdf8;"><h3 style="margin-bottom:10px;">Top 3 Highest Edge Picks</h3>'
        for _, h, a, n, o in top3:
            comb_odds *= o
            html += f'<div style="margin:6px 0;">• {h} vs {a}<br><span style="padding-left:18px;">{n} — <span class="odds">@{o}</span></span></div>'
        html += f'<div style="margin-top:12px;font-weight:bold;font-size:16px;">Combined Odds: {comb_odds:.2f}</div>'
        html += f'<div style="margin-top:6px;">Stake: £20 → Return: £{20*comb_odds:.2f}</div></div>'
    else:
        html += '<p class="empty">No markets available</p>'
    html += "</div>"

    # Future Tab
    html += '<div class="card"><h2>📅 Future Fixtures (3-Day Value)</h2>'
    for dt in ["2026-11-05", "2026-11-06", "2026-11-07"]:
        html += f'<h3 style="color:#eab308;margin:16px 0 8px;">{dt}</h3>'
        day_fixtures = FIXTURES.get(dt, [])
        if not day_fixtures:
            html += '<p style="color:#64748b;font-size:13px;">No fixtures scheduled</p>'
            continue
        for fx in day_fixtures:
            html += f'<div class="match"><div class="m-head"><span class="teams">{fx["home"]} vs {fx["away"]}</span><span class="m-time">{fx["time"]}</span></div>'
            html += f'<div class="league">{fx["league"]}</div>'
            for mk in fx["markets"]:
                e = calc_edge(mk["odds"], mk["prob"])
                html += f'<div class="mkt"><div class="mkt-nm">{mk["name"]}</div><div>Odds: <span class="odds">@{mk["odds"]}</span> | Edge: <span class="edge">+{e}%</span></div></div>'
            html += "</div>"
    html += "</div>"

    # Bankers Tab
    html += '<div class="card"><h2>💰 Bankers Daily (Confidence >= 75%)</h2>'
    found = False
    for fx in FIXTURES.get("2026-11-05", []):
        if fx.get("banker", False):
            found = True
            html += f'<div class="match banker"><div class="m-head"><span class="teams">{fx["home"]} vs {fx["away"]}<span class="banker-tag">BANKER</span></span><span class="m-time">{fx["time"]}</span></div>'
            html += f'<div class="league">{fx["league"]}</div>'
            for mk in fx["markets"]:
                if mk["prob"] >= 0.75:
                    e = calc_edge(mk["odds"], mk["prob"])
                    html += f'<div class="mkt" style="border-color:#eab308;"><div class="mkt-nm">{mk["name"]}</div><div>Odds: <span class="odds">@{mk["odds"]}</span> | Conf: {mk["prob"]*100:.1f}% | Edge: <span class="edge">+{e}%</span></div></div>'
            html += "</div>"
    if not found:
        html += '<p class="empty">No banker selections today</p>'
    html += "</div>"

    html += "</div></body></html>"
    return html

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
