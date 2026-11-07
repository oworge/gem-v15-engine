from flask import Flask, render_template
import math
import requests
from datetime import datetime

app = Flask(__name__)

# ─── YOUR RENDER API ENDPOINT ───────────────────────────────────
# Update this to match your actual API URL in Render
RENDER_API_URL = "https://gem-v15-engine.onrender.com/api/fixtures"

def fetch_live_fixtures():
    """Pull fixtures from YOUR API running on Render"""
    try:
        resp = requests.get(RENDER_API_URL, timeout=20)
        if resp.status_code == 200:
            data = resp.json()
            fixtures = []
            today = datetime.utcnow().strftime("%Y-%m-%d")
            
            # Handle different API response formats
            fixture_list = data.get("fixtures", data.get("matches", data if isinstance(data, list) else []))
            
            for m in fixture_list:
                f_date = m.get("date", m.get("kickoff_date", "")).split("T")[0]
                if f_date == today or not f_date:  # include if no date filter
                    home = m.get("home_team", m.get("home", "TBC")).strip()
                    away = m.get("away_team", m.get("away", "TBC")).strip()
                    fixtures.append({
                        "ko": m.get("time", m.get("kickoff_time", "TBC")),
                        "league": m.get("competition", m.get("league", "UK Football")),
                        "home": home,
                        "away": away,
                        "h_attack": get_attack(home),
                        "h_defence": get_defence(home),
                        "a_attack": get_attack(away),
                        "a_defence": get_defence(away)
                    })
            if fixtures:
                print(f"✅ Pulled {len(fixtures)} fixtures from your Render API")
                return fixtures
            print("⚠️ API returned data but no fixtures matched")
    except Exception as e:
        print(f"🔌 Render API connection: {e}")
    
    # Fallback: sample data if API unreachable
    print("ℹ️ Using fallback data")
    return [
        {"ko":"12:30","league":"Premier League","home":"Leeds United","away":"Tottenham","h_attack":1.65,"h_defence":1.45,"a_attack":2.15,"a_defence":1.15},
        {"ko":"15:00","league":"Premier League","home":"Arsenal","away":"Hull City","h_attack":2.85,"h_defence":0.55,"a_attack":0.85,"a_defence":2.45},
        {"ko":"15:00","league":"Premier League","home":"Fulham","away":"Newcastle","h_attack":1.95,"h_defence":1.35,"a_attack":2.05,"a_defence":1.45},
        {"ko":"17:30","league":"Premier League","home":"Nottm Forest","away":"Man City","h_attack":1.15,"h_defence":2.25,"a_attack":3.25,"a_defence":0.45},
        {"ko":"15:00","league":"Premier League","home":"Liverpool","away":"Ipswich Town","h_attack":3.05,"h_defence":0.45,"a_attack":0.75,"a_defence":2.85},
        {"ko":"15:00","league":"Premier League","home":"Brighton","away":"Brentford","h_attack":2.25,"h_defence":1.05,"a_attack":1.55,"a_defence":1.65},
    ]

# ─── TEAM STRENGTH DATABASE ─────────────────────────────────────
ELITE_ATTACK = ["Man City","Liverpool","Arsenal","Chelsea"]
TOP_ATTACK = ["Tottenham","Aston Villa","Newcastle","Brighton","Man Utd","Manchester United"]
MID_ATTACK = ["Fulham","West Ham","Brentford","Everton","Leeds United","Bournemouth"]

ELITE_DEF = ["Man City","Arsenal","Liverpool","Chelsea"]
TOP_DEF = ["Brighton","Tottenham","Aston Villa","Newcastle"]
MID_DEF = ["Fulham","Brentford","Everton","West Ham"]

def get_attack(name):
    if any(t in name for t in ELITE_ATTACK): return 2.95
    if any(t in name for t in TOP_ATTACK): return 2.20
    if any(t in name for t in MID_ATTACK): return 1.65
    return 1.05

def get_defence(name):
    if any(t in name for t in ELITE_DEF): return 0.55
    if any(t in name for t in TOP_DEF): return 1.00
    if any(t in name for t in MID_DEF): return 1.35
    return 1.85

# ─── ADVANCED POISSON ENGINE ───────────────────────────────────
def poisson(lmbda, k):
    return (math.pow(lmbda, k) * math.exp(-lmbda)) / math.factorial(k)

def predict_match(m):
    home_adv = 1.18
    home_exp = m["h_attack"] * m["a_defence"] * home_adv
    away_exp = m["a_attack"] * m["h_defence"]
    
    h_probs = {g: poisson(home_exp, g) for g in range(8)}
    a_probs = {g: poisson(away_exp, g) for g in range(8)}
    
    hg = max(h_probs, key=h_probs.get)
    ag = max(a_probs, key=a_probs.get)
    
    home_win_prob = sum(h_probs[h] * sum(a_probs[a] for a in range(h)) for h in range(8))
    away_win_prob = sum(a_probs[a] * sum(h_probs[h] for h in range(a)) for a in range(8))
    draw_prob = sum(h_probs[g] * a_probs[g] for g in range(8))
    
    max_p = max(home_win_prob, away_win_prob, draw_prob)
    conf = round(max_p * 100)
    
    if max_p == home_win_prob:
        selection = f"{m['home']} Win"
        fair_odds = round(100 / conf + 0.12, 2)
    elif max_p == away_win_prob:
        selection = f"{m['away']} Win"
        fair_odds = round(100 / conf + 0.22, 2)
    else:
        selection = "Draw"
        fair_odds = round(100 / conf + 0.38, 2)
    
    margin = 0.065 if conf > 65 else 0.095 if conf > 50 else 0.13
    soft_odds = round(fair_odds * (1 + margin), 2)
    ev = round(((soft_odds / fair_odds) - 1) * 100, 1)
    ev_str = f"+{ev}%" if ev >= 0 else f"{ev}%"
    
    stake_amt = round(25 * (conf / 75), 1)
    stake = f"£{stake_amt} (0.25 Kelly)"
    
    return {
        "match": f"{m['home']} vs {m['away']}",
        "ko": m["ko"],
        "league": m["league"],
        "selection": selection,
        "confidence": f"{conf}%",
        "score": f"{hg} - {ag}",
        "soft_fair": f"{soft_odds} / {fair_odds}",
        "ev": ev_str,
        "stake": stake,
        "hg": hg, "ag": ag,
        "ev_value": ev
    }

def get_all_picks():
    fixtures = fetch_live_fixtures()
    return [predict_match(m) for m in fixtures]

# ─── YOUR API ENDPOINT (served from the same app) ──────────────
@app.route('/api/fixtures')
def api_fixtures():
    """Your Render API endpoint — returns processed fixture data"""
    return {
        "generated": datetime.utcnow().isoformat(),
        "count": len(get_all_picks()),
        "fixtures": get_all_picks()
    }

# ─── DASHBOARD ROUTES ──────────────────────────────────────────
@app.route('/')
@app.route('/value-filter')
def value_filter():
    picks = get_all_picks()
    cards = [p for p in picks if p["ev_value"] > 5]
    return render_template('base.html', active='value', cards=cards, title="Value Filter Deck")

@app.route('/daily-picks')
def daily_picks():
    cards = sorted(get_all_picks(), key=lambda x: x["ev_value"], reverse=True)[:4]
    return render_template('base.html', active='daily', cards=cards, title="Daily Picks — Top EV")

@app.route('/acca-generator')
def acca_generator():
    cards = get_all_picks()
    return render_template('base.html', active='acca', cards=cards, title="Acca Generator")

@app.route('/bet-builder')
def bet_builder():
    cards = get_all_picks()
    return render_template('base.html', active='betbuilder', cards=cards, title="Bet Builder")

@app.route('/correct-score')
def correct_score():
    picks = get_all_picks()
    cards = [p for p in picks if p["hg"] + p["ag"] >= 2]
    return render_template('base.html', active='correctscore', cards=cards, title="Correct Score Deck")

@app.route('/future-games')
def future_games():
    cards = get_all_picks()
    return render_template('base.html', active='future', cards=cards, title="Future Games")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
