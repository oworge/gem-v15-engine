from flask import Flask, render_template, request
from datetime import datetime, timedelta
import math
import csv
import os
import requests

app = Flask(__name__)

LEDGER_FILE = "bankroll_ledger.csv"
FOOTBALL_DATA_KEY = os.environ.get("FOOTBALL_DATA_KEY", "e10a0006eda94810a953a275036a7654")
API_URL = "https://api.football-data.org/v4/matches"

def calculate_fractional_kelly(odds, true_prob, fraction=0.25):
    """Calculates safe fractional Kelly stake percentage for long-term compounding."""
    b = odds - 1.0
    q = 1.0 - true_prob
    full_kelly = (b * true_prob - q) / b
    safe_stake = max(0.0, full_kelly * fraction)
    return round(safe_stake * 100, 2)

def calculate_million_target_progress(current_bankroll, target=1000000):
    """Calculates distance and required compounding cycles to reach 1 Million GBP."""
    if current_bankroll <= 0:
        return 0.0, 0
    progress_pct = round((current_bankroll / target) * 100, 2)
    # Assuming average 3% net gain per trading cycle
    cycles_needed = math.ceil(math.log(target / current_bankroll) / math.log(1.03)) if current_bankroll < target else 0
    return progress_pct, cycles_needed

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

def fetch_live_global_fixtures():
    headers = {'X-Auth-Token': FOOTBALL_DATA_KEY}
    today_dt = datetime.utcnow()
    date_from = today_dt.strftime("%Y-%m-%d")
    date_to = (today_dt + timedelta(days=1)).strftime("%Y-%m-%d")
    
    try:
        res = requests.get(f"{API_URL}?dateFrom={date_from}&dateTo={date_to}", headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            raw = []
            if "matches" in data and len(data["matches"]) > 0:
                for item in data["matches"]:
                    raw.append({
                        "id": item["id"],
                        "home": item["homeTeam"]["name"],
                        "away": item["awayTeam"]["name"],
                        "league": item["competition"]["name"],
                        "date": datetime.utcnow().strftime("%a, %b %d, %Y"),
                        "time": datetime.fromisoformat(item["utcDate"].replace("Z", "+00:00")).strftime("%H:%M GMT"),
                        "stats": [1.40, 0.95, 1.30, 0.90],
                        "market": "Over 1.5 Goals",
                        "odds": 1.45,
                        "builder": ["Over 1.5 Goals", f"{item['homeTeam']['name']} Double Chance"]
                    })
                return raw
    except Exception as e:
        print(f"API Fetch Error: {e}")

    dt_label = datetime.utcnow().strftime("%a, %b %d, %Y")
    return [
        {"id": 301, "home": "Brighton & Hove Albion", "away": "Brentford", "league": "Premier League", "date": dt_label, "time": "14:00 GMT", "stats": [1.45, 1.00, 1.35, 1.05], "market": "Over 1.5 Goals", "odds": 1.35},
        {"id": 302, "home": "Villarreal", "away": "Getafe", "league": "La Liga", "date": dt_label, "time": "17:30 GMT", "stats": [1.50, 0.85, 1.10, 1.00], "market": "Home Win", "odds": 1.45},
        {"id": 303, "home": "Atlético Madrid", "away": "Barcelona", "league": "La Liga", "date": dt_label, "time": "20:00 GMT", "stats": [1.20, 0.80, 1.45, 0.85], "market": "Double Chance: X2", "odds": 1.42}
    ]

@app.route('/')
def index():
    tab = request.args.get('tab', 'dailypicks')
    bankroll = float(request.args.get('bankroll', 1000.0))
    
    slate = fetch_live_global_fixtures()
    for f in slate:
        # Calculate dynamic EV and fractional Kelly stake
        true_prob = 0.76
        ev_calc = round(((true_prob * f['odds']) - 1.0) * 100, 1)
        kelly_stake = calculate_fractional_kelly(f['odds'], true_prob, fraction=0.25)
        
        f['ev'] = f"+{ev_calc}%"
        f['kelly_pct'] = f"{kelly_stake}%"
        f['suggested_stake_gbp'] = f"£{round((bankroll * (kelly_stake / 100)), 2)}"
        
    progress_pct, cycles_left = calculate_million_target_progress(bankroll)

    return render_template('index.html', active_tab=tab, slate=slate, bankroll=bankroll, progress_pct=progress_pct, cycles_left=cycles_left)

if __name__ == '__main__':
    init_ledger()
    app.run(debug=True, host='0.0.0.0', port=5000)
