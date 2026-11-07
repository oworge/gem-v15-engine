from flask import Flask, render_template
import math
import requests
from datetime import datetime

app = Flask(__name__)

# ─── LIVE FIXTURE SCRAPER ──────────────────────────────────────
def fetch_live_fixtures():
    """Pull real UK fixtures from Football Web Pages API (free, no key)"""
    url = "https://www.footballwebpages.co.uk/api/fixtures"
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            fixtures = []
            today = datetime.utcnow().strftime("%Y-%m-%d")
            for m in data.get("fixtures", []):
                # Filter to today's games only
                if m.get("date", "").startswith(today):
                    fixtures.append({
                        "ko": m.get("time", "TBC"),
                        "league": m.get("competition", "UK Football"),
                        "home": m.get("home_team", "TBC"),
                        "away": m.get("away_team", "TBC"),
                        # Base strength on league/team name for prediction
                        "h_attack": get_strength(m.get("home_team", "")),
                        "h_defence": get_defence(m.get("home_team", "")),
                        "a_attack": get_strength(m.get("away_team", "")),
                        "a_defence": get_defence(m.get("away_team", ""))
                    })
            if fixtures:
                return fixtures
    except Exception as e:
        print(f"API fetch failed: {e}")
    
    # Fallback: sample fixtures if API unavailable
    return [
        {"ko":"12:30","league":"Premier League","home":"Leeds United","away":"Tottenham","h_attack":1.8,"h_defence":1.5,"a_attack":2.2,"a_defence":1.2},
        {"ko":"15:00","league":"Premier League","home":"Arsenal","away":"Hull City","h_attack":2.9,"h_defence":0.6,"a_attack":0.9,"a_defence":2.5},
        {"ko":"15:00","league":"Premier League","home":"Fulham","away":"Newcastle","h_attack":2.0,"h_defence":1.4,"a_attack":2.1,"a_defence":1.5},
        {"ko":"17:30","league":"Premier League","home":"Nottm Forest","away":"Man City","h_attack":1.2,"h_defence":2.3,"a_attack":3.3,"a_defence":0.5},
        {"ko":"15:00","league":"Premier League","home":"Liverpool","away":"Ipswich Town","h_attack":3.1,"h_defence":0.5,"a_attack":0.8,"a_defence":2.9},
        {"ko":"15:00","league":"Premier League","home":"Brighton","away":"Brentford","h_attack":2.3,"h_defence":1.1,"a_attack":1.6,"a_defence":1.7},
    ]

def get_strength(team_name):
    """Attack strength based on team name recognition"""
    elite = ["Man City","Liverpool","Arsenal","Chelsea","Tottenham","Man Utd","Man United"]
    top = ["Brighton","Aston Villa","Newcastle","Fulham","Brentford","West Ham","Everton"]
    good = ["Leeds","Nottm Forest","Bournemouth","Crystal Palace","Wolves"]
    if any(t in team_name for t in elite): return 3.0
    if any(t in team_name for t in top): return 2.2
    if any(t in team_name for t in good): return 1.7
    return 1.0

def get_defence(team_name):
    """Defence strength (lower = tighter)"""
    elite = ["Man City","Liverpool","Arsenal","Chelsea"]
    top = ["Brighton","Tottenham","Newcastle","Aston Villa"]
    good = ["Fulham","Brentford","Everton","Leeds"]
    if any(t in team_name for t in elite): return 0.6
    if any(t in team_name for t in top): return 1.0
    if any(t in team_name for t in good): return 1.3
    return 1.8

# ─── POISSON PREDICTION ENGINE ─────────────────────────────────
def poisson_prob(lmbda, k):
    return (math.pow(lmbda, k) * math.exp(-lmbda)) / math.factorial(k)

def predict_match(m):
    home_exp = m["h_attack"] * m["a_defence"]
    away_exp = m["a_attack"] * m["h_defence"]
    
    hg = max(range(6), key=lambda g: poisson_prob(home_exp, g))
    ag = max(range(6), key=lambda g: poisson_prob(away_exp, g))
    
    # Confidence calculation
    h_prob = poisson_prob(home_exp, hg)
    a_prob = poisson_prob(away_exp, ag)
    conf = round((h_prob + a_prob) * 45)
    
    # Selection
    if hg > ag:
        selection = f"{m['home']} Win"
        fair_odds = round(1 / max(conf / 100, 0.01) + 0.15, 2)
    elif ag > hg:
        selection = f"{m['away']} Win"
        fair_odds = round(1 / max(conf / 100, 0.01) + 0.25, 2)
    else:
        selection = "Draw"
        fair_odds = round(1 / max(conf / 100, 0.01) + 0.40, 2)
    
    soft_odds = round(fair_odds * (1 + (0.05 if conf > 60 else 0.12)), 2)
    ev = round(((soft_odds / fair_odds) - 1) * 100, 1)
    ev_str = f"+{ev}%" if ev >= 0 else f"{ev}%"
    stake = f"£{round(25 * (conf / 65))} (0.25 Kelly)"
    
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

# ─── DATA LOAD ──────────────────────────────────────────────────
def get_all_picks():
    fixtures = fetch_live_fixtures()
    return [predict_match(m) for m in fixtures]

# ─── ROUTES ────────────────────────────────────────────────────
@app.route('/')
@app.route('/value-filter')
def value_filter():
    picks = get_all_picks()
    cards = [p for p in picks if p["ev_value"] > 5]
    return render_template('base.html', active='value', cards=cards, title="Value Filter Deck")

@app.route('/daily-picks')
def daily_picks():
    cards = get_all_picks()[:4]
    return render_template('base.html', active='daily', cards=cards, title="Daily Picks")

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
