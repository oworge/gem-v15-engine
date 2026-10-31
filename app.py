from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import os, math

app = FastAPI(title="GEM V15.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FIXTURES = [
    {
        "date": "31 Oct 12:30",
        "league": "Premier League",
        "match": "Chelsea vs Man Utd",
        "prediction": "Chelsea Win & Over 1.5 Goals",
        "correct_score": "2 - 1",
        "odds": "1.91",
        "ev_edge": "+6.4%",
        "banker": True,
        "home_xg": 1.68,
        "away_xg": 1.05,
        "over_2_5_pct": 72.5,
        "btts_pct": 58.2,
        "pick": "Chelsea Win",
        "pick_odds": 1.72,
        "builder_picks": [
            {"pick": "Chelsea Win or Draw (1X)", "odds": "1.28"},
            {"pick": "Over 1.5 Goals", "odds": "1.32"},
            {"pick": "Both Teams to Score", "odds": "1.72"},
            {"pick": "Over 4.5 Chelsea Corners", "odds": "1.50"}
        ]
    },
    {
        "date": "31 Oct 15:00",
        "league": "Premier League",
        "match": "Man City vs Brighton",
        "prediction": "Man City Win & Over 2.5 Goals",
        "correct_score": "3 - 0",
        "odds": "1.55",
        "ev_edge": "+7.1%",
        "banker": True,
        "home_xg": 2.35,
        "away_xg": 0.82,
        "over_2_5_pct": 81.3,
        "btts_pct": 52.0,
        "pick": "Man City Win",
        "pick_odds": 1.40,
        "builder_picks": [
            {"pick": "Man City Win or Draw (1X)", "odds": "1.12"},
            {"pick": "Over 2.5 Goals", "odds": "1.45"},
            {"pick": "Man City Over 1.5 Goals", "odds": "1.60"},
            {"pick": "Over 9.5 Total Corners", "odds": "1.55"}
        ]
    },
    {
        "date": "31 Oct 17:30",
        "league": "Bundesliga",
        "match": "Bayern vs Dortmund",
        "prediction": "Both Teams To Score & Over 2.5",
        "correct_score": "2 - 2",
        "odds": "1.85",
        "ev_edge": "+6.9%",
        "banker": False,
        "home_xg": 2.10,
        "away_xg": 1.85,
        "over_2_5_pct": 85.0,
        "btts_pct": 78.5,
        "pick": "BTTS & O2.5",
        "pick_odds": 1.95,
        "builder_picks": [
            {"pick": "Both Teams To Score", "odds": "1.62"},
            {"pick": "Over 2.5 Goals", "odds": "1.48"},
            {"pick": "Bayern Win", "odds": "1.55"},
            {"pick": "Over 3.5 Goals", "odds": "2.20"}
        ]
    },
    {
        "date": "31 Oct 20:00",
        "league": "La Liga",
        "match": "Barcelona vs Alaves",
        "prediction": "Barcelona Win & Over 2.5 Goals",
        "correct_score": "3 - 1",
        "odds": "1.38",
        "ev_edge": "+8.2%",
        "banker": True,
        "home_xg": 2.42,
        "away_xg": 0.75,
        "over_2_5_pct": 76.8,
        "btts_pct": 49.5,
        "pick": "Barcelona Win",
        "pick_odds": 1.22,
        "builder_picks": [
            {"pick": "Barcelona -1.5 Handicap", "odds": "1.85"},
            {"pick": "Over 2.5 Goals", "odds": "1.52"},
            {"pick": "Barcelona Win & BTTS", "odds": "2.45"},
            {"pick": "Over 10.5 Total Corners", "odds": "1.60"}
        ]
    },
    {
        "date": "01 Nov 19:45",
        "league": "Serie A",
        "match": "AC Milan vs Inter",
        "prediction": "Draw or BTTS & Over 2.5",
        "correct_score": "1 - 1",
        "odds": "1.67",
        "ev_edge": "+5.4%",
        "banker": False,
        "home_xg": 1.35,
        "away_xg": 1.42,
        "over_2_5_pct": 68.0,
        "btts_pct": 65.5,
        "pick": "Draw or Inter",
        "pick_odds": 1.78,
        "builder_picks": [
            {"pick": "Double Chance: Draw or Inter", "odds": "1.55"},
            {"pick": "Both Teams To Score", "odds": "1.58"},
            {"pick": "Over 2.5 Goals", "odds": "1.65"},
            {"pick": "Inter Win or Draw (X2)", "odds": "1.30"}
        ]
    }
]

@app.api_route("/api/data", methods=["GET", "HEAD"])
@app.api_route("/api/fixtures", methods=["GET", "HEAD"])
@app.api_route("/api/slate", methods=["GET", "HEAD"])
async def get_data():
    return {
        "status": "ok",
        "fixtures": FIXTURES,
        "weights": {
            "attack_alpha": 1.18,
            "defense_beta": 0.82,
            "home_advantage": 1.14
        }
    }

@app.api_route("/api/acca", methods=["GET", "HEAD"])
async def get_acca(legs: int = 5):
    legs = max(2, min(5, legs))
    return {
        "status": "ok",
        "legs": legs,
        "selection": FIXTURES[:legs]
    }

@app.api_route("/", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def serve_index(request: Request):
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>GEM Engine Running ✅</h1>")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
