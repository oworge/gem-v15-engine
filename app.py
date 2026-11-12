# -*- coding: utf-8 -*-
from flask import Flask, render_template_string, request

app = Flask(__name__)

TABS_DATA = {
    "daily_picks": [
        {"match": "Turkiye vs. Belgium", "comp": "UEFA Nations League (Today, 12 Nov 2026)", "pick": "Over 1.5 Goals (+12.3% EV | +6.8% Edge)", "odds": "1.75"},
        {"match": "England vs. Croatia", "comp": "UEFA Nations League (Today, 12 Nov 2026)", "pick": "Double Chance (1X) (+3.7% EV | +2.9% Edge)", "odds": "1.07"},
        {"match": "Italy vs. France", "comp": "UEFA Nations League (Today, 12 Nov 2026)", "pick": "Over 1.5 Goals (+11.2% EV | +6.1% Edge)", "odds": "1.80"},
        {"match": "Spain vs. Switzerland", "comp": "UEFA Nations League (Today, 12 Nov 2026)", "pick": "Both Teams to Score (Yes) (+8.4% EV | +4.7% Edge)", "odds": "1.67"},
        {"match": "Portugal vs. Poland", "comp": "UEFA Nations League (Today, 12 Nov 2026)", "pick": "Over 2.5 Match Goals (+9.1% EV | +5.2% Edge)", "odds": "1.80"}
    ],
    "three_fold": [
        {"match": "Leg 1: Turkiye vs. Belgium", "comp": "UEFA Nations League (Today, 12 Nov 2026)", "pick": "Over 1.5 Goals (Goal Floor Filter)", "odds": "1.75"},
        {"match": "Leg 2: England vs. Croatia", "comp": "UEFA Nations League (Today, 12 Nov 2026)", "pick": "Double Chance (1X) (Structural Buffer)", "odds": "1.07"},
        {"match": "Leg 3: Italy vs. France", "comp": "UEFA Nations League (Today, 12 Nov 2026)", "pick": "Over 1.5 Goals (Goal Floor Filter)", "odds": "1.80"},
        {"match": "3-Fold Confluence Multiplex", "comp": "Kelly Stake: 2.2% | Joint Prob: 43.6%", "pick": "Combined Accumulator Odds (+11.8% EV)", "odds": "3.37"}
    ],
    "six_fold": [
        {"match": "6-Fold Syndicate Matrix", "comp": "UEFA Nations League Slate (12 Nov 2026)", "pick": "Turkiye O1.5 + Eng 1X + Ita O1.5 + Esp BTTS + Por O2.5 + Ger 1X", "odds": "12.40"}
    ],
    "btts_goals": [
        {"match": "Spain vs. Switzerland", "comp": "UEFA Nations League (Today, 12 Nov 2026)", "pick": "Both Teams to Score (Yes) (+8.4% EV | +4.7% Edge)", "odds": "1.67"},
        {"match": "Portugal vs. Poland", "comp": "UEFA Nations League (Today, 12 Nov 2026)", "pick": "Over 2.5 Match Goals (+9.1% EV | +5.2% Edge)", "odds": "1.80"}
    ],
    "bet_builder": [
        {"match": "Italy vs. France", "comp": "UEFA Nations League (Today, 12 Nov 2026)", "pick": "Over 1.5 Goals & Under 5.5 Cards (+6.5% EV | +3.9% Edge)", "odds": "2.10"}
    ],
    "true_clv": [
        {"match": "Turkiye vs. Belgium", "comp": "Open: 1.85 -> Close: 1.75", "pick": "Over 1.5 Goals (+5.7% True CLV Beat)", "odds": "1.75"},
        {"match": "England vs. Croatia", "comp": "Open: 1.12 -> Close: 1.07", "pick": "Double Chance (1X) (+4.6% True CLV Beat)", "odds": "1.07"},
        {"match": "Italy vs. France", "comp": "Open: 1.91 -> Close: 1.80", "pick": "Over 1.5 Goals (+6.1% True CLV Beat)", "odds": "1.80"}
    ],
    "tactical_health": [
        {"match": "Negative Binomial & Monte Carlo", "comp": "5,000 Simulation Paths | r=1.5", "pick": "CIRF Lookahead Audit: Zero Fatigue Flags", "odds": "PASS"}
    ]
}

@app.route('/')
def dashboard():
    active_tab = request.args.get('tab', 'daily_picks')
    current_data = TABS_DATA.get(active_tab, TABS_DATA['daily_picks'])

    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Scorecast PRO | EdgeMetrix Pro 26</title>
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; }
            body {
                background: linear-gradient(180deg, #1b2256 0%, #11163b 100%);
                color: #ffffff;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                min-height: 100vh;
                padding: 16px;
                display: flex;
                justify-content: center;
            }
            .container {
                width: 100%;
                max-width: 540px;
            }
            .top-bar {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 14px;
            }
            .circle-btn {
                width: 34px;
                height: 34px;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.15);
                color: #e2e8f0;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 14px;
                text-decoration: none;
            }
            .circle-btn.bolt { color: #facc15; }
            .brand-title {
                font-size: 20px;
                font-weight: 800;
                letter-spacing: 0.3px;
            }
            .brand-title span { color: #facc15; }
            .subtitle-pill {
                background: rgba(255, 255, 255, 0.06);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 999px;
                text-align: center;
                padding: 8px 14px;
                font-size: 12px;
                color: #cbd5e1;
                margin-bottom: 14px;
            }
            .nav-pills {
                display: flex;
                gap: 8px;
                overflow-x: auto;
                padding-bottom: 10px;
                margin-bottom: 10px;
                scrollbar-width: none;
            }
            .nav-pills::-webkit-scrollbar { display: none; }
            .nav-pills a {
                background: #2c357a;
                color: #e2e8f0;
                text-decoration: none;
                padding: 8px 16px;
                border-radius: 999px;
                font-size: 12px;
                font-weight: 600;
                white-space: nowrap;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            .nav-pills a.active {
                background: #facc15;
                color: #11163b;
                font-weight: 800;
                border-color: #facc15;
            }
            .hero-card {
                background: linear-gradient(180deg, #273075 0%, #1e2661 100%);
                border: 1px solid rgba(250, 204, 21, 0.45);
                border-radius: 14px;
                padding: 18px 16px;
                text-align: center;
                margin-bottom: 14px;
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.25);
            }
            .engine-badge {
                display: inline-block;
                background: rgba(250, 204, 21, 0.15);
                border: 1px solid rgba(250, 204, 21, 0.5);
                color: #facc15;
                font-size: 10px;
                font-weight: 800;
                padding: 4px 12px;
                border-radius: 999px;
                letter-spacing: 0.5px;
                margin-bottom: 10px;
            }
            .hero-card h2 {
                color: #facc15;
                font-size: 19px;
                font-weight: 800;
                line-height: 1.25;
                margin-bottom: 6px;
            }
            .hero-card p {
                color: #cbd5e1;
                font-size: 12px;
            }
            .slate-box {
                background: #1d255e;
                border: 1px solid rgba(250, 204, 21, 0.35);
                border-radius: 14px;
                padding: 12px;
                display: flex;
                flex-direction: column;
                gap: 10px;
            }
            .match-card {
                background: #262f73;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 10px;
                padding: 12px 14px;
            }
            .match-top {
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-size: 11px;
                margin-bottom: 6px;
                gap: 8px;
            }
            .match-name {
                color: #e2e8f0;
                font-weight: 600;
            }
            .match-comp {
                color: #facc15;
                font-weight: 600;
                text-align: right;
            }
            .match-bottom {
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 10px;
            }
            .match-pick {
                color: #ffffff;
                font-size: 13px;
                font-weight: 700;
            }
            .odds-pill {
                background: #15808d;
                color: #5eead4;
                font-weight: 800;
                font-size: 12px;
                padding: 4px 10px;
                border-radius: 6px;
                border: 1px solid rgba(94, 234, 212, 0.3);
                white-space: nowrap;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="top-bar">
                <a href="/" class="circle-btn">&#8592;</a>
                <div class="brand-title">AI Scorecast <span>PRO</span></div>
                <a href="/" class="circle-btn bolt">&#9889;</a>
            </div>

            <div class="subtitle-pill">Quantitative Value Engine &amp; Multi-Tier Slates</div>

            <div class="nav-pills">
                <a href="/?tab=daily_picks" class="{{ 'active' if active_tab == 'daily_picks' else '' }}">Daily Picks</a>
                <a href="/?tab=three_fold" class="{{ 'active' if active_tab == 'three_fold' else '' }}">3-Fold</a>
                <a href="/?tab=six_fold" class="{{ 'active' if active_tab == 'six_fold' else '' }}">6-Fold</a>
                <a href="/?tab=btts_goals" class="{{ 'active' if active_tab == 'btts_goals' else '' }}">BTTS &amp; Goals</a>
                <a href="/?tab=bet_builder" class="{{ 'active' if active_tab == 'bet_builder' else '' }}">Bet Builder</a>
                <a href="/?tab=true_clv" class="{{ 'active' if active_tab == 'true_clv' else '' }}">True CLV</a>
                <a href="/?tab=tactical_health" class="{{ 'active' if active_tab == 'tactical_health' else '' }}">Tactical Health</a>
            </div>

            <div class="hero-card">
                <div class="engine-badge">&#128081; AI ANALYSIS ENGINE ACTIVE</div>
                <h2>EdgeMetrix Pro 26 &mdash; Live Slate (Today, 12 Nov 2026)</h2>
                <p>Quantitative Engine &amp; Multi-Tier Slates</p>
            </div>

            <div class="slate-box">
                {% for row in data %}
                <div class="match-card">
                    <div class="match-top">
                        <span class="match-name">&#9917; {{ row.match }}</span>
                        <span class="match-comp">{{ row.comp }}</span>
                    </div>
                    <div class="match-bottom">
                        <span class="match-pick">{{ row.pick }}</span>
                        <span class="odds-pill">{{ row.odds }}</span>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template, active_tab=active_tab, data=current_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
"true_clv":[{"match":"Turkiye vs. Belgium","comp":"Open: 1.85 -> Close: 1.75","pick":"Over 1.5 Goals (+5.7% CLV)","odds":"1.75"}],"tactical_health":[{"match":"NegBin & Monte Carlo","comp":"5,000 Sims | r=1.5","pick":"CIRF Audit: Zero Fatigue Flags","odds":"PASS"}]}
@app.route('/')
def dashboard():
    tab = request.args.get('tab', 'daily_picks')
    return render_template('index.html', active_tab=tab, data=DATA.get(tab, DATA['daily_picks']))
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
