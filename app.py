from flask import Flask, render_template, request
from data_generator import DAILY_PICKS, BET_BUILDERS, get_global_daily_picks, get_live_steam_clv

app = Flask(__name__)

def get_perfect_value_alert(picks):
    for p in picks:
        if any(tag in p["pick"] for tag in ["+12.", "+11.", "+10.", "+13.", "+14."]):
            return p
    return picks[0] if picks else None


DATA = {
    "daily_picks": get_global_daily_picks, get_live_steam_clv(),
    "btts_goals": [
        {"match": "Turkiye vs. Belgium", "comp": "UEFA Nations League (12 Nov)", "pick": "Both Teams to Score (Yes) (+8.9% EV)", "odds": "1.72"},
        {"match": "Italy vs. France", "comp": "UEFA Nations League (12 Nov)", "pick": "Both Teams to Score (Yes) (+7.6% EV)", "odds": "1.80"}
    ],
    "bet_builder": BET_BUILDERS,
    "correct_score": [
        {"match": "Turkiye vs. Belgium", "comp": "Poisson Matrix (18.4% Prob)", "pick": "Correct Score: 1 - 2 (+9.2% EV)", "odds": "8.50"},
        {"match": "England vs. Croatia", "comp": "Poisson Matrix (16.8% Prob)", "pick": "Correct Score: 2 - 0 (+7.4% EV)", "odds": "7.00"},
        {"match": "Italy vs. France", "comp": "Poisson Matrix (15.2% Prob)", "pick": "Correct Score: 1 - 1 (+6.8% EV)", "odds": "6.50"},
        {"match": "Czechia vs. Spain", "comp": "Poisson Matrix (17.5% Prob)", "pick": "Correct Score: 0 - 2 (+8.1% EV)", "odds": "7.50"}
    ],
    "true_clv": [
        {"match": "Turkiye vs. Belgium", "comp": "Open: 1.85 -> Close: 1.75", "pick": "Over 1.5 Goals (+5.7% CLV)", "odds": "1.75"},
        {"match": "England vs. Croatia", "comp": "Open: 1.12 -> Close: 1.07", "pick": "Double Chance (1X) (+4.6% CLV)", "odds": "1.07"}
    ],
    "tactical_health": [
        {"match": "NegBin & Monte Carlo", "comp": "5,000 Sims | r=1.5", "pick": "CIRF Audit: Zero Fatigue Flags", "odds": "PASS"}
    ]
}

@app.route('/')
def dashboard():
    tab = request.args.get('tab', 'daily_picks')
    picks = get_global_daily_picks, get_live_steam_clv()
    DATA['daily_picks'] = picks
    DATA['true_clv'] = get_live_steam_clv()
    return render_template('index.html', active_tab=tab, data=DATA.get(tab, picks), alert=get_perfect_value_alert(picks))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
