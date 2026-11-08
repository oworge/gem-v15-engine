from flask import Flask, render_template, request
import math

app = Flask(__name__)

def poisson_probability(lmbda, k):
    """Calculates Poisson probability for k goals given expected lambda."""
    return (math.exp(-lmbda) * (lmbda ** k)) / math.factorial(k)

def calculate_match_prediction(home_att, away_def, away_att, home_def, league_avg_goals=2.7):
    """Dynamically calculates expected goals and core market probabilities."""
    # Expected goals calculation (lambda)
    home_lambda = max(0.5, home_att * away_def * (league_avg_goals / 2))
    away_lambda = max(0.5, away_att * home_def * (league_avg_goals / 2))
    
    # Exact score matrix probability (0-0 up to 4-4)
    best_score = "1 - 1"
    max_prob = 0.0
    for h in range(5):
        for a in range(5):
            prob = poisson_probability(home_lambda, h) * poisson_probability(away_lambda, a)
            if prob > max_prob:
                max_prob = prob
                best_score = f"{h} - {a}"
                
    # Market estimations
    home_win_prob = sum(poisson_probability(home_lambda, h) * poisson_probability(away_lambda, a) for h in range(5) for a in range(5) if h > a)
    btts_prob = (1 - poisson_probability(home_lambda, 0)) * (1 - poisson_probability(away_lambda, 0))
    over_25_prob = 1 - (poisson_probability(home_lambda, 0) * poisson_probability(away_lambda, 0) + 
                         poisson_probability(home_lambda, 1) * poisson_probability(away_lambda, 0) + 
                         poisson_probability(home_lambda, 0) * poisson_probability(away_lambda, 1))
    
    return round(home_lambda, 2), round(away_lambda, 2), best_score, round(btts_prob * 100, 1), round(over_25_prob * 100, 1)

def get_master_slate():
    # Raw stats: [Home Att, Away Def, Away Att, Home Def]
    raw_fixtures = [
        {"id": 1, "home": "Manchester United", "away": "Aston Villa", "league": "English Premier League", "date": "Sun, Nov 8, 2026", "time": "16:30 GMT", "stats": [1.35, 0.90, 1.25, 0.95], "market": "Over 1.5 Goals", "odds": 1.35, "ev": "+6.2%", "rating": "10/10", "builder": ["Over 1.5 Match Goals", "Bruno Fernandes 1+ Shots on Target", "John McGinn 2+ Fouls Committed", "Marcus Rashford 1+ Fouls Won", "Aston Villa Over 1.5 Cards"], "builder_odds": 4.85},
        {"id": 2, "home": "Atlético Madrid", "away": "Barcelona", "league": "Spanish La Liga", "date": "Sun, Nov 8, 2026", "time": "20:00 GMT", "stats": [1.20, 0.80, 1.45, 0.85], "market": "Double Chance: X2", "odds": 1.42, "ev": "+5.8%", "rating": "10/10", "builder": ["Double Chance X2", "Under 3.5 Match Goals", "Gavi 2+ Fouls Committed", "Lamine Yamal 1+ Fouls Won", "Over 4.5 Cards"], "builder_odds": 5.20},
        {"id": 3, "home": "Fiorentina", "away": "Juventus", "league": "Italian Serie A", "date": "Sun, Nov 8, 2026", "time": "19:45 GMT", "stats": [1.10, 0.85, 1.20, 0.75], "market": "Double Chance: X2", "odds": 1.38, "ev": "+5.1%", "rating": "10/10", "builder": ["Double Chance X2", "Under 2.5 Goals", "Manuel Locatelli 2+ Fouls Committed", "Moise Kean 1+ Shots on Target", "Over 3.5 Cards"], "builder_odds": 5.10},
        {"id": 4, "home": "Bayer Leverkusen", "away": "Borussia Dortmund", "league": "German Bundesliga", "date": "Sun, Nov 8, 2026", "time": "17:30 GMT", "stats": [1.55, 1.05, 1.45, 1.00], "market": "BTTS - Yes", "odds": 1.65, "ev": "+7.4%", "rating": "10/10", "builder": ["BTTS - Yes", "Over 2.5 Goals", "Florian Wirtz 1+ Shots on Target", "Julian Brandt 1+ Fouls Won", "Granit Xhaka 2+ Fouls Committed"], "builder_odds": 4.50},
        {"id": 5, "home": "AC Milan", "away": "Napoli", "league": "Italian Serie A", "date": "Sun, Nov 8, 2026", "time": "19:45 GMT", "stats": [1.30, 0.95, 1.35, 0.90], "market": "BTTS & Over 2.5", "odds": 2.10, "ev": "+8.2%", "rating": "10/10", "builder": ["BTTS & Over 2.5", "Christian Pulisic 1+ Shots on Target", "Khvicha Kvaratskhelia 2+ Fouls Won", "Stanislav Lobotka 2+ Fouls Committed", "Over 3.5 Cards"], "builder_odds": 6.75},
        {"id": 6, "home": "Arsenal", "away": "Chelsea", "league": "English Premier League", "date": "Mon, Nov 9, 2026", "time": "15:00 GMT", "stats": [1.45, 0.75, 1.20, 0.85], "market": "Home Win", "odds": 1.85, "ev": "+6.4%", "rating": "10/10", "builder": ["Arsenal Win", "Bukayo Saka 1+ Shots on Target", "Cole Palmer 1+ Fouls Won", "Moises Caicedo 2+ Fouls Committed", "Arsenal Over 5.5 Corners"], "builder_odds": 5.40},
        {"id": 7, "home": "Real Madrid", "away": "Valencia", "league": "Spanish La Liga", "date": "Mon, Nov 9, 2026", "time": "21:00 GMT", "stats": [1.60, 0.80, 1.05, 1.10], "market": "Real Madrid Win", "odds": 1.45, "ev": "+5.9%", "rating": "10/10", "builder": ["Real Madrid Win", "Kylian Mbappé 2+ Shots on Target", "Jude Bellingham 1+ Fouls Won", "Pepelu 2+ Fouls Committed", "Real Madrid Most Corners"], "builder_odds": 4.10},
        {"id": 8, "home": "Bayern Munich", "away": "RB Leipzig", "league": "German Bundesliga", "date": "Mon, Nov 9, 2026", "time": "18:30 GMT", "stats": [1.70, 1.00, 1.35, 0.95], "market": "Over 2.5 Goals", "odds": 1.55, "ev": "+6.8%", "rating": "10/10", "builder": ["Over 2.5 Goals", "Harry Kane 2+ Shots on Target", "Xavi Simons 1+ Fouls Won", "Joshua Kimmich 2+ Fouls Committed", "BTTS - Yes"], "builder_odds": 4.60},
        {"id": 9, "home": "Paris Saint-Germain", "away": "Marseille", "league": "French Ligue 1", "date": "Tue, Nov 10, 2026", "time": "20:45 GMT", "stats": [1.55, 0.85, 1.25, 0.95], "market": "PSG Win & Over 1.5", "odds": 1.78, "ev": "+7.1%", "rating": "10/10", "builder": ["PSG Win & Over 1.5", "Ousmane Dembélé 1+ Shots on Target", "Mason Greenwood 2+ Fouls Won", "Vitinha 2+ Fouls Committed", "Over 3.5 Cards"], "builder_odds": 5.80},
        {"id": 10, "home": "Inter Milan", "away": "Lazio", "league": "Italian Serie A", "date": "Tue, Nov 10, 2026", "time": "15:00 GMT", "stats": [1.45, 0.75, 1.15, 0.90], "market": "Inter Win", "odds": 1.62, "ev": "+6.5%", "rating": "10/10", "builder": ["Inter Win", "Lautaro Martínez 1+ Shots on Target", "Mattia Zaccagni 1+ Fouls Won", "Nicolò Barella 2+ Fouls Committed", "Under 4.5 Cards"], "builder_odds": 4.90}
    ]
    
    slate = []
    for f in raw_fixtures:
        h_lam, a_lam, cs, btts_pct, over_pct = calculate_match_prediction(f["stats"][0], f["stats"][1], f["stats"][2], f["stats"][3])
        f["correct_score"] = cs
        f["cs_odds"] = round(7.0 + (abs(h_lam - a_lam) * 2), 2)
        f["model_xG"] = f"{h_lam} - {a_lam}"
        f["btts_prob"] = f"{btts_pct}%"
        f["over_prob"] = f"{over_pct}%"
        slate.append(f)
        
    return slate

@app.route('/')
def index():
    tab = request.args.get('tab', 'dailypicks')
    slate = get_master_slate()
    
    acca_legs = int(request.args.get('legs', 3))
    selected_market = request.args.get('market_filter', 'All')
    
    filtered_pool = slate if selected_market == 'All' else [f for f in slate if selected_market.lower() in f['market'].lower()]
    current_acca = filtered_pool[:acca_legs]
    
    combined_odds = round(product := __import__('functools').reduce(lambda x, y: x * y, [l['odds'] for l in current_acca], 1.0), 2) if current_acca else 1.0

    return render_template('index.html', active_tab=tab, slate=slate, current_acca=current_acca, acca_legs=acca_legs, selected_market=selected_market, combined_odds=combined_odds)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
