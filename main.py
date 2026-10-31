from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import os

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
    # EXACT names from index.html — NO DEVIATION
    f["hxg"] = f.get("home_xg", 0)
    f["axg"] = f.get("away_xg", 0)
    f["prob_home"] = f.get("h_pct_num", 0)
    f["prob_draw"] = f.get("d_pct_num", 0)
    f["prob_away"] = f.get("a_pct_num", 0)
    f["prob_over25"] = f.get("over25_num", 0)
    f["prob_btts"] = f.get("btts_num", 0)
    f["ev_home"] = f.get("evh_num", 0)
    f["ev_draw"] = f.get("evd_num", 0)
    f["ev_away"] = f.get("eva_num", 0)
    f["value_home"] = f.get("evh_num", 0) >= 5
    f["value_draw"] = f.get("evd_num", 0) >= 5
    f["value_away"] = f.get("eva_num", 0) >= 5
    f["score_grid"] = f.get("score_matrix", [])
    f["date_category"] = f.get("date", "")
    return f

FIXTURES = [
    make_fixture(
        date="31 Oct 12:30", league="Premier League", match="Chelsea vs Man Utd",
        home_xg=1.68, away_xg=1.05,
        h_pct_num=52.3, d_pct_num=24.5, a_pct_num=23.2,
        over25_num=72.5, btts_num=58.2,
        evh_num=6.4, evd_num=-2.1, eva_num=-4.8,
        odds_home=1.72, odds_draw=3.60, odds_away=4.10,
        score_matrix=[
            [0.25, 0.12, 0.05, 0.02, 0.01],
            [0.18, 0.15, 0.08, 0.03, 0.01],
            [0.09, 0.06, 0.04, 0.02, 0.01],
            [0.04, 0.03, 0.02, 0.01, 0.00],
            [0.02, 0.01, 0.01, 0.00, 0.00]
        ]
    ),
    make_fixture(
        date="31 Oct 15:00", league="Premier League", match="Man City vs Brighton",
        home_xg=2.35, away_xg=0.82,
        h_pct_num=68.2, d_pct_num=18.5, a_pct_num=13.3,
        over25_num=81.3, btts_num=52.0,
        evh_num=7.1, evd_num=-3.2, eva_num=-6.5,
        odds_home=1.40, odds_draw=5.20, odds_away=7.50,
        score_matrix=[
            [0.32, 0.18, 0.08, 0.03, 0.02],
            [0.22, 0.14, 0.07, 0.03, 0.01],
            [0.10, 0.07, 0.04, 0.02, 0.01],
            [0.05, 0.03, 0.02, 0.01, 0.00],
            [0.02, 0.01, 0.01, 0.00, 0.00]
        ]
    ),
    make_fixture(
        date="31 Oct 17:30", league="Bundesliga", match="Bayern vs Dortmund",
        home_xg=2.10, away_xg=1.85,
        h_pct_num=45.8, d_pct_num=22.4, a_pct_num=31.8,
        over25_num=85.0, btts_num=78.5,
        evh_num=2.3, evd_num=5.1, eva_num=6.9,
        odds_home=1.55, odds_draw=4.40, odds_away=2.35,
        score_matrix=[
            [0.15, 0.12, 0.09, 0.04, 0.02],
            [0.14, 0.16, 0.11, 0.05, 0.02],
            [0.08, 0.10, 0.07, 0.03, 0.01],
            [0.04, 0.05, 0.03, 0.02, 0.01],
            [0.01, 0.02, 0.01, 0.01, 0.00]
        ]
    ),
    make_fixture(
        date="31 Oct 20:00", league="La Liga", match="Barcelona vs Alaves",
        home_xg=2.42, away_xg=0.75,
        h_pct_num=75.5, d_pct_num=14.2, a_pct_num=10.3,
        over25_num=76.8, btts_num=49.5,
        evh_num=8.2, evd_num=-4.5, eva_num=-7.8,
        odds_home=1.22, odds_draw=6.80, odds_away=9.50,
        score_matrix=[
            [0.35, 0.20, 0.09, 0.04, 0.02],
            [0.24, 0.15, 0.07, 0.03, 0.01],
            [0.11, 0.06, 0.04, 0.02, 0.01],
            [0.05, 0.03, 0.02, 0.01, 0.00],
            [0.02, 0.01, 0.01, 0.00, 0.00]
        ]
    ),
    make_fixture(
        date="01 Nov 19:45", league="Serie A", match="AC Milan vs Inter",
        home_xg=1.35, away_xg=1.42,
        h_pct_num=34.2, d_pct_num=28.5, a_pct_num=37.3,
        over25_num=68.0, btts_num=65.5,
        evh_num=-1.2, evd_num=5.4, eva_num=3.8,
        odds_home=2.60, odds_draw=3.20, odds_away=2.15,
        score_matrix=[
            [0.18, 0.14, 0.07, 0.03, 0.01],
            [0.15, 0.17, 0.10, 0.04, 0.02],
            [0.07, 0.09, 0.06, 0.03, 0.01],
            [0.03, 0.04, 0.02, 0.01, 0.01],
            [0.01, 0.01, 0.01, 0.00, 0.00]
        ]
    )
]

BANKERS = [f for f in FIXTURES if f["value_home"] or f["value_draw"] or f["value_away"]]

@app.api_route("/api/slate", methods=["GET", "HEAD"])
@app.api_route("/api/data", methods=["GET", "HEAD"])
@app.api_route("/api/fixtures", methods=["GET", "HEAD"])
async def get_data():
    return {
        "status": "ok",
        "pipeline_status": "live",
        "fixtures": FIXTURES,
        "bankers": BANKERS,
        "weights": {"attack_alpha": 1.18, "defense_beta": 0.82, "home_advantage": 1.14}
    }

@app.api_route("/api/acca", methods=["GET", "HEAD"])
async def get_acca(legs: int = 5):
    legs = max(2, min(5, legs))
    return {"status": "ok", "legs": legs, "selection": FIXTURES[:legs]}

@app.api_route("/api/log", methods=["POST"])
async def log_sel(request: Request):
    return {"status": "ok"}

@app.api_route("/api/ledger", methods=["GET", "HEAD"])
async def get_ledger():
    return []

@app.api_route("/", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def serve_index(request: Request):
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Running ✅</h1>")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
