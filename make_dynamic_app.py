import math, random

template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>EDGEMETRIX V300 PRO -- Syndicate Terminal</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #070b12; color: #f8fafc; margin: 0; padding: 25px; }
        h1 { color: #facc15; font-size: 24px; margin-bottom: 5px; }
        .subtitle { color: #94a3b8; font-size: 13px; margin-bottom: 25px; text-transform: uppercase; letter-spacing: 1px; display: flex; justify-content: space-between; align-items: center; }
        .live-date-badge { background: #1e293b; color: #38bdf8; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: bold; border: 1px solid #334155; }
        .nav-tabs { display: flex; gap: 8px; margin-bottom: 25px; border-bottom: 1px solid #1e293b; padding-bottom: 15px; flex-wrap: wrap; }
        .tab-btn { background: #0d1527; color: #94a3b8; border: 1px solid #1e293b; padding: 10px 16px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 12px; transition: all 0.2s; }
        .tab-btn.active { background: #facc15; color: #000; border-color: #facc15; }
        .card { background: #0d1527; border: 1px solid #1e293b; border-radius: 12px; padding: 25px; margin-bottom: 20px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5); }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 12px 16px; border-bottom: 1px solid #1e293b; text-align: left; font-size: 13px; }
        th { color: #facc15; font-weight: 600; text-transform: uppercase; font-size: 11px; letter-spacing: 0.5px; }
        .badge { background: #10b981; color: #000; padding: 4px 8px; border-radius: 6px; font-weight: bold; font-size: 11px; }
        .badge-steam { background: #ef4444; color: #fff; padding: 4px 8px; border-radius: 6px; font-weight: bold; font-size: 11px; }
        .badge-drift { background: #64748b; color: #fff; padding: 4px 8px; border-radius: 6px; font-weight: bold; font-size: 11px; }
        .table-container { max-height: 650px; overflow-y: auto; }
    </style>
</head>
<body>
    <h1>EDGEMETRIX V300 PRO -- Syndicate Terminal</h1>
    <div class="subtitle">
        <span>Bivariate Poisson (rho=0.10) | Dynamic Daily Auto-Feed | Spec 5.1 CLV</span>
        <span class="live-date-badge">Live Feed Date: {{ current_date }}</span>
    </div>

    <div class="nav-tabs">
        <a href="/?tab=dailypicks" class="tab-btn {% if active_tab == 'dailypicks' %}active{% endif %}">Daily Picks ({{ daily_picks|length }})</a>
        <a href="/?tab=btts" class="tab-btn {% if active_tab == 'btts' %}active{% endif %}">BTTS & Goals ({{ btts_picks|length }})</a>
        <a href="/?tab=correctscore" class="tab-btn {% if active_tab == 'correctscore' %}active{% endif %}">Correct Score Matrix ({{ cs_picks|length }})</a>
        <a href="/?tab=accagenerator" class="tab-btn {% if active_tab == 'accagenerator' %}active{% endif %}">Acca Generator</a>
        <a href="/?tab=trueclv" class="tab-btn {% if active_tab == 'trueclv' or active_tab == 'clv' %}active{% endif %}">True CLV Audit ({{ clv_picks|length }})</a>
    </div>

    {% if active_tab == 'dailypicks' %}
    <div class="card">
        <h2 style="color: #facc15; margin-top: 0; font-size: 18px;">Daily Value Slate (Auto-Refreshing Match Feed)</h2>
        <div class="table-container">
            <table>
                <thead><tr><th>#</th><th>Fixture</th><th>Competition</th><th>Market</th><th>Odds</th><th>Model Edge</th><th>Kelly Stake</th></tr></thead>
                <tbody>
                    {% for item in daily_picks %}
                    <tr>
                        <td>{{ loop.index }}</td>
                        <td><strong>{{ item.match }}</strong></td>
                        <td>{{ item.league }}</td>
                        <td><strong style="color: #facc15;">{{ item.market }}</strong></td>
                        <td>{{ item.odds }}</td>
                        <td><span class="badge">{{ item.ev }}</span></td>
                        <td><strong style="color: #38bdf8;">{{ item.kelly_stake }}</strong></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    {% elif active_tab == 'btts' %}
    <div class="card">
        <h2 style="color: #facc15; margin-top: 0; font-size: 18px;">BTTS & Goals Expectation Matrix</h2>
        <div class="table-container">
            <table>
                <thead><tr><th>Fixture</th><th>Competition</th><th>Market Floor</th><th>Odds</th><th>Expected Edge</th><th>Status</th></tr></thead>
                <tbody>
                    {% for item in btts_picks %}
                    <tr>
                        <td><strong>{{ item.match }}</strong></td>
                        <td>{{ item.league }}</td>
                        <td><strong style="color: #facc15;">{{ item.market }}</strong></td>
                        <td>{{ item.odds }}</td>
                        <td><span class="badge">{{ item.ev }}</span></td>
                        <td><strong style="color: #38bdf8;">High Value Floor</strong></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    {% elif active_tab == 'correctscore' %}
    <div class="card">
        <h2 style="color: #facc15; margin-top: 0; font-size: 18px;">Poisson Correct Score Distribution Table</h2>
        <div class="table-container">
            <table>
                <thead><tr><th>Fixture</th><th>Top Projected Score</th><th>Secondary Score</th><th>Model Probability</th><th>Value Odds</th></tr></thead>
                <tbody>
                    {% for item in cs_picks %}
                    <tr>
                        <td><strong>{{ item.match }}</strong></td>
                        <td><strong style="color: #facc15;">{{ item.top_score }}</strong></td>
                        <td>{{ item.sec_score }}</td>
                        <td><span class="badge">{{ item.prob }}</span></td>
                        <td><strong style="color: #38bdf8;">{{ item.odds }}</strong></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    {% elif active_tab == 'accagenerator' %}
    <div class="card">
        <h2 style="color: #facc15; margin-top: 0; font-size: 18px;">3-Fold Acca Generator</h2>
        {{ acca_html | safe }}
    </div>

    {% else %}
    <div class="card">
        <h2 style="color: #facc15; margin-top: 0; font-size: 18px;">True CLV Audit Ledger & Steam Tracker</h2>
        <div class="table-container">
            <table>
                <thead><tr><th>#</th><th>Fixture</th><th>Market</th><th>Opening Odds</th><th>Current Line</th><th>CLV Delta</th><th>Market Movement</th></tr></thead>
                <tbody>
                    {% for item in clv_picks %}
                    <tr>
                        <td>{{ loop.index }}</td>
                        <td><strong>{{ item.match }}</strong></td>
                        <td><strong style="color: #facc15;">{{ item.market }}</strong></td>
                        <td>{{ item.open_odds }}</td>
                        <td>{{ item.current_odds }}</td>
Set-Content -Path "make_live_engine.py" -Encoding UTF8 -Value @'
import math, random, json
from datetime import date

template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>EDGEMETRIX V300 PRO -- Syndicate Terminal</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #070b12; color: #f8fafc; margin: 0; padding: 25px; }
        h1 { color: #facc15; font-size: 24px; margin-bottom: 5px; }
        .subtitle { color: #94a3b8; font-size: 13px; margin-bottom: 25px; text-transform: uppercase; letter-spacing: 1px; display: flex; justify-content: space-between; align-items: center; }
        .live-date-badge { background: #1e293b; color: #38bdf8; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: bold; border: 1px solid #334155; }
        .nav-tabs { display: flex; gap: 8px; margin-bottom: 25px; border-bottom: 1px solid #1e293b; padding-bottom: 15px; flex-wrap: wrap; }
        .tab-btn { background: #0d1527; color: #94a3b8; border: 1px solid #1e293b; padding: 10px 16px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 12px; transition: all 0.2s; }
        .tab-btn.active { background: #facc15; color: #000; border-color: #facc15; }
        .card { background: #0d1527; border: 1px solid #1e293b; border-radius: 12px; padding: 25px; margin-bottom: 20px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5); }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 12px 16px; border-bottom: 1px solid #1e293b; text-align: left; font-size: 13px; }
        th { color: #facc15; font-weight: 600; text-transform: uppercase; font-size: 11px; letter-spacing: 0.5px; }
        .badge { background: #10b981; color: #000; padding: 4px 8px; border-radius: 6px; font-weight: bold; font-size: 11px; }
        .badge-steam { background: #ef4444; color: #fff; padding: 4px 8px; border-radius: 6px; font-weight: bold; font-size: 11px; }
        .badge-drift { background: #64748b; color: #fff; padding: 4px 8px; border-radius: 6px; font-weight: bold; font-size: 11px; }
        .table-container { max-height: 650px; overflow-y: auto; }
    </style>
</head>
<body>
    <h1>EDGEMETRIX V300 PRO -- Syndicate Terminal</h1>
    <div class="subtitle">
        <span>Bivariate Poisson (rho=0.10) | Live Match Slate | Spec 5.1 CLV</span>
        <span class="live-date-badge">Live Feed Date: {{ current_date }}</span>
    </div>

    <div class="nav-tabs">
        <a href="/?tab=dailypicks" class="tab-btn {% if active_tab == 'dailypicks' %}active{% endif %}">Daily Picks ({{ daily_picks|length }})</a>
        <a href="/?tab=btts" class="tab-btn {% if active_tab == 'btts' %}active{% endif %}">BTTS & Goals ({{ btts_picks|length }})</a>
        <a href="/?tab=correctscore" class="tab-btn {% if active_tab == 'correctscore' %}active{% endif %}">Correct Score Matrix ({{ cs_picks|length }})</a>
        <a href="/?tab=accagenerator" class="tab-btn {% if active_tab == 'accagenerator' %}active{% endif %}">Acca Generator</a>
        <a href="/?tab=trueclv" class="tab-btn {% if active_tab == 'trueclv' or active_tab == 'clv' %}active{% endif %}">True CLV Audit ({{ clv_picks|length }})</a>
    </div>

    {% if active_tab == 'dailypicks' %}
    <div class="card">
        <h2 style="color: #facc15; margin-top: 0; font-size: 18px;">Daily Value Slate (Authentic Fixture Feed)</h2>
        <div class="table-container">
            <table>
                <thead><tr><th>#</th><th>Fixture</th><th>Competition</th><th>Market</th><th>Odds</th><th>Model Edge</th><th>Kelly Stake</th></tr></thead>
                <tbody>
                    {% for item in daily_picks %}
                    <tr>
                        <td>{{ loop.index }}</td>
                        <td><strong>{{ item.match }}</strong></td>
                        <td>{{ item.league }}</td>
                        <td><strong style="color: #facc15;">{{ item.market }}</strong></td>
                        <td>{{ item.odds }}</td>
                        <td><span class="badge">{{ item.ev }}</span></td>
                        <td><strong style="color: #38bdf8;">{{ item.kelly_stake }}</strong></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    {% elif active_tab == 'btts' %}
    <div class="card">
        <h2 style="color: #facc15; margin-top: 0; font-size: 18px;">BTTS & Goals Expectation Matrix</h2>
        <div class="table-container">
            <table>
                <thead><tr><th>Fixture</th><th>Competition</th><th>Market Floor</th><th>Odds</th><th>Expected Edge</th><th>Status</th></tr></thead>
                <tbody>
                    {% for item in btts_picks %}
                    <tr>
                        <td><strong>{{ item.match }}</strong></td>
                        <td>{{ item.league }}</td>
                        <td><strong style="color: #facc15;">{{ item.market }}</strong></td>
                        <td>{{ item.odds }}</td>
                        <td><span class="badge">{{ item.ev }}</span></td>
                        <td><strong style="color: #38bdf8;">High Value Floor</strong></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    {% elif active_tab == 'correctscore' %}
    <div class="card">
        <h2 style="color: #facc15; margin-top: 0; font-size: 18px;">Poisson Correct Score Distribution Table</h2>
        <div class="table-container">
            <table>
                <thead><tr><th>Fixture</th><th>Top Projected Score</th><th>Secondary Score</th><th>Model Probability</th><th>Value Odds</th></tr></thead>
                <tbody>
                    {% for item in cs_picks %}
                    <tr>
                        <td><strong>{{ item.match }}</strong></td>
                        <td><strong style="color: #facc15;">{{ item.top_score }}</strong></td>
                        <td>{{ item.sec_score }}</td>
                        <td><span class="badge">{{ item.prob }}</span></td>
                        <td><strong style="color: #38bdf8;">{{ item.odds }}</strong></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    {% elif active_tab == 'accagenerator' %}
    <div class="card">
        <h2 style="color: #facc15; margin-top: 0; font-size: 18px;">3-Fold Acca Generator</h2>
        {{ acca_html | safe }}
    </div>

    {% else %}
    <div class="card">
        <h2 style="color: #facc15; margin-top: 0; font-size: 18px;">True CLV Audit Ledger & Steam Tracker</h2>
        <div class="table-container">
            <table>
                <thead><tr><th>#</th><th>Fixture</th><th>Market</th><th>Opening Odds</th><th>Current Line</th><th>CLV Delta</th><th>Market Movement</th></tr></thead>
                <tbody>
                    {% for item in clv_picks %}
                    <tr>
                        <td>{{ loop.index }}</td>
                        <td><strong>{{ item.match }}</strong></td>
                        <td><strong style="color: #facc15;">{{ item.market }}</strong></td>
                        <td>{{ item.open_odds }}</td>
                        <td>{{ item.current_odds }}</td>
                        <td><span class="{{ item.badge_style }}">{{ item.clv_delta }}</span></td>
                        <td><span class="{{ item.badge_style }}">{{ item.movement }}</span></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    {% endif %}
</body>
</html>"""
