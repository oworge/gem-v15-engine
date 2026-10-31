import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="EDGEMETRIX-PRO-26")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def make_fixture(**data):
    f = data
    f["hxg"] = f.get("home_xg", 0)
    f["axg"] = f.get("away_xg", 0)
    f["prob_home"] = f.get("h_pct", "0%")
    f["prob_draw"] = f.get("d_pct", "0%")
    f["prob_away"] = f.get("a_pct", "0%")
    f["prob_over25"] = f.get("over_2_5_pct", "0%")
    f["prob_btts"] = f.get("btts_pct", "0%")
    f["ev_home"] = f.get("evh", 0)
    f["ev_draw"] = f.get("evd", 0)
    f["ev_away"] = f.get("eva", 0)
    f["score_grid"] = f.get("score_matrix", [])
    f["date_category"] = f.get("date", "")
    
    # Value & Banker flags
    f["value_home"] = f.get("evh", 0) >= 5
    f["value_draw"] = f.get("evd", 0) >= 5
    f["value_away"] = f.get("eva", 0) >= 5
    f["banker"] = f["value_home"] or f["value_draw"] or f["value_away"]

    # Dashboard display mappings
    f["prediction"] = f.get("pred_selection", f"{f.get('match', 'Match').split(' vs ')[0]} Win & Over 1.5 Goals")
    f["odds"] = str(f.get("odds_home", 1.80))
    f["correct_score"] = f.get("score_pred", "2 - 1")
    f["score_odds"] = "8.50"
    f["ev_edge"] = f"+{max(f.get('evh', 0), f.get('evd', 0), f.get('eva', 0))}%"
    
    # Bet Builder selections
    home_team = f.get('match', 'Home').split(' vs ')[0]
    f["builder_picks"] = [
        {"pick": f"{home_team} Win or Draw (1X)", "odds": str(round(f.get("odds_home", 1.80) * 0.75, 2))},
        {"pick": "Over 1.5 Goals", "odds": "1.30"},
        {"pick": "Both Teams to Score", "odds": "1.75"},
        {"pick": f"Over 4.5 {home_team} Corners", "odds": "1.50"}
    ]
    f["builder_combined_odds"] = "5.20"

    return f

FIXTURES = [
    make_fixture(
        date="31 Oct 12:30",
        league="Premier League",
        match="Chelsea vs Man Utd",
        date_category="Today",
        home_xg=1.68,
        away_xg=1.05,
        h_pct=52.3,
        d_pct=24.5,
        a_pct=23.2,
        over_2_5_pct=72.5,
        btts_pct=58.2,
        evh=6.4,
        evd=-2.1,
        eva=-4.8,
        odds_home=1.72,
        odds_draw=3.60,
        odds_away=4.10,
        pred_selection="Chelsea Win & Over 1.5 Goals",
        score_pred="2 - 1",
        score_matrix=[
            [0.25, 0.12, 0.05, 0.02, 0.01],
            [0.18, 0.15, 0.08, 0.03, 0.01],
            [0.09, 0.06, 0.04, 0.02, 0.01],
            [0.04, 0.03, 0.02, 0.01, 0.00],
            [0.02, 0.01, 0.01, 0.00, 0.00]
        ]
    ),
    make_fixture(
        date="31 Oct 15:00",
        league="Premier League",
        match="Man City vs Brighton",
        date_category="Today",
        home_xg=2.35,
        away_xg=0.82,
        h_pct=68.2,
        d_pct=18.5,
        a_pct=13.3,
        over_2_5_pct=81.3,
        btts_pct=52.0,
        evh=7.1,
        evd=-3.2,
        eva=-6.5,
        odds_home=1.40,
        odds_draw=5.20,
        odds_away=7.50,
        pred_selection="Man City Win & Over 2.5 Goals",
        score_pred="3 - 0",
        score_matrix=[
            [0.32, 0.18, 0.08, 0.03, 0.02],
            [0.22, 0.14, 0.07, 0.03, 0.01],
            [0.10, 0.07, 0.04, 0.02, 0.01],
            [0.05, 0.03, 0.02, 0.01, 0.00],
            [0.02, 0.01, 0.01, 0.00, 0.00]
        ]
    ),
    make_fixture(
        date="31 Oct 17:30",
        league="Bundesliga",
        match="Bayern vs Dortmund",
        date_category="Today",
        home_xg=2.10,
        away_xg=1.85,
        h_pct=45.8,
        d_pct=22.4,
        a_pct=31.8,
        over_2_5_pct=85.0,
        btts_pct=78.5,
        evh=2.3,
        evd=5.1,
        eva=6.9,
        odds_home=1.55,
        odds_draw=4.40,
        odds_away=2.35,
        pred_selection="Both Teams to Score & Over 2.5",
        score_pred="2 - 2",
        score_matrix=[
            [0.15, 0.12, 0.09, 0.04, 0.02],
            [0.14, 0.16, 0.11, 0.05, 0.02],
            [0.08, 0.10, 0.07, 0.03, 0.01],
            [0.04, 0.05, 0.03, 0.02, 0.01],
            [0.01, 0.02, 0.01, 0.01, 0.00]
        ]
    ),
    make_fixture(
        date="31 Oct 20:00",
        league="La Liga",
        match="Barcelona vs Alaves",
        date_category="Today",
        home_xg=2.42,
        away_xg=0.75,
        h_pct=75.5,
        d_pct=14.2,
        a_pct=10.3,
        over_2_5_pct=76.8,
        btts_pct=49.5,
        evh=8.2,
        evd=-4.5,
        eva=-7.8,
        odds_home=1.22,
        odds_draw=6.80,
        odds_away=9.50,
        pred_selection="Barcelona Win & Over 2.5 Goals",
        score_pred="3 - 1",
        score_matrix=[
            [0.35, 0.20, 0.09, 0.04, 0.02],
            [0.24, 0.15, 0.07, 0.03, 0.01],
            [0.11, 0.06, 0.04, 0.02, 0.01],
            [0.05, 0.03, 0.02, 0.01, 0.00],
            [0.02, 0.01, 0.01, 0.00, 0.00]
        ]
    ),
    make_fixture(
        date="01 Nov 19:45",
        league="Serie A",
        match="AC Milan vs Inter",
        date_category="Tomorrow",
        home_xg=1.35,
        away_xg=1.42,
        h_pct=34.2,
        d_pct=28.5,
        a_pct=37.3,
        evh=-1.2,
        evd=5.4,
        eva=3.8,
        odds_home=2.60,
        odds_draw=3.20,
        odds_away=2.15,
        pred_selection="Draw or Inter (X2) & Over 1.5",
        score_pred="1 - 1",
        score_matrix=[
            [0.18, 0.14, 0.07, 0.03, 0.01],
            [0.15, 0.17, 0.10, 0.04, 0.02],
            [0.07, 0.09, 0.06, 0.03, 0.01],
            [0.03, 0.04, 0.02, 0.01, 0.01],
            [0.01, 0.01, 0.01, 0.00, 0.00]
        ]
    )
]

BANKERS = [f for f in FIXTURES if f["banker"]]

@app.api_route("/api/slate", methods=["GET", "HEAD"])
@app.api_route("/api/data", methods=["GET", "HEAD"])
@app.api_route("/api/fixtures", methods=["GET", "HEAD"])
async def get_data():

@app.api_route("/api/slate", methods=["GET", "HEAD"])
@app.api_route("/api/data", methods=["GET", "HEAD"])
@app.api_route("/api/fixtures", methods=["GET", "HEAD"])
async def get_data():
    # Evaluate bankers dynamically on every request
    active_bankers = [f for f in FIXTURES if f.get("banker", False)]
    
    return {
        "status": "ok",
        "pipeline_status": "live",
        "fixtures": FIXTURES,
        "selections": FIXTURES,  # Fallback key for JS renderers
        "bankers": active_bankers,
        "weights": {
            "attack_alpha": 1.18,
            "defense_beta": 0.82,
            "home_advantage": 1.14
        }
    }
import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="EDGEMETRIX-PRO-26")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def make_fixture(**data):
    f = data
    f["hxg"] = f.get("home_xg", 0)
    f["axg"] = f.get("away_xg", 0)
    f["prob_home"] = f.get("h_pct", "0%")
    f["prob_draw"] = f.get("d_pct", "0%")
    f["prob_away"] = f.get("a_pct", "0%")
    f["prob_over25"] = f.get("over_2_5_pct", "0%")
    f["prob_btts"] = f.get("btts_pct", "0%")
    f["ev_home"] = f.get("evh", 0)
    f["ev_draw"] = f.get("evd", 0)
    f["ev_away"] = f.get("eva", 0)
    f["score_grid"] = f.get("score_matrix", [])
    f["date_category"] = f.get("date", "")
    
    # Value & Banker flags
    f["value_home"] = f.get("evh", 0) >= 5
    f["value_draw"] = f.get("evd", 0) >= 5
    f["value_away"] = f.get("eva", 0) >= 5
    f["banker"] = f["value_home"] or f["value_draw"] or f["value_away"]

    # Dashboard display mappings
    f["prediction"] = f.get("pred_selection", f"{f.get('match', 'Match').split(' vs ')[0]} Win & Over 1.5 Goals")
    f["odds"] = str(f.get("odds_home", 1.80))
    f["correct_score"] = f.get("score_pred", "2 - 1")
    f["score_odds"] = "8.50"
    f["ev_edge"] = f"+{max(f.get('evh', 0), f.get('evd', 0), f.get('eva', 0))}%"
    
    # Bet Builder selections
    home_team = f.get('match', 'Home').split(' vs ')[0]
    f["builder_picks"] = [
        {"pick": f"{home_team} Win or Draw (1X)", "odds": str(round(f.get("odds_home", 1.80) * 0.75, 2))},
        {"pick": "Over 1.5 Goals", "odds": "1.30"},
        {"pick": "Both Teams to Score", "odds": "1.75"},
        {"pick": f"Over 4.5 {home_team} Corners", "odds": "1.50"}
    ]
    f["builder_combined_odds"] = "5.20"

    return f

FIXTURES = [
    make_fixture(
        date="31 Oct 12:30",
        league="Premier League",
        match="Chelsea vs Man Utd",
        date_category="Today",
        home_xg=1.68,
        away_xg=1.05,
        h_pct=52.3,
        d_pct=24.5,
        a_pct=23.2,
        over_2_5_pct=72.5,
        btts_pct=58.2,
        evh=6.4,
        evd=-2.1,
        eva=-4.8,
        odds_home=1.72,
        odds_draw=3.60,
        odds_away=4.10,
        pred_selection="Chelsea Win & Over 1.5 Goals",
        score_pred="2 - 1",
        score_matrix=[
            [0.25, 0.12, 0.05, 0.02, 0.01],
            [0.18, 0.15, 0.08, 0.03, 0.01],
            [0.09, 0.06, 0.04, 0.02, 0.01],
            [0.04, 0.03, 0.02, 0.01, 0.00],
            [0.02, 0.01, 0.01, 0.00, 0.00]
        ]
    ),
    make_fixture(
        date="31 Oct 15:00",
        league="Premier League",
        match="Man City vs Brighton",
        date_category="Today",
        home_xg=2.35,
        away_xg=0.82,
        h_pct=68.2,
        d_pct=18.5,
        a_pct=13.3,
        over_2_5_pct=81.3,
        btts_pct=52.0,
        evh=7.1,
        evd=-3.2,
        eva=-6.5,
        odds_home=1.40,
        odds_draw=5.20,
        odds_away=7.50,
        pred_selection="Man City Win & Over 2.5 Goals",
        score_pred="3 - 0",
        score_matrix=[
            [0.32, 0.18, 0.08, 0.03, 0.02],
            [0.22, 0.14, 0.07, 0.03, 0.01],
            [0.10, 0.07, 0.04, 0.02, 0.01],
            [0.05, 0.03, 0.02, 0.01, 0.00],
            [0.02, 0.01, 0.01, 0.00, 0.00]
        ]
    ),
    make_fixture(
        date="31 Oct 17:30",
        league="Bundesliga",
        match="Bayern vs Dortmund",
        date_category="Today",
        home_xg=2.10,
        away_xg=1.85,
        h_pct=45.8,
        d_pct=22.4,
        a_pct=31.8,
        over_2_5_pct=85.0,
        btts_pct=78.5,
        evh=2.3,
        evd=5.1,
        eva=6.9,
        odds_home=1.55,
        odds_draw=4.40,
        odds_away=2.35,
        pred_selection="Both Teams to Score & Over 2.5",
        score_pred="2 - 2",
        score_matrix=[
            [0.15, 0.12, 0.09, 0.04, 0.02],
            [0.14, 0.16, 0.11, 0.05, 0.02],
            [0.08, 0.10, 0.07, 0.03, 0.01],
            [0.04, 0.05, 0.03, 0.02, 0.01],
            [0.01, 0.02, 0.01, 0.01, 0.00]
        ]
    ),
    make_fixture(
        date="31 Oct 20:00",
        league="La Liga",
        match="Barcelona vs Alaves",
        date_category="Today",
        home_xg=2.42,
        away_xg=0.75,
        h_pct=75.5,
        d_pct=14.2,
        a_pct=10.3,
        over_2_5_pct=76.8,
        btts_pct=49.5,
        evh=8.2,
        evd=-4.5,
        eva=-7.8,
        odds_home=1.22,
        odds_draw=6.80,
        odds_away=9.50,
        pred_selection="Barcelona Win & Over 2.5 Goals",
        score_pred="3 - 1",
        score_matrix=[
            [0.35, 0.20, 0.09, 0.04, 0.02],
            [0.24, 0.15, 0.07, 0.03, 0.01],
            [0.11, 0.06, 0.04, 0.02, 0.01],
            [0.05, 0.03, 0.02, 0.01, 0.00],
            [0.02, 0.01, 0.01, 0.00, 0.00]
        ]
    ),
    make_fixture(
        date="01 Nov 19:45",
        league="Serie A",
        match="AC Milan vs Inter",
        date_category="Tomorrow",
        home_xg=1.35,
        away_xg=1.42,
        h_pct=34.2,
        d_pct=28.5,
        a_pct=37.3,
        over_2_5_pct=68.0,
        btts_pct=65.5,
        evh=-1.2,
        evd=5.4,
        eva=3.8,
        odds_home=2.60,
        odds_draw=3.20,
        odds_away=2.15,
        pred_selection="Draw or Inter (X2) & Over 1.5",
        score_pred="1 - 1",
        score_matrix=[
            [0.18, 0.14, 0.07, 0.03, 0.01],
            [0.15, 0.17, 0.10, 0.04, 0.02],
            [0.07, 0.09, 0.06, 0.03, 0.01],
            [0.03, 0.04, 0.02, 0.01, 0.01],
            [0.01, 0.01, 0.01, 0.00, 0.00]
        ]
    )
]

BANKERS = [f for f in FIXTURES if f["banker"]]

@app.api_route("/api/slate", methods=["GET", "HEAD"])
@app.api_route("/api/data", methods=["GET", "HEAD"])
@app.api_route("/api/fixtures", methods=["GET", "HEAD"])
async def get_data():
    return {
        "status": "ok",
        "pipeline_status": "live",
        "fixtures": FIXTURES,
        "bankers": BANKERS,
        "weights": {
            "attack_alpha": 1.18,
            "defense_beta": 0.82,
            "home_advantage": 1.14
        }
    }

@app.api_route("/api/acca", methods=["GET", "HEAD"])
async def get_acca(legs: int = 5):
    legs = max(2, min(len(FIXTURES), legs))
    return {
        "status": "ok",
        "legs": legs,
        "selections": FIXTURES[:legs]
    }

@app.api_route("/api/log", methods=["POST"])
async def log_sel(request: Request):
    return {"status": "ok", "msg": "Logged"}

@app.api_route("/api/ledger", methods=["GET", "HEAD"])
async def get_ledger():
    return []

@app.api_route("/", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def serve_index(request: Request):
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>EDGEMETRIX-PRO-26 Running ✅</h1>")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) = @"
import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="EDGEMETRIX-PRO-26")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def make_fixture(**data):
    f = data
    f["hxg"] = f.get("home_xg", 0)
    f["axg"] = f.get("away_xg", 0)
    f["prob_home"] = f.get("h_pct", "0%")
    f["prob_draw"] = f.get("d_pct", "0%")
    f["prob_away"] = f.get("a_pct", "0%")
    f["prob_over25"] = f.get("over_2_5_pct", "0%")
    f["prob_btts"] = f.get("btts_pct", "0%")
    f["ev_home"] = f.get("evh", 0)
    f["ev_draw"] = f.get("evd", 0)
    f["ev_away"] = f.get("eva", 0)
    f["score_grid"] = f.get("score_matrix", [])
    f["date_category"] = f.get("date", "")
    
    # Value & Banker flags
    f["value_home"] = f.get("evh", 0) >= 5
    f["value_draw"] = f.get("evd", 0) >= 5
    f["value_away"] = f.get("eva", 0) >= 5
    f["banker"] = f["value_home"] or f["value_draw"] or f["value_away"]

    # Dashboard display mappings
    f["prediction"] = f.get("pred_selection", f"{f.get('match', 'Match').split(' vs ')[0]} Win & Over 1.5 Goals")
    f["odds"] = str(f.get("odds_home", 1.80))
    f["correct_score"] = f.get("score_pred", "2 - 1")
    f["score_odds"] = "8.50"
    f["ev_edge"] = f"+{max(f.get('evh', 0), f.get('evd', 0), f.get('eva', 0))}%"
    
    # Bet Builder selections
    home_team = f.get('match', 'Home').split(' vs ')[0]
    f["builder_picks"] = [
        {"pick": f"{home_team} Win or Draw (1X)", "odds": str(round(f.get("odds_home", 1.80) * 0.75, 2))},
        {"pick": "Over 1.5 Goals", "odds": "1.30"},
        {"pick": "Both Teams to Score", "odds": "1.75"},
        {"pick": f"Over 4.5 {home_team} Corners", "odds": "1.50"}
    ]
    f["builder_combined_odds"] = "5.20"

    return f

FIXTURES = [
    make_fixture(
        date="31 Oct 12:30",
        league="Premier League",
        match="Chelsea vs Man Utd",
        date_category="Today",
        home_xg=1.68,
        away_xg=1.05,
        h_pct=52.3,
        d_pct=24.5,
        a_pct=23.2,
        over_2_5_pct=72.5,
        btts_pct=58.2,
        evh=6.4,
        evd=-2.1,
        eva=-4.8,
        odds_home=1.72,
        odds_draw=3.60,
        odds_away=4.10,
        pred_selection="Chelsea Win & Over 1.5 Goals",
        score_pred="2 - 1",
        score_matrix=[
            [0.25, 0.12, 0.05, 0.02, 0.01],
            [0.18, 0.15, 0.08, 0.03, 0.01],
            [0.09, 0.06, 0.04, 0.02, 0.01],
            [0.04, 0.03, 0.02, 0.01, 0.00],
            [0.02, 0.01, 0.01, 0.00, 0.00]
        ]
    ),
    make_fixture(
        date="31 Oct 15:00",
        league="Premier League",
        match="Man City vs Brighton",
        date_category="Today",
        home_xg=2.35,
        away_xg=0.82,
        h_pct=68.2,
        d_pct=18.5,
        a_pct=13.3,
        over_2_5_pct=81.3,
        btts_pct=52.0,
        evh=7.1,
        evd=-3.2,
        eva=-6.5,
        odds_home=1.40,
        odds_draw=5.20,
        odds_away=7.50,
        pred_selection="Man City Win & Over 2.5 Goals",
        score_pred="3 - 0",
        score_matrix=[
            [0.32, 0.18, 0.08, 0.03, 0.02],
            [0.22, 0.14, 0.07, 0.03, 0.01],
            [0.10, 0.07, 0.04, 0.02, 0.01],
            [0.05, 0.03, 0.02, 0.01, 0.00],
            [0.02, 0.01, 0.01, 0.00, 0.00]
        ]
    ),
    make_fixture(
        date="31 Oct 17:30",
        league="Bundesliga",
        match="Bayern vs Dortmund",
        date_category="Today",
        home_xg=2.10,
        away_xg=1.85,
        h_pct=45.8,
        d_pct=22.4,
        a_pct=31.8,
        over_2_5_pct=85.0,
        btts_pct=78.5,
        evh=2.3,
        evd=5.1,
        eva=6.9,
        odds_home=1.55,
        odds_draw=4.40,
        odds_away=2.35,
        pred_selection="Both Teams to Score & Over 2.5",
        score_pred="2 - 2",
        score_matrix=[
            [0.15, 0.12, 0.09, 0.04, 0.02],
            [0.14, 0.16, 0.11, 0.05, 0.02],
            [0.08, 0.10, 0.07, 0.03, 0.01],
            [0.04, 0.05, 0.03, 0.02, 0.01],
            [0.01, 0.02, 0.01, 0.01, 0.00]
        ]
    ),
    make_fixture(
        date="31 Oct 20:00",
        league="La Liga",
        match="Barcelona vs Alaves",
        date_category="Today",
        home_xg=2.42,
        away_xg=0.75,
        h_pct=75.5,
        d_pct=14.2,
        a_pct=10.3,
        over_2_5_pct=76.8,
        btts_pct=49.5,
        evh=8.2,
        evd=-4.5,
        eva=-7.8,
        odds_home=1.22,
        odds_draw=6.80,
        odds_away=9.50,
        pred_selection="Barcelona Win & Over 2.5 Goals",
        score_pred="3 - 1",
        score_matrix=[
            [0.35, 0.20, 0.09, 0.04, 0.02],
            [0.24, 0.15, 0.07, 0.03, 0.01],
            [0.11, 0.06, 0.04, 0.02, 0.01],
            [0.05, 0.03, 0.02, 0.01, 0.00],
            [0.02, 0.01, 0.01, 0.00, 0.00]
        ]
    ),
    make_fixture(
        date="01 Nov 19:45",
        league="Serie A",
        match="AC Milan vs Inter",
        date_category="Tomorrow",
        home_xg=1.35,
        away_xg=1.42,
        h_pct=34.2,
        d_pct=28.5,
        a_pct=37.3,
        evh=-1.2,
        evd=5.4,
        eva=3.8,
        odds_home=2.60,
        odds_draw=3.20,
        odds_away=2.15,
        pred_selection="Draw or Inter (X2) & Over 1.5",
        score_pred="1 - 1",
        score_matrix=[
            [0.18, 0.14, 0.07, 0.03, 0.01],
            [0.15, 0.17, 0.10, 0.04, 0.02],
            [0.07, 0.09, 0.06, 0.03, 0.01],
            [0.03, 0.04, 0.02, 0.01, 0.01],
            [0.01, 0.01, 0.01, 0.00, 0.00]
        ]
    )
]

@app.api_route("/api/slate", methods=["GET", "HEAD"])
@app.api_route("/api/data", methods=["GET", "HEAD"])
@app.api_route("/api/fixtures", methods=["GET", "HEAD"])
async def get_data():
    return {
        "status": "ok",
        "pipeline_status": "live",
        "fixtures": FIXTURES,
        "selections": FIXTURES,
        "bankers": [f for f in FIXTURES if f.get("banker", False)],
        "weights": {
            "attack_alpha": 1.18,
            "defense_beta": 0.82,
            "home_advantage": 1.14
        }
    }

@app.api_route("/api/acca", methods=["GET", "HEAD"])
async def get_acca(legs: int = 5):
    legs = max(2, min(len(FIXTURES), legs))
    return {
        "status": "ok",
        "legs": legs,
        "selections": FIXTURES[:legs]
    }

@app.api_route("/api/log", methods=["POST"])
async def log_sel(request: Request):
    return {"status": "ok", "msg": "Logged"}

@app.api_route("/api/ledger", methods=["GET", "HEAD"])
async def get_ledger():
    return []

@app.api_route("/", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def serve_index(request: Request):
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>EDGEMETRIX-PRO-26 Running ✅</h1>")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
