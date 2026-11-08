from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    tab = request.args.get('tab', 'dailypicks')
    
    slate = [
        {"id": 1, "home": "Manchester United", "away": "Aston Villa", "league": "English Premier League", "time": "16:30 GMT", "market": "Over 1.5 Goals", "odds": 1.35, "ev": "+6.2%", "rating": "10/10"},
        {"id": 2, "home": "Atlético Madrid", "away": "Barcelona", "league": "Spanish La Liga", "time": "20:00 GMT", "market": "Double Chance: X2", "odds": 1.42, "ev": "+5.8%", "rating": "10/10"},
        {"id": 3, "home": "Fiorentina", "away": "Juventus", "league": "Italian Serie A", "time": "19:45 GMT", "market": "Double Chance: X2", "odds": 1.38, "ev": "+5.1%", "rating": "10/10"},
        {"id": 4, "home": "Bayer Leverkusen", "away": "Borussia Dortmund", "league": "German Bundesliga", "time": "17:30 GMT", "market": "BTTS - Yes", "odds": 1.65, "ev": "+7.4%", "rating": "10/10"},
        {"id": 5, "home": "AC Milan", "away": "Napoli", "league": "Italian Serie A", "time": "19:45 GMT", "market": "BTTS & Over 2.5", "odds": 2.10, "ev": "+8.2%", "rating": "10/10"},
        {"id": 6, "home": "Arsenal", "away": "Chelsea", "league": "English Premier League", "time": "15:00 GMT", "market": "Home Win", "odds": 1.85, "ev": "+6.4%", "rating": "10/10"},
        {"id": 7, "home": "Real Madrid", "away": "Valencia", "league": "Spanish La Liga", "time": "21:00 GMT", "market": "Real Madrid Win", "odds": 1.45, "ev": "+5.9%", "rating": "10/10"},
        {"id": 8, "home": "Bayern Munich", "away": "RB Leipzig", "league": "German Bundesliga", "time": "18:30 GMT", "market": "Over 2.5 Goals", "odds": 1.55, "ev": "+6.8%", "rating": "10/10"},
        {"id": 9, "home": "Paris Saint-Germain", "away": "Marseille", "league": "French Ligue 1", "time": "20:45 GMT", "market": "PSG Win & Over 1.5", "odds": 1.78, "ev": "+7.1%", "rating": "10/10"},
        {"id": 10, "home": "Inter Milan", "away": "Lazio", "league": "Italian Serie A", "time": "15:00 GMT", "market": "Inter Win", "odds": 1.62, "ev": "+6.5%", "rating": "10/10"},
        {"id": 11, "home": "Feyenoord", "away": "PSV Eindhoven", "league": "Dutch Eredivisie", "time": "14:30 GMT", "market": "BTTS - Yes", "odds": 1.50, "ev": "+5.5%", "rating": "9.8/10"},
        {"id": 12, "home": "Benfica", "away": "Sporting CP", "league": "Portuguese Primeira Liga", "time": "21:30 GMT", "market": "Under 3.5 Goals", "odds": 1.38, "ev": "+4.9%", "rating": "9.7/10"}
    ]
    
    acca_legs = int(request.args.get('legs', 3))
    selected_market = request.args.get('market_filter', 'All')
    
    filtered_pool = slate if selected_market == 'All' else [f for f in slate if selected_market.lower() in f['market'].lower()]
    current_acca = filtered_pool[:acca_legs]
    
    combined_odds = round(product := __import__('functools').reduce(lambda x, y: x * y, [l['odds'] for l in current_acca], 1.0), 2) if current_acca else 1.0

    return render_template('index.html', active_tab=tab, slate=slate, current_acca=current_acca, acca_legs=acca_legs, selected_market=selected_market, combined_odds=combined_odds)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
