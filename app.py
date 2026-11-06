from flask import Flask, render_template_string, request, jsonify
import os
from datetime import datetime, date
import logging
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("EDGEMETRIX")

app = Flask(__name__)

# ============================================================
# HIGH-VOLUME GLOBAL & UK PYRAMID MASTER FIXTURES DATABASE
# ============================================================

GLOBAL_MASTER_FIXTURES = {
    "2026-11-06": [
        # --- UK PYRAMID (Championship, League One, League Two, National League) ---
        {
            "id": 101,
            "region": "UK Pyramid",
            "home": "Leeds United",
            "away": "West Bromwich Albion",
            "league": "Championship (England)",
            "time": "20:00 GMT",
            "banker": True,
            "xg_home": 1.85,
            "xg_away": 1.10,
            "markets": [
                {"id": "101_1", "name": "Leeds United 1X & Over 1.5 Goals", "odds": 1.34, "prob": 0.82, "type": "Goals/DC"},
                {"id": "101_2", "name": "Leeds United Win", "odds": 1.68, "prob": 0.67, "type": "1X2"},
                {"id": "101_3", "name": "Over 2.5 Goals", "odds": 1.80, "prob": 0.58, "type": "Goals"}
            ]
        },
        {
            "id": 102,
            "region": "UK Pyramid",
            "home": "Birmingham City",
            "away": "Wrexham",
            "league": "League One (England)",
            "time": "19:45 GMT",
            "banker": False,
            "xg_home": 1.70,
            "xg_away": 1.35,
            "markets": [
                {"id": "102_1", "name": "Both Teams To Score (BTTS)", "odds": 1.75, "prob": 0.62, "type": "BTTS"},
                {"id": "102_2", "name": "Over 2.5 Goals", "odds": 1.88, "prob": 0.56, "type": "Goals"}
            ]
        },
        {
            "id": 103,
            "region": "UK Pyramid",
            "home": "Notts County",
            "away": "Chesterfield",
            "league": "League Two (England)",
            "time": "19:45 GMT",
            "banker": False,
            "xg_home": 1.90,
            "xg_away": 1.50,
            "markets": [
                {"id": "103_1", "name": "Over 2.5 Goals", "odds": 1.65, "prob": 0.69, "type": "Goals"},
                {"id": "103_2", "name": "Notts County 1X Double Chance", "odds": 1.25, "prob": 0.81, "type": "Double Chance"}
            ]
        },
        {
            "id": 104,
            "region": "UK Pyramid",
            "home": "Barnet",
            "away": "Oldham Athletic",
            "league": "National League (England)",
            "time": "19:45 GMT",
            "banker": True,
            "xg_home": 1.75,
            "xg_away": 1.15,
            "markets": [
                {"id": "104_1", "name": "Barnet Win or Draw (1X) & Over 1.5", "odds": 1.38, "prob": 0.79, "type": "Goals/DC"},
                {"id": "104_2", "name": "Barnet Win", "odds": 1.95, "prob": 0.55, "type": "1X2"}
            ]
        },
        # --- EUROPE ---
        {
            "id": 1,
            "region": "Europe",
            "home": "Hammarby IF",
            "away": "IF Elfsborg",
            "league": "Allsvenskan (Sweden)",
            "time": "18:00 GMT",
            "banker": True,
            "xg_home": 1.82,
            "xg_away": 1.15,
            "markets": [
                {"id": "1_1", "name": "Hammarby 1X & Over 1.5 Goals", "odds": 1.30, "prob": 0.835, "type": "Goals/DC"},
                {"id": "1_2", "name": "Hammarby Win", "odds": 1.65, "prob": 0.68, "type": "1X2"},
                {"id": "1_3", "name": "Over 2.5 Goals", "odds": 1.85, "prob": 0.57, "type": "Goals"}
            ]
        },
        {
            "id": 2,
            "region": "Europe",
            "home": "Everton",
            "away": "Coventry City",
            "league": "Premier League (England)",
            "time": "20:00 GMT",
            "banker": True,
            "xg_home": 1.75,
            "xg_away": 1.05,
            "markets": [
                {"id": "2_1", "name": "Everton 1X & Over 1.5 Goals", "odds": 1.32, "prob": 0.812, "type": "Goals/DC"},
                {"id": "2_2", "name": "Everton Win", "odds": 1.70, "prob": 0.65, "type": "1X2"},
                {"id": "2_3", "name": "Both Teams To Score (BTTS - Yes)", "odds": 1.95, "prob": 0.54, "type": "BTTS"}
            ]
        },
        {
            "id": 3,
            "region": "Europe",
            "home": "Sevilla",
            "away": "Deportivo Alavés",
            "league": "La Liga (Spain)",
            "time": "20:00 GMT",
            "banker": True,
            "xg_home": 1.65,
            "xg_away": 0.95,
            "markets": [
                {"id": "3_1", "name": "Sevilla 1X Double Chance", "odds": 1.26, "prob": 0.82, "type": "Double Chance"},
                {"id": "3_2", "name": "Sevilla Win", "odds": 1.90, "prob": 0.58, "type": "1X2"},
                {"id": "3_3", "name": "Under 2.5 Goals", "odds": 1.60, "prob": 0.65, "type": "Goals"}
            ]
        },
        {
            "id": 4,
            "region": "Europe",
            "home": "Atalanta",
            "away": "Lazio",
            "league": "Serie A (Italy)",
            "time": "19:45 GMT",
            "banker": False,
            "xg_home": 1.80,
            "xg_away": 1.40,
            "markets": [
                {"id": "4_1", "name": "Over 2.5 Goals", "odds": 1.75, "prob": 0.62, "type": "Goals"},
                {"id": "4_2", "name": "Both Teams To Score (BTTS)", "odds": 1.68, "prob": 0.64, "type": "BTTS"}
            ]
        },
        # --- AMERICAS ---
        {
            "id": 7,
            "region": "Americas",
            "home": "LA Galaxy",
            "away": "Seattle Sounders",
            "league": "MLS (USA)",
            "time": "02:30 GMT",
            "banker": False,
            "xg_home": 1.90,
            "xg_away": 1.45,
            "markets": [
                {"id": "7_1", "name": "Over 2.5 Goals", "odds": 1.72, "prob": 0.61, "type": "Goals"},
                {"id": "7_2", "name": "LA Galaxy Win", "odds": 2.05, "prob": 0.52, "type": "1X2"}
            ]
        },
        {
            "id": 8,
            "region": "Americas",
            "home": "Flamengo",
            "away": "Palmeiras",
            "league": "Brasileirão (Brazil)",
            "time": "23:00 GMT",
            "banker": True,
            "xg_home": 1.60,
            "xg_away": 1.30,
            "markets": [
                {"id": "8_1", "name": "Flamengo 1X Double Chance", "odds": 1.28, "prob": 0.79, "type": "Double Chance"}
            ]
        },
        # --- ASIA ---
        {
            "id": 10,
            "region": "Asia",
            "home": "Vissel Kobe",
            "away": "Yokohama F. Marinos",
            "league": "J1 League (Japan)",
            "time": "11:00 GMT",
            "banker": True,
            "xg_home": 1.70,
            "xg_away": 1.20,
            "markets": [
                {"id": "10_1", "name": "Vissel Kobe 1X & Over 1.5 Goals", "odds": 1.35, "prob": 0.78, "type": "Goals/DC"}
            ]
        }
    ],
    "2026-11-07": [
        {
            "id": 105,
            "region": "UK Pyramid",
            "home": "Sunderland",
            "away": "Sheffield United",
            "league": "Championship (England)",
            "time": "15:00 GMT",
            "banker": True,
            "xg_home": 1.75,
            "xg_away": 1.20,
            "markets": [
                {"id": "105_1", "name": "Sunderland 1X & Over 1.5 Goals", "odds": 1.36, "prob": 0.78, "type": "Goals/DC"}
            ]
        },
        {
            "id": 12,
            "region": "Europe",
            "home": "Real Madrid",
            "away": "Valencia",
            "league": "La Liga (Spain)",
            "time": "20:00 GMT",
            "banker": True,
            "xg_home": 2.15,
            "xg_away": 1.00,
            "markets": [
                {"id": "12_1", "name": "Real Madrid Win & Over 1.5", "odds": 1.40, "prob": 0.81, "type": "Goals/1X2"}
            ]
        },
        {
            "id": 13,
            "region": "Europe",
            "home": "Arsenal",
            "away": "Chelsea",
            "league": "Premier League (England)",
            "time": "17:30 GMT",
            "banker": False,
            "xg_home": 1.75,
            "xg_away": 1.45,
            "markets": [
                {"id": "13_1", "name": "Arsenal 1X & Over 1.5 Goals", "odds": 1.45, "prob": 0.74, "type": "Goals/DC"}
            ]
        }
    ],
    "2026-11-08": [
        {
            "id": 106,
            "region": "UK Pyramid",
            "home": "Stockport County",
            "away": "Wigan Athletic",
            "league": "League One (England)",
            "time": "15:00 GMT",
            "banker": True,
            "xg_home": 1.80,
            "xg_away": 1.05,
            "markets": [
                {"id": "106_1", "name": "Stockport Win", "odds": 1.72, "prob": 0.66, "type": "1X2"}
            ]
        },
        {
            "id": 15,
            "region": "Europe",
            "home": "Bayern Munich",
            "away": "Borussia Dortmund",
            "league": "Bundesliga (Germany)",
            "time": "17:30 GMT",
            "banker": True,
            "xg_home": 2.20,
            "xg_away": 1.60,
            "markets": [
                {"id": "15_1", "name": "Bayern Win & Over 2.5", "odds": 1.80, "prob": 0.62, "type": "Goals/1X2"}
            ]
        }
    ]
}

def get_active_fixtures():
    today_str = date.today().isoformat()
    active_date = today_str if today_str in GLOBAL_MASTER_FIXTURES else "2026-11-06"
    return active_date, GLOBAL_MASTER_FIXTURES.get(active_date, [])

def calc_edge(odds, prob):
    if odds <= 1.0:
        return 0.0
    return round((prob - (1 / odds)) * 100, 2)

@app.route("/healthz")
def health_check():
    return jsonify({
        "status": "healthy",
        "engine": "EDGEMETRIX V300 (UK Pyramid & Global Slate)",
        "timestamp": datetime.utcnow().isoformat(),
        "active_regions": ["UK Pyramid", "Europe", "Americas", "Asia"]
    }), 200

@app.route("/")
def index():
    active_tab = request.args.get("tab", "daily_picks")
    default_date, default_slate = get_active_fixtures()
    selected_date = request.args.get("date", default_date)
    selected_region = request.args.get("region", "ALL")
    legs_count = int(request.args.get("legs", 5))

    slate = GLOBAL_MASTER_FIXTURES.get(selected_date, default_slate)
    if selected_region != "ALL":
        slate = [f for f in slate if f.get("region") == selected_region]

    selected_market_ids = request.args.getlist("builder_market")

    sel_reg_all = 'selected' if selected_region == 'ALL' else ''
    sel_reg_uk = 'selected' if selected_region == 'UK Pyramid' else ''
    sel_reg_eur = 'selected' if selected_region == 'Europe' else ''
    sel_reg_am = 'selected' if selected_region == 'Americas' else ''
    sel_reg_asia = 'selected' if selected_region == 'Asia' else ''

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
    .audit-bar { background: #0f172a; border: 1px solid rgba(56,189,248,0.3); padding: 10px 14px; border-radius: 8px; margin-bottom: 16px; font-size: 12px; color: #38bdf8; display: flex; justify-content: space-between; align-items: center; }
    select, input[type="date"] { background: #0f172a; color: white; border: 1px solid #38bdf8; padding: 8px 12px; border-radius: 6px; font-size: 14px; }
    .btn { background: #16a34a; color: white; border: none; padding: 12px 20px; border-radius: 8px; font-weight: bold; cursor: pointer; width: 100%; font-size: 14px; transition: background 0.2s ease; }
    .btn:hover { background: #15803d; }
    .slip { background: #0369a1; border-radius: 10px; padding: 16px; color: white; margin-top: 16px; border: 1px solid #38bdf8; box-shadow: 0 4px 16px rgba(3, 105, 161, 0.3); }
    .mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }
    </style></head><body><div class="header"><h1 class="title">EDGEMETRIX V300</h1><div style="color:#38bdf8; font-size:12px; margin-top:4px;">UK Pyramid & Global Football Analytics Engine Active</div></div><div class="tabs"><a class="tab-btn """ + ('active' if active_tab=='daily_picks' else '') + """" href="/?tab=daily_picks">Daily Picks</a><a class="tab-btn """ + ('active' if active_tab=='bet_builder' else '') + """" href="/?tab=bet_builder">Bet Builder</a><a class="tab-btn """ + ('active' if active_tab=='ai_acca' else '') + """" href="/?tab=ai_acca">AI Acca Generator</a><a class="tab-btn """ + ('active' if active_tab=='future' else '') + """" href="/?tab=future">Future (3-Day Value)</a><a class="tab-btn """ + ('active' if active_tab=='bankers' else '') + """" href="/?tab=bankers">Bankers Daily</a><a class="tab-btn """ + ('active' if active_tab=='acca_gen' else '') + """" href="/?tab=acca_gen">Acca Generator Tab</a></div>"""

    html += f'''<div class="audit-bar">
        <span>🏴󠁧󠁢󠁥󠁮󠁧󠁿 <strong>Scope Filter:</strong> {selected_region if selected_region != 'ALL' else 'All Regions (UK Pyramid, Europe, Americas, Asia)'} ({len(slate)} Matches Loaded)</span>
        <form method="GET" style="display:inline; margin:0;">
            <input type="hidden" name="tab" value="{active_tab}">
            <select name="region" onchange="this.form.submit()" style="padding:4px 8px; font-size:12px;">
                <option value="ALL" {sel_reg_all}>All Regions</option>
                <option value="UK Pyramid" {sel_reg_uk}>UK Pyramid (Championship - National)</option>
                <option value="Europe" {sel_reg_eur}>Europe</option>
                <option value="Americas" {sel_reg_am}>Americas</option>
                <option value="Asia" {sel_reg_asia}>Asia</option>
            </select>
        </form>
    </div>'''

    if active_tab == 'daily_picks':
        html += f'<div class="card"><h2 style="color:#38bdf8;margin-top:0;">UK Pyramid & Global Value Feed ({selected_date})</h2><p style="color:#94a3b8;font-size:13px;">Scanned across Championship, Leagues 1 & 2, National League, and top international tiers.</p>'
        all_evaluated = []
        for f in slate:
            for m in f['markets']:
                edge = calc_edge(m['odds'], m['prob'])
                if edge > 0:
                    all_evaluated.append((edge, f['home'], f['away'], f['league'], f['region'], f['time'], m['name'], m['odds'], m['prob'], f.get('xg_home', 0), f.get('xg_away', 0)))
        all_evaluated.sort(key=lambda x: x[0], reverse=True)

        if all_evaluated:
            html += '<div class="grid">'
            for edge, home, away, league, region, time_str, m_name, odds, prob, xgh, xga in all_evaluated:
                html += f'''<div class="market-item" style="border-color:rgba(56,189,248,0.3); margin-bottom:8px;">
                    <div style="color:#38bdf8; font-weight:bold; margin-bottom:4px;">{home} vs {away} <span style="font-weight:normal; font-size:11px; color:#94a3b8;">({league})</span></div>
                    <div><strong>{m_name}</strong></div>
                    <div style="font-size:11px; color:#cbd5e1; margin-top:3px;">Region: {region} | xG: <span class="mono">{xgh} - {xga}</span></div>
                    <div style="margin-top:4px; display:flex; justify-content:space-between;">
                        <span>Odds: @<span class="mono">{odds}</span> | Prob: <span class="mono">{prob*100:.1f}%</span></span>
                        <span class="edge-badge">+{edge}% Edge</span>
                    </div>
                </div>'''
            html += '</div>'
        else:
            html += '<p style="color:#94a3b8;">No positive edge markets found for this filter.</p>'
        html += '</div>'

    elif active_tab == 'bet_builder':
        html += '<div class="card"><h2 style="color:#38bdf8;margin-top:0;">Custom Bet Builder</h2><form method="GET"><input type="hidden" name="tab" value="bet_builder"><input type="hidden" name="region" value="' + selected_region + '">'
        for f in slate:
            html += f'''<div class="match-card"><strong>{f['home']} vs {f['away']}</strong> <span style="font-size:12px; color:#94a3b8;" class="mono">({f['league']})</span><div class="grid">'''
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
        html += '<div class="card"><h2 style="color:#38bdf8;margin-top:0;">AI High-Edge Acca Generator</h2><p style="color:#94a3b8;font-size:13px;">Auto-generated 5-fold compounding slip including UK lower leagues.</p>'
        all_markets = []
        for f in slate:
            for m in f['markets']:
                edge = calc_edge(m['odds'], m['prob'])
                all_markets.append((edge, f['home'], f['away'], f['league'], m['name'], m['odds']))
        all_markets.sort(key=lambda x: x[0], reverse=True)
        top_legs = all_markets[:5]
        if top_legs:
            combined = 1.0
            for leg in top_legs:
                combined *= leg[5]
            html += f'''<div class="slip"><h3 style="margin-top:0;">5-Fold AI Acca (UK & Global)</h3><div>Combined Odds: <strong class="mono">@{combined:.2f}</strong></div>'''
            for edge, fix_h, fix_a, league, m_name, o in top_legs:
                html += f'<div style="font-size:13px;margin-top:6px;" class="mono">• <strong>{fix_h} vs {fix_a}</strong> ({league}) — {m_name} (@{o}) <span class="edge-badge">[+{edge}% Edge]</span></div>'
            html += f'<div style="margin-top:12px;">Recommended Stake: £20.00 | Potential Return: <strong class="mono">£{20*combined:.2f}</strong></div></div>'
        else:
            html += '<p style="color:#94a3b8;">Insufficient markets available.</p>'
        html += '</div>'

    elif active_tab == 'future':
        html += '<div class="card"><h2 style="color:#38bdf8;margin-top:0;">Future Value Slate (3-Day Horizon)</h2>'
        for d in sorted(GLOBAL_MASTER_FIXTURES.keys()):
            if d > date.today().isoformat():
                html += f'<h3 style="color:#eab308;border-bottom:1px solid #334155;padding-bottom:4px;margin-top:16px;">Fixtures for {d}</h3>'
                for f in GLOBAL_MASTER_FIXTURES.get(d, []):
                    html += f'''<div class="match-card"><strong>{f['home']} vs {f['away']}</strong> <span class="mono">({f['league']} - {f['time']})</span><div class="grid">'''
                    for m in f['markets']:
                        edge = calc_edge(m['odds'], m['prob'])
                        html += f'''<div class="market-item">{m['name']} (@<span class="mono">{m['odds']}</span>) | <span class="edge-badge">Edge: +{edge}%</span></div>'''
                    html += '</div></div>'
        html += '</div>'

    elif active_tab == 'bankers':
        html += '<div class="card"><h2 style="color:#eab308;margin-top:0;">Bankers Daily (High Confidence &ge;75%)</h2>'
        found_banker = False
        for f in slate:
            if f['banker']:
                found_banker = True
                html += f'''<div class="match-card"><div style="display:flex;justify-content:space-between;"><strong>{f['home']} vs {f['away']}</strong><span class="banker-badge">BANKER PLAY</span></div><div class="grid" style="margin-top:8px;">'''
                for m in f['markets']:
                    if m['prob'] >= 0.75:
                        html += f'''<div class="market-item" style="border-color:#eab308;"><strong>{m['name']}</strong> (@<span class="mono">{m['odds']}</span>)<br>Confidence: <strong class="mono">{m['prob']*100:.1f}%</strong></div>'''
                html += '</div></div>'
        if not found_banker:
            html += '<p style="color:#94a3b8;">No high-confidence bankers active for this filter.</p>'
        html += '</div>'

    elif active_tab == 'acca_gen':
        legs_options = ""
        for i in range(1, 21):
            sel_leg = 'selected' if i == legs_count else ''
            legs_options += f'<option value="{i}" {sel_leg}>{i} Leg{"s" if i > 1 else ""}</option>'

        html += f'''<div class="card"><h2 style="color:#38bdf8;margin-top:0;">Advanced Acca Generator</h2>
        <form method="GET" style="display:grid;grid-template-columns:repeat(auto-fit, minmax(200px, 1fr));gap:12px;margin-bottom:16px;">
            <input type="hidden" name="tab" value="acca_gen">
            <input type="hidden" name="region" value="{selected_region}">
            <div>
                <label style="font-size:12px;color:#94a3b8;display:block;margin-bottom:4px;">1. Select Date:</label>
                <input type="date" name="date" value="{selected_date}" style="width:100%;">
            </div>
            <div>
                <label style="font-size:12px;color:#94a3b8;display:block;margin-bottom:4px;">2. Number of Legs (1-20):</label>
                <select name="legs" style="width:100%;">
                    {legs_options}
                </select>
            </div>
            <div style="grid-column: 1 / -1;">
                <button type="submit" class="btn">Generate Custom Acca</button>
            </div>
        </form>'''

        pool = []
        for f in slate:
            for m in f['markets']:
                edge = calc_edge(m['odds'], m['prob'])
                pool.append((edge, f"{f['home']} vs {f['away']}", f['league'], m['name'], m['odds']))
        pool.sort(key=lambda x: x[0], reverse=True)
        generated_legs = pool[:legs_count]
        if generated_legs:
            acc_odds = 1.0
            for leg in generated_legs:
                acc_odds *= leg[4]
            html += f'''<div class="slip"><h3 style="margin-top:0;">Generated {len(generated_legs)}-Leg Accumulator Slip</h3><div style="font-size:14px;margin-bottom:10px;">Date: <strong class="mono">{selected_date}</strong> | Combined Odds: <strong class="mono">@{acc_odds:.2f}</strong></div>'''
            for edge, fix, league, m_name, o in generated_legs:
                html += f'<div style="font-size:13px;margin-top:6px;border-bottom:1px solid rgba(255,255,255,0.2);padding-bottom:4px;" class="mono">• <strong>{fix}</strong> ({league}) — {m_name} (@{o}) <span class="edge-badge">[+{edge}% Edge]</span></div>'
            html += f'<div style="margin-top:12px;">Recommended Stake: £20.00 | Potential Return: <strong class="mono">£{20*acc_odds:.2f}</strong></div></div>'
        else:
            html += '<p style="color:#f87171;">No matching markets found.</p>'
        html += '</div>'

    html += '</body></html>'
    return render_template_string(html)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
