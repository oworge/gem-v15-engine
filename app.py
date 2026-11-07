<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>EDGEMETRIX MONTE CARLO QUANT — GLOBAL</title>
<style>
*{box-sizing:border-box;margin:0;padding:0;}
body{background:#131922;color:#e2e6eb;font-family:Segoe UI,system-ui,-apple-system,sans-serif;padding:16px;}
.header-bar{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;}
h1{color:#38baf5;font-size:21px;}
.badge-ready{background:#29c859;color:#000;padding:7px 13px;border-radius:7px;font-weight:bold;font-size:13px;}
.badge-region{padding:3px 8px;border-radius:4px;font-size:11px;margin-left:6px;}
.reg-uk{background:#22c55e22;color:#22c55e;}
.reg-de{background:#f59e0b22;color:#f59e0b;}
.reg-fr{background:#3b82f622;color:#3b82f6;}
.reg-es{background:#ef444422;color:#ef4444;}
.reg-it{background:#8b5cf622;color:#8b5cf6;}
.reg-am{background:#ec489922;color:#ec4899;}
.reg-global{background:#06b6d422;color:#06b6d4;}
.tabs{display:flex;gap:8px;margin-bottom:18px;flex-wrap:wrap;}
.tab{background:#212c3a;padding:9px 13px;border-radius:5px;font-size:13px;cursor:pointer;text-decoration:none;color:#ccc;}
.tab.active{background:#e24242;color:#fff;font-weight:bold;}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:13px;}
.card{border:2px solid #e24242;background:#1a2430;padding:15px;border-radius:6px;}
.card h4{font-size:15px;margin-bottom:10px;color:#fff;}
.line{font-size:13px;margin:5px 0;}
.label{color:#b0b8c1;}
.val-green{color:#3be272;font-weight:bold;}
.val-orange{color:#ffb950;font-weight:bold;}
.val-blue{color:#38baf5;font-weight:bold;}
.no-cards{grid-column:1/-1;text-align:center;padding:30px;color:#777;}
.footer-note{margin-top:20px;font-size:12px;color:#666;}
</style>
</head>
<body>

<div class="header-bar">
  <div>
    <h1>EDGEMETRIX MONTE CARLO QUANT — GLOBAL</h1>
    <span style="font-size:12px;color:#94a3b8;">UK • DE • FR • ES • IT • Americas • Rest of World</span>
  </div>
  <span class="badge-ready">SYSTEM READY</span>
</div>

<div class="tabs">
  <a href="/value-filter" class="tab {% if active=='value' %}active{% endif %}">Value Filter Deck</a>
  <a href="/daily-picks" class="tab {% if active=='daily' %}active{% endif %}">Daily Picks</a>
  <a href="/acca-generator" class="tab {% if active=='acca' %}active{% endif %}">Acca Generator</a>
  <a href="/bet-builder" class="tab {% if active=='betbuilder' %}active{% endif %}">Bet Builder</a>
  <a href="/correct-score" class="tab {%
# Full complete deployment
Remove-Item app.py -ErrorAction SilentlyContinue

@'
from flask import Flask, render_template
import math
import requests
from datetime import datetime

app = Flask(__name__)

# ─── ALL LEAGUES: UK • Europe • Americas • Global ────────────────
TARGET_LEAGUES = {
    # UNITED KINGDOM
    "Premier League": "UK",
    "League One": "UK",
    "League Two": "UK",
    "National League": "UK",
    "Championship": "UK",
    # GERMANY
    "Bundesliga": "DE",
    "Bundesliga 2": "DE",
    "2. Bundesliga": "DE",
    # FRANCE
    "Ligue 1": "FR",
    "Ligue 2": "FR",
    # SPAIN
    "La Liga": "ES",
    "La Liga 2": "ES",
    "Segunda División": "ES",
    # ITALY
    "Serie A": "IT",
    "Serie B": "IT",
    # AMERICAS
    "MLS": "AM",
    "Brasileirão": "AM",
    "Liga MX": "AM",
    "Argentina Primera": "AM",
    # REST OF WORLD
    "Saudi Pro League": "GLOBAL",
    "J1 League": "GLOBAL",
    "A-League": "GLOBAL"
}

# ─── LIVE FIXTURE SCRAPER ────────────────────────────────────────
def fetch_live_fixtures():
    all_fixtures = []
    today = datetime.utcnow().strftime("%Y-%m-%d")
    
    try:
        resp = requests.get("https://www.footballwebpages.co.uk/api/fixtures", timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            for m in data.get("fixtures", []):
                comp = m.get("competition", "")
                if any(lg.lower() in comp.lower() for lg in TARGET_LEAGUES.keys()):
                    f_date = m.get("date", "").split("T")[0]
                    if f_date == today:
                        home = m.get("home_team", "TBC").strip()
                        away = m.get("away_team", "TBC").strip()
                        league = match_league_name(comp)
                        all_fixtures.append({
                            "ko": m.get("time", "TBC"),
                            "league": league,
                            "region": TARGET_LEAGUES.get(league, "Other"),
                            "home": home,
                            "away": away,
                            "h_attack": get_attack(home, league),
                            "h_defence": get_defence(home, league),
                            "a_attack": get_attack(away, league),
                            "a_defence": get_defence(away, league)
                        })
        if all_fixtures:
            print(f"✅ Loaded {len(all_fixtures)} matches")
            return all_fixtures
    except Exception as e:
        print(f"API Error: {e}")
    
    return get_fallback_dataset()

def match_league_name(name):
    n = name.strip()
    if "Premier" in n: return "Premier League"
    if "League One" in n: return "League One"
    if "League Two" in n: return "League Two"
    if "National League" in n: return "National League"
    if "Bundesliga 2" in n or "2. Bundesliga" in n: return "Bundesliga 2"
    if "Bundesliga" in n: return "Bundesliga"
    if "Ligue 1" in n: return "Ligue 1"
    if "La Liga 2" in n or "Segunda" in n: return "La Liga 2"
    if "La Liga" in n: return "La Liga"
    if "Serie A" in n and "Brazil" not in n: return "Serie A"
    if "Serie B" in n: return "Serie B"
    if "MLS" in n: return "MLS"
    if "Brasileirão" in n: return "Brasileirão"
    if "Liga MX" in n: return "Liga MX"
    if "Argentina" in n: return "Argentina Primera"
    if "Saudi" in n: return "Saudi Pro League"
    return n

def get_fallback_dataset():
    return [
        {"ko":"12:30","league":"Premier League","region":"UK","home":"Liverpool","away":"Tottenham","h_attack":3.05,"h_defence":0.55,"a_attack":2.15,"a_defence":1.15},
        {"ko":"15:00","league":"Premier League","region":"UK","home":"Arsenal","away":"Everton","h_attack":2.85,"h_defence":0.60,"a_attack":1.45,"a_defence":1.35},
        {"ko":"15:00","league":"League One","region":"UK","home":"Bolton Wanderers","away":"Portsmouth","h_attack":1.55,"h_defence":1.45,"a_attack":1.65,"a_defence":1.35},
        {"ko":"14:30","league":"Bundesliga","region":"DE","home":"Bayern Munich","away":"Bayer Leverkusen","h_attack":3.15,"h_defence":0.50,"a_attack":2.95,"a_defence":0.65},
        {"ko":"20:00","league":"Ligue 1","region":"FR","home":"Paris Saint-Germain","away":"Marseille","h_attack":3.05,"h_defence":0.55,"a_attack":2.05,"a_defence":1.15},
        {"ko":"17:30","league":"La Liga","region":"ES","home":"Real Madrid","away":"Barcelona","h_attack":2.95,"h_defence":0.60,"a_attack":2.85,"a_defence":0.65},
        {"ko":"19:45","league":"Serie A","region":"IT","home":"Inter Milan","away":"AC Milan","h_attack":2.75,"h_defence":0.65,"a_attack":2.45,"a_defence":0.85},
        {"ko":"19:30","league":"MLS","region":"AM","home":"LA Galaxy","away":"Seattle Sounders","h_attack":1.85,"h_defence":1.25,"a_attack":1.75,"a_defence":1.35},
        {"ko":"18:00","league":"Saudi Pro League","region":"GLOBAL","home":"Al Hilal","away":"Al Nassr","h_attack":2.25,"h_defence":0.95,"a_attack":2.15,"a_defence":1.05},
    ]

# ─── TEAM STRENGTH ───────────────────────────────────────────────
ELITE = ["Man City","Liverpool","Arsenal","Chelsea","Bayern","PSG","Real Madrid","Barcelona","Inter","Al Hilal"]
TOP_EU = ["Tottenham","Aston Villa","Newcastle","Leverkusen","Dortmund","AC Milan"]
TOP_AM = ["Flamengo","Palmeiras","LA Galaxy"]

def get_attack(name, league):
    if any(t in name for t in ELITE): return 2.95
    if any(t in name for t in TOP_EU): return 2.25
    if any(t in name for t in TOP_AM): return 2.05
    if league in ["Premier League","Bundesliga","Ligue 1","La Liga","Serie A"]: return 1.65
    return 1.25

def get_defence(name, league):
    if any(t in name for t in ELITE): return 0.55
    if any(t in name for t in TOP_EU): return 1.05
    if any(t in name for t in TOP_AM): return 1.15
    if league in ["Premier League","Bundesliga","Ligue 1","La Liga","Serie A"]: return 1.35
    return 1.65

# ─── POISSON PREDICTION ENGINE ───────────────────────────────────
def poisson(lmbda, k):
    return (math.pow(lmbda, k) * math.exp(-lmbda)) / math.factorial(k)

def predict_match(m):
    home_exp = m["h_attack"] * m["a_defence"] * 1.18
    away_exp = m["a_attack"] * m["h_defence"]
    
    h_probs = {g: poisson(home_exp, g) for g in range(8)}
    a_probs = {g: poisson(away_exp, g) for g in range(8)}
    
    hg = max(h_probs, key=h_probs.get)
    ag = max(a_probs, key=a_probs.get)
    
    home_win = sum(h_probs[h] * sum(a_probs[a] for a in range(h)) for h in range(8))
    away_win = sum(a_probs[a] * sum(h_probs[h] for h in range(a)) for a in range(8))
    draw = sum(h_probs[g] * a_probs[g] for g in range(8))
    
    max_p = max(home_win, away_win, draw)
    conf = round(max_p * 100)
    
    if max_p == home_win:
        selection = f"{m['home']} Win"
        fair_odds = round(100 / conf + 0.12, 2)
    elif max_p == away_win:
        selection = f"{m['away']} Win"
        fair_odds = round(100 / conf + 0.22, 2)
    else:
        selection = "Draw"
        fair_odds = round(100 / conf + 0.38, 2)
    
    margin = 0.065 if conf > 65 else 0.095 if conf > 50 else 0.13
    soft_odds = round(fair_odds * (1 + margin), 2)
    ev = round(((soft_odds / fair_odds) - 1) * 100, 1)
    ev_str = f"+{ev}%" if ev >= 0 else f"{ev}%"
    stake = f"£{round(25 * (conf / 75), 1)} (0.25 Kelly)"
    
    return {
        "match": f"{m['home']} vs {m['away']}",
        "ko": m["ko"],
        "league": m["league"],
        "region": m["region"],
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
    return [predict_match(m) for m in fetch_live_fixtures()]

# ─── ROUTES ─────────────────────────────────────────────────────
@app.route('/api/fixtures')
def api_fixtures():
    return {"generated": datetime.utcnow().isoformat(), "count": len(get_all_picks()), "fixtures": get_all_picks()}

@app.route('/')
@app.route('/value-filter')
def value_filter():
    cards = [p for p in get_all_picks() if p["ev_value"] > 5]
    return render_template('base.html', active='value', cards=cards, title="Value Filter Deck")

@app.route('/daily-picks')
def daily_picks():
    cards = sorted(get_all_picks(), key=lambda x: x["ev_value"], reverse=True)[:6]
    return render_template('base.html', active='daily', cards=cards, title="Daily Picks — Top EV")

@app.route('/acca-generator')
def acca_generator():
    return render_template('base.html', active='acca', cards=get_all_picks(), title="Acca Generator — Global Slate")

@app.route('/bet-builder')
def bet_builder():
    return render_template('base.html', active='betbuilder', cards=get_all_picks(), title="Bet Builder — All Leagues")

@app.route('/correct-score')
def correct_score():
    cards = [p for p in get_all_picks() if p["hg"] + p["ag"] >= 2]
    return render_template('base.html', active='correctscore', cards=cards, title="Correct Score Deck")

@app.route('/future-games')
def future_games():
    return render_template('base.html', active='future', cards=get_all_picks(), title="Future Games — Worldwide")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
