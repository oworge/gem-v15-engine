from flask import Flask, render_template, request
from datetime import datetime
import math
import csv
import os

app = Flask(__name__)

LEDGER_FILE = "bankroll_ledger.csv"

def init_ledger():
    if not os.path.exists(LEDGER_FILE):
        with open(LEDGER_FILE, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "Fixture", "Market", "Odds", "EV_%", "Kelly_Stake_%", "Result"])

def log_trade(fixture, market, odds, ev, stake):
    init_ledger()
    with open(LEDGER_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), fixture, market, odds, ev, stake, "PENDING"])

def poisson_probability(lmbda, k):
    try:
        return (math.exp(-lmbda) * (lmbda ** k)) / math.factorial(k)
    except:
        return 0.0

def calculate_enhanced_prediction(home_att, away_def, away_att, home_def, market_odds):
    try:
        home_lambda = max(0.5, home_att * away_def * 1.35)
        away_lambda = max(0.5, away_att * home_def * 1.20)
        
        home_win_prob = sum(poisson_probability(home_lambda, h) * poisson_probability(away_lambda, a) for h in range(5) for a in range(5) if h > a)
        ai_consensus_boost = 1.04 if home_lambda > away_lambda else 0.98
        adjusted_prob = min(0.95, home_win_prob * ai_consensus_boost)
        
        implied_prob = 1.0 / market_odds
        ev_margin = ((adjusted_prob - implied_prob) / implied_prob) * 100
        
        best_score = "1 - 1"
        max_prob = 0.0
        for h in range(5):
            for a in range(5):
                prob = poisson_probability(home_lambda, h) * poisson_probability(away_lambda, a)
                if prob > max_prob:
                    max_prob = prob
                    best_score = f"{h} - {a}"
                    
        return round(home_lambda, 2), round(away_lambda, 2), best_score, round(ev_margin, 1)
    except Exception as e:
        return 1.25, 1.10, "1 - 1", 5.0

def get_master_slate():
    today_str = datetime.now().strftime("Sun, Nov 8, 2026")
    
    # Expanded Master Pool covering UK, Europe, Top 5 Leagues, Americas, Rest of World & Republic of Ireland
    raw_fixtures = [
        # UK / English Leagues
        {"id": 1, "home": "Brighton & Hove Albion", "away": "Brentford", "league": "English Premier League", "date": today_str, "time": "14:00 GMT", "stats": [1.45, 1.00, 1.35, 1.05], "market": "Over 1.5 Goals", "odds": 1.35, "builder": ["Over 1.5 Match Goals", "Kaoru Mitoma 1+ Shots on Target", "Yoane Wissa 1+ Shots on Target", "Carlos Baleba 2+ Fouls Committed", "Over 3.5 Cards"], "builder_odds": 4.60},
        {"id": 2, "home": "Manchester United", "away": "Aston Villa", "league": "English Premier League", "date": today_str, "time": "16:30 GMT", "stats": [1.35, 0.90, 1.25, 0.95], "market": "Over 1.5 Goals", "odds": 1.38, "builder": ["Over 1.5 Match Goals", "Bruno Fernandes 1+ Shots on Target", "John McGinn 2+ Fouls Committed", "Marcus Rashford 1+ Fouls Won", "Aston Villa Over 1.5 Cards"], "builder_odds": 4.85},
        {"id": 3, "home": "Crystal Palace", "away": "Liverpool", "league": "English Premier League", "date": today_str, "time": "14:00 GMT", "stats": [1.10, 0.95, 1.60, 0.80], "market": "Liverpool Win & Over 1.5", "odds": 1.75, "builder": ["Liverpool Win & Over 1.5", "Mohamed Salah 1+ Shots on Target", "Eberechi Eze 1+ Fouls Won", "Cheick Doucouré 2+ Fouls Committed", "Liverpool Most Corners"], "builder_odds": 5.40},
        {"id": 4, "home": "Leeds United", "away": "West Bromwich Albion", "league": "English Championship", "date": today_str, "time": "12:30 GMT", "stats": [1.50, 0.90, 1.15, 1.00], "market": "Home Win", "odds": 1.72, "builder": ["Leeds Win", "Over 2.5 Cards", "Gnonto 1+ Shots on Target"], "builder_odds": 3.90},
        
        # Spain (La Liga)
        {"id": 5, "home": "Villarreal", "away": "Getafe", "league": "Spanish La Liga", "date": today_str, "time": "18:30 GMT", "stats": [1.50, 0.85, 1.10, 1.00], "market": "Double Chance: 1X & Over 1.5", "odds": 1.45, "builder": ["Double Chance 1X & Over 1.5", "Gerard Moreno 1+ Shots on Target", "Mason Greenwood 1+ Fouls Won", "Mauro Arambarri 2+ Fouls Committed", "Over 4.5 Cards"], "builder_odds": 5.10},
        {"id": 6, "home": "Atlético Madrid", "away": "Barcelona", "league": "Spanish La Liga", "date": today_str, "time": "20:00 GMT", "stats": [1.20, 0.80, 1.45, 0.85], "market": "Double Chance: X2", "odds": 1.42, "builder": ["Double Chance X2", "Under 3.5 Match Goals", "Gavi 2+ Fouls Committed", "Lamine Yamal 1+ Fouls Won", "Over 4.5 Cards"], "builder_odds": 5.20},
        
        # Germany (Bundesliga)
        {"id": 7, "home": "Bayer Leverkusen", "away": "Borussia Dortmund", "league": "German Bundesliga", "date": today_str, "time": "17:30 GMT", "stats": [1.60, 1.00, 1.45, 0.95], "market": "BTTS - Yes", "odds": 1.65, "builder": ["BTTS - Yes", "Florian Wirtz 1+ Shots on Target", "Granit Xhaka 2+ Fouls"], "builder_odds": 4.10},
        
        # Italy (Serie A)
        {"id": 8, "home": "AC Milan", "away": "Napoli", "league": "Italian Serie A", "date": today_str, "time": "19:45 GMT", "stats": [1.30, 0.95, 1.35, 0.90], "market": "BTTS & Over 2.5", "odds": 2.10, "builder": ["BTTS & Over 2.5", "Christian Pulisic 1+ Shots on Target", "Over 3.5 Cards"], "builder_odds": 6.75},
        
        # France (Ligue 1)
        {"id": 9, "home": "Marseille", "away": "Nice", "league": "French Ligue 1", "date": today_str, "time": "16:00 GMT", "stats": [1.40, 0.90, 1.20, 0.95], "market": "Home Win", "odds": 1.80, "builder": ["Marseille Win", "Over 1.5 Goals"], "builder_odds": 2.95},
        
        # The Americas
        {"id": 10, "home": "LA Galaxy", "away": "Seattle Sounders", "league": "MLS (The Americas)", "date": today_str, "time": "22:00 GMT", "stats": [1.65, 1.10, 1.40, 1.05], "market": "Over 2.5 Goals", "odds": 1.55, "builder": ["Over 2.5 Goals", "BTTS - Yes"], "builder_odds": 2.30},
        
        # Republic of Ireland
        {"id": 11, "home": "Shamrock Rovers", "away": "Bohemians", "league": "League of Ireland Premier", "date": today_str, "time": "19:00 GMT", "stats": [1.55, 0.75, 1.05, 1.10], "market": "Shamrock Win", "odds": 1.50, "builder": ["Shamrock Win", "Under 3.5 Goals"], "builder_odds": 2.45},
        
        # Rest of the World
        {"id": 12, "home": "Al Hilal", "away": "Al Nassr", "league": "Saudi Pro League (Rest of World)", "date": today_str, "time": "18:00 GMT", "stats": [1.70, 1.00, 1.65, 1.05], "market": "BTTS & Over 2.5", "odds": 1.85, "builder": ["BTTS & Over 2.5", "Mitrovic 1+ Shots on Target", "Ronaldo 1+ Shots on Target"], "builder_odds": 3.80}
    ]
    
    slate = []
    for f in raw_fixtures:
        h_lam, a_lam, cs, ev_calc = calculate_enhanced_prediction(f["stats"][0], f["stats"][1], f["stats"][2], f["stats"][3], f["odds"])
        f["correct_score"] = cs
        f["cs_odds"] = round(7.0 + (abs(h_lam - a_lam) * 2), 2)
        f["ev"] = f"+{ev_calc}%" if ev_calc > 0 else f"{ev_calc}%"
        f["rating"] = "10/10" if ev_calc > 5.0 else "9.4/10"
        
        # Uncapped inclusion: If EV meets our +EV threshold, it enters the global slate
        if ev_calc >= 5.0:
            log_trade(f"{f['home']} vs {f['away']}", f['market'], f['odds'], f['ev'], "2.0%")
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
    
    try:
        combined_odds = round(product := __import__('functools').reduce(lambda x, y: x * y, [l['odds'] for l in current_acca], 1.0), 2) if current_acca else 1.0
    except:
        combined_odds = 1.0

    return render_template('index.html', active_tab=tab, slate=slate, current_acca=current_acca, acca_legs=acca_legs, selected_market=selected_market, combined_odds=combined_odds)

if __name__ == '__main__':
    init_ledger()
    app.run(debug=True, host='0.0.0.0', port=5000)
