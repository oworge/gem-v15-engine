from flask import Flask, render_template_string, request

app = Flask(__name__)

FIXTURES = {
    "2026-11-05": [
        {
            "home": "AC Milan", "away": "Ferencváros",
            "league": "UEFA Europa League", "time": "17:45 GMT",
            "banker": True,
            "markets": [
                {"name": "Over 1.5 Goals & Milan 1X", "odds": 1.42, "prob": 0.77, "type": "Goals/DC"},
                {"name": "BTTS — Yes", "odds": 1.72, "prob": 0.62, "type": "BTTS"},
                {"name": "AC Milan Win", "odds": 1.35, "prob": 0.78, "type": "1X2"}
            ]
        },
        {
            "home": "Bayer Leverkusen", "away": "Marseille",
            "league": "UEFA Europa League", "time": "20:00 GMT",
            "banker": True,
            "markets": [
                {"name": "Over 1.5 Goals", "odds": 1.35, "prob": 0.80, "type": "Goals"},
                {"name": "Leverkusen Win", "odds": 1.42, "prob": 0.76, "type": "1X2"}
            ]
        },
        {
            "home": "Real Sociedad", "away": "Lyon",
            "league": "UEFA Europa League", "time": "17:45 GMT",
            "banker": False,
            "markets": [
                {"name": "Over 1.5 Goals", "odds": 1.30, "prob": 0.81, "type": "Goals"},
                {"name": "Draw or Lyon (X2)", "odds": 1.50, "prob": 0.71, "type": "Double Chance"}
            ]
        }
    ],
    "2026-11-06": [
        {
            "home": "Borussia Dortmund", "away": "VfB Stuttgart",
            "league": "Bundesliga", "time": "19:30 GMT",
            "banker": True,
            "markets": [
                {"name": "Over 2.5 Goals", "odds": 1.50, "prob": 0.75, "type": "Goals"}
            ]
        }
    ],
    "2026-11-07": [
        {
            "home": "Manchester City", "away": "Liverpool",
            "league": "Premier League", "time": "12:30 GMT",
            "banker": True,
            "markets": [
                {"name": "BTTS & Over 2.5", "odds": 1.65, "prob": 0.72, "type": "BTTS"}
            ]
        }
    ]
}

def edge(odds, prob):
    return round((prob - (1 / odds)) * 100, 2)

@app.route("/")
def index():
    tab = request.args.get("tab", "daily")
    sel_date = request.args.get("date", "2026-11-05")
    legs = int(request.args.get("legs", 3))
    mfilter = request.args.get("market_filter", "ALL")
    selected = request.args.getlist("markets")

    html_top = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EDGEMETRIX V300</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{background:#0b0f19;color:#f1f5f9;font-family:-apple-system,Segoe UI,Roboto,sans-serif;padding:16px;min-height:100vh}
        .wrap{max-width:760px;margin:0 auto}
        .hdr{text-align:center;margin-bottom:24px;padding-bottom:16px;border-bottom:1px solid #1e293b}
        h1{color:#38bdf8;font-size:24px}
        .stat{color:#4ade80;font-size:14px;margin-top:6px}
        .tabs{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:20px;border-bottom:1px solid #1e293b;padding-bottom:8px}
        .tab{padding:10px 14px;border-radius:8px;text-decoration:none;font-size:13px;font-weight:600;background:#1e293b;color:#94a3b8;border:1px solid transparent;white-space:nowrap}
        .tab.active{background:#0284c7;color:white;border-color:#38bdf8}
        .card{background:#1e293b;border-radius:12px;padding:20px;margin-bottom:16px;border:1px solid #334155}
        .card h2{color:#e2e8f0;font-size:17px;margin-bottom:16px;padding-bottom:8px;border-bottom:1px solid #334155}
        .match{background:#0f172a;border-radius:10px;padding:14px;margin-bottom:12px;border-left:3px solid #38bdf8}
        .m-head{display:flex;justify-content:space-between;flex-wrap:wrap;gap:4px;margin-bottom:4px}
        .teams{font-weight:700}
        .m-time{color:#94a3b8;font-size:12px}
        .league{color:#94a3b8;font-size:12px;margin-bottom:10px}
        .mkt{background:#1e293b;border-radius:8px;padding:10px;margin:6px 0;border:1px solid #334155}
        .mkt-nm{font-weight:600;font-size:14px;margin-bottom:4px}
        .mkt-dets{display:flex;flex-wrap:wrap;gap:10px;font-size:13px}
        .odds{color:#fbbf24;font-weight:600}
        .edge{color:#4ade80;font-weight:700}
        .banker{border-left-color:#eab308}
        .banker-tag{display:inline-block;background:#eab308;color:#0f172a;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:bold;margin-left:8px}
        select,input[type="date"]{background:#0f172a;color:white;border:1px solid #38bdf8;padding:8px 10px;border-radius:6px;font-size:14px}
        .btn{background:#16a34a;color:white;border:none;padding:12px 20px;border-radius:8px;font-weight:bold;cursor:pointer;width:100%;font-size:15px;margin-top:10px}
        .slip{background:#0369a1;border-radius:10px;padding:16px;margin-top:16px;border:1px solid #38bdf8}
        .chk{margin-right:8px}
        .form-row{display:flex;flex-wrap:wrap;gap:12px;margin-bottom:12px}
        .form-col{flex:1;min-width:160px}
        label{font-size:13px;color:#94a3b8;display:block;margin-bottom:4px}
        @media(max-width:520px){
            body{padding:10px}
            .card{padding:14px}
            .mkt-dets{flex-direction:column;gap:2px}
        }
    </style>
</head>
<body>
<div class="wrap">
    <div class="hdr">
        <h1>⚽ EDGEMETRIX V300</h1>
        <p class="stat">● ONLINE — Flask & Render Active</p>
    </div>
    <nav class="tabs">
        <a class="tab """ + ("active" if tab=="daily" else "") + """ href="/?tab=daily">Daily Picks</a>
        <a class="tab """ + ("active" if tab=="builder" else "") + """ href="/?tab=builder">Bet Builder</a>
        <a class="tab """ + ("active" if tab=="ai" else "") + """ href="/?tab=ai">AI Acca Generator</a>
        <a class="tab """ + ("active" if tab=="future" else "") + """ href="/?tab=future">Future (3-Day Value)</a>
        <a class="tab """ + ("active" if tab=="bankers" else "") + """ href="/?tab=bankers">Bankers Daily</a>
        <a class="tab """ + ("active" if tab=="advanced" else "") + """ href="/?tab=advanced">Acca Generator</a>
    </nav>
"""

    html_content = ""

    # TAB 1 — Daily Picks
    if tab == "daily":
        html_content = '<div class="card"><h2>📊 Daily High‑Confluence Value Picks</h2>'
        for fx in FIXTURES["2026-11-05"]:
            html_content += f'<div class="match"><div class="m-head"><span class="teams">{fx["home"]} vs {fx["away"]}</span><span class="m-time">{fx["time"]}</span></div>'
            html_content += f'<div class="league">{fx["league"]}</div>'
            for mk in fx["markets"]:
                e = edge(mk["odds"], mk["prob"])
                html_content += f'<div class="mkt"><div class="mkt-nm">{mk["name"]}</div><div class="mkt-dets"><span class="odds">Odds: {mk["odds"]}</span><span>Prob: {mk["prob"]*100:.1f}%</span><span class="edge">Edge: +{e}%</span></div></div>'
            html_content += "</div>"
        html_content += "</div>"

    # TAB 2 — Bet Builder
    elif tab == "builder":
        html_content = '<div class="card"><h2>🔨 Custom Bet Builder</h2><form method="GET"><input type="hidden" name="tab" value="builder">'
        for fx in FIXTURES["2026-11-05"]:
            html_content += f'<div class="match"><div class="m-head"><span class="teams">{fx["home"]} vs {fx["away"]}</span><span class="m-time">{fx["time"]}</span></div>'
            html_content += f'<div class="league">{fx["league"]}</div>'
            for mk in fx["markets"]:
                checked = "checked" if f"{fx['home']}-{mk['name']}" in selected else ""
                html_content += f'<label class="mkt" style="cursor:pointer"><input type="checkbox" name="markets" value="{fx["home"]}-{mk["name"]}" {checked} class="chk">{mk["name"]} — <span class="odds">@{mk["odds"]}</span></label>'
            html_content += "</div>"
        html_content += '<button type="submit" class="btn">Build Custom Slip</button></form>'
        if selected:
            total_odds = 1.0
            picks = []
            for fx in FIXTURES["2026-11-05"]:
                for mk in fx["markets"]:
                    val = f"{fx['home']}-{mk['name']}"
                    if val in selected:
                        total_odds *= mk["odds"]
                        picks.append(f"{fx['home']} vs {fx['away']}: {mk['name']} (@{mk['odds']})")
            html_content += f'<div class="slip"><h3 style="margin-bottom:10px;">Your Custom Slip</h3>'
            for p in picks:
                html_content += f'<div style="margin:4px 0; font-size:14px;">• {p}</div>'
            html_content += f'<div style="margin-top:12px; font-weight:bold; font-size:16px;">Combined Odds: {total_odds:.2f}</div>'
            html_content += f'<div style="margin-top:6px; font-size:14px;">Stake: £20 → Return: £{20*total_odds:.2f}</div></div>'
        html_content += "</div>"

    # TAB 3 — AI Acca Generator
    elif tab == "ai":
        all_mkts = []
        for fx in FIXTURES["2026-11-05"]:
            for mk in fx["markets"]:
                all_mkts.append((-edge(mk["odds"], mk["prob"]), fx["home"], fx["away"], mk["name"], mk["odds"]))
        all_mkts.sort()
        top3 = all_mkts[:3]
        comb_odds = 1.0
        for _, h, a, n, o in top3:
            comb_odds *= o
        html_content = f'<div class="card"><h2>🤖 AI High‑Edge 3‑Fold Generator</h2><p style="color:#94a3b8; font-size:13px; margin-bottom:16px;">Auto‑selected picks with maximum calculated edge</p>'
        html_content += '<div class="slip"><h3 style="margin-bottom:10px;">AI Compiled 3‑Fold</h3>'
        for _, h, a, n, o in top3:
            html_content += f'<div style="margin:6px 0;">• {h} vs {a}<br><span style="padding-left:18px;">{n} — <span class="odds">@{o}</span></span></div>'
        html_content += f'<div style="margin-top:12px; font-weight:bold; font-size:16px;">Combined Odds: {comb_odds:.2f}</div>'
        html_content += f'<div style="margin-top:6px;">Stake: £20 → Return: £{20*comb_odds:.2f}</div></div></div>'

    # TAB 4 — Future 3‑Day Value
    elif tab == "future":
        html_content = '<div class="card"><h2>📅 Future (3‑Day Value)</h2>'
        for dt in ["2026-11-05", "2026-11-06", "2026-11-07"]:
            html_content += f'<h3 style="color:#eab308; margin:16px 0 8px;">{dt}</h3>'
            for fx in FIXTURES.get(dt, []):
                html_content += f'<div class="match"><div class="m-head"><span class="teams">{fx["home"]} vs {fx["away"]}</span><span class="m-time">{fx["time"]}</span></div>'
                html_content += f'<div class="league">{fx["league"]}</div>'
                for mk in fx["markets"]:
                    e = edge(mk["odds"], mk["prob"])
                    html_content += f'<div class="mkt"><div class="mkt-nm">{mk["name"]}</div><div class="mkt-dets"><span class="odds">@{mk["odds"]}</span><span class="edge">Edge: +{e}%</span></div></div>'
                html_content += "</div>"
        html_content += "</div>"

    # TAB 5 — Bankers Daily
    elif tab == "bankers":
        html_content = '<div class="card"><h2>💰 Bankers Daily (Confidence ≥ 75%)</h2>'
        for fx in FIXTURES["2026-11-05"]:
            if fx["banker"]:
                html_content += f'<div class="match banker"><div class="m-head"><span class="teams">{fx["home"]} vs {fx["away"]}<span class="banker-tag">BANKER</span></span><span class="m-time">{fx["time"]}</span></div>'
                html_content += f'<div class="league">{fx["league"]}</div>'
                for mk in fx["markets"]:
                    if mk["prob"] >= 0.75:
                        e = edge(mk["odds"], mk["prob"])
                        html_content += f'<div class="mkt" style="border-color:#eab308;"><div class="mkt-nm">{mk["name"]}</div><div class="mkt-dets"><span class="odds">@{mk["odds"]}</span><span>Conf: {mk["prob"]*100:.1f}%</span><span class="edge">Edge: +{e}%</span></div></div>'
                html_content += "</div>"
        html_content += "</div>"

    # TAB 6 — Advanced Acca Generator
    elif tab == "advanced":
        html_content = '<div class="card"><h2>⚙️ Advanced Acca Generator</h2>'
        html_content += f'<form method="GET"><input type="hidden" name="tab" value="advanced"><div class="form-row">'
        html_content += f'<div class="form-col"><label>Select Date</label><input type="date" name="date" value="{sel_date}"></div>'
        html_content += f'<div class="form-col"><label>Number of Legs</label><select name="legs">'
        for n in range(1, 21):
            sel = "selected" if n == legs else ""
            html_content += f'<option value="{n}" {sel}>{n}</option>'
        html_content += "</select></div>"
        html_content += f'<div class="form-col"><label>Market Filter</label><select name="market_filter">'
        for opt in ["ALL", "Goals", "BTTS", "Double Chance", "1X2"]:
            sel = "selected" if opt == mfilter else ""
            html_content += f'<option value="{opt}" {sel}>{opt}</option>'
        html_content += "</select></div></div>"
        html_content += '<button type="submit" class="btn">Generate Custom Acca</button></form>'

        slate = FIXTURES.get(sel_date, FIXTURES["2026-11-05"])
        pool = []
        for fx in slate:
            for mk in fx["markets"]:
                if mfilter == "ALL" or mfilter in mk["type"]:
                    pool.append((-edge(mk["odds"], mk["prob"]), fx["home"], fx["away"], mk["name"], mk["odds"]))
        pool.sort()
        selected_legs = pool[:legs]
        if selected_legs:
            total = 1.0
            for _, h, a, n, o in selected_legs:
                total *= o
            html_content += f'<div class="slip"><h3 style="margin-bottom:10px;">{legs}-Leg Accumulator — {sel_date}</h3>'
            for _, h, a, n, o in selected_legs:
                html_content += f'<div style="margin:4px 0; font-size:14px;">• {h} vs {a}: {n} (@{o})</div>'
            html_content += f'<div style="margin-top:12px; font-weight:bold; font-size:16px;">Combined Odds: {total:.2f}</div>'
            html_content += f'<div style="margin-top:6px;">Stake: £20 → Return: £{20*total:.2f}</div></div>'
        else:
            html_content += '<p style="color:#f87171; margin-top:16px;">No markets match your selected filters.</p>'
        html_content += "</div>"

    html_end = """
</div>
</body>
</html>
    """

    return render_template_string(html_top + html_content + html_end)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
