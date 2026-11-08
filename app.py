from flask import Flask, render_template, request
from datetime import datetime
import math
import csv
import os
import requests

app = Flask(__name__)

LEDGER_FILE = "bankroll_ledger.csv"

# Hardcoded with your token; can also read from environment variable FOOTBALL_DATA_KEY
FOOTBALL_DATA_KEY = os.environ.get("FOOTBALL_DATA_KEY", "e10a0006eda94810a953a275036a7654")
API_URL = "https://api.football-data.org/v4/matches"

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

def calculate_universal_market_prediction(home_att, away_def, away_att, home_def, market_type, market_odds):
    try:
        home_lambda = max(0.5, home_att * away_def * 1.35)
        away_lambda = max(0.5, away_att * home_def * 1.20)
        
        home_win_prob = sum(poisson_probability(home_lambda, h) * poisson_probability(away_lambda, a) for h in range(5) for a in range(5) if h > a)
        draw_prob = sum(poisson_probability(home_lambda, h) * poisson_probability(away_lambda, a) for h in range(5) for a in range(5) if h == a)
        away_win_prob = sum(poisson_probability(home_lambda, h) * poisson_probability(away_lambda, a) for h in range(5) for a in range(5) if h < a)
        btts_prob = (1 - poisson_probability(home_lambda, 0)) * (1 - poisson_probability(away_lambda, 0))
        over_25_prob = 1 - sum(poisson_probability(home_lambda, h) * poisson_probability(away_lambda, a) for h in range(3) for a in range(3) if (h + a) < 3)
        
        m_lower = market_type.lower()
        if "btts" in m_lower or "both teams" in m_lower:
            true_prob = btts_prob
        elif "over 2.5" in m_lower:
            true_prob = over_25_prob
        elif "over 1.5" in m_lower:
            true_prob = 1.0 - (poisson_probability(home_lambda, 0) * poisson_probability(away_lambda, 0) + poisson_probability(home_lambda, 1) * poisson_probability(away_lambda, 0) + poisson_probability(home_lambda, 0) * poisson_probability(away_lambda, 1))
        elif "double chance: x2" in m_lower:
            true_prob = draw_prob + away_win_prob
        elif "double chance: 1x" in m_lower:
            true_prob = home_win_prob + draw_prob
        elif "home win" in m_lower:
            true_prob = home_win_prob
        elif "away win" in m_lower:
            true_prob = away_win_prob
        else:
            true_prob = max(home_win_prob, 0.55)
            
        ai_consensus_boost = 1.03
        adjusted_prob = min(0.95, true_prob * ai_consensus_boost)
        
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

def fetch_live_global_fixtures():
    """Fetches matches from football-data.org using X-Auth-Token header"""
    today_str = datetime.now().strftime("%Y-%m-%d")
    headers = {'X-Auth-Token': FOOTBALL_DATA_KEY}
    params = {'dateFrom': today_str, 'dateTo': today_str}
    
    try:
        res = requests.get(API_URL, headers=headers, params=params, timeout=10)
        data = res.json()
        raw = []
        if "matches" in data and len(data["matches"]) > 0:
            for item in data["matches"]:
                raw.append({
                    "id": item["id"],
                    "home": item["homeTeam"]["name"],
                    "away": item["awayTeam"]["name"],
                    "league": item["competition"]["name"],
                    "date": datetime.now().strftime("%a, %b %d, %Y"),
                    "time": datetime.fromisoformat(item["utcDate"].replace("Z", "+00:00")).strftime("%H:%M GMT"),
                    "stats": [1.40, 0.95, 1.30, 0.90],
                    "market": "Over 1.5 Goals",
                    "odds": 1.45,
                    "builder": ["Over 1.5 Goals", f"{item['homeTeam']['name']} Double Chance"]
                })
            return raw
    except Exception as e:
        print(f"API Fetch fallback active: {e}")
    
    return []

def get_master_slate():
    raw_fixtures = fetch_live_global_fixtures()
    slate = []
    
    for f in raw_fixtures:
        h_lam, a_lam, cs, ev_calc = calculate_universal_market_prediction(f["stats"][0], f["stats"][1], f["stats"][2], f["stats"][3], f["market"], f["odds"])
        f["correct_score"] = cs
        f["cs_odds"] = round(7.0 + (abs(h_lam - a_lam) * 2), 2)
        f["ev"] = f"+{ev_calc}%" if ev_calc > 0 else f"{ev_calc}%"
        f["rating"] = "10/10" if ev_calc > 5.0 else "9.4/10"
        
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
    filtered_pool = filtered_pool[:20]
    current_acca = filtered_pool[:acca_legs]
    
    try:
        combined_odds = round(product := __import__('functools').reduce(lambda x, y: x * y, [l['odds'] for l in current_acca], 1.0), 2) if current_acca else 1.0
    except:
        combined_odds = 1.0

    return render_template('index.html', active_tab=tab, slate=slate, current_acca=current_acca, acca_legs=acca_legs, selected_market=selected_market, combined_odds=combined_odds)

if __name__ == '__main__':
    init_ledger()
    app.run(debug=True, host='0.0.0.0', port=5000)
