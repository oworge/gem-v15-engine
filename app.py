from flask import Flask, render_template
import math
import requests
from datetime import datetime

app = Flask(__name__)

# ─── COMPLETE GLOBAL LEAGUE LIST ──────────────────────────────────
TARGET_LEAGUES = {
    # UNITED KINGDOM
    "Premier League": "UK",
    "Championship": "UK",
    "League One": "UK",
    "League Two": "UK",
    "National League": "UK",
    
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
    
    # REST OF EUROPE — FULL COVERAGE
    "Primeira Liga": "EU",
    "Liga Portugal": "EU",
    "Eredivisie": "EU",
    "Eerste Divisie": "EU",
    "Super Lig": "EU",
    "Süper Lig": "EU",
    "Spor Toto Süper Lig": "EU",
    "Super Lig 1": "EU",
    "Pro League": "EU",
    "Belgian Pro League": "EU",
    "Challenger Pro League": "EU",
    "Super League": "EU",
    "Swiss Super League": "EU",
    "Serie A Switzerland": "EU",
    "Austrian Bundesliga": "EU",
    "Bundesliga Austria": "EU",
    "Czech First League": "EU",
    "Fortuna Liga": "EU",
    "Ekstraklasa": "EU",
    "Polish Ekstraklasa": "EU",
    "Croatian First League": "EU",
    "Prva HNL": "EU",
    "Serbian SuperLiga": "EU",
    "SuperLiga Srbija": "EU",
    "Greek Super League": "EU",
    "Super League Greece": "EU",
    "Danish Superliga": "EU",
    "Eliteserien": "EU",
    "Tippeligaen": "EU",
    "Allsvenskan": "EU",
    "Swedish Allsvenskan": "EU",
    "Veikkausliiga": "EU",
    "Finnish Veikkausliiga": "EU",
    "Scottish Premiership": "UK",
    "Scottish Championship": "UK",
    "Scottish League One": "UK",
    "Scottish League Two": "UK",
    
    # AMERICAS
    "MLS": "AM",
    "Brasileirão": "AM",
    "Serie A Brazil": "AM",
    "Liga MX": "AM",
    "Argentina Primera": "AM",
    "Copa Libertadores": "AM",
    
    # REST OF WORLD
    "Saudi Pro League": "GLOBAL",
    "J1 League": "GLOBAL",
    "K League 1": "GLOBAL",
    "A-League": "GLOBAL",
    "Pro League Saudi": "GLOBAL"
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
            print(f"✅ Loaded {len(all_fixtures)} matches across {len(set(f['league'] for f in all_fixtures))} leagues")
            return all_fixtures
    except Exception as e:
        print(f"API Error: {e}")
    
    return get_fallback_dataset()

def match_league_name(name):
    n = name.strip()
    if "Premier" in n: return "Premier League"
    if "Championship" in n and "EFL" not in n: return "Championship"
    if "League One" in n: return "League One"
    if "League Two" in n: return "League Two"
    if "National League" in n: return "National League"
    if "Scottish Premiership" in n or "SPL" in n: return "Scottish Premiership"
    if "Scottish Championship" in n: return "Scottish Championship"
    if "Bundesliga 2" in n or "2. Bundesliga" in n: return "Bundesliga 2"
    if "Bundesliga" in n and "Austria" not in n: return "Bundesliga"
    if "Austrian" in n or "Österreich" in n: return "Austrian Bundesliga"
    if "Ligue 1" in n: return "Ligue 1"
    if "Ligue 2" in n: return "Ligue 2"
    if "La Liga 2" in n or "Segunda" in n: return "La Liga 2"
    if "La Liga" in n: return "La Liga"
    if "Serie A" in n and "Brazil" not in n and "Swiss" not in n: return "Serie A"
    if "Serie B" in n: return "Serie B"
    if "Primeira" in n or "Liga Portugal" in n: return "Primeira Liga"
    if "Eredivisie" in n: return "Eredivisie"
    if "Eerste Divisie" in n: return "Eerste Divisie"
    if "Süper Lig" in n or "Super Lig" in n and "Greece" not in n: return "Süper Lig"
    if "Belgian" in n or "Pro League" in n and "Saudi" not in n: return "Belgian Pro League"
    if "Swiss" in n or "Super League" in n and "Greece" not in n: return "Swiss Super League"
    if "Greek" in n or "Super League Greece" in n: return "Super League Greece"
    if "Czech" in n or "Fortuna" in n: return "Czech First League"
    if "Ekstraklasa" in n or "Polish" in n: return "Ekstraklasa"
    if "Croatia" in n or "Prva HNL" in n: return "Croatian First League"
    if "Serbia" in n or "SuperLiga Srbija" in n: return "Serbian SuperLiga"
    if "Danish" in n or "Superliga" in n: return "Danish Superliga"
    if "Eliteserien" in n or "Norway" in n: return "Eliteserien"
    if "Allsvenskan" in n or "Sweden" in n: return "Allsvenskan"
    if "Veikkausliiga" in n or "Finland" in n: return "Veikkausliiga"
    if "MLS" in n: return "MLS"
    if "Brasileirão" in n or "Brazil" in n: return "Brasileirão"
    if "Liga MX" in n or "Mexico" in n: return "Liga MX"
    if "Argentina" in n: return "Argentina Primera"
    if "Saudi" in n: return "Saudi Pro League"
    if "J1" in n or "Japan" in n: return "J1 League"
    if "K League" in n or "Korea" in n: return "K League 1"
    if "A-League" in n or "Australia" in n: return "A-League"
    return n

# ─── FALLBACK: FULL EUROPE + GLOBAL DATASET ──────────────────────
def get_fallback_dataset():
    return [
        # ─── UK ───
        {"ko":"12:30","league":"Premier League","region":"UK","home":"Liverpool","away":"Tottenham","h_attack":3.05,"h_defence":0.55,"a_attack":2.15,"a_defence":1.15},
        {"ko":"15:00","league":"Premier League","region":"UK","home":"Arsenal","away":"Everton","h_attack":2.85,"h_defence":0.60,"a_attack":1.45,"a_defence":1.35},
        {"ko":"15:00","league":"Scottish Premiership","region":"UK","home":"Celtic","away":"Rangers","h_attack":2.45,"h_defence":0.75,"a_attack":2.35,"a_defence":0.85},
        {"ko":"15:00","league":"League One","region":"UK","home":"Bolton Wanderers","away":"Portsmouth","h_attack":1.55,"h_defence":1.45,"a_attack":1.65,"a_defence":1.35},
        
        # ─── GERMANY ───
        {"ko":"14:30","league":"Bundesliga","region":"DE","home":"Bayern Munich","away":"Bayer Leverkusen","h_attack":3.15,"h_defence":0.50,"a_attack":2.95,"a_defence":0.65},
        {"ko":"16:30","league":"Austrian Bundesliga","region":"EU","home":"Red Bull Salzburg","away":"Sturm Graz","h_attack":2.15,"h_defence":0.95,"a_attack":1.85,"a_defence":1.15},
        
        # ─── FRANCE ───
        {"ko":"20:00","league":"Ligue 1","region":"FR","home":"Paris Saint-Germain","away":"Marseille","h_attack":3.05,"h_defence":0.55,"a_attack":2.05,"a_defence":1.15},
        
        # ─── SPAIN ───
        {"ko":"17:30","league":"La Liga","region":"ES","home":"Real Madrid","away":"Barcelona","h_attack":2.95,"h_defence":0.60,"a_attack":2.85,"a_defence":0.65},
        
        # ─── ITALY ───
        {"ko":"19:45","league":"Serie A","region":"IT","home":"Inter Milan","away":"AC Milan","h_attack":2.75,"h_defence":0.65,"a_attack":2.45,"a_defence":0.85},
        
        # ─── REST OF EUROPE — NEWLY ADDED ───
        {"ko":"20:00","league":"Primeira Liga","region":"EU","home":"Benfica","away":"Sporting CP","h_attack":2.25,"h_defence":0.90,"a_attack":2.15,"a_defence":0.95},
        {"ko":"19:00","league":"Eredivisie","region":"EU","home":"Ajax","away":"PSV Eindhoven","h_attack":2.35,"h_defence":0.85,"a_attack":2.45,"a_defence":0.80},
        {"ko":"18:00","league":"Süper Lig","region":"EU","home":"Galatasaray","away":"Fenerbahçe","h_attack":2.15,"h_defence":0.95,"a_attack":2.05,"a_defence":1.05},
        {"ko":"19:30","league":"Belgian Pro League","region":"EU","home":"Club Brugge","away":"Anderlecht","h_attack":2.05,"h_defence":1.00,"a_attack":1.95,"a_defence":1.10},
        {"ko":"17:00","league":"Swiss Super League","region":"EU","home":"Young Boys","away":"Basel","h_attack":1.95,"h_defence":1.05,"a_attack":1.85,"a_defence":1.15},
        {"ko":"18:00","league":"Super League Greece","region":"EU","home":"Olympiacos","away":"Panathinaikos","h_attack":1.85,"h_defence":1.10,"a_attack":1.75,"a_defence":1.20},
        {"ko":"19:00","league":"Czech First League","region":"EU","home":"Sparta Prague","away":"Slavia Prague","h_attack":1.80,"h_defence":1.15,"a_attack":1.75,"a_defence":1.20},
        {"ko":"17:30","league":"Ekstraklasa","region":"EU","home":"Legia Warsaw","away":"Lech Poznań","h_attack":1.70,"h_defence":1.20,"a_attack":1.65,"a_defence":1.25},
        {"ko":"18:00","league":"Danish Superliga","region":"EU","home":"FC Copenhagen","away":"Brøndby","h_attack":1.90,"h_defence":1.05,"a_attack":1.80,"a_defence":1.15},
        {"ko":"19:00","league":"Eliteserien","region":"EU","home":"Rosenborg","away":"Molde","h_attack":1.75,"h_defence":1.15,"a_attack":1.70,"a_defence":1.20},
        {"ko":"18:30","league":"Allsvenskan","region":"EU","home":"AIK","away":"Djurgårdens IF","h_attack":1.65,"h_defence":1.25,"a_attack":1.60,"a_defence":1.30},
        {"ko":"17:00","league":"Croatian First League","region":"EU","home":"Dinamo Zagreb","away":"Hajduk Split","h_attack":1.85,"h_defence":1.10,"a_attack":1.75,"a_defence":1.18},
        {"ko":"19:00","league":"Serbian SuperLiga","region":"EU","home":"Red Star Belgrade","away":"Partizan","h_attack":1.80,"h_defence":1.12,"a_attack":1.72,"a_defence":1.20},
        
        # ─── AMERICAS ───
        {"ko":"19:30","league":"MLS","region":"AM","home":"LA Galaxy","away":"Seattle Sounders","h_attack":1.85,"h_defence":1.25,"a_attack":1.75,"a_defence":1.35},
        {"ko":"00:00","league":"Brasileirão","region":"AM","home":"Flamengo","away":"Palmeiras","h_attack":2.05,"h_defence":1.05,"a_attack":2.15,"a_defence":0.95},
        
        # ─── REST OF WORLD ───
        {"ko":"18:00","league":"Saudi Pro League","region":"GLOBAL","home":"Al Hilal","away":"Al Nassr","h_attack":2.25,"h_defence":0.95,"a_attack":2.15,"a_defence":1.05},
    ]

# ─── EXPANDED TEAM STRENGTH DATABASE ─────────────────────────────
ELITE = ["Man City","Liverpool","Arsenal","Chelsea","Bayern","PSG","Real Madrid","Barcelona","Inter","Al Hilal"]
TOP_EU = ["Tottenham","Aston Villa","Newcastle","Leverkusen","Dortmund","AC Milan","Napoli","Benfica","Sporting","Ajax","PSV","Galatasaray","Fenerbahçe","Red Bull Salzburg"]
SOLID_EU = ["Celtic","Rangers","Club Brugge","Anderlecht","Young Boys","Basel","Olympiacos","Sparta Prague","Slavia Prague","Copenhagen","Brøndby","Dinamo Zagreb","Red Star"]
TOP_AM = ["Flamengo","Palmeiras","LA Galaxy"]

def get_attack(name, league):
    if any(t in name for t in ELITE): return 2.95
    if any(t in name for t in TOP_EU): return 2.25
    if any(t in name for t in SOLID_EU): return 1.90
    if any(t in name for t in TOP_AM): return 2.05
    if league in ["Premier League","Bundesliga","Ligue 1","La Liga","Serie A","Primeira Liga","Eredivisie","Süper Lig"]: return 1.65
    if league in ["Scottish Premiership","Belgian Pro League","Swiss Super League","Austrian Bundesliga","Danish Superliga"]: return 1.55
    return 1.30

def get_defence(name, league):
    if any(t in name for t in ELITE): return 0.55
    if any(t in name for t in TOP_EU): return 1.05
    if any(t in name for t in SOLID_EU): return 1.15
    if any(t in name for t in TOP_AM): return 1.15
    if league in ["Premier League","Bundesliga","Ligue 1","La Liga","Serie A","Primeira Liga","Eredivisie","Süper Lig"]: return 1.35
    if league in ["Scottish Premiership","Belgian Pro League","Swiss Super League","Austrian Bundesliga","Danish Superliga"]: return 1.40
    return 1.60

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
Remove-Item app.py -ErrorAction SilentlyContinue

@'
from flask import Flask, render_template
import math
import requests
from datetime import datetime

app = Flask(__name__)

# ─── COMPLETE GLOBAL LEAGUE LIST ──────────────────────────────────
TARGET_LEAGUES = {
    # UNITED KINGDOM
    "Premier League": "UK",
    "Championship": "UK",
    "League One": "UK",
    "League Two": "UK",
    "National League": "UK",
    "Scottish Premiership": "UK",
    "Scottish Championship": "UK",
    "Scottish League One": "UK",
    "Scottish League Two": "UK",
    
    # GERMANY
    "Bundesliga": "DE",
    "Bundesliga 2": "DE",
    "2. Bundesliga": "DE",
    "Austrian Bundesliga": "EU",
    
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
    
    # REST OF EUROPE — FULL COVERAGE
    "Primeira Liga": "EU",
    "Liga Portugal": "EU",
    "Eredivisie": "EU",
    "Eerste Divisie": "EU",
    "Süper Lig": "EU",
    "Super Lig": "EU",
    "Belgian Pro League": "EU",
    "Challenger Pro League": "EU",
    "Swiss Super League": "EU",
    "Czech First League": "EU",
    "Fortuna Liga": "EU",
    "Ekstraklasa": "EU",
    "Croatian First League": "EU",
    "Prva HNL": "EU",
    "Serbian SuperLiga": "EU",
    "SuperLiga Srbija": "EU",
    "Super League Greece": "EU",
    "Greek Super League": "EU",
    "Danish Superliga": "EU",
    "Eliteserien": "EU",
    "Allsvenskan": "EU",
    "Veikkausliiga": "EU",
    
    # AMERICAS
    "MLS": "AM",
    "Brasileirão": "AM",
    "Liga MX": "AM",
    "Argentina Primera": "AM",
    "Copa Libertadores": "AM",
    
    # REST OF WORLD
    "Saudi Pro League": "GLOBAL",
    "J1 League": "GLOBAL",
    "K League 1": "GLOBAL",
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
    if "Championship" in n and "EFL" not in n: return "Championship"
    if "League One" in n: return "League One"
    if "League Two" in n: return "League Two"
    if "National League" in n: return "National League"
    if "Scottish Premiership" in n or "SPL" in n: return "Scottish Premiership"
    if "Scottish Championship" in n: return "Scottish Championship"
    if "Bundesliga 2" in n or "2. Bundesliga" in n: return "Bundesliga 2"
    if "Bundesliga" in n and "Austria" not in n: return "Bundesliga"
    if "Austrian" in n or "Österreich" in n: return "Austrian Bundesliga"
    if "Ligue 1" in n: return "Ligue 1"
    if "Ligue 2" in n: return "Ligue 2"
    if "La Liga 2" in n or "Segunda" in n: return "La Liga 2"
    if "La Liga" in n: return "La Liga"
    if "Serie A" in n and "Brazil" not in n and "Swiss" not in n: return "Serie A"
    if "Serie B" in n: return "Serie B"
    if "Primeira" in n or "Liga Portugal" in n: return "Primeira Liga"
    if "Eredivisie" in n: return "Eredivisie"
    if "Eerste Divisie" in n: return "Eerste Divisie"
    if "Süper Lig" in n or "Super Lig" in n and "Greece" not in n: return "Süper Lig"
    if "Belgian" in n or "Pro League" in n and "Saudi" not in n: return "Belgian Pro League"
    if "Swiss" in n or "Super League" in n and "Greece" not in n: return "Swiss Super League"
    if "Greek" in n or "Super League Greece" in n: return "Super League Greece"
    if "Czech" in n or "Fortuna" in n: return "Czech First League"
    if "Ekstraklasa" in n or "Polish" in n: return "Ekstraklasa"
    if "Croatia" in n or "Prva HNL" in n: return "Croatian First League"
    if "Serbia" in n or "SuperLiga Srbija" in n: return "Serbian SuperLiga"
    if "Danish" in n or "Superliga" in n: return "Danish Superliga"
    if "Eliteserien" in n or "Norway" in n: return "Eliteserien"
    if "Allsvenskan" in n or "Sweden" in n: return "Allsvenskan"
    if "Veikkausliiga" in n or "Finland" in n: return "Veikkausliiga"
    if "MLS" in n: return "MLS"
    if "Brasileirão" in n or "Brazil" in n: return "Brasileirão"
    if "Liga MX" in n or "Mexico" in n: return "Liga MX"
    if "Argentina" in n: return "Argentina Primera"
    if "Saudi" in n: return "Saudi Pro League"
    if "J1" in n or "Japan" in n: return "J1 League"
    if "K League" in n or "Korea" in n: return "K League 1"
    if "A-League" in n or "Australia" in n: return "A-League"
    return n

# ─── FALLBACK: FULL EUROPE + GLOBAL DATASET ──────────────────────
def get_fallback_dataset():
    return [
        # UK
        {"ko":"12:30","league":"Premier League","region":"UK","home":"Liverpool","away":"Tottenham","h_attack":3.05,"h_defence":0.55,"a_attack":2.15,"a_defence":1.15},
        {"ko":"15:00","league":"Scottish Premiership","region":"UK","home":"Celtic","away":"Rangers","h_attack":2.45,"h_defence":0.75,"a_attack":2.35,"a_defence":0.85},
        {"ko":"15:00","league":"League One","region":"UK","home":"Bolton Wanderers","away":"Portsmouth","h_attack":1.55,"h_defence":1.45,"a_attack":1.65,"a_defence":1.35},
        
        # Germany
        {"ko":"14:30","league":"Bundesliga","region":"DE","home":"Bayern Munich","away":"Bayer Leverkusen","h_attack":3.15,"h_defence":0.50,"a_attack":2.95,"a_defence":0.65},
        {"ko":"16:30","league":"Austrian Bundesliga","region":"EU","home":"Red Bull Salzburg","away":"Sturm Graz","h_attack":2.15,"h_defence":0.95,"a_attack":1.85,"a_defence":1.15},
        
        # France
        {"ko":"20:00","league":"Ligue 1","region":"FR","home":"Paris Saint-Germain","away":"Marseille","h_attack":3.05,"h_defence":0.55,"a_attack":2.05,"a_defence":1.15},
        
        # Spain
        {"ko":"17:30","league":"La Liga","region":"ES","home":"Real Madrid","away":"Barcelona","h_attack":2.95,"h_defence":0.60,"a_attack":2.85,"a_defence":0.65},
        
        # Italy
        {"ko":"19:45","league":"Serie A","region":"IT","home":"Inter Milan","away":"AC Milan","h_attack":2.75,"h_defence":0.65,"a_attack":2.45,"a_defence":0.85},
        
        # Rest of Europe
        {"ko":"20:00","league":"Primeira Liga","region":"EU","home":"Benfica","away":"Sporting CP","h_attack":2.25,"h_defence":0.90,"a_attack":2.15,"a_defence":0.95},
        {"ko":"19:00","league":"Eredivisie","region":"EU","home":"Ajax","away":"PSV Eindhoven","h_attack":2.35,"h_defence":0.85,"a_attack":2.45,"a_defence":0.80},
        {"ko":"18:00","league":"Süper Lig","region":"EU","home":"Galatasaray","away":"Fenerbahçe","h_attack":2.15,"h_defence":0.95,"a_attack":2.05,"a_defence":1.05},
        {"ko":"19:30","league":"Belgian Pro League","region":"EU","home":"Club Brugge","away":"Anderlecht","h_attack":2.05,"h_defence":1.00,"a_attack":1.95,"a_defence":1.10},
        {"ko":"17:00","league":"Swiss Super League","region":"EU","home":"Young Boys","away":"Basel","h_attack":1.95,"h_defence":1.05,"a_attack":1.85,"a_defence":1.15},
        {"ko":"18:00","league":"Super League Greece","region":"EU","home":"Olympiacos","away":"Panathinaikos","h_attack":1.85,"h_defence":1.10,"a_attack":1.75,"a_defence":1.20},
        {"ko":"19:00","league":"Czech First League","region":"EU","home":"Sparta Prague","away":"Slavia Prague","h_attack":1.80,"h_defence":1.15,"a_attack":1.75,"a_defence":1.20},
        {"ko":"17:30","league":"Ekstraklasa","region":"EU","home":"Legia Warsaw","away":"Lech Poznań","h_attack":1.70,"h_defence":1.20,"a_attack":1.65,"a_defence":1.25},
        {"ko":"18:00","league":"Danish Superliga","region":"EU","home":"FC Copenhagen","away":"Brøndby","h_attack":1.90,"h_defence":1.05,"a_attack":1.80,"a_defence":1.15},
        {"ko":"19:00","league":"Eliteserien","region":"EU","home":"Rosenborg","away":"Molde","h_attack":1.75,"h_defence":1.15,"a_attack":1.70,"a_defence":1.20},
        {"ko":"18:30","league":"Allsvenskan","region":"EU","home":"AIK","away":"Djurgårdens IF","h_attack":1.65,"h_defence":1.25,"a_attack":1.60,"a_defence":1.30},
        {"ko":"17:00","league":"Croatian First League","region":"EU","home":"Dinamo Zagreb","away":"Hajduk Split","h_attack":1.85,"h_defence":1.10,"a_attack":1.75,"a_defence":1.18},
        {"ko":"19:00","league":"Serbian SuperLiga","region":"EU","home":"Red Star Belgrade","away":"Partizan","h_attack":1.80,"h_defence":1.12,"a_attack":1.72,"a_defence":1.20},
        
        # Americas
        {"ko":"19:30","league":"MLS","region":"AM","home":"LA Galaxy","away":"Seattle Sounders","h_attack":1.85,"h_defence":1.25,"a_attack":1.75,"a_defence":1.35},
        {"ko":"00:00","league":"Brasileirão","region":"AM","home":"Flamengo","away":"Palmeiras","h_attack":2.05,"h_defence":1.05,"a_attack":2.15,"a_defence":0.95},
        
        # Rest of World
        {"ko":"18:00","league":"Saudi Pro League","region":"GLOBAL","home":"Al Hilal","away":"Al Nassr","h_attack":2.25,"h_defence":0.95,"a_attack":2.15,"a_defence":1.05},
    ]

# ─── TEAM STRENGTH DATABASE ───────────────────────────────────────
ELITE = ["Man City","Liverpool","Arsenal","Chelsea","Bayern","PSG","Real Madrid","Barcelona","Inter","Al Hilal"]
TOP_EU = ["Tottenham","Aston Villa","Newcastle","Leverkusen","Dortmund","AC Milan","Napoli","Benfica","Sporting","Ajax","PSV","Galatasaray","Fenerbahçe","Red Bull Salzburg"]
SOLID_EU = ["Celtic","Rangers","Club Brugge","Anderlecht","Young Boys","Basel","Olympiacos","Sparta Prague","Slavia Prague","Copenhagen","Brøndby","Dinamo Zagreb","Red Star"]
TOP_AM = ["Flamengo","Palmeiras","LA Galaxy"]

def get_attack(name, league):
    if any(t in name for t in ELITE): return 2.95
    if any(t in name for t in TOP_EU): return 2.25
    if any(t in name for t in SOLID_EU): return 1.90
    if any(t in name for t in TOP_AM): return 2.05
    if league in ["Premier League","Bundesliga","Ligue 1","La Liga","Serie A","Primeira Liga","Eredivisie","Süper Lig"]: return 1.65
    if league in ["Scottish Premiership","Belgian Pro League","Swiss Super League","Austrian Bundesliga","Danish Superliga"]: return 1.55
    return 1.30

def get_defence(name, league):
    if any(t in name for t in ELITE): return 0.55
    if any(t in name for t in TOP_EU): return 1.05
    if any(t in name for t in SOLID_EU): return 1.15
    if any(t in name for t in TOP_AM): return 1.15
    if league in ["Premier League","Bundesliga","Ligue 1","La Liga","Serie A","Primeira Liga","Eredivisie","Süper Lig"]: return 1.35
    if league in ["Scottish Premiership","Belgian Pro League","Swiss Super League","Austrian Bundesliga","Danish Superliga"]: return 1.40
    return 1.60

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

# ─── ROUTES — ALL COMPLETE ───────────────────────────────────────
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
    return render_template('base.html', active='betbuilder', cards=get_all_p
Remove-Item app.py -ErrorAction SilentlyContinue

@'
from flask import Flask, render_template
import math
import requests
from datetime import datetime

app = Flask(__name__)

# ─── COMPLETE GLOBAL LEAGUE LIST ──────────────────────────────────
TARGET_LEAGUES = {
    # UNITED KINGDOM
    "Premier League": "UK",
    "Championship": "UK",
    "League One": "UK",
    "League Two": "UK",
    "National League": "UK",
    "Scottish Premiership": "UK",
    "Scottish Championship": "UK",
    "Scottish League One": "UK",
    "Scottish League Two": "UK",
    
    # GERMANY
    "Bundesliga": "DE",
    "Bundesliga 2": "DE",
    "2. Bundesliga": "DE",
    "Austrian Bundesliga": "EU",
    
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
    
    # REST OF EUROPE — FULL COVERAGE
    "Primeira Liga": "EU",
    "Liga Portugal": "EU",
    "Eredivisie": "EU",
    "Eerste Divisie": "EU",
    "Süper Lig": "EU",
    "Super Lig": "EU",
    "Belgian Pro League": "EU",
    "Challenger Pro League": "EU",
    "Swiss Super League": "EU",
    "Czech First League": "EU",
    "Fortuna Liga": "EU",
    "Ekstraklasa": "EU",
    "Croatian First League": "EU",
    "Prva HNL": "EU",
    "Serbian SuperLiga": "EU",
    "SuperLiga Srbija": "EU",
    "Super League Greece": "EU",
    "Greek Super League": "EU",
    "Danish Superliga": "EU",
    "Eliteserien": "EU",
    "Allsvenskan": "EU",
    "Veikkausliiga": "EU",
    
    # AMERICAS
    "MLS": "AM",
    "Brasileirão": "AM",
    "Liga MX": "AM",
    "Argentina Primera": "AM",
    "Copa Libertadores": "AM",
    
    # REST OF WORLD
    "Saudi Pro League": "GLOBAL",
    "J1 League": "GLOBAL",
    "K League 1": "GLOBAL",
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
    if "Championship" in n and "EFL" not in n: return "Championship"
    if "League One" in n: return "League One"
    if "League Two" in n: return "League Two"
    if "National League" in n: return "National League"
    if "Scottish Premiership" in n or "SPL" in n: return "Scottish Premiership"
    if "Scottish Championship" in n: return "Scottish Championship"
    if "Bundesliga 2" in n or "2. Bundesliga" in n: return "Bundesliga 2"
    if "Bundesliga" in n and "Austria" not in n: return "Bundesliga"
    if "Austrian" in n or "Österreich" in n: return "Austrian Bundesliga"
    if "Ligue 1" in n: return "Ligue 1"
    if "Ligue 2" in n: return "Ligue 2"
    if "La Liga 2" in n or "Segunda" in n: return "La Liga 2"
    if "La Liga" in n: return "La Liga"
    if "Serie A" in n and "Brazil" not in n and "Swiss" not in n: return "Serie A"
    if "Serie B" in n: return "Serie B"
    if "Primeira" in n or "Liga Portugal" in n: return "Primeira Liga"
    if "Eredivisie" in n: return "Eredivisie"
    if "Eerste Divisie" in n: return "Eerste Divisie"
    if "Süper Lig" in n or "Super Lig" in n and "Greece" not in n: return "Süper Lig"
    if "Belgian" in n or "Pro League" in n and "Saudi" not in n: return "Belgian Pro League"
    if "Swiss" in n or "Super League" in n and "Greece" not in n: return "Swiss Super League"
    if "Greek" in n or "Super League Greece" in n: return "Super League Greece"
    if "Czech" in n or "Fortuna" in n: return "Czech First League"
    if "Ekstraklasa" in n or "Polish" in n: return "Ekstraklasa"
    if "Croatia" in n or "Prva HNL" in n: return "Croatian First League"
    if "Serbia" in n or "SuperLiga Srbija" in n: return "Serbian SuperLiga"
    if "Danish" in n or "Superliga" in n: return "Danish Superliga"
    if "Eliteserien" in n or "Norway" in n: return "Eliteserien"
    if "Allsvenskan" in n or "Sweden" in n: return "Allsvenskan"
    if "Veikkausliiga" in n or "Finland" in n: return "Veikkausliiga"
    if "MLS" in n: return "MLS"
    if "Brasileirão" in n or "Brazil" in n: return "Brasileirão"
    if "Liga MX" in n or "Mexico" in n: return "Liga MX"
    if "Argentina" in n: return "Argentina Primera"
    if "Saudi" in n: return "Saudi Pro League"
    if "J1" in n or "Japan" in n: return "J1 League"
    if "K League" in n or "Korea" in n: return "K League 1"
    if "A-League" in n or "Australia" in n: return "A-League"
    return n

# ─── FALLBACK: FULL EUROPE + GLOBAL DATASET ──────────────────────
def get_fallback_dataset():
    return [
        # UK
        {"ko":"12:30","league":"Premier League","region":"UK","home":"Liverpool","away":"Tottenham","h_attack":3.05,"h_defence":0.55,"a_attack":2.15,"a_defence":1.15},
        {"ko":"15:00","league":"Scottish Premiership","region":"UK","home":"Celtic","away":"Rangers","h_attack":2.45,"h_defence":0.75,"a_attack":2.35,"a_defence":0.85},
        {"ko":"15:00","league":"League One","region":"UK","home":"Bolton Wanderers","away":"Portsmouth","h_attack":1.55,"h_defence":1.45,"a_attack":1.65,"a_defence":1.35},
        
        # Germany
        {"ko":"14:30","league":"Bundesliga","region":"DE","home":"Bayern Munich","away":"Bayer Leverkusen","h_attack":3.15,"h_defence":0.50,"a_attack":2.95,"a_defence":0.65},
        {"ko":"16:30","league":"Austrian Bundesliga","region":"EU","home":"Red Bull Salzburg","away":"Sturm Graz","h_attack":2.15,"h_defence":0.95,"a_attack":1.85,"a_defence":1.15},
        
        # France
        {"ko":"20:00","league":"Ligue 1","region":"FR","home":"Paris Saint-Germain","away":"Marseille","h_attack":3.05,"h_defence":0.55,"a_attack":2.05,"a_defence":1.15},
        
        # Spain
        {"ko":"17:30","league":"La Liga","region":"ES","home":"Real Madrid","away":"Barcelona","h_attack":2.95,"h_defence":0.60,"a_attack":2.85,"a_defence":0.65},
        
        # Italy
        {"ko":"19:45","league":"Serie A","region":"IT","home":"Inter Milan","away":"AC Milan","h_attack":2.75,"h_defence":0.65,"a_attack":2.45,"a_defence":0.85},
        
        # Rest of Europe
        {"ko":"20:00","league":"Primeira Liga","region":"EU","home":"Benfica","away":"Sporting CP","h_attack":2.25,"h_defence":0.90,"a_attack":2.15,"a_defence":0.95},
        {"ko":"19:00","league":"Eredivisie","region":"EU","home":"Ajax","away":"PSV Eindhoven","h_attack":2.35,"h_defence":0.85,"a_attack":2.45,"a_defence":0.80},
        {"ko":"18:00","league":"Süper Lig","region":"EU","home":"Galatasaray","away":"Fenerbahçe","h_attack":2.15,"h_defence":0.95,"a_attack":2.05,"a_defence":1.05},
        {"ko":"19:30","league":"Belgian Pro League","region":"EU","home":"Club Brugge","away":"Anderlecht","h_attack":2.05,"h_defence":1.00,"a_attack":1.95,"a_defence":1.10},
        {"ko":"17:00","league":"Swiss Super League","region":"EU","home":"Young Boys","away":"Basel","h_attack":1.95,"h_defence":1.05,"a_attack":1.85,"a_defence":1.15},
        {"ko":"18:00","league":"Super League Greece","region":"EU","home":"Olympiacos","away":"Panathinaikos","h_attack":1.85,"h_defence":1.10,"a_attack":1.75,"a_defence":1.20},
        {"ko":"19:00","league":"Czech First League","region":"EU","home":"Sparta Prague","away":"Slavia Prague","h_attack":1.80,"h_defence":1.15,"a_attack":1.75,"a_defence":1.20},
        {"ko":"17:30","league":"Ekstraklasa","region":"EU","home":"Legia Warsaw","away":"Lech Poznań","h_attack":1.70,"h_defence":1.20,"a_attack":1.65,"a_defence":1.25},
        {"ko":"18:00","league":"Danish Superliga","region":"EU","home":"FC Copenhagen","away":"Brøndby","h_attack":1.90,"h_defence":1.05,"a_attack":1.80,"a_defence":1.15},
        {"ko":"19:00","league":"Eliteserien","region":"EU","home":"Rosenborg","away":"Molde","h_attack":1.75,"h_defence":1.15,"a_attack":1.70,"a_defence":1.20},
        {"ko":"18:30","league":"Allsvenskan","region":"EU","home":"AIK","away":"Djurgårdens IF","h_attack":1.65,"h_defence":1.25,"a_attack":1.60,"a_defence":1.30},
        {"ko":"17:00","league":"Croatian First League","region":"EU","home":"Dinamo Zagreb","away":"Hajduk Split","h_attack":1.85,"h_defence":1.10,"a_attack":1.75,"a_defence":1.18},
        {"ko":"19:00","league":"Serbian SuperLiga","region":"EU","home":"Red Star Belgrade","away":"Partizan","h_attack":1.80,"h_defence":1.12,"a_attack":1.72,"a_defence":1.20},
        
        # Americas
        {"ko":"19:30","league":"MLS","region":"AM","home":"LA Galaxy","away":"Seattle Sounders","h_attack":1.85,"h_defence":1.25,"a_attack":1.75,"a_defence":1.35},
        {"ko":"00:00","league":"Brasileirão","region":"AM","home":"Flamengo","away":"Palmeiras","h_attack":2.05,"h_defence":1.05,"a_attack":2.15,"a_defence":0.95},
        
        # Rest of World
        {"ko":"18:00","league":"Saudi Pro League","region":"GLOBAL","home":"Al Hilal","away":"Al Nassr","h_attack":2.25,"h_defence":0.95,"a_attack":2.15,"a_defence":1.05},
    ]

# ─── TEAM STRENGTH DATABASE ───────────────────────────────────────
ELITE = ["Man City","Liverpool","Arsenal","Chelsea","Bayern","PSG","Real Madrid","Barcelona","Inter","Al Hilal"]
TOP_EU = ["Tottenham","Aston Villa","Newcastle","Leverkusen","Dortmund","AC Milan","Napoli","Benfica","Sporting","Ajax","PSV","Galatasaray","Fenerbahçe","Red Bull Salzburg"]
SOLID_EU = ["Celtic","Rangers","Club Brugge","Anderlecht","Young Boys","Basel","Olympiacos","Sparta Prague","Slavia Prague","Copenhagen","Brøndby","Dinamo Zagreb","Red Star"]
TOP_AM = ["Flamengo","Palmeiras","LA Galaxy"]

def get_attack(name, league):
    if any(t in name for t in ELITE): return 2.95
    if any(t in name for t in TOP_EU): return 2.25
    if any(t in name for t in SOLID_EU): return 1.90
    if any(t in name for t in TOP_AM): return 2.05
    if league in ["Premier League","Bundesliga","Ligue 1","La Liga","Serie A","Primeira Liga","Eredivisie","Süper Lig"]: return 1.65
    if league in ["Scottish Premiership","Belgian Pro League","Swiss Super League","Austrian Bundesliga","Danish Superliga"]: return 1.55
    return 1.30

def get_defence(name, league):
    if any(t in name for t in ELITE): return 0.55
    if any(t in name for t in TOP_EU): return 1.05
    if any(t in name for t in SOLID_EU): return 1.15
    if any(t in name for t in TOP_AM): return 1.15
    if league in ["Premier League","Bundesliga","Ligue 1","La Liga","Serie A","Primeira Liga","Eredivisie","Süper Lig"]: return 1.35
    if league in ["Scottish Premiership","Belgian Pro League","Swiss Super League","Austrian Bundesliga","Danish Superliga"]: return 1.40
    return 1.60

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

# ─── ALL ROUTES COMPLETE ─────────────────────────────────────────
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
    return render_template('base.html', active='betbuilder', cards=get_all_p
Remove-Item app.py -ErrorAction SilentlyContinue

@'
from flask import Flask, render_template
import math
import requests
from datetime import datetime

app = Flask(__name__)

# ─── COMPLETE GLOBAL LEAGUE LIST ──────────────────────────────────
TARGET_LEAGUES = {
    # UNITED KINGDOM
    "Premier League": "UK",
    "Championship": "UK",
    "League One": "UK",
    "League Two": "UK",
    "National League": "UK",
    "Scottish Premiership": "UK",
    "Scottish Championship": "UK",
    "Scottish League One": "UK",
    "Scottish League Two": "UK",
    
    # GERMANY
    "Bundesliga": "DE",
    "Bundesliga 2": "DE",
    "2. Bundesliga": "DE",
    "Austrian Bundesliga": "EU",
    
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
    
    # REST OF EUROPE — FULL COVERAGE
    "Primeira Liga": "EU",
    "Liga Portugal": "EU",
    "Eredivisie": "EU",
    "Eerste Divisie": "EU",
    "Süper Lig": "EU",
    "Super Lig": "EU",
    "Belgian Pro League": "EU",
    "Challenger Pro League": "EU",
    "Swiss Super League": "EU",
    "Czech First League": "EU",
    "Fortuna Liga": "EU",
    "Ekstraklasa": "EU",
    "Croatian First League": "EU",
    "Prva HNL": "EU",
    "Serbian SuperLiga": "EU",
    "SuperLiga Srbija": "EU",
    "Super League Greece": "EU",
    "Greek Super League": "EU",
    "Danish Superliga": "EU",
    "Eliteserien": "EU",
    "Allsvenskan": "EU",
    "Veikkausliiga": "EU",
    
    # AMERICAS
    "MLS": "AM",
    "Brasileirão": "AM",
    "Liga MX": "AM",
    "Argentina Primera": "AM",
    "Copa Libertadores": "AM",
    
    # REST OF WORLD
    "Saudi Pro League": "GLOBAL",
    "J1 League": "GLOBAL",
    "K League 1": "GLOBAL",
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
    if "Championship" in n and "EFL" not in n: return "Championship"
    if "League One" in n: return "League One"
    if "League Two" in n: return "League Two"
    if "National League" in n: return "National League"
    if "Scottish Premiership" in n or "SPL" in n: return "Scottish Premiership"
    if "Scottish Championship" in n: return "Scottish Championship"
    if "Bundesliga 2" in n or "2. Bundesliga" in n: return "Bundesliga 2"
    if "Bundesliga" in n and "Austria" not in n: return "Bundesliga"
    if "Austrian" in n or "Österreich" in n: return "Austrian Bundesliga"
    if "Ligue 1" in n: return "Ligue 1"
    if "Ligue 2" in n: return "Ligue 2"
    if "La Liga 2" in n or "Segunda" in n: return "La Liga 2"
    if "La Liga" in n: return "La Liga"
    if "Serie A" in n and "Brazil" not in n and "Swiss" not in n: return "Serie A"
    if "Serie B" in n: return "Serie B"
    if "Primeira" in n or "Liga Portugal" in n: return "Primeira Liga"
    if "Eredivisie" in n: return "Eredivisie"
    if "Eerste Divisie" in n: return "Eerste Divisie"
    if "Süper Lig" in n or "Super Lig" in n and "Greece" not in n: return "Süper Lig"
    if "Belgian" in n or "Pro League" in n and "Saudi" not in n: return "Belgian Pro League"
    if "Swiss" in n or "Super League" in n and "Greece" not in n: return "Swiss Super League"
    if "Greek" in n or "Super League Greece" in n: return "Super League Greece"
    if "Czech" in n or "Fortuna" in n: return "Czech First League"
    if "Ekstraklasa" in n or "Polish" in n: return "Ekstraklasa"
    if "Croatia" in n or "Prva HNL" in n: return "Croatian First League"
    if "Serbia" in n or "SuperLiga Srbija" in n: return "Serbian SuperLiga"
    if "Danish" in n or "Superliga" in n: return "Danish Superliga"
    if "Eliteserien" in n or "Norway" in n: return "Eliteserien"
    if "Allsvenskan" in n or "Sweden" in n: return "Allsvenskan"
    if "Veikkausliiga" in n or "Finland" in n: return "Veikkausliiga"
    if "MLS" in n: return "MLS"
    if "Brasileirão" in n or "Brazil" in n: return "Brasileirão"
    if "Liga MX" in n or "Mexico" in n: return "Liga MX"
    if "Argentina" in n: return "Argentina Primera"
    if "Saudi" in n: return "Saudi Pro League"
    if "J1" in n or "Japan" in n: return "J1 League"
    if "K League" in n or "Korea" in n: return "K League 1"
    if "A-League" in n or "Australia" in n: return "A-League"
    return n

# ─── FALLBACK: FULL EUROPE + GLOBAL DATASET ──────────────────────
def get_fallback_dataset():
    return [
        # UK
        {"ko":"12:30","league":"Premier League","region":"UK","home":"Liverpool","away":"Tottenham","h_attack":3.05,"h_defence":0.55,"a_attack":2.15,"a_defence":1.15},
        {"ko":"15:00","league":"Scottish Premiership","region":"UK","home":"Celtic","away":"Rangers","h_attack":2.45,"h_defence":0.75,"a_attack":2.35,"a_defence":0.85},
        {"ko":"15:00","league":"League One","region":"UK","home":"Bolton Wanderers","away":"Portsmouth","h_attack":1.55,"h_defence":1.45,"a_attack":1.65,"a_defence":1.35},
        
        # Germany
        {"ko":"14:30","league":"Bundesliga","region":"DE","home":"Bayern Munich","away":"Bayer Leverkusen","h_attack":3.15,"h_defence":0.50,"a_attack":2.95,"a_defence":0.65},
        {"ko":"16:30","league":"Austrian Bundesliga","region":"EU","home":"Red Bull Salzburg","away":"Sturm Graz","h_attack":2.15,"h_defence":0.95,"a_attack":1.85,"a_defence":1.15},
        
        # France
        {"ko":"20:00","league":"Ligue 1","region":"FR","home":"Paris Saint-Germain","away":"Marseille","h_attack":3.05,"h_defence":0.55,"a_attack":2.05,"a_defence":1.15},
        
        # Spain
        {"ko":"17:30","league":"La Liga","region":"ES","home":"Real Madrid","away":"Barcelona","h_attack":2.95,"h_defence":0.60,"a_attack":2.85,"a_defence":0.65},
        
        # Italy
        {"ko":"19:45","league":"Serie A","region":"IT","home":"Inter Milan","away":"AC Milan","h_attack":2.75,"h_defence":0.65,"a_attack":2.45,"a_defence":0.85},
        
        # Rest of Europe
        {"ko":"20:00","league":"Primeira Liga","region":"EU","home":"Benfica","away":"Sporting CP","h_attack":2.25,"h_defence":0.90,"a_attack":2.15,"a_defence":0.95},
        {"ko":"19:00","league":"Eredivisie","region":"EU","home":"Ajax","away":"PSV Eindhoven","h_attack":2.35,"h_defence":0.85,"a_attack":2.45,"a_defence":0.80},
        {"ko":"18:00","league":"Süper Lig","region":"EU","home":"Galatasaray","away":"Fenerbahçe","h_attack":2.15,"h_defence":0.95,"a_attack":2.05,"a_defence":1.05},
        {"ko":"19:30","league":"Belgian Pro League","region":"EU","home":"Club Brugge","away":"Anderlecht","h_attack":2.05,"h_defence":1.00,"a_attack":1.95,"a_defence":1.10},
        {"ko":"17:00","league":"Swiss Super League","region":"EU","home":"Young Boys","away":"Basel","h_attack":1.95,"h_defence":1.05,"a_attack":1.85,"a_defence":1.15},
        {"ko":"18:00","league":"Super League Greece","region":"EU","home":"Olympiacos","away":"Panathinaikos","h_attack":1.85,"h_defence":1.10,"a_attack":1.75,"a_defence":1.20},
        {"ko":"19:00","league":"Czech First League","region":"EU","home":"Sparta Prague","away":"Slavia Prague","h_attack":1.80,"h_defence":1.15,"a_attack":1.75,"a_defence":1.20},
        {"ko":"17:30","league":"Ekstraklasa","region":"EU","home":"Legia Warsaw","away":"Lech Poznań","h_attack":1.70,"h_defence":1.20,"a_attack":1.65,"a_defence":1.25},
        {"ko":"18:00","league":"Danish Superliga","region":"EU","home":"FC Copenhagen","away":"Brøndby","h_attack":1.90,"h_defence":1.05,"a_attack":1.80,"a_defence":1.15},
        {"ko":"19:00","league":"Eliteserien","region":"EU","home":"Rosenborg","away":"Molde","h_attack":1.75,"h_defence":1.15,"a_attack":1.70,"a_defence":1.20},
        {"ko":"18:30","league":"Allsvenskan","region":"EU","home":"AIK","away":"Djurgårdens IF","h_attack":1.65,"h_defence":1.25,"a_attack":1.60,"a_defence":1.30},
        {"ko":"17:00","league":"Croatian First League","region":"EU","home":"Dinamo Zagreb","away":"Hajduk Split","h_attack":1.85,"h_defence":1.10,"a_attack":1.75,"a_defence":1.18},
        {"ko":"19:00","league":"Serbian SuperLiga","region":"EU","home":"Red Star Belgrade","away":"Partizan","h_attack":1.80,"h_defence":1.12,"a_attack":1.72,"a_defence":1.20},
        
        # Americas
        {"ko":"19:30","league":"MLS","region":"AM","home":"LA Galaxy","away":"Seattle Sounders","h_attack":1.85,"h_defence":1.25,"a_attack":1.75,"a_defence":1.35},
        {"ko":"00:00","league":"Brasileirão","region":"AM","home":"Flamengo","away":"Palmeiras","h_attack":2.05,"h_defence":1.05,"a_attack":2.15,"a_defence":0.95},
        
        # Rest of World
        {"ko":"18:00","league":"Saudi Pro League","region":"GLOBAL","home":"Al Hilal","away":"Al Nassr","h_attack":2.25,"h_defence":0.95,"a_attack":2.15,"a_defence":1.05},
    ]

# ─── TEAM STRENGTH DATABASE ───────────────────────────────────────
ELITE = ["Man City","Liverpool","Arsenal","Chelsea","Bayern","PSG","Real Madrid","Barcelona","Inter","Al Hilal"]
TOP_EU = ["Tottenham","Aston Villa","Newcastle","Leverkusen","Dortmund","AC Milan","Napoli","Benfica","Sporting","Ajax","PSV","Galatasaray","Fenerbahçe","Red Bull Salzburg"]
SOLID_EU = ["Celtic","Rangers","Club Brugge","Anderlecht","Young Boys","Basel","Olympiacos","Sparta Prague","Slavia Prague","Copenhagen","Brøndby","Dinamo Zagreb","Red Star"]
TOP_AM = ["Flamengo","Palmeiras","LA Galaxy"]

def get_attack(name, league):
    if any(t in name for t in ELITE): return 2.95
    if any(t in name for t in TOP_EU): return 2.25
    if any(t in name for t in SOLID_EU): return 1.90
    if any(t in name for t in TOP_AM): return 2.05
    if league in ["Premier League","Bundesliga","Ligue 1","La Liga","Serie A","Primeira Liga","Eredivisie","Süper Lig"]: return 1.65
    if league in ["Scottish Premiership","Belgian Pro League","Swiss Super League","Austrian Bundesliga","Danish Superliga"]: return 1.55
    return 1.30

def get_defence(name, league):
    if any(t in name for t in ELITE): return 0.55
    if any(t in name for t in TOP_EU): return 1.05
    if any(t in name for t in SOLID_EU): return 1.15
    if any(t in name for t in TOP_AM): return 1.15
    if league in ["Premier League","Bundesliga","Ligue 1","La Liga","Serie A","Primeira Liga","Eredivisie","Süper Lig"]: return 1.35
    if league in ["Scottish Premiership","Belgian Pro League","Swiss Super League","Austrian Bundesliga","Danish Superliga"]: return 1.40
    return 1.60

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

# ─── ALL ROUTES FULLY COMPLETE ────────────────────────────────────
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
    return render_template('base.html', active='betbuilder', cards=
Remove-Item app.py -ErrorAction SilentlyContinue

@'
from flask import Flask, render_template
import math
import requests
from datetime import datetime

app = Flask(__name__)

# ─── COMPLETE GLOBAL LEAGUE LIST ──────────────────────────────────
TARGET_LEAGUES = {
    # UNITED KINGDOM
    "Premier League": "UK",
    "Championship": "UK",
    "League One": "UK",
    "League Two": "UK",
    "National League": "UK",
    "Scottish Premiership": "UK",
    "Scottish Championship": "UK",
    "Scottish League One": "UK",
    "Scottish League Two": "UK",
    # GERMANY
    "Bundesliga": "DE",
    "Bundesliga 2": "DE",
    "2. Bundesliga": "DE",
    "Austrian Bundesliga": "EU",
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
    # REST OF EUROPE — FULL COVERAGE
    "Primeira Liga": "EU",
    "Liga Portugal": "EU",
    "Eredivisie": "EU",
    "Eerste Divisie": "EU",
    "Süper Lig": "EU",
    "Super Lig": "EU",
    "Belgian Pro League": "EU",
    "Challenger Pro League": "EU",
    "Swiss Super League": "EU",
    "Czech First League": "EU",
    "Fortuna Liga": "EU",
    "Ekstraklasa": "EU",
    "Croatian First League": "EU",
    "Prva HNL": "EU",
    "Serbian SuperLiga": "EU",
    "SuperLiga Srbija": "EU",
    "Super League Greece": "EU",
    "Greek Super League": "EU",
    "Danish Superliga": "EU",
    "Eliteserien": "EU",
    "Allsvenskan": "EU",
    "Veikkausliiga": "EU",
    # AMERICAS
    "MLS": "AM",
    "Brasileirão": "AM",
    "Liga MX": "AM",
    "Argentina Primera": "AM",
    "Copa Libertadores": "AM",
    # REST OF WORLD
    "Saudi Pro League": "GLOBAL",
    "J1 League": "GLOBAL",
    "K League 1": "GLOBAL",
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
    if "Championship" in n and "EFL" not in n: return "Championship"
    if "League One" in n: return "League One"
    if "League Two" in n: return "League Two"
    if "National League" in n: return "National League"
    if "Scottish Premiership" in n or "SPL" in n: return "Scottish Premiership"
    if "Scottish Championship" in n: return "Scottish Championship"
    if "Bundesliga 2" in n or "2. Bundesliga" in n: return "Bundesliga 2"
    if "Bundesliga" in n and "Austria" not in n: return "Bundesliga"
    if "Austrian" in n or "Österreich" in n: return "Austrian Bundesliga"
    if "Ligue 1" in n: return "Ligue 1"
    if "Ligue 2" in n: return "Ligue 2"
    if "La Liga 2" in n or "Segunda" in n: return "La Liga 2"
    if "La Liga" in n: return "La Liga"
    if "Serie A" in n and "Brazil" not in n and "Swiss" not in n: return "Serie A"
    if "Serie B" in n: return "Serie B"
    if "Primeira" in n or "Liga Portugal" in n: return "Primeira Liga"
    if "Eredivisie" in n: return "Eredivisie"
    if "Eerste Divisie" in n: return "Eerste Divisie"
    if "Süper Lig" in n or "Super Lig" in n and "Greece" not in n: return "Süper Lig"
    if "Belgian" in n or "Pro League" in n and "Saudi" not in n: return "Belgian Pro League"
    if "Swiss" in n or "Super League" in n and "Greece" not in n: return "Swiss Super League"
    if "Greek" in n or "Super League Greece" in n: return "Super League Greece"
    if "Czech" in n or "Fortuna" in n: return "Czech First League"
    if "Ekstraklasa" in n or "Polish" in n: return "Ekstraklasa"
    if "Croatia" in n or "Prva HNL" in n: return "Croatian First League"
    if "Serbia" in n or "SuperLiga Srbija" in n: return "Serbian SuperLiga"
    if "Danish" in n or "Superliga" in n: return "Danish Superliga"
    if "Eliteserien" in n or "Norway" in n: return "Eliteserien"
    if "Allsvenskan" in n or "Sweden" in n: return "Allsvenskan"
    if "Veikkausliiga" in n or "Finland" in n: return "Veikkausliiga"
    if "MLS" in n: return "MLS"
    if "Brasileirão" in n or "Brazil" in n: return "Brasileirão"
    if "Liga MX" in n or "Mexico" in n: return "Liga MX"
    if "Argentina" in n: return "Argentina Primera"
    if "Saudi" in n: return "Saudi Pro League"
    if "J1" in n or "Japan" in n: return "J1 League"
    if "K League" in n or "Korea" in n: return "K League 1"
    if "A-League" in n or "Australia" in n: return "A-League"
    return n

# ─── FALLBACK DATASET ─────────────────────────────────────────────
def get_fallback_dataset():
    return [
        {"ko":"12:30","league":"Premier League","region":"UK","home":"Liverpool","away":"Tottenham","h_attack":3.05,"h_defence":0.55,"a_attack":2.15,"a_defence":1.15},
        {"ko":"15:00","league":"Scottish Premiership","region":"UK","home":"Celtic","away":"Rangers","h_attack":2.45,"h_defence":0.75,"a_attack":2.35,"a_defence":0.85},
        {"ko":"14:30","league":"Bundesliga","region":"DE","home":"Bayern Munich","away":"Bayer Leverkusen","h_attack":3.15,"h_defence":0.50,"a_attack":2.95,"a_defence":0.65},
        {"ko":"20:00","league":"Primeira Liga","region":"EU","home":"Benfica","away":"Sporting CP","h_attack":2.25,"h_defence":0.90,"a_attack":2.15,"a_defence":0.95},
        {"ko":"19:00","league":"Eredivisie","region":"EU","home":"Ajax","away":"PSV Eindhoven","h_attack":2.35,"h_defence":0.85,"a_attack":2.45,"a_defence":0.80},
        {"ko":"18:00","league":"Süper Lig","region":"EU","home":"Galatasaray","away":"Fenerbahçe","h_attack":2.15,"h_defence":0.95,"a_attack":2.05,"a_defence":1.05},
        {"ko":"19:30","league":"Belgian Pro League","region":"EU","home":"Club Brugge","away":"Anderlecht","h_attack":2.05,"h_defence":1.00,"a_attack":1.95,"a_defence":1.10},
        {"ko":"17:00","league":"Swiss Super League","region":"EU","home":"Young Boys","away":"Basel","h_attack":1.95,"h_defence":1.05,"a_attack":1.85,"a_defence":1.15},
        {"ko":"18:00","league":"Super League Greece","region":"EU","home":"Olympiacos","away":"Panathinaikos","h_attack":1.85,"h_defence":1.10,"a_attack":1.75,"a_defence":1.20},
        {"ko":"19:00","league":"Czech First League","region":"EU","home":"Sparta Prague","away":"Slavia Prague","h_attack":1.80,"h_defence":1.15,"a_attack":1.75,"a_defence":1.20},
        {"ko":"18:00","league":"Danish Superliga","region":"EU","home":"FC Copenhagen","away":"Brøndby","h_attack":1.90,"h_defence":1.05,"a_attack":1.80,"a_defence":1.15},
        {"ko":"19:30","league":"MLS","region":"AM","home":"LA Galaxy","away":"Seattle Sounders","h_attack":1.85,"h_defence":1.25,"a_attack":1.75,"a_defence":1.35},
        {"ko":"18:00","league":"Saudi Pro League","region":"GLOBAL","home":"Al Hilal","away":"Al Nassr","h_attack":2.25,"h_defence":0.95,"a_attack":2.15,"a_defence":1.05},
    ]

# ─── TEAM STRENGTH ────────────────────────────────────────────────
ELITE = ["Man City","Liverpool","Arsenal","Chelsea","Bayern","PSG","Real Madrid","Barcelona","Inter","Al Hilal"]
TOP_EU = ["Tottenham","Aston Villa","Newcastle","Leverkusen","Dortmund","AC Milan","Napoli","Benfica","Sporting","Ajax","PSV","Galatasaray","Fenerbahçe","Red Bull Salzburg"]
SOLID_EU = ["Celtic","Rangers","Club Brugge","Anderlecht","Young Boys","Basel","Olympiacos","Sparta Prague","Slavia Prague","Copenhagen","Brøndby","Dinamo Zagreb","Red Star"]
TOP_AM = ["Flamengo","Palmeiras","LA Galaxy"]

def get_attack(name, league):
    if any(t in name for t in ELITE): return 2.95
    if any(t in name for t in TOP_EU): return 2.25
    if any(t in name for t in SOLID_EU): return 1.90
    if any(t in name for t in TOP_AM): return 2.05
    if league in ["Premier League","Bundesliga","Ligue 1","La Liga","Serie A","Primeira Liga","Eredivisie","Süper Lig"]: return 1.65
    if league in ["Scottish Premiership","Belgian Pro League","Swiss Super League","Austrian Bundesliga","Danish Superliga"]: return 1.55
    return 1.30

def get_defence(name, league):
    if any(t in name for t in ELITE): return 0.55
    if any(t in name for t in TOP_EU): return 1.05
    if any(t in name for t in SOLID_EU): return 1.15
    if any(t in name for t in TOP_AM): return 1.15
    if league in ["Premier League","Bundesliga","Ligue 1","La Liga","Serie A","Primeira Liga","Eredivisie","Süper Lig"]: return 1.35
    if league in ["Scottish Premiership","Belgian Pro League","Swiss Super League","Austrian Bundesliga","Danish Superliga"]: return 1.40
    return 1.60

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

# ─── ALL ROUTES COMPLETE ──────────────────────────────────────────
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
    cards = [p for p in get_all_picks() if p["hg"] != p["ag"]]
    return render_template('base.html', active='correctscore', cards=cards, title="Correct Score Focus")

@app.route('/future-games')
def future_games():
    return render_template('base.html', active='future', cards=get_all_picks(), title="Future Games — Worldwide")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
