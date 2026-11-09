from flask import Flask, render_template, request
import os

# Set absolute path for templates folder to prevent TemplateNotFound errors on Render
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
app = Flask(__name__, template_folder=template_dir)

def get_fixture_slate():
    return [
        {"home": "Arsenal", "away": "Chelsea", "league": "Premier League", "time": "15:00 GMT", "market": "Home Win", "odds": "1.85", "ev": "+21.6%", "correct_score": "2-1", "cs_odds": "7.50", "btts_prob": "65.4%"},
        {"home": "Manchester City", "away": "Liverpool", "league": "Premier League", "time": "17:30 GMT", "market": "Over 2.5 Goals", "odds": "1.72", "ev": "+18.4%", "correct_score": "2-2", "cs_odds": "9.20", "btts_prob": "74.1%"},
        {"home": "Real Madrid", "away": "Barcelona", "league": "La Liga", "time": "20:00 GMT", "market": "BTTS - Yes", "odds": "1.65", "ev": "+15.8%", "correct_score": "1-2", "cs_odds": "8.00", "btts_prob": "71.0%"},
        {"home": "Inter Milan", "away": "Juventus", "league": "Serie A", "time": "19:45 GMT", "market": "Under 2.5 Goals", "odds": "1.90", "ev": "+12.1%", "correct_score": "1-0", "cs_odds": "6.80", "btts_prob": "48.2%"},
        {"home": "Bayern Munich", "away": "Borussia Dortmund", "league": "Bundesliga", "time": "17:30 GMT", "market": "Home Win", "odds": "1.55", "ev": "+14.2%", "correct_score": "3-1", "cs_odds": "10.50", "btts_prob": "69.5%"},
        {"home": "PSG", "away": "Marseille", "league": "Ligue 1", "time": "20:00 GMT", "market": "Over 1.5 Goals", "odds": "1.40", "ev": "+19.3%", "correct_score": "2-0", "cs_odds": "7.00", "btts_prob": "58.0%"},
        {"home": "AC Milan", "away": "Napoli", "league": "Serie A", "time": "14:00 GMT", "market": "BTTS - Yes", "odds": "1.80", "ev": "+16.5%", "correct_score": "1-1", "cs_odds": "6.20", "btts_prob": "66.3%"},
        {"home": "Bayer Leverkusen", "away": "RB Leipzig", "league": "Bundesliga", "time": "14:30 GMT", "market": "Over 2.5 Goals", "odds": "1.75", "ev": "+17.1%", "correct_score": "2-1", "cs_odds": "8.40", "btts_prob": "72.0%"},
        {"home": "Atletico Madrid", "away": "Villarreal", "league": "La Liga", "time": "16:15 GMT", "market": "Home Win", "odds": "1.70", "ev": "+13.9%", "correct_score": "2-0", "cs_odds": "7.10", "btts_prob": "52.4%"},
        {"home": "Tottenham Hotspur", "away": "Newcastle United", "league": "Premier League", "time": "14:00 GMT", "market": "BTTS - Yes", "odds": "1.60", "ev": "+20.4%", "correct_score": "2-2", "cs_odds": "9.50", "btts_prob": "78.9%"},
        {"home": "Ajax", "away": "PSV Eindhoven", "league": "Eredivisie", "time": "13:30 GMT", "market": "Over 2.5 Goals", "odds": "1.68", "ev": "+11.8%", "correct_score": "3-2", "cs_odds": "12.00", "btts_prob": "81.2%"},
        {"home": "Benfica", "away": "Sporting CP", "league": "Primeira Liga", "time": "20:30 GMT", "market": "Home Win", "odds": "2.10", "ev": "+22.5%", "correct_score": "1-0", "cs_odds": "7.80", "btts_prob": "51.5%"}
    ]

@app.route("/")
def index():
    try:
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
    except Exception as e:
        return f"Application Error: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
