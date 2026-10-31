from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import os, json, math
from datetime import datetime

app = FastAPI(title="GEM V15.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ODDS_API_KEY = os.getenv("ODDS_API_KEY", "")

class QuantEngine:
    def __init__(self):
        self.weights = {
            "attack_alpha": 1.18,
            "defense_beta": 0.82,
            "home_advantage": 1.14,
            "decay_lambda": 0.04
        }
        self.learning_rate = 0.015

    def calculate_poisson_probability(self, home_rating, away_rating, max_goals=5):
        exp_home_goals = home_rating * self.weights["attack_alpha"] * self.weights["home_advantage"]
        exp_away_goals = away_rating * self.weights["defense_beta"]
        home_win_prob = draw_prob = away_win_prob = 0.0
        for h in range(max_goals + 1):
            p_h = (math.pow(exp_home_goals, h) * math.exp(-exp_home_goals)) / math.factorial(h)
            for a in range(max_goals + 1):
                p_a = (math.pow(exp_away_goals, a) * math.exp(-exp_away_goals)) / math.factorial(a)
                p_joint = p_h * p_a
                if h > a: home_win_prob += p_joint
                elif h == a: draw_prob += p_joint
                else: away_win_prob += p_joint
        return home_win_prob, draw_prob, away_win_prob

    def find_ev_edge(self, model_prob, bookmaker_odds):
        if bookmaker_odds <= 1.0: return 0.0
        return round((model_prob * bookmaker_odds - 1.0) * 100, 2)

GEM_Engine = QuantEngine()

FIXTURES = [
    {
        "date": "31 Oct 12:30",
        "league": "Premier League",
        "match": "Chelsea vs Man Utd",
        "prediction": "Chelsea Win & Over 1.5 Goals",
        "correct_score": "2 - 1",
        "odds": "1.91",
        "ev_edge": "+6.4%",
        "banker": True
    },
    {
        "date": "31 Oct 15:00",
        "league": "Premier League",
        "match": "Man City vs Brighton",
        "prediction": "Man City Win & Over 2.5 Goals",
        "correct_score": "3 - 0",
        "odds": "1.55",
        "ev_edge": "+7.1%",
        "banker": True
    },
    {
        "date": "31 Oct 17:30",
        "league": "Bundesliga",
        "match": "Bayern vs Dortmund",
        "prediction": "Both Teams To Score & Over 2.5",
        "correct_score": "2 - 2",
        "odds": "1.85",
        "ev_edge": "+6.9%",
        "banker": False
    },
    {
        "date": "31 Oct 20:00",
        "league": "La Liga",
        "match": "Barcelona vs Alaves",
        "prediction": "Barcelona Win & Over 2.5 Goals",
        "correct_score": "3 - 1",
        "odds": "1.38",
        "ev_edge": "+8.2%",
        "banker": True
    },
    {
        "date": "01 Nov 19:45",
        "league": "Serie A",
        "match": "AC Milan vs Inter",
        "prediction": "Draw or BTTS & Over 2.5",
        "correct_score": "1 - 1",
        "odds": "1.67",
        "ev_edge": "+5.4%",
        "banker": False
    }
]

@app.api_route("/", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def serve_index(request: Request):
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    return HTMLResponse(content="<h1>GEM Engine Running ✅</h1>")

@app.api_route("/api/data", methods=["GET", "HEAD"])
@app.api_route("/api/fixtures", methods=["GET", "HEAD"])
@app.api_route("/api/slate", methods=["GET", "HEAD"])
async def get_data():
    return {
        "status": "ok",
        "fixtures": FIXTURES,
        "weights": GEM_Engine.weights
    }

@app.api_route("/api/acca", methods=["GET", "HEAD"])
async def get_acca(legs: int = 5):
    legs = max(2, min(20, legs))
    return {
        "status": "ok",
        "legs": legs,
        "selection": FIXTURES[:legs]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
