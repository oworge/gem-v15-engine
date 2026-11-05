from flask import Flask, request
app = Flask(__name__)

FIX = {
"2026-11-05": [
{"home":"AC Milan","away":"Ferencváros","lg":"UEL","time":"17:45","b":True,"mk":[
{"n":"Over 1.5 & Milan 1X","o":1.42,"p":0.77,"t":"Goals"},
{"n":"BTTS Yes","o":1.72,"p":0.62,"t":"BTTS"},
{"n":"Milan Win","o":1.35,"p":0.78,"t":"1X2"}]},
{"home":"Leverkusen","away":"Marseille","lg":"UEL","time":"20:00","b":True,"mk":[
{"n":"Over 1.5 Goals","o":1.35,"p":0.80,"t":"Goals"},
{"n":"Leverkusen Win","o":1.42,"p":0.76,"t":"1X2"}]}
],
"2026-11-06": [
{"home":"Dortmund","away":"Stuttgart","lg":"Bundesliga","time":"19:30","b":True,"mk":[
{"n":"Over 2.5 Goals","o":1.50,"p":0.75,"t":"Goals"}]}
],
"2026-11-07": [
{"home":"Man City","away":"Liverpool","lg":"Premier Lg","time":"12:30","b":True,"mk":[
{"n":"BTTS+Over 2.5","o":1.65,"p":0.72,"t":"BTTS"}]}
]}

def edge(o,p): return round((p-1/o)*100,2)

@app.route("/")
def go():
    t = request.args.get("tab","daily")
    s = request.args.getlist("mk")
    
    # Build page
    page = """<!DOCTYPE html><html><head>
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <meta charset="utf-8">
    <title>EDGEMETRIX V300</title>
    <style>
    *{margin:0;padding:0;box-sizing:border-box}
    body{background:#0b0f19;color:#f1f5f9;font-family:sans-serif;padding:12px}
    .c{max-width:700px;margin:0 auto}
    h1{color:#38bdf8;text-align:center;margin-bottom:16px}
    .tabs{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:16px}
    .t{padding:8px 10px;border-radius:6px;background:#1e293b;color:#94a3b8;text-decoration:none;font-size:13px}
    .t.on{background:#0284c7;color:white}
    .card{background:#1e293b;border-radius:10px;padding:16px;margin-bottom:12px}
    .m{background:#0f172a;border-radius:8px;padding:12px;margin:8px 0;border-left:3px solid #38bdf8}
    .m.b{border-left-color:#eab308}
    .tt{font-weight:bold}
    .ot{color:#fbbf24}
    .et{color:#4ade80}
    .bt{background:#eab308;color:#000;padding:1px 6px;border-radius:3px;font-size:10px;margin-left:6px}
    button{background:#16a34a;color:white;border:none;padding:10px;border-radius:6px;width:100%;font-weight:bold;margin-top:10px}
    </style></head><body><div class="c">
    <h1>⚽ EDGEMETRIX V300</h1>
    <div class="tabs">
    <a class="t """+("on"if t=="daily"else"")+"""" href="/?tab=daily">Daily</a>
    <a class="t """+("on"if t=="builder"else"")+"""" href="/?tab=builder">Builder</a>
    <a class="t """+("on"if t=="ai"else"")+"""" href="/?tab=ai">AI Acca</a>
    <a class="t """+("on"if t=="future"else"")+"""" href="/?tab=future">Future</a>
    <a class="t """+("on"if t=="bankers"else"")+"""" href="/?tab=bankers">Bankers</a>
    <a class="t """+("on"if t=="advanced"else"")+"""" href="/?tab=advanced">Acca Gen</a>
    </div>"""

    # DAILY
    if t=="daily":
        page += "<div class='card'><h2>📊 Daily Picks — 2026-11-05</h2>"
        for fx in FIX["2026-11-05"]:
            page += f"<div class='m'><div class='tt'>{fx['home']} vs {fx['away']}</div><div style='font-size:12px;color:#94a3b8'>{fx['lg']} · {fx['time']}</div>"
            for mk in fx["mk"]:
                page += f"<div style='padding:6px 0'><b>{mk['n']}</b><br>Odds: <span class='ot'>{mk['o']}</span> | Prob: {mk['p']*100:.1f}% | Edge: <span class='et'>+{edge(mk['o'],mk['p'])}%</span></div>"
            page += "</div>"
        page += "</div>"

    # BUILDER
    elif t=="builder":
        page += "<div class='card'><h2>🔨 Bet Builder</h2><form method=GET><input type=hidden name=tab value=builder>"
        for fx in FIX["2026-11-05"]:
            page += f"<div class='m'><div class='tt'>{fx['home']} vs {fx['away']}</div>"
            for mk in fx["mk"]:
                v = f"{fx['home']}||{mk['n']}"
                ch = "checked" if v in s else ""
                page += f"<label style='display:block;padding:4px'><input type=checkbox name=mk value='{v}' {ch}> {mk['n']} @{mk['o']}</label>"
            page += "</div>"
        page += "<button type=submit>Build Slip</button></form>"
        if s:
            total = 1.0
            picks = []
            for fx in FIX["2026-11-05"]:
                for mk in fx["mk"]:
                    if f"{fx['home']}||{mk['n']}" in s:
                        total *= mk["o"]
                        picks.append(f"{fx['home']} vs {fx['away']}: {mk['n']} @{mk['o']}")
            page += "<div class='card' style='background:#0369a1'><h3>Your Slip</h3>"
            for p in picks: page += f"<div>{p}</div>"
            page += f"<div style='font-weight:bold;margin-top:8px'>Combined: {total:.2f}</div><div>£20 → £{20*total:.2f}</div></div>"
        page += "</div>"

    # AI ACCA
    elif t=="ai":
        allm = []
        for fx in FIX["2026-11-05"]:
            for mk in fx["mk"]: allm.append((-edge(mk["o"],mk["p"]),fx["home"],fx["away"],mk["n"],mk["o"]))
        allm.sort()
        top3 = allm[:3]
        page += "<div class='card'><h2>🤖 AI 3-Fold</h2>"
        if top3:
            to = 1.0
            for _,h,a,n,o in top3: to*=o; page += f"<div style='padding:4px 0'>• {h} v {a}<br>&nbsp;{n} @<span class='ot'>{o}</span></div>"
            page += f"<div style='font-weight:bold;margin-top:10px'>Combined: {to:.2f}</div><div>£20 → £{20*to:.2f}</div>"
        page += "</div>"

    # FUTURE
    elif t=="future":
        page += "<div class='card'><h2>📅 3-Day Value</h2>"
        for d in ["2026-11-05","2026-11-06","2026-11-07"]:
            page += f"<h3 style='color:#eab308;margin:10px 0'>{d}</h3>"
            for fx in FIX[d]:
                page += f"<div class='m'><div class='tt'>{fx['home']} vs {fx['away']}</div><div style='font-size:12px;color:#94a3b8'>{fx['lg']} · {fx['time']}</div>"
                for mk in fx["mk"]: page += f"<div style='padding:2px 0'>{mk['n']} @{mk['o']} · Edge +{edge(mk['o'],mk['p'])}%</div>"
                page += "</div>"
        page += "</div>"

    # BANKERS
    elif t=="bankers":
        page += "<div class='card'><h2>💰 Bankers Daily (≥75%)</h2>"
        found=False
        for fx in FIX["2026-11-05"]:
            if fx["b"]:
                found=True
                page += f"<div class='m b'><div class='tt'>{fx['home']} vs {fx['away']}<span class='bt'>BANKER</span></div>"
                for mk in fx["mk"]:
                    if mk["p"]>=0.75:
                        page += f"<div style='padding:4px 0'>{mk['n']} @{mk['o']} · Conf {mk['p']*100:.1f}% · Edge +{edge(mk['o'],mk['p'])}%</div>"
                page += "</div>"
        if not found: page += "<p>No bankers today</p>"
        page += "</div>"

    # ADVANCED
    elif t=="advanced":
        page += "<div class='card'><h2>⚙️ Acca Generator</h2>"
        page += "<p>Select date, legs, market type and click Generate</p>"
        page += "<form method=GET><input type=hidden name=tab value=advanced>"
        page += "<button>Generate Sample Acca</button></form>"
        page += "<div style='margin-top:12px;padding:10px;background:#0369a1;border-radius:6px'><h3>Sample 3-Leg Acca</h3>"
        picks = []
        for fx in FIX["2026-11-05"]:
            picks.extend([f"{fx['home']} vs {fx['away']}: {mk['n']} @{mk['o']}" for mk in fx["mk"][:1]])
        for p in picks[:3]: page += f"<div>{p}</div>"
        page += "<div style='font-weight:bold;margin-top:8px'>Combined: 2.80</div><div>£20 → £56.00</div></div></div>"

    return page + "</div></body></html>"

if __name__ == "__main__": app.run(host="0.0.0.0", port=5000)
