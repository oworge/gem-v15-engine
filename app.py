from flask import Flask,request
app=Flask(__name__)

FIXTURES={
"2026-11-05":[
{"home":"AC Milan","away":"Ferencváros","league":"UEFA Europa League","time":"17:45 GMT","banker":True,
"markets":[{"name":"Over 1.5 Goals & Milan 1X","odds":1.42,"prob":0.77,"type":"Goals/DC"},
{"name":"BTTS — Yes","odds":1.72,"prob":0.62,"type":"BTTS"},
{"name":"AC Milan Win","odds":1.35,"prob":0.78,"type":"1X2"}]},
{"home":"Bayer Leverkusen","away":"Marseille","league":"UEFA Europa League","time":"20:00 GMT","banker":True,
"markets":[{"name":"Over 1.5 Goals","odds":1.35,"prob":0.80,"type":"Goals"},
{"name":"Leverkusen Win","odds":1.42,"prob":0.76,"type":"1X2"}]},
{"home":"Real Sociedad","away":"Lyon","league":"UEFA Europa League","time":"17:45 GMT","banker":False,
"markets":[{"name":"Over 1.5 Goals","odds":1.30,"prob":0.81,"type":"Goals"},
{"name":"Draw or Lyon (X2)","odds":1.50,"prob":0.71,"type":"Double Chance"}]}
],
"2026-11-06":[
{"home":"Borussia Dortmund","away":"VfB Stuttgart","league":"Bundesliga","time":"19:30 GMT","banker":True,
"markets":[{"name":"Over 2.5 Goals","odds":1.50,"prob":0.75,"type":"Goals"}]}
],
"2026-11-07":[
{"home":"Manchester City","away":"Liverpool","league":"Premier League","time":"12:30 GMT","banker":True,
"markets":[{"name":"BTTS & Over 2.5","odds":1.65,"prob":0.72,"type":"BTTS"}]}
]}

def edge(o,p):return round((p-1/o)*100,2)

@app.route("/")
def idx():
    tab=request.args.get("tab","daily").strip()
    dt=request.args.get("date","2026-11-05").strip()
    legs=int(request.args.get("legs",3))
    mf=request.args.get("market_filter","ALL").strip()
    sel=request.args.getlist("markets")

    h="""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>EDGEMETRIX V300</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0b0f19;color:#f1f5f9;font-family:sans-serif;padding:16px}
.wrap{max-width:760px;margin:0 auto}
.hdr{text-align:center;margin-bottom:20px}
h1{color:#38bdf8;font-size:22px}
.tabs{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:16px;border-bottom:1px solid #1e293b;padding-bottom:8px}
.tab{padding:9px 11px;border-radius:8px;text-decoration:none;font-size:12px;font-weight:600;background:#1e293b;color:#94a3b8;border:1px solid transparent}
.tab.active{background:#0284c7;color:white;border-color:#38bdf8}
.card{background:#1e293b;border-radius:12px;padding:18px;margin-bottom:14px;border:1px solid #334155}
.card h2{color:#e2e8f0;font-size:16px;margin-bottom:14px;padding-bottom:8px;border-bottom:1px solid #334155}
.match{background:#0f172a;border-radius:10px;padding:12px;margin-bottom:10px;border-left:3px solid #38bdf8}
.match.banker{border-left-color:#eab308}
.m-head{display:flex;justify-content:space-between;margin-bottom:4px}
.teams{font-weight:700}
.m-time{color:#94a3b8;font-size:12px}
.league{color:#94a3b8;font-size:12px;margin-bottom:8px}
.mkt{background:#1e293b;border-radius:8px;padding:10px;margin:6px 0;border:1px solid #334155}
.odds{color:#fbbf24;font-weight:600}
.edge{color:#4ade80;font-weight:700}
.banker-tag{background:#eab308;color:#0f172a;padding:2px 6px;border-radius:4px;font-size:10px;font-weight:bold;margin-left:8px}
select,input[type="date"]{background:#0f172a;color:white;border:1px solid #38bdf8;padding:7px;border-radius:6px}
.btn{background:#16a34a;color:white;border:none;padding:11px;border-radius:8px;font-weight:bold;cursor:pointer;width:100%;font-size:15px;margin-top:8px}
.slip{background:#0369a1;border-radius:10px;padding:14px;margin-top:14px;border:1px solid #38bdf8}
.chk{margin-right:8px}
.fr{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:10px}
.fc{flex:1;min-width:140px}
label{font-size:13px;color:#94a3b8;display:block;margin-bottom:3px}
.empty{color:#f87171;text-align:center;padding:16px}
</style></head><body><div class="wrap">
<div class="hdr"><h1>⚽ EDGEMETRIX V300</h1><p style="color:#4ade80;font-size:13px">● LIVE — All Tabs Active</p></div>
<nav class="tabs">
<a class="tab """+("active"if tab=="daily"else"")+""" href="/?tab=daily">Daily</a>
<a class="tab """+("active"if tab=="builder"else"")+""" href="/?tab=builder">Bet Builder</a>
<a class="tab """+("active"if tab=="ai"else"")+""" href="/?tab=ai">AI Acca</a>
<a class="tab """+("active"if tab=="future"else"")+""" href="/?tab=future">Future</a>
<a class="tab """+("active"if tab=="bankers"else"")+""" href="/?tab=bankers">Bankers</a>
<a class="tab """+("active"if tab=="advanced"else"")+""" href="/?tab=advanced">Acca Gen</a>
</nav>"""

    # TAB1: Daily Picks
    if tab=="daily":
        h+='<div class="card"><h2>📊 Daily Picks — 2026-11-05</h2>'
        fxz=FIXTURES.get("2026-11-05",[])
        if not fxz:h+='<p class="empty">No fixtures</p>'
        else:
            for fx in fxz:
                h+=f'<div class="match"><div class="m-head"><span class="teams">{fx["home"]} vs {fx["away"]}</span><span class="m-time">{fx["time"]}</span></div>'
                h+=f'<div class="league">{fx["league"]}</div>'
                for mk in fx["markets"]:
                    h+=f'<div class="mkt"><div>{mk["name"]}</div><div>Odds: <span class="odds">{mk["odds"]}</span> | Prob: {mk["prob"]*100:.1f}% | Edge: <span class="edge">+{edge(mk["odds"],mk["prob"])}%</span></div></div>'
                h+="</div>"
        h+="</div>"

    # TAB2: Bet Builder
    elif tab=="builder":
        h+='<div class="card"><h2>🔨 Bet Builder</h2><form method="GET"><input type="hidden" name="tab" value="builder">'
        for fx in FIXTURES.get("2026-11-05",[]):
            h+=f'<div class="match"><div class="m-head"><span class="teams">{fx["home"]} vs {fx["away"]}</span><span class="m-time">{fx["time"]}</span></div>'
            h+=f'<div class="league">{fx["league"]}</div>'
            for mk in fx["markets"]:
                v=f"{fx['home']}||{mk['name']}"
                ch="checked"if v in sel else""
                h+=f'<label class="mkt" style="cursor:pointer"><input type="checkbox" name="markets" value="{v}" {ch} class="chk">{mk["name"]} — <span class="odds">@{mk["odds"]}</span></label>'
            h+="</div>"
        h+='<button type="submit" class="btn">Build Slip</button></form>'
        if sel:
            tot=1.0;ps=[]
            for fx in FIXTURES.get("2026-11-05",[]):
                for mk in fx["markets"]:
                    if f"{fx['home']}||{mk['name']}"in sel:
                        tot*=mk["odds"];ps.append(f"{fx['home']} vs {fx['away']}: {mk['name']} @{mk['odds']}")
            if ps:
                h+='<div class="slip"><h3>Your Slip</h3>'
                for p in ps:h+=f'<div style="margin:4px 0">{p}</div>'
                h+=f'<div style="margin-top:10px;font-weight:bold">Combined: {tot:.2f}</div><div>Stake £20 → Return £{20*tot:.2f}</div></div>'
        h+="</div>"

    # TAB3: AI Acca
    elif tab=="ai":
        mkts=[]
        for fx in FIXTURES.get("2026-11-05",[]):
            for mk in fx["markets"]:mkts.append((-edge(mk["odds"],mk["prob"]),fx["home"],fx["away"],mk["name"],mk["odds"]))
        mkts.sort();top=mkts[:3]
        h+='<div class="card"><h2>🤖 AI High-Edge 3-Fold</h2>'
        if not top:h+='<p class="empty">No data</p>'
        else:
            to=1.0
            h+='<div class="slip"><h3>Top 3 Picks</h3>'
            for _,h_,a,n,o in top:to*=o;h+=f'<div style="margin:6px 0">• {h_} vs {a}<br>&nbsp;&nbsp;{n} — <span class="odds">@{o}</span></div>'
            h+=f'<div style="margin-top:10px;font-weight:bold">Combined Odds: {to:.2f}</div><div>£20 stake → £{20*to:.2f}</div></div>'
        h+="</div>"

    # TAB4: Future
    elif tab=="future":
        h+='<div class="card"><h2>📅 Future 3-Day Value</h2>'
        for d in ["2026-11-05","2026-11-06","2026-11-07"]:
            h+=f'<h3 style="color:#eab308;margin:14px 0 6px">{d}</h3>'
            day=FIXTURES.get(d,[])
            if not day:h+='<p style="color:#64748b;font-size:13px">No fixtures</p>';continue
            for fx in day:
                h+=f'<div class="match"><div class="m-head"><span class="teams">{fx["home"]} vs {fx["away"]}</span><span class="m-time">{fx["time"]}</span></div>'
                h+=f'<div class="league">{fx["league"]}</div>'
                for mk in fx["markets"]:h+=f'<div class="mkt"><div>{mk["name"]}</div><div>Odds: <span class="odds">@{mk["odds"]}</span> | Edge: <span class="edge">+{edge(mk["odds"],mk["prob"])}%</span></div></div>'
                h+="</div>"
        h+="</div>"

    # TAB5: Bankers
    elif tab=="bankers":
        h+='<div class="card"><h2>💰 Bankers Daily (≥75% Conf)</h2>';fd=False
        for fx in FIXTURES.get("2026-11-05",[]):
            if fx.get("banker"):
                fd=True
                h+=f'<div class="match banker"><div class="m-head"><span class="teams">{fx["home"]} vs {fx["away"]}<span class="banker-tag">BANKER</span></span><span class="m-time">{fx["time"]}</span></div>'
                h+=f'<div class="league">{fx["league"]}</div>'
                for mk in fx["markets"]:
                    if mk["prob"]>=0.75:h+=f'<div class="mkt" style="border-color:#eab308"><div>{mk["name"]}</div><div>Odds: <span class="odds">@{mk["odds"]}</span> | Conf: {mk["prob"]*100:.1f}% | Edge: <span class="edge">+{edge(mk["odds"],mk["prob"])}%</span></div></div>'
                h+="</div>"
        if not fd:h+='<p class="empty">No bankers today</p>'
        h+="</div>"

    # TAB6: Acca Generator
    elif tab=="advanced":
        h+='<div class="card"><h2>⚙️ Advanced Acca Generator</h2>'
        h+=f'<form method="GET"><input type="hidden" name="tab" value="advanced"><div class="fr">'
        h+=f'<div class="fc"><label>Date</label><input type="date" name="date" value="{dt}"></div>'
        h+=f'<div class="fc"><label>Legs (1-20)</label><select name="legs">'
        for n in range(1,21):h+=f'<option value="{n}">{"selected"if n==legs else""}</option>'
        h+="</select></div>"
        h+=f'<div class="fc"><label>Filter</label><select name="market_filter">'
        for o in ["ALL","Goals","BTTS","Double Chance","1X2"]:h+=f'<option value="{o}">{"selected"if o==mf else""}</option>'
        h+="</select></div></div>"
        h+='<button type="submit" class="btn">Generate Acca</button></form>'
        sl=FIXTURES.get(dt,FIXTURES.get("2026-11-05",[]))
        pl=[]
        for fx in sl:
            for mk in fx["markets"]:
                if mf=="ALL"or mf in mk.get("type",""):pl.append((-edge(mk["odds"],mk["prob"]),fx["home"],fx["away"],mk["name"],mk["odds"]))
        pl.sort();sel=pl[:legs]
        if sel:
            to=1.0
            for _,_,_,_,o in sel:to*=o
            h+=f'<div class="slip"><h3>{legs}-Leg Acca — {dt}</h3>'
            for _,h_,a,n,o in sel:h+=f'<div style="margin:4px 0">{h_} vs {a}: {n} @{o}</div>'
            h+=f'<div style="margin-top:10px;font-weight:bold">Combined: {to:.2f}</div><div>£20 → £{20*to:.2f}</div></div>'
        h+="</div>"

    return h+"</div></body></html>"

if __name__=="__main__":app.run(host="0.0.0.0",port=5000)
