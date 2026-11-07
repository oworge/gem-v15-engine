from flask import Flask, render_template
import math

app = Flask(__name__)

# Today's UK fixtures with strength data
MATCHES = [
    {
        "id": 1,
        "ko": "12:30",
        "league": "Premier League",
        "home": "Leeds United",
        "away": "Tottenham",
        "h_attack": 1.8, "h_defence": 1.5,
        "a_attack": 2.2, "a_defence": 1.2
    },
    {
        "id": 2,
        "ko": "15:00",
        "league": "Premier League",
        "home": "Arsenal",
        "away": "Hull City",
        "h_attack": 2.9, "h_defence": 0.6,
        "a_attack": 0.9, "a_defence": 2.5
    },
    {
        "id": 3,
        "ko": "15:00",
        "league": "Premier League",
        "home": "Fulham",
        "away": "Newcastle",
        "h_attack": 2.0, "h_defence": 1.4,
        "a_attack": 2.1, "a_defence": 1.5
    },
    {
        "id": 4,
        "ko": "17:30",
        "league": "Premier League",
        "home": "Nottm Forest",
        "away": "Man City",
        "h_attack": 1.2, "h_defence": 2.3,
        "a_attack": 3.3, "a_defence": 0.5
    },
    {
        "id": 5,
        "ko": "15:00",
        "league": "Premier League",
        "home": "Liverpool",
        "away": "Ipswich Town",
        "h_attack": 3.1, "h_defence": 0.5,
        "a_attack": 0.8, "a_defence": 2.9
    },
    {
        "id": 6,
        "ko": "15:00",
        "league": "Premier League",
        "home": "Brighton",
        "away": "Brentford",
        "h_attack": 2.3, "h_defence": 1.1,
        "a_attack": 1.6, "a_defence": 1.7
    },
    {
        "id": 7,
        "ko": "15:00",
        "league": "Premier League",
        "home": "Bournemouth",
        "away": "Sunderland",
        "h_attack": 2.4, "h_defence": 1.3,
        "a_attack": 1.3, "a_defence": 2.0
    },
    {
        "id": 8,
        "ko": "15:00",
        "league": "Premier League",
        "home": "Crystal Palace",
        "away": "Everton",
        "h_attack": 1.6, "h_defence": 1.7,
        "a_attack": 1.5, "a_defence": 1.8
    }
]

def poisson_prob(lmbda, k):
    return (math.pow(lmbda, k) * math.exp(-lmbda)) / math.factorial(k)

def predict_match(m):
    home_exp = m["h_attack"] * m["a_defence"]
    away_exp = m["a_attack"] * m["h_defence"]
    
    hg = max(range(6), key=lambda g: poisson_prob(home_exp, g))
    ag = max(range(6), key=lambda g: poisson_prob(away_exp, g))
    
    # Calculate confidence
    h_prob = poisson_prob(home_exp, hg)
    a_prob = poisson_prob(away_exp, ag)
    conf = round((h_prob + a_prob) * 45)
    
    # Selection
    if hg > ag:
        selection = f"{m['home']} Win"
        fair_odds = round(1 / (conf / 100) + 0.15, 2)
    elif ag > hg:
        selection = f"{m['away']} Win"
        fair_odds = round(1 / (conf / 100) + 0.25, 2)
    else:
        selection = "Draw"
        fair_odds = round(1 / (conf / 100) + 0.40, 2)
    
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
        "hg": hg, "ag": ag
    }

# Generate all predictions
ALL_PICKS = [predict_match(m) for m in MATCHES]

# Tab-specific subsets
VALUE_FILTER = [p for p in ALL_PICKS if float(p["ev"].strip('%')) > 5]
DAILY_PICKS = ALL_PICKS[:4]
ACCA_BUILDER = ALL_PICKS
CORRECT_SCORE = [p for p in ALL_PICKS if p["hg"] + p["ag"] >= 2]
FUTURE_GAMES = ALL_PICKS

@app.route('/')
@app.route('/value-filter')
def value_filter():
    return render_template('base.html', active='value', cards=VALUE_FILTER, title="Value Filter Deck")

@app.route('/daily-picks')
def daily_picks():
    return render_template('base.html', active='daily', cards=DAILY_PICKS, title="Daily Picks")

@app.route('/acca-generator')
def acca_generator():
    return render_template('base.html', active='acca', cards=ACCA_BUILDER, title="Acca Generator")

@app.route('/bet-builder')
def bet_builder():
    return render_template('base.html', active='betbuilder', cards=ALL_PICKS, title="Bet Builder")

@app.route('/correct-score')
def correct_score():
    return render_template('base.html', active='correctscore', cards=CORRECT_SCORE, title="Correct Score Deck")

@app.route('/future-games')
def future_games():
    return render_template('base.html', active='future', cards=FUTURE_GAMES, title="Future Games")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
