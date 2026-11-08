# -*- coding: utf-8 -*-
from datetime import datetime
import os, requests
from models import calculate_universal_market_prediction, calculate_fractional_kelly

def populate_match_metrics(match_list, bankroll=1000.0):
    processed = []
    for f in match_list:
        h_lam, a_lam, cs, ev_calc, btts_pct, true_prob, cs_odds = calculate_universal_market_prediction(
            f["stats"][0], f["stats"][1], f["stats"][2], f["stats"][3], f["market"], f["odds"]
        )
        kelly_stake = calculate_fractional_kelly(f["odds"], true_prob, fraction=0.25)
        f["correct_score"] = cs
        f["cs_odds"] = cs_odds
        f["btts_prob"] = f"{btts_pct}%"
        f["btts_market"] = "BTTS - Yes" if btts_pct >= 52.0 else "BTTS - No"
        f["ev"] = f"+{ev_calc}%" if ev_calc > 0 else f"{ev_calc}%"
        f["kelly_pct"] = f"{kelly_stake}%"
        f["suggested_stake_gbp"] = f"£{round((bankroll * (kelly_stake / 100)), 2)}"
        processed.append(f)
    return processed

def fetch_live_global_fixtures(bankroll=1000.0, api_key="", api_url=""):
    headers = {"X-Auth-Token": api_key}
    dt_label = datetime.utcnow().strftime("%a, %b %d, %Y")
    raw = []
    try:
        res = requests.get(api_url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if "matches" in data and len(data["matches"]) > 0:
                for item in data["matches"]:
                    raw.append({
                        "id": item["id"],
                        "home": item["homeTeam"]["name"],
                        "away": item["awayTeam"]["name"],
                        "league": item["competition"]["name"],
                        "date": dt_label,
                        "time": datetime.fromisoformat(item["utcDate"].replace("Z", "+00:00")).strftime("%H:%M GMT"),
                        "stats": [1.40, 0.95, 1.30, 0.90],
                        "market": "Over 1.5 Goals",
                        "odds": 1.45,
                        "builder": ["Over 1.5 Goals", f"{item['homeTeam']['name']} Double Chance"]
                    })
                return populate_match_metrics(raw, bankroll)
    except Exception as e:
        print(f"API Fetch Error: {e}")

    fallback = [
        {"id": 601, "home": "Brighton & Hove Albion", "away": "Brentford", "league": "Premier League", "date": dt_label, "time": "14:00 GMT", "stats": [1.45, 1.00, 1.35, 1.05], "market": "Over 1.5 Goals", "odds": 1.35},
        {"id": 602, "home": "Crystal Palace", "away": "Liverpool", "league": "Premier League", "date": dt_label, "time": "14:00 GMT", "stats": [1.10, 0.95, 1.60, 0.80], "market": "Over 2.5 Goals", "odds": 1.75},
        {"id": 603, "home": "Ipswich Town", "away": "AFC Bournemouth", "league": "Premier League", "date": dt_label, "time": "14:00 GMT", "stats": [1.20, 1.10, 1.40, 0.95], "market": "Over 2.5 Goals", "odds": 1.80},
        {"id": 604, "home": "Sunderland", "away": "Chelsea", "league": "Premier League", "date": dt_label, "time": "14:00 GMT", "stats": [1.15, 1.15, 1.55, 0.85], "market": "Away Win", "odds": 1.95},
        {"id": 605, "home": "Manchester United", "away": "Aston Villa", "league": "Premier League", "date": dt_label, "time": "16:30 GMT", "stats": [1.35, 0.90, 1.25, 0.95], "market": "BTTS - Yes", "odds": 1.62},
        {"id": 606, "home": "Elche", "away": "Real Betis", "league": "La Liga", "date": dt_label, "time": "13:00 GMT", "stats": [1.15, 1.05, 1.30, 0.95], "market": "Under 2.5 Goals", "odds": 1.65},
        {"id": 607, "home": "Real Sociedad", "away": "Rayo Vallecano", "league": "La Liga", "date": dt_label, "time": "15:15 GMT", "stats": [1.45, 0.80, 1.05, 1.05], "market": "Home Win", "odds": 1.75},
        {"id": 608, "home": "Villarreal", "away": "Getafe", "league": "La Liga", "date": dt_label, "time": "17:30 GMT", "stats": [1.50, 0.85, 1.10, 1.00], "market": "Home Win", "odds": 1.45},
        {"id": 609, "home": "Celta Vigo", "away": "Levante", "league": "La Liga", "date": dt_label, "time": "17:30 GMT", "stats": [1.40, 0.90, 1.15, 1.05], "market": "Home Win", "odds": 1.80},
        {"id": 610, "home": "Atlético Madrid", "away": "Barcelona", "league": "La Liga", "date": dt_label, "time": "20:00 GMT", "stats": [1.20, 0.80, 1.45, 0.85], "market": "Double Chance", "odds": 1.42},
        {"id": 611, "home": "Napoli", "away": "Lazio", "league": "Serie A", "date": dt_label, "time": "11:30 GMT", "stats": [1.40, 0.90, 1.25, 0.95], "market": "Home Win", "odds": 2.10},
        {"id": 612, "home": "Genoa", "away": "AC Milan", "league": "Serie A", "date": dt_label, "time": "14:00 GMT", "stats": [1.10, 1.05, 1.45, 0.85], "market": "Away Win", "odds": 1.85},
        {"id": 613, "home": "Monza", "away": "Atalanta", "league": "Serie A", "date": dt_label, "time": "14:00 GMT", "stats": [1.05, 1.20, 1.50, 0.90], "market": "Away Win", "odds": 1.75},
        {"id": 614, "home": "Inter Milan", "away": "Como 1907", "league": "Serie A", "date": dt_label, "time": "17:00 GMT", "stats": [1.70, 0.80, 1.05, 1.10], "market": "Home Win", "odds": 1.38},
        {"id": 615, "home": "Fiorentina", "away": "Juventus", "league": "Serie A", "date": dt_label, "time": "19:45 GMT", "stats": [1.10, 0.95, 1.20, 0.80], "market": "Under 2.5 Goals", "odds": 1.62},
        {"id": 616, "home": "Köln", "away": "Bayer Leverkusen", "league": "Bundesliga", "date": dt_label, "time": "14:30 GMT", "stats": [1.15, 1.10, 1.65, 0.90], "market": "Away Win", "odds": 1.85},
        {"id": 617, "home": "Freiburg", "away": "Union Berlin", "league": "Bundesliga", "date": dt_label, "time": "16:30 GMT", "stats": [1.30, 0.95, 1.10, 1.05], "market": "Home Win", "odds": 2.00},
        {"id": 618, "home": "Lens", "away": "Marseille", "league": "Ligue 1", "date": dt_label, "time": "19:45 GMT", "stats": [1.30, 0.90, 1.35, 0.90], "market": "BTTS - Yes", "odds": 1.80},
        {"id": 619, "home": "FC Twente", "away": "Ajax", "league": "Eredivisie", "date": dt_label, "time": "13:30 GMT", "stats": [1.40, 1.00, 1.30, 0.95], "market": "Over 2.5 Goals", "odds": 1.65},
        {"id": 620, "home": "Vitória de Guimarães", "away": "FC Porto", "league": "Primeira Liga", "date": dt_label, "time": "18:00 GMT", "stats": [1.05, 1.10, 1.55, 0.85], "market": "Away Win", "odds": 1.50},
        {"id": 621, "home": "Club Brugge", "away": "Anderlecht", "league": "Belgian Pro League", "date": dt_label, "time": "12:30 GMT", "stats": [1.50, 0.90, 1.10, 1.05], "market": "Home Win", "odds": 1.45}
    ]
    return populate_match_metrics(fallback, bankroll)
