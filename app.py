from flask import Flask, render_template, request
import os

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
app = Flask(__name__, template_folder=template_dir)

def get_fixture_slate():
    return [
        {"home": "Plymouth Parkway", "away": "Berkhamsted", "league": "English FA Cup", "date": "Mon 9 Nov", "time": "19:30 GMT", "market": "Home Win", "odds": "2.05", "ev": "+14.2%", "correct_score": "2-0", "cs_odds": "8.00", "btts_prob": "45.0%"},
        {"home": "Chelmsford", "away": "Ebbsfleet", "league": "National League South", "date": "Mon 9 Nov", "time": "19:45 GMT", "market": "BTTS - Yes", "odds": "1.75", "ev": "+12.5%", "correct_score": "1-1", "cs_odds": "6.50", "btts_prob": "68.0%"},
        {"home": "Kristiansund", "away": "Valerenga", "league": "Eliteserien", "date": "Mon 9 Nov", "time": "18:00 GMT", "market": "Over 2.5 Goals", "odds": "1.80", "ev": "+16.1%", "correct_score": "2-1", "cs_odds": "9.00", "btts_prob": "62.4%"},
        {"home": "Arsenal", "away": "Chelsea", "league": "Premier League", "date": "Tue 10 Nov", "time": "15:00 GMT", "market": "Home Win", "odds": "1.85", "ev": "+21.6%", "correct_score": "2-1", "cs_odds": "7.50", "btts_prob": "65.4%"},
        {"home": "Manchester City", "away": "Liverpool", "league": "Premier League", "date": "Tue 10 Nov", "time": "17:30 GMT", "market": "Over 2.5 Goals", "odds": "1.72", "ev": "+18.4%", "correct_score": "2-2", "cs_odds": "9.20", "btts_prob": "74.1%"},
        {"home": "Real Madrid", "away": "Barcelona", "league": "La Liga", "date": "Wed 11 Nov", "time": "20:00 GMT", "market": "BTTS - Yes", "odds": "1.65", "ev": "+15.8%", "correct_score": "1-2", "cs_odds": "8.00", "btts_prob": "71.0%"}
    ]

@app.route("/")
def index():
    active_tab = request.args.get("tab", "dailypicks")
    slate = get_fixture_slate()
    
    try:
        acca_legs = int(request.args.get("legs", 3))
    except (ValueError, TypeError):
        acca_legs = 3
        
    selected_market = request.args.get("market_filter", "Home Win")
    market_options = ["Home Win", "Over 2.5 Goals", "BTTS - Yes", "Under 2.5 Goals", "Over 1.5 Goals"]
    
    filtered_slate = [f for f in slate if selected_market in f["market"] or selected_market == "All"]
    current_acca = filtered_slate[:acca_legs] if filtered_slate else slate[:acca_legs]
    if not current_acca:
        current_acca = slate[:3]
    
    combined = 1.0
    for item in current_acca:
        try:
            combined *= float(item["odds"])
        except (ValueError, TypeError):
            pass
    combined_odds = round(combined, 2)

    return render_template(
        "index.html",
        active_tab=active_tab,
        slate=slate,
        current_acca=current_acca,
        acca_legs=acca_legs,
        market_options=market_options,
        selected_market=selected_market,
        combined_odds=combined_odds
    )

if __name__ == "__main__":
    app.run(debug=True, port=5000)
