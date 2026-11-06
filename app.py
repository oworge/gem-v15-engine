from flask import Flask, request
from datetime import datetime
import requests

import requests

API_KEY = "b0d3f3a531msh968e8e49e41e1dp1c4e8b0jsn1d5c89f38c86"
API_HOST = "api-football-v1.p.rapidapi.com"

def fetch_live_fixtures():
    """Fetch today's fixtures from free API"""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST
    }
    params = {"date": today, "timezone": "UTC"}
    
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        if resp.status_code != 200:
            raise Exception(f"API returned {resp.status_code}")
        
        data = resp.json()
        matches = []
        
        for item in data.get("response", []):
            home = item["teams"]["home"]["name"]
            away = item["teams"]["away"]["name"]
            league = item["league"]["name"]
            kickoff = item["fixture"]["date"]
            time_only = kickoff.split("T")[1][:5] + " GMT"
            
            matches.append({
                "home": home,
                "away": away,
                "league": league,
                "time": time_only,
                "is_banker": False,
                "markets": [
                    {"name": home + " Win", "odds": 2.00, "prob": 0.53},
                    {"name": "Over 2.5 Goals", "odds": 1.75, "prob": 0.60},
                    {"name": "BTTS - Yes", "odds": 1.80, "prob": 0.58}
                ]
            })
        
        # Mark top matches as bankers
        if matches:
            for i in range(min(3, len(matches))):
                matches[i]["is_banker"] = True
                matches[i]["markets"][0]["prob"] = 0.75
                matches[i]["markets"][0]["odds"] = 1.38
        
        return {today: matches}
    
    except Exception as e:
        print(f"API fetch failed: {e}")
        # Fallback fixtures if API down
        return {
            today: [
                {
                    "home": "Everton",
                    "away": "Coventry City",
                    "league": "Premier League",
                    "time": "19:45 GMT",
                    "is_banker": True,
                    "markets": [
                        {"name": "Everton Win", "odds": 1.70, "prob": 0.65},
                        {"name": "Over 2.5 Goals", "odds": 1.75, "prob": 0.60},
                        {"name": "BTTS - Yes", "odds": 1.82, "prob": 0.58}
                    ]
                }
            ]
        }

FIXTURES = fetch_live_fixtures()
todays_matches = FIXTURES.get(datetime.utcnow().strftime("%Y-%m-%d"), [])
