from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

# Sample/Engine data provider ensuring clean separation of fields
def get_fixture_slate():
    return [
        {"home": "Genoa", "away": "AC Milan", "league": "Serie A", "time": "14:00 GMT", "market": "Over 1.5 Goals", "odds": "1.91", "ev": "+21.6%", "correct_score": "1-1", "cs_odds": "6.50", "btts_prob": "62.1%"},
        {"home": "Monza", "away": "Atalanta", "league": "Serie A", "time": "16:30 GMT", "market": "Over 1.5 Goals", "odds": "1.85", "ev": "+18.7%", "correct_score": "0-2", "cs_odds": "7.20", "btts_prob": "54.0%"},
        {"home": "Inter Milan", "away": "Como 1907", "league": "Serie A", "time": "19:45 GMT", "market": "Home Win", "odds": "1.45", "ev": "+12.4%", "correct_score": "2-0", "cs_odds": "5.80", "btts_prob": "45.0%"},
        {"home": "Fiorentina", "away": "Juventus", "league": "Serie A", "time": "12:30 GMT", "market": "BTTS - Yes", "odds": "1.95", "ev": "+15.2%", "correct_score": "1-1", "cs_odds": "6.10", "btts_prob": "63.0%"},
        {"home": "Köln", "away": "Bayer Leverkusen", "league": "Bundesliga", "time": "15:30 GMT", "market": "Away Win", "odds": "1.75", "ev": "+14.8%", "correct_score": "1-2", "cs_odds": "8.00", "btts_prob": "68.1%"},
        {"home": "Freiburg", "away": "Union Berlin", "league": "Bundesliga", "time": "17:30 GMT", "market": "Under 2.5 Goals", "odds": "1.80", "ev": "+11.5%", "correct_score": "1-0", "cs_odds": "7.50", "btts_prob": "48.2%"}
    ]

@app.route("/")
def index():
    active_tab = request.args.get("tab", "dailypicks")
    slate = get_fixture_slate()
    
    # Acca generator setup
    acca_legs = int(request.args.get("legs", 3))
    selected_market = request.args.get("market_filter", "Over 1.5 Goals")
    market_options = ["Over 1.5 Goals", "Home Win", "BTTS - Yes", "Under 2.5 Goals"]
    
    filtered_slate = [f for f in slate if selected_market in f["market"] or selected_market == "All"]
    current_acca = filtered_slate[:acca_legs]
    
    # Calculate combined odds safely
    combined = 1.0
    for item in current_acca:
        try:
            combined *= float(item["odds"])
        except ValueError:
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
