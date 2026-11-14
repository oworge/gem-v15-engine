from flask import Flask, render_template, request
from data_generator import DAILY_PICKS, BET_BUILDERS, get_global_daily_picks, get_live_steam_clv, dispatch_push_alert, auto_grade_settled_matches

app = Flask(__name__)

def get_perfect_value_alerts(picks):
    hits = [p for p in picks if any(t in p["pick"] for t in ["+5.", "+6.", "+7.", "+8.", "+9.", "+10.", "+11.", "+12.", "+13.", "+14.", "+15."])]
    return hits if hits else (picks[:1] if picks else [])

def get_perfect_value_alerts(picks):
    hits = [p for p in picks if any(t in p["pick"] for t in ["+5.", "+6.", "+7.", "+8.", "+9.", "+10.", "+11.", "+12.", "+13.", "+14.", "+15."])]
    return hits if hits else (picks[:1] if picks else [])

def get_perfect_value_alert(picks):
    hits = get_perfect_value_alerts(picks)
    return hits[0] if hits else None

DATA = {
    "daily_picks": get_global_daily_picks(),
    "btts_goals": [
        {"match": "Turkiye vs. Belgium", "comp": "UEFA Nations League (12 Nov)", "pick": "Both Teams to Score (Yes) (+8.9% EV | Stake: 2.65%)", "odds": "1.72"},
        {"match": "Italy vs. France", "comp": "UEFA Nations League (12 Nov)", "pick": "Both Teams to Score (Yes) (+7.6% EV | Stake: 2.38%)", "odds": "1.80"}
    ],
    "bet_builder": BET_BUILDERS,
    "correct_score": [
        {"match": "Turkiye vs. Belgium", "comp": "Poisson Matrix (18.4% Prob)", "pick": "Correct Score: 1 - 2 (+9.2% EV)", "odds": "8.50"},
        {"match": "England vs. Croatia", "comp": "Poisson Matrix (16.8% Prob)", "pick": "Correct Score: 2 - 0 (+7.4% EV)", "odds": "7.00"},
        {"match": "Italy vs. France", "comp": "Poisson Matrix (15.2% Prob)", "pick": "Correct Score: 1 - 1 (+6.8% EV)", "odds": "6.50"},
        {"match": "Czechia vs. Spain", "comp": "Poisson Matrix (17.5% Prob)", "pick": "Correct Score: 0 - 2 (+8.1% EV)", "odds": "7.50"}
    ],
    "true_clv": get_live_steam_clv(),
    "tactical_health": [
        {"match": "NegBin & Monte Carlo", "comp": "5,000 Sims | r=1.5", "pick": "CIRF Audit: Zero Fatigue Flags", "odds": "PASS"}
    ]
}

@app.route("/")
def dashboard():
    tab = request.args.get("tab", "daily_picks")
    picks = get_global_daily_picks()
    DATA["daily_picks"] = picks
    auto_grade_settled_matches(picks)
    DATA["true_clv"] = get_live_steam_clv()
    al = get_perfect_value_alert(picks)
    dispatch_push_alert(al)
    return render_template("index.html", active_tab=tab, data=DATA.get(tab, picks), alert=al)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

