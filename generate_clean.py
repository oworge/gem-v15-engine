# coding: utf-8
import os

app_code = """# coding: utf-8
from flask import Flask, render_template, request, redirect, url_for
import os
import sqlite3

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
app = Flask(__name__, template_folder=template_dir)

DB_NAME = 'syndicate_ledger.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tracked_slips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            home TEXT,
            away TEXT,
            market TEXT,
            odds TEXT,
            stake REAL,
            status TEXT,
            clv_edge TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def get_full_fixture_slate():
    return [
        {'home': 'FC Botosani', 'away': 'Otelul Galati', 'league': 'Romanian SuperLiga', 'date': 'Mon 9 Nov', 'time': '18:00 GMT', 'market': 'Under 2.5 Goals', 'odds': '1.68', 'ev': '+12.1%', 'clv_benchmark': '1.63 (+3.0% CLV Edge)', 'tactical_health': 'Oracle Verified (h: 1.2, a: 0.9)', 'clv_edge_pct': '+3.0%', 'correct_score': '1-0', 'cs_odds': '6.50'},
        {'home': 'Torreense', 'away': 'Uniao de Leiria', 'league': 'Liga Portugal 2', 'date': 'Mon 9 Nov', 'time': '20:15 GMT', 'market': 'BTTS - Yes', 'odds': '1.78', 'ev': '+14.5%', 'clv_benchmark': '1.72 (+3.6% CLV Edge)', 'tactical_health': 'Oracle Verified (h: 1.4, a: 1.2)', 'clv_edge_pct': '+3.6%', 'correct_score': '1-1', 'cs_odds': '7.20'},
        {'home': 'Plymouth Parkway', 'away': 'Berkhamsted', 'league': 'English FA Cup', 'date': 'Mon 9 Nov', 'time': '14:30 GMT', 'market': 'Home Win', 'odds': '2.05', 'ev': '+14.2%', 'clv_benchmark': '1.98 (+3.5% CLV Edge)', 'tactical_health': 'Oracle Verified (h: 2.1, a: 0.8)', 'clv_edge_pct': '+3.5%', 'correct_score': '2-0', 'cs_odds': '8.50'},
        {'home': 'Hacken W', 'away': 'Chelsea W', 'league': "Womens Champions League", 'date': 'Mon 9 Nov', 'time': '17:45 GMT', 'market': 'Over 2.5 Goals', 'odds': '1.72', 'ev': '+16.8%', 'clv_benchmark': '1.66 (+4.2% CLV Edge)', 'tactical_health': 'Oracle Verified (h: 1.8, a: 2.4)', 'clv_edge_pct': '+4.2%', 'correct_score': '1-3', 'cs_odds': '11.00'},
        {'home': 'Real Madrid W', 'away': 'Paris FC W', 'league': "Womens Champions League", 'date': 'Mon 9 Nov', 'time': '17:45 GMT', 'market': 'Home Win', 'odds': '1.60', 'ev': '+15.0%', 'clv_benchmark': '1.55 (+3.8% CLV Edge)', 'tactical_health': 'Oracle Verified (h: 2.0, a: 0.7)', 'clv_edge_pct': '+3.8%', 'correct_score': '2-0', 'cs_odds': '6.80'},
        {'home': 'Inter Milan W', 'away': 'Man City W', 'league': "Womens Champions League", 'date': 'Mon 9 Nov', 'time': '20:00 GMT', 'market': 'Away Win', 'odds': '1.80', 'ev': '+18.2%', 'clv_benchmark': '1.74 (+4.5% CLV Edge)', 'tactical_health': 'Oracle Verified (h: 1.2, a: 2.2)', 'clv_edge_pct': '+4.5%', 'correct_score': '1-2', 'cs_odds': '8.00'}
    ]

def get_bet_builder_fixtures():
    return [
        {
            'home': 'Plymouth Parkway', 'away': 'Berkhamsted', 'league': 'English FA Cup', 'date': 'Mon 9 Nov', 'time': '14:30 GMT',
            'builder_legs': [
                {'selection': 'Double Chance: 1X (Home Win or Draw)', 'odds': '1.30', 'ev': '+12.4%'},
                {'selection': 'Over 1.5 Match Goals', 'odds': '1.25', 'ev': '+11.8%'},
                {'selection': 'Plymouth Parkway Over 0.5 First Half Goals', 'odds': '1.55', 'ev': '+14.1%'},
                {'selection': 'BTTS - Yes', 'odds': '1.65', 'ev': '+10.5%'},
                {'selection': 'Berkhamsted Under 1.5 Team Goals', 'odds': '1.36', 'ev': '+13.2%'}
            ],
            'combined_odds': '5.62'
        }
    ]

@app.route('/', methods=['GET', 'POST'])
def index():
    active_tab = request.args.get('tab', 'dailypicks')
    full_slate = get_full_fixture_slate()
    builder_slate = get_bet_builder_fixtures()
    
    try:
        acca_legs = int(request.args.get('legs', 3))
    except (ValueError, TypeError):
        acca_legs = 3
    selected_market = request.args.get('market_filter', 'All Markets')
    market_options = ['All Markets', 'Home Win', 'Away Win', 'Over 2.5 Goals', 'Under 2.5 Goals', 'BTTS - Yes']
    
    if selected_market != 'All Markets':
        filtered_slate = [x for x in full_slate if x['market'] == selected_market]
        if not filtered_slate:
            filtered_slate = full_slate
    else:
        filtered_slate = full_slate

    current_acca = filtered_slate[:acca_legs]
    
    total_odds = 1.0
    for item in current_acca:
        total_odds *= float(item['odds'])
    combined_odds = f'{round(total_odds, 2):.2f}'

    if request.method == 'POST':
        home = request.form.get('home')
        away = request.form.get('away')
        market = request.form.get('market')
        odds = request.form.get('odds')
        stake = float(request.form.get('stake', 10.0))
        clv_edge = request.form.get('clv_edge', '+0.0%')
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO tracked_slips (home, away, market, odds, stake, status, clv_edge) VALUES (?, ?, ?, ?, ?, ?, ?)',
                       (home, away, market, odds, stake, 'Active / Auditing', clv_edge))
        conn.commit()
        conn.close()
        return redirect(url_for('index', tab='true_clv'))

    return render_template(
        'index.html',
        active_tab=active_tab,
        slate=full_slate,
        builder_slate=builder_slate,
        current_acca=current_acca,
        acca_legs=acca_legs,
        selected_market=selected_market,
        market_options=market_options,
        combined_odds=combined_odds
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000)
"""

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_code)

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EDGEMETRIX V300 PRO -- Syndicate Terminal</title>
    <style>
        :root { --bg-dark: #070b12; --card-bg: #0d1527; --card-border: #1e293b; --tab-bg: #0d1527; --tab-border: #1e2d4a; --tab-hover-bg: #14213d; --gold-primary: #facc15; --gold-gradient: linear-gradient(135deg, #facc15 0%, #ca8a04 100%); --gold-shadow: rgba(250, 204, 21, 0.4); --text-main: #f8fafc; --text-muted: #94a3b8; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: var(--bg-dark); color: var(--text-main); margin: 0; padding: 0 0 24px 0; }
        .hero-banner { position: relative; background: linear-gradient(180deg, rgba(7, 11, 18, 0.4) 0%, rgba(7, 11, 18, 0.95) 100%), url('https://images.unsplash.com/photo-1508098682722-e99c43a406b2?q=80&w=1200&auto=format&fit=crop') center/cover no-repeat; padding: 40px 20px 28px 20px; text-align: center; border-bottom: 1px solid var(--card-border); margin-bottom: 24px; }
        .ai-pill { display: inline-flex; align-items: center; gap: 6px; background: rgba(13, 21, 39, 0.85); border: 1px solid rgba(250, 204, 21, 0.5); color: var(--gold-primary); padding: 6px 16px; border-radius: 20px; font-size: 11px; font-weight: 800; letter-spacing: 0.12em; text-transform: uppercase; box-shadow: 0 0 12px rgba(250, 204, 21, 0.2); margin-bottom: 14px; }
        .hero-title { font-size: 34px; font-weight: 900; margin: 0 0 8px 0; letter-spacing: -0.02em; color: #ffffff; }
        .hero-title span { color: var(--gold-primary); background: var(--gold-gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .hero-subtitle { color: var(--text-muted); font-size: 14px; max-width: 500px; margin: 0 auto; }
        .main-container { padding: 0 24px; }
        .nav-tabs { display: flex; gap: 10px; margin-bottom: 24px; flex-wrap: wrap; align-items: center; }
        .tab-btn { background-color: var(--tab-bg); color: var(--text-muted); border: 1px solid var(--tab-border); padding: 10px 20px; border-radius: 12px; text-decoration: none; font-weight: 600; font-size: 14px; transition: all 0.2s ease; white-space: nowrap; }
        .tab-btn:hover { background-color: var(--tab-hover-bg); color: var(--text-main); border-color: rgba(250, 204, 21, 0.4); }
        .tab-btn.active { background: var(--gold-gradient); color: #000000; border-color: var(--gold-primary); box-shadow: 0 0 16px var(--gold-shadow); font-weight: 800; }
        .card { background-color: var(--card-bg); border-radius: 16px; padding: 20px; border: 1.5px solid var(--card-border); margin-bottom: 20px; }
        .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
        .card-title { color: var(--gold-primary); font-size: 18px; font-weight: 800; margin: 0; text-transform: uppercase; }
        .acca-filter-bar { display: flex; gap: 16px; align-items: center; background-color: rgba(7, 11, 18, 0.6); padding: 14px 18px; border-radius: 12px; border: 1px solid var(--card-border); margin-bottom: 20px; flex-wrap: wrap; }
        .filter-group { display: flex; align-items: center; gap: 8px; }
        .filter-label { color: var(--text-muted); font-size: 13px; font-weight: 700; text-transform: uppercase; }
        .filter-select { background-color: #111827; color: #ffffff; border: 1px solid var(--tab-border); padding: 8px 14px; border-radius: 8px; font-weight: 600; font-size: 14px; outline: none; cursor: pointer; }
        table { width: 100%; border-collapse: collapse; text-align: left; }
        th, td { padding: 14px 12px; border-bottom: 1px solid var(--card-border); font-size: 14px; }
        th { background-color: rgba(7, 11, 18, 0.7); color: var(--gold-primary); font-size: 12px; text-transform: uppercase; }
        .badge-green { background-color: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(52, 211, 153, 0.3); padding: 4px 10px; border-radius: 6px; font-weight: 700; font-size: 12px; }
        .badge-gold { background-color: rgba(250, 204, 21, 0.15); color: var(--gold-primary); border: 1px solid rgba(250, 204, 21, 0.3); padding: 4px 10px; border-radius: 6px; font-weight: 700; font-size: 12px; }
        .btn-log { background: var(--gold-gradient); color: #000000; border: none; padding: 8px 18px; border-radius: 8px; cursor: pointer; font-weight: 800; font-size: 13px; }
        .builder-grid { display: grid; gap: 10px; margin-top: 12px; }
        .builder-item { background-color: rgba(7, 11, 18, 0.6); border: 1px solid var(--card-border); border-radius: 10px; padding: 10px 14px; display: flex; justify-content: space-between; align-items: center; }
    </style>
</head>
<body>
    <div class="hero-banner">
        <div class="ai-pill">AI ANALYSIS ENGINE ACTIVE</div>
        <h1 class="hero-title">EDGEMETRIX V300 <span>PRO</span></h1>
        <p class="hero-subtitle">Manage your predictions more consciously with AI-powered VIP analyses.</p>
    </div>
    <div class="main-container">
        <div class="nav-tabs">
            <a href="/?tab=dailypicks" class="tab-btn {% if active_tab == 'dailypicks' %}active{% endif %}">Daily Picks</a>
            <a href="/?tab=allfixtures" class="tab-btn {% if active_tab == 'allfixtures' %}active{% endif %}">All Fixtures</a>
            <a href="/?tab=betbuilder" class="tab-btn {% if active_tab == 'betbuilder' %}active{% endif %}">Bet Builder</a>
            <a href="/?tab=btts" class="tab-btn {% if active_tab == 'btts' %}active{% endif %}">BTTS</a>
            <a href="/?tab=tacticalhealth" class="tab-btn {% if active_tab == 'tacticalhealth' %}active{% endif %}">Tactical Health</a>
            <a href="/?tab=clvaudit" class="tab-btn {% if active_tab == 'clvaudit' %}active{% endif %}">CLV Audit Ledger</a>
            <a href="/?tab=true_clv" class="tab-btn {% if active_tab == 'true_clv' %}active{% endif %}">TRUE CLV</a>
            <a href="/?tab=accagenerator" class="tab-btn {% if active_tab == 'accagenerator' %}active{% endif %}">Acca Generator</a>
            <a href="/?tab=correctscore" class="tab-btn {% if active_tab == 'correctscore' %}active{% endif %}">Correct Score</a>
        </div>
        {% if active_tab == 'accagenerator' %}
        <form method="GET" action="/" class="acca-filter-bar">
            <input type="hidden" name="tab" value="accagenerator">
            <div class="filter-group">
                <span class="filter-label">Leg Count:</span>
                <select name="legs" class="filter-select" onchange="this.form.submit()">
                    {% for n in range(2, 7) %}
                    <option value="{{ n }}" {% if acca_legs == n %}selected{% endif %}>{{ n }} Legs</option>
                    {% endfor %}
                </select>
            </div>
            <div class="filter-group">
                <span class="filter-label">Market Filter:</span>
                <select name="market_filter" class="filter-select" onchange="this.form.submit()">
                    {% for m in market_options %}
                    <option value="{{ m }}" {% if selected_market == m %}selected{% endif %}>{{ m }}</option>
                    {% endfor %}
                </select>
            </div>
            <div style="margin-left: auto; text-align: right;">
                <span class="filter-label">TOTAL ACCA ODDS:</span>
                <strong style="color: var(--gold-primary); font-size: 20px; margin-left: 8px;">{{ combined_odds }}</strong>
            </div>
        </form>
        <div class="card">
            <div class="card-header">
                <h2 class="card-title">OPTIMIZED ACCUMULATION SLATE ({{ acca_legs }} SELECTIONS)</h2>
            </div>
            <table>
                <thead>
                    <tr><th>Fixture & League</th><th>Date / Time</th><th>Market Selection</th><th>Entry Odds</th><th>Model Edge (+EV)</th><th>Action</th></tr>
                </thead>
                <tbody>
                    {% for item in current_acca %}
                    <tr>
                        <td><strong>{{ item.home }} vs {{ item.away }}</strong><br><small style="color: var(--text-muted);">{{ item.league }}</small></td>
                        <td>{{ item.date }}<br><small style="color: var(--text-muted);">{{ item.time }}</small></td>
                        <td><strong style="color: var(--gold-primary);">{{ item.market }}</strong></td>
                        <td><strong>{{ item.odds }}</strong></td>
                        <td><span class="badge-green">{{ item.ev }}</span></td>
                        <td>
                            <form action="/" method="POST" style="margin:0;">
                                <input type="hidden" name="home" value="{{ item.home }}">
                                <input type="hidden" name="away" value="{{ item.away }}">
                                <input type="hidden" name="market" value="{{ item.market }}">
                                <input type="hidden" name="odds" value="{{ item.odds }}">
                                <input type="hidden" name="stake" value="10.0">
                                <input type="hidden" name="clv_edge" value="{{ item.clv_edge_pct }}">
                                <button type="submit" class="btn-log">Log Bet</button>
                            </form>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% elif active_tab == 'betbuilder' %}
        {% for match in builder_slate %}
        <div class="card">
            <div class="card-header">
                <div><h3 class="card-title" style="margin:0;">{{ match.home }} vs {{ match.away }}</h3><small style="color: var(--text-muted);">{{ match.league }} • {{ match.date }} ({{ match.time }})</small></div>
                <div style="text-align:right;"><span style="color: var(--text-muted); font-size: 12px;">5-LEG BUILDER ODDS:</span><br><strong style="color: var(--gold-primary); font-size: 18px;">{{ match.combined_odds }}</strong></div>
            </div>
            <div class="builder-grid">
                {% for leg in match.builder_legs %}
                <div class="builder-item">
                    <div><span style="color: var(--gold-primary); font-weight:700;">Leg {{ loop.index }}:</span> <span>{{ leg.selection }}</span></div>
                    <div><strong style="margin-right:10px;">{{ leg.odds }}</strong><span class="badge-green">{{ leg.ev }}</span></div>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endfor %}
        {% else %}
        <div class="card">
            <div class="card-header">
                <h2 class="card-title">
                    {% if active_tab == 'true_clv' %}TRUE CLV -- UNCONSTRAINED SLATE
                    {% elif active_tab == 'correctscore' %}CORRECT SCORE -- POISSON MODEL MATRIX
                    {% else %}{{ active_tab|replace('_', ' ')|upper }}{% endif %}
                </h2>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Fixture & League</th><th>Date / Time</th>
                        {% if active_tab == 'correctscore' %}<th>Predicted Correct Score</th><th>CS Model Odds</th>
                        {% else %}<th>Market Selection</th><th>Entry Odds</th>{% endif %}
                        <th>Model Edge (+EV)</th>
                        {% if active_tab == 'true_clv' or active_tab == 'clvaudit' %}<th>True CLV Target</th><th>Tactical Metrics</th>{% endif %}
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in slate %}
                    <tr>
                        <td><strong>{{ item.home }} vs {{ item.away }}</strong><br><small style="color: var(--text-muted);">{{ item.league }}</small></td>
                        <td>{{ item.date }}<br><small style="color: var(--text-muted);">{{ item.time }}</small></td>
                        {% if active_tab == 'correctscore' %}
                        <td><strong style="color: var(--gold-primary); font-size: 16px;">Score: {{ item.correct_score }}</strong></td>
                        <td><strong style="color: #ffffff;">{{ item.cs_odds }}</strong></td>
                        {% else %}
                        <td><strong style="color: var(--gold-primary);">{{ item.market }}</strong></td>
                        <td><strong>{{ item.odds }}</strong></td>
                        {% endif %}
                        <td><span class="badge-green">{{ item.ev }}</span></td>
                        {% if active_tab == 'true_clv' or active_tab == 'clvaudit' %}
                        <td><span class="badge-gold">{{ item.clv_benchmark }}</span></td>
                        <td><small style="color: var(--text-muted);">{{ item.tactical_health }}</small></td>
                        {% endif %}
                        <td>
                            <form action="/" method="POST" style="margin:0;">
                                <input type="hidden" name="home" value="{{ item.home }}">
                                <input type="hidden" name="away" value="{{ item.away }}">
                                <input type="hidden" name="market" value="{% if active_tab == 'correctscore' %}Score: {{ item.correct_score }}{% else %}{{ item.market }}{% endif %}">
                                <input type="hidden" name="odds" value="{% if active_tab == 'correctscore' %}{{ item.cs_odds }}{% else %}{{ item.odds }}{% endif %}">
                                <input type="hidden" name="stake" value="10.0">
                                <input type="hidden" name="clv_edge" value="{{ item.clv_edge_pct }}">
                                <button type="submit" class="btn-log">Log Bet</button>
                            </form>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% endif %}
    </div>
</body>
</html>"""

os.makedirs('templates', exist_ok=True)
with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("Clean files successfully generated.")
