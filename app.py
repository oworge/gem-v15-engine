from flask import Flask, render_template_string, request
import os

app = Flask(__name__)

FIXTURES_DATA = {
    "2026-11-06": [
        {
            "id": 1,
            "home": "Hammarby IF",
            "away": "IF Elfsborg",
            "league": "Allsvenskan",
            "time": "18:00 GMT",
            "banker": True,
            "markets": [
                {"id": "1_1", "name": "Hammarby 1X & Over 1.5 Goals", "odds": 1.30, "prob": 0.835, "type": "Goals/DC"},
                {"id": "1_2", "name": "Hammarby Win", "odds": 1.65, "prob": 0.68, "type": "1X2"}
            ]
        },
        {
            "id": 2,
            "home": "Everton",
            "away": "Coventry City",
            "league": "Premier League",
            "time": "20:00 GMT",
            "banker": True,
            "markets": [
                {"id": "2_1", "name": "Everton 1X & Over 1.5 Goals", "odds": 1.32, "prob": 0.812, "type": "Goals/DC"},
                {"id": "2_2", "name": "Everton Win", "odds": 1.70, "prob": 0.65, "type": "1X2"}
            ]
        },
        {
            "id": 3,
            "home": "Sevilla",
            "away": "Deportivo Alavés",
            "league": "La Liga",
            "time": "20:00 GMT",
            "banker": True,
            "markets": [
                {"id": "3_1", "name": "Sevilla 1X Double Chance", "odds": 1.26, "prob": 0.82, "type": "Double Chance"},
                {"id": "3_2", "name": "Sevilla Win", "odds": 1.90, "prob": 0.58, "type": "1X2"}
            ]
        },
        {
            "id": 4,
            "home": "Silkeborg",
            "away": "Lyngby",
            "league": "Superliga",
            "time": "18:00 GMT",
            "banker": False,
            "markets": [
                {"id": "4_1", "name": "Over 1.5 Goals Floor Play", "odds": 1.35, "prob": 0.80, "type": "Goals"}
            ]
        }
    ],
    "2026-11-07": [
        {
            "id": 5,
            "home": "Valencia",
            "away": "Real Madrid",
            "league": "La Liga",
            "time": "21:00 CET",
            "banker": True,
            "markets": [
                {"id": "5_1", "name": "Real Madrid Win & Over 1.5", "odds": 1.42, "prob": 0.78, "type": "Goals/1X2"}
            ]
        }
    ]
}

def calc_edge(odds, prob):
    return round((prob - (1 / odds)) * 100, 2)

@app.route("/")
def index():
    active_tab = request.args.get("tab", "daily_picks")
    selected_date = request.args.get("date", "2026-11-06")
    legs_count = int(request.args.get("legs", 3))
    market_filter = request.args.get("market_filter", "ALL")

    slate = FIXTURES_DATA.get(selected_date, FIXTURES_DATA["2026-11-06"])
    selected_market_ids = request.args.getlist("builder_market")

    html = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>EDGEMETRIX V300</title><style>
    body { background: radial-gradient(circle at top, #0f172a 0%, #0b0f19 100%); color: #f1f5f9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding: 16px; margin: 0; min-height: 100vh; }
    .header { background: #1e293b; padding: 18px 20px; border-radius: 12px; border: 1px solid rgba(56, 189, 248, 0.2); margin-bottom: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.4); }
    .title { color: #38bdf8; font-size: 24px; font-weight: 800; margin: 0; letter-spacing: -0.5px; }
    .tabs { display: flex; gap: 8px; overflow-x: auto; padding-bottom: 8px; border-bottom: 2px solid #334155; margin-bottom: 20px; }
    .tab-btn { background: #1e293b; color: #94a3b8; padding: 10px 16px; border-radius: 8px; text-decoration: none; font-size: 13px; font-weight: 700; white-space: nowrap; border: 1px solid #334155; transition: all 0.2s ease; }
    .tab-btn:hover { color: #f1f5f9; border-color: rgba(56, 189, 248, 0.4); }
    .tab-btn.active { background: #0284c7; color: white; border-color: #38bdf8; box-shadow: 0 4px 12px rgba(2, 132, 199, 0.4); }
    .card { background: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid rgba(56, 189, 248, 0.15); margin-bottom: 16px; box-shadow: 0 4px 16px rgba(0,0,0,0.3); }
    .match-card { background: #0f172a; padding: 16px; border-radius: 10px; margin-bottom: 12px; border: 1px solid #334155; transition: transform 0.2s ease, border-color 0.2s ease; }
    .match-card:hover { transform: translateY(-2px); border-color: rgba(56, 189, 248, 0.4); }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 10px; margin-top: 10px; }
    .market-item { background: #1e293b; padding: 10px 12px; border-radius: 6px; border: 1px solid #334155; font-size: 13px; display: block; font-family: monospace; }
    .edge-badge { color: #4ade80; font-weight: bold; text-shadow: 0 0 8px rgba(74, 222, 128, 0.2); }
    .banker-badge { background: #eab308; color: #0f172a; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }
    select, input[type="date"] { background: #0f172a; color: white; border: 1px solid #38bdf8; padding: 8px 12px; border-radius: 6px; font-size: 14px; }
    .btn { background: #16a34a; color: white; border: none; padding: 12px 20px; border-radius: 8px; font-weight: bold; cursor: pointer; width: 100%; font-size: 14px; transition: background 0.2s ease; }
    .btn:hover { background: #15803d; }
    .slip { background: #0369a1; border-radius: 10px; padding: 16px; color: white; margin-top: 16px; border: 1px solid #38bdf8; box-shadow: 0 4px 16px rgba(3, 105, 161, 0.3); }
    .mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }
    </style></head><body><div class="header"><h1 class="title">EDGEMETRIX V300</h1><div style="color:#38bdf8; font-size:12px; margin-top:4px;">Quantitative Football Analytics Engine — Sharpened Terminal UI</div></div><div class="tabs"><a class="tab-btn """ + ('active' if active_tab=='daily_picks' else '') + """" href="/?tab=daily_picks">Daily Picks</a><a class="tab-btn """ + ('active' if active_tab=='bet_builder' else '') + """" href="/?tab=bet_builder">Bet Builder</a><a class="tab-btn """ + ('active' if active_tab=='ai_acca' else '') + """" href="/?tab=ai_acca">AI Acca Generator</a><a class="tab-btn """ + ('active' if active_tab=='future' else '') + """" href="/?tab=future">Future (3-Day Value)</a><a class="tab-btn """ + ('active' if active_tab=='bankers' else '') + """" href="/?tab=bankers">Bankers Daily</a><a class="tab-btn """ + ('active' if active_tab=='acca_gen' else '') + """" href="/?tab=acca_gen">Acca Generator Tab</a></div>"""

    if active_tab == 'daily_picks':
        html += '<div class="card"><h2 style="color:#38bdf8;margin-top:0;">Daily High-Confluence Value Picks (Nov 6)</h2>'
        for f in slate:
            html += f'''<div class="match-card"><div style="display:flex;justify-content:space-between;"><strong>{f['home']} vs {f['away']}</strong><span style="color:#38bdf8;font-size:12px;" class="mono">{f['time']}</span></div><div style="color:#94a3b8;font-size:12px;margin-bottom:8px;">{f['league']}</div><div class="grid">'''
            for m in f['markets']:
                edge = calc_edge(m['odds'], m['prob'])
                html += f'''<div class="market-item"><strong>{m['name']}</strong> (@<span class="mono">{m['odds']}</span>)<br>Prob: <span class="mono">{m['prob']*100:.1f}%</span> | <span class="edge-badge">Edge: +{edge}%</span></div>'''
            html += '</div></div>'
        html += '</div>'

    elif active_tab == 'bet_builder':
        html += '<div class="card"><h2 style="color:#38bdf8;margin-top:0;">Custom Bet Builder</h2><form method="GET"><input type="hidden" name="tab" value="bet_builder">'
        for f in slate:
            html += f'''<div class="match-card"><strong>{f['home']} vs {f['away']}</strong><div class="grid">'''
            for m in f['markets']:
                checked = 'checked' if m['id'] in selected_market_ids else ''
                html += f'''<label class="market-item" style="cursor:pointer;"><input type="checkbox" name="builder_market" value="{m['id']}" {checked}> <strong>{m['name']}</strong> (@<span class="mono">{m['odds']}</span>)</label>'''
            html += '</div></div>'
        html += '<button type="submit" class="btn">Build Custom Slip</button></form>'
        if selected_market_ids:
            tot_odds = 1.0
            legs = []
            for f in slate:
                for m in f['markets']:
                    if m['id'] in selected_market_ids:
                        tot_odds *= m['odds']
                        legs.append((f"{f['home']} vs {f['away']}", m['name'], m['odds']))
            html += f'''<div class="slip"><h3 style="margin-top:0;">Selected Bet Builder Slip</h3><div>Combined Odds: <strong class="mono">@{tot_odds:.2f}</strong></div>'''
            for fix, m_name, o in legs:
                html += f'<div style="font-size:13px;margin-top:4px;" class="mono">• {fix} — {m_name} (@{o})</div>'
            html += f'<div style="margin-top:10px;">Recommended Stake: £20.00 | Potential Return: <strong class="mono">£{20*tot_odds:.2f}</strong></div></div>'
        html += '</div>'

    elif active_tab == 'ai_acca':
        html += '<div class="card"><h2 style="color:#38bdf8;margin-top:0;">AI High-Edge Acca Generator</h2><p style="color:#94a3b8;font-size:13px;">Auto-generated 3-fold based on maximum engine edge.</p>'
        all_markets = []
        for f in slate:
            for m in f['markets']:
                edge = calc_edge(m['odds'], m['prob'])
                all_markets.append((edge, f"{f['home']} vs {f['away']}", m['name'], m['odds']))
        all_markets.sort(key=lambda x: x[0], reverse=True)
        top_3 = all_markets[:3]
        combined = 1.0
        for leg in top_3:
            combined *= leg[3]
        html += f'''<div class="slip"><h3 style="margin-top:0;">AI Compiled 3-Fold Slip</h3><div>Combined Odds: <strong class="mono">@{combined:.2f}</strong></div>'''
        for edge, fix, m_name, o in top_3:
            html += f'<div style="font-size:13px;margin-top:6px;" class="mono">• <strong>{fix}</strong> — {m_name} (@{o}) <span class="edge-badge">[+{edge}% Edge]</span></div>'
        html += f'<div style="margin-top:12px;">Recommended Stake: £20.00 | Potential Return: <strong class="mono">£{20*combined:.2f}</strong></div></div></div>'

    elif active_tab == 'future':
        html += '<div class="card"><h2 style="color:#38bdf8;margin-top:0;">3-Day Future Value Slate</h2>'
        for d in ['2026-11-07', '2026-11-08']:
            html += f'<h3 style="color:#eab308;border-bottom:1px solid #334155;padding-bottom:4px;">Fixtures for {d}</h3>'
            for f in FIXTURES_DATA.get(d, []):
                html += f'''<div class="match-card"><strong>{f['home']} vs {f['away']}</strong> <span class="mono">({f['league']} - {f['time']})</span><div class="grid">'''
                for m in f['markets']:
                    edge = calc_edge(m['odds'], m['prob'])
                    html += f'''<div class="market-item">{m['name']} (@<span class="mono">{m['odds']}</span>) | <span class="edge-badge">Edge: +{edge}%</span></div>'''
                html += '</div></div>'
        html += '</div>'

    elif active_tab == 'bankers':
        html += '<div class="card"><h2 style="color:#eab308;margin-top:0;">Bankers Daily (Lowest Variance Picks)</h2>'
        for f in slate:
            if f['banker']:
                html += f'''<div class="match-card"><div style="display:flex;justify-content:space-between;"><strong>{f['home']} vs {f['away']}</strong><span class="banker-badge">HIGH CONFIDENCE BANKER</span></div><div class="grid" style="margin-top:8px;">'''
                for m in f['markets']:
                    if m['prob'] >= 0.75:
                        html += f'''<div class="market-item" style="border-color:#eab308;"><strong>{m['name']}</strong> (@<span class="mono">{m['odds']}</span>)<br>Model Confidence: <strong class="mono">{m['prob']*100:.1f}%</strong></div>'''
                html += '</div></div>'
        html += '</div>'

    elif active_tab == 'acca_gen':
        html += f'''<div class="card"><h2 style="color:#38bdf8;margin-top:0;">Advanced Acca Generator</h2><form method="GET" style="display:grid;grid-template-columns:repeat(auto-fit, minmax(200px, 1fr));gap:12px;margin-bottom:16px;"><input type="hidden" name="tab" value="acca_gen"><div><label style="font-size:12px;color:#94a3b8;display:block;margin-bottom:4px;">1. Select Date (Calendar):</label><input type="date" name="date" value="{selected_date}" style="width:100%;"></div><div><label style="font-size:12px;color:#94a3b8;display:block;margin-bottom:4px;">2. Number of Legs (1-20 Dropdown):</label><select name="legs" style="width:100%;">'''
        for i in range(1, 21):
            sel = 'selected' if i == legs_count else ''
            html += f'<option value="{i}" {sel}>{i} Leg{"s" if i > 1 else ""}</option>'
        html += f'''</select></div><div><label style="font-size:12px;color:#94a3b8;display:block;margin-bottom:4px;">3. Market Selection Dropdown:</label><select name="market_filter" style="width:100%;"><option value="ALL" {'selected' if market_filter=='ALL' else ''}>All Markets</option><option value="Goals" {'selected' if market_filter=='Goals' else ''}>Over/Under Goals</option><option value="Double Chance" {'selected' if market_filter=='Double Chance' else ''}>Double Chance (1X/X2)</option><option value="BTTS" {'selected' if market_filter=='BTTS' else ''}>Both Teams To Score</option></select></div><div style="grid-column: 1 / -1;"><button type="submit" class="btn">Generate Custom Acca</button></div></form>'''
        pool = []
        for f in slate:
            for m in f['markets']:
                if market_filter == 'ALL' or market_filter in m['type']:
                    edge = calc_edge(m['odds'], m['prob'])
                    pool.append((edge, f"{f['home']} vs {f['away']}", m['name'], m['odds']))
        pool.sort(key=lambda x: x[0], reverse=True)
        generated_legs = pool[:legs_count]
        if generated_legs:
            acc_odds = 1.0
            for leg in generated_legs:
                acc_odds *= leg[3]
            html += f'''<div class="slip"><h3 style="margin-top:0;">Generated {len(generated_legs)}-Leg Accumulator Slip</h3><div style="font-size:14px;margin-bottom:10px;">Date: <strong class="mono">{selected_date}</strong> | Combined Odds: <strong class="mono">@{acc_odds:.2f}</strong></div>'''
            for edge, fix, m_name, o in generated_legs:
                html += f'<div style="font-size:13px;margin-top:6px;border-bottom:1px solid rgba(255,255,255,0.2);padding-bottom:4px;" class="mono">• <strong>{fix}</strong> — {m_name} (@{o}) <span class="edge-badge">[+{edge}% Edge]</span></div>'
            html += f'<div style="margin-top:12px;">Recommended Stake: £20.00 | Potential Return: <strong class="mono">£{20*acc_odds:.2f}</strong></div></div>'
        else:
            html += '<p style="color:#f87171;">No matching markets found for the selected filters.</p>'
        html += '</div>'

    html += '</body></html>'
    return render_template_string(html)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
