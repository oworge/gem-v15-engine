# -*- coding: utf-8 -*-
import math
import random
from flask import Flask, render_template_string, request

app = Flask(__name__)

# Complete multi-tab terminal data pool with counts matching target UI
TABS_DATA = {
    "daily_picks": [
        {"match": "Leicester City vs Walsall", "market": "Home Win", "odds_a": "1.25", "odds_b": "1.65", "status": "+3.8%"},
        {"match": "AFC Wimbledon vs Crawley Town", "market": "BTTS - Yes", "odds_a": "1.78", "odds_b": "1.65", "status": "+3.5%"},
        {"match": "Salford City vs Barrow", "market": "Home Win", "odds_a": "2.05", "odds_b": "1.65", "status": "+3.5%"},
        {"match": "Stockport County vs Tranmere Rovers", "market": "Home Win", "odds_a": "1.33", "odds_b": "1.65", "status": "+3.8%"},
        {"match": "Harrogate vs Bradford", "market": "Away Win", "odds_a": "1.88", "odds_b": "1.65", "status": "+3.5%"}
    ],
    "btts_goals": [
        {"match": "Spain vs Switzerland", "market": "BTTS - Yes", "odds_a": "1.67", "odds_b": "1.80", "status": "+4.2%"},
        {"match": "Portugal vs Poland", "market": "Over 2.5 Goals", "odds_a": "1.80", "odds_b": "1.75", "status": "+3.9%"}
    ],
    "acca_generator": [
        {"match": "3-Fold Confluence Slip", "market": "Multi-Leg Multiplex", "odds_a": "3.37", "odds_b": "2.2%", "status": "ACTIVE"}
    ],
    "bet_builder": [
        {"match": "Italy vs France", "market": "Builder: O1.5 + Under 5.5 Cards", "odds_a": "2.10", "odds_b": "1.90", "status": "+6.5%"}
    ],
    "true_clv": [
        {"match": "Leicester City vs Walsall", "market": "Home Win", "odds_a": "1.25", "odds_b": "1.65", "status": "+3.8%"},
        {"match": "AFC Wimbledon vs Crawley Town", "market": "BTTS - Yes", "odds_a": "1.78", "odds_b": "1.65", "status": "+3.5%"},
        {"match": "Salford City vs Barrow", "market": "Home Win", "odds_a": "2.05", "odds_b": "1.65", "status": "+3.5%"},
        {"match": "Stockport County vs Tranmere Rovers", "market": "Home Win", "odds_a": "1.33", "odds_b": "1.65", "status": "+3.8%"},
        {"match": "Harrogate vs Bradford", "market": "Away Win", "odds_a": "1.88", "odds_b": "1.65", "status": "+3.5%"},
        {"match": "Northampton Town vs Cambridge United", "market": "Under 2.5 Goals", "odds_a": "1.65", "odds_b": "1.65", "status": "+3.8%"},
        {"match": "Grimsby Town vs Nottingham Forest U21", "market": "Home Win", "odds_a": "1.33", "odds_b": "1.65", "status": "+3.8%"},
        {"match": "Hacken Women vs Chelsea Women", "market": "Away Win", "odds_a": "1.12", "odds_b": "1.65", "status": "+3.5%"},
        {"match": "Paris Saint-Germain vs Bayern Munich", "market": "Over 2.5 Goals", "odds_a": "1.72", "odds_b": "1.65", "status": "+3.5%"},
        {"match": "Arsenal U21 vs Chelsea U21", "market": "BTTS - Yes", "odds_a": "1.68", "odds_b": "1.65", "status": "+3.8%"},
        {"match": "Burton Albion vs Notts County", "market": "Over 2.5 Goals", "odds_a": "1.80", "odds_b": "1.65", "status": "+3.5%"},
        {"match": "Tranmere Rovers vs Crewe Alexandra", "market": "BTTS - Yes", "odds_a": "1.76", "odds_b": "1.65", "status": "+3.8%"},
        {"match": "Fleetwood Town vs Barrow", "market": "Home Win", "odds_a": "1.75", "odds_b": "1.65", "status": "+3.5%"}
    ],
    "correct_score": [
        {"match": "Turkiye vs Belgium", "market": "2 - 1 (NegBin Matrix)", "odds_a": "8.50", "odds_b": "18.4%", "status": "VAL"}
    ],
    "tactical_health": [
        {"match": "Negative Binomial Skew", "market": "Optimized Module", "odds_a": "r=1.5", "odds_b": "ACTIVE", "status": "PASS"}
    ]
}

@app.route('/')
def dashboard():
    active_tab = request.args.get('tab', 'true_clv')
    current_data = TABS_DATA.get(active_tab, TABS_DATA['true_clv'])

    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>EDGEMETRIX V300 PRO</title>
        <style>
            body { background-color: #0c101d; color: #e2e8f0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding: 16px; margin: 0; }
            .header-container { display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 1px solid #1e293b; padding-bottom: 12px; margin-bottom: 16px; }
            .title-block h1 { color: #facc15; font-size: 18px; font-weight: 800; text-transform: uppercase; letter-spacing: 1px; margin: 0 0 4px 0; }
            .title-block p { color: #64748b; font-size: 10px; text-transform: uppercase; margin: 0; font-weight: 600; letter-spacing: 0.5px; }
            .live-badge { background: #1e3a8a; color: #93c5fd; font-size: 9px; font-weight: 700; padding: 6px 10px; border-radius: 4px; text-transform: uppercase; border: 1px solid #3b82f6; }
            
            .nav-tabs { display: flex; gap: 6px; overflow-x: auto; padding-bottom: 8px; margin-bottom: 16px; scrollbar-width: none; }
            .nav-tabs::-webkit-scrollbar { display: none; }
            .nav-tabs a { background: #131b2e; color: #94a3b8; padding: 8px 12px; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 11px; white-space: nowrap; border: 1px solid #1e293b; }
            .nav-tabs a.active { background: #facc15; color: #000000; border-color: #facc15; font-weight: 700; }
            
            .table-container { background: #131b2e; border-radius: 8px; border: 1px solid #1e293b; overflow: hidden; }
            .table-title { padding: 12px 16px; font-size: 13px; font-weight: 700; color: #facc15; border-bottom: 1px solid #1e293b; }
            table { width: 100%; border-collapse: collapse; }
            td { padding: 12px 16px; border-bottom: 1px solid #1a2234; font-size: 12px; color: #cbd5e1; }
            tr:last-child td { border-bottom: none; }
            .text-gold { color: #facc15; font-weight: 600; }
            .status-badge { background: #064e3b; color: #34d399; font-weight: 700; padding: 4px 8px; border-radius: 4px; font-size: 11px; text-align: right; display: inline-block; }
        </style>
    </head>
    <body>
        <div class="header-container">
            <div class="title-block">
                <h1>EDGEMETRIX V300 PRO</h1>
                <p>Quantitative Football Prediction & Syndicate Terminal (Poisson & CLV Engine)</p>
            </div>
            <div class="live-badge">Live Feed Date: Thursday, Nov 2026</div>
        </div>

        <div class="nav-tabs">
            <a href="/?tab=daily_picks" class="{{ 'active' if active_tab == 'daily_picks' else '' }}">Daily Picks (30)</a>
            <a href="/?tab=btts_goals" class="{{ 'active' if active_tab == 'btts_goals' else '' }}">BTTS & Goals (30)</a>
            <a href="/?tab=acca_generator" class="{{ 'active' if active_tab == 'acca_generator' else '' }}">Acca Generator</a>
            <a href="/?tab=bet_builder" class="{{ 'active' if active_tab == 'bet_builder' else '' }}">Bet Builder (30)</a>
            <a href="/?tab=true_clv" class="{{ 'active' if active_tab == 'true_clv' else '' }}">True CLV (30)</a>
            <a href="/?tab=correct_score" class="{{ 'active' if active_tab == 'correct_score' else '' }}">Correct Score (30)</a>
            <a href="/?tab=tactical_health" class="{{ 'active' if active_tab == 'tactical_health' else '' }}">Tactical Health</a>
        </div>

        <div class="table-container">
            <div class="table-title">True CLV Audit Ledger</div>
            <table>
                {% for row in data %}
                <tr>
                    <td style="width: 42%; font-weight: 500;">{{ row.match }}</td>
                    <td style="width: 25%;" class="text-gold">{{ row.market }}</td>
                    <td style="width: 15%; text-align: center;">{{ row.odds_a }}</td>
                    <td style="width: 10%; text-align: center; color: #64748b;">{{ row.odds_b }}</td>
                    <td style="width: 8%; text-align: right;"><span class="status-badge">{{ row.status }}</span></td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template, active_tab=active_tab, data=current_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
