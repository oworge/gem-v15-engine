from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI(title="AI Scorecast PRO")

COMBO_BANKERS = [
    {"banker": 1, "date": "2026-10-27", "match": "Sevilla vs. Osasuna", "selection": "Sevilla Win or Draw (1X)", "odds": 1.25, "model_prob": "84.0%", "ev_edge": "+5.00%", "confidence": "HIGH BANKER"},
    {"banker": 2, "date": "2026-10-27", "match": "Galatasaray vs. Fenerbahce", "selection": "Over 1.5 Match Goals", "odds": 1.30, "model_prob": "82.0%", "ev_edge": "+6.60%", "confidence": "HIGH BANKER"},
    {"banker": 3, "date": "2026-10-27", "match": "Santa Clara vs. Benfica", "selection": "Benfica Win", "odds": 1.36, "model_prob": "77.0%", "ev_edge": "+4.72%", "confidence": "SOLID BANKER"},
    {"banker": 4, "date": "2026-10-27", "match": "Fleetwood vs. Arsenal", "selection": "Arsenal Win", "odds": 1.18, "model_prob": "91.0%", "ev_edge": "+7.38%", "confidence": "HIGH BANKER"},
    {"banker": 5, "date": "2026-10-27", "match": "Sabah vs. Borussia Dortmund", "selection": "Over 2.5 Match Goals", "odds": 1.40, "model_prob": "76.0%", "ev_edge": "+6.40%", "confidence": "SOLID BANKER"},
    {"banker": 6, "date": "2026-10-27", "match": "PSG vs. Barcelona", "selection": "Over 1.5 Match Goals", "odds": 1.22, "model_prob": "85.0%", "ev_edge": "+5.25%", "confidence": "HIGH BANKER"},
    {"banker": 7, "date": "2026-10-28", "match": "Manchester City vs. Brighton", "selection": "Manchester City Win", "odds": 1.32, "model_prob": "80.0%", "ev_edge": "+5.60%", "confidence": "HIGH BANKER"}
]

GOAL_COUNT_VALUE = [
    {"date": "2026-10-27", "league": "Brazil Serie A U20", "match": "Cruzeiro U20 vs. Atletico Mineiro U20", "selection": "Over 2.5 Goals", "odds": 1.57, "model_prob": "75.0%", "xg_projected": "3.20", "ev_edge": "+17.75%"},
    {"date": "2026-10-27", "league": "Friendly", "match": "Sabah vs. Borussia Dortmund", "selection": "Over 2.5 Goals", "odds": 1.40, "model_prob": "76.0%", "xg_projected": "3.35", "ev_edge": "+6.40%"},
    {"date": "2026-10-27", "league": "UEFA Champions League", "match": "Real Madrid vs. Juventus", "selection": "Over 2.5 Goals", "odds": 1.68, "model_prob": "68.0%", "xg_projected": "2.95", "ev_edge": "+14.24%"},
    {"date": "2026-10-28", "league": "EFL Cup", "match": "Bournemouth vs. Aston Villa", "selection": "Over 2.5 Goals", "odds": 1.62, "model_prob": "70.0%", "xg_projected": "3.10", "ev_edge": "+13.40%"},
    {"date": "2026-10-28", "league": "EFL Cup", "match": "Manchester City vs. Brighton", "selection": "Over 2.5 Goals", "odds": 1.50, "model_prob": "74.0%", "xg_projected": "3.45", "ev_edge": "+11.00%"},
    {"date": "2026-10-28", "league": "EFL Cup", "match": "Liverpool vs. Chelsea", "selection": "Over 2.5 Goals", "odds": 1.55, "model_prob": "72.0%", "xg_projected": "3.25", "ev_edge": "+11.60%"}
]

CORNER_PREDICTIONS = [
    {"date": "2026-10-27", "match": "Sevilla vs. Osasuna", "selection": "Sevilla Over 4.5 Corners", "odds": 1.44, "model_prob": "78.0%", "avg_corners": "6.2", "ev_edge": "+12.32%"},
    {"date": "2026-10-27", "match": "Galatasaray vs. Fenerbahce", "selection": "Over 9.5 Match Corners", "odds": 1.72, "model_prob": "65.0%", "avg_corners": "11.4", "ev_edge": "+11.80%"},
    {"date": "2026-10-27", "match": "PSG vs. Barcelona", "selection": "PSG Over 5.5 Corners", "odds": 1.65, "model_prob": "67.0%", "avg_corners": "7.1", "ev_edge": "+10.55%"},
    {"date": "2026-10-28", "match": "Liverpool vs. Chelsea", "selection": "Over 9.5 Match Corners", "odds": 1.60, "model_prob": "69.0%", "avg_corners": "10.8", "ev_edge": "+10.40%"},
    {"date": "2026-10-28", "match": "Manchester City vs. Brighton", "selection": "Man City Over 6.5 Corners", "odds": 1.53, "model_prob": "72.0%", "avg_corners": "8.3", "ev_edge": "+10.16%"}
]

FOLDS_369 = [
    {"tier": "3-Fold Conservative", "odds": "2.21", "combined_prob": "45.2%", "legs": "Sevilla 1X, Galatasaray Over 1.5, Arsenal Win"},
    {"tier": "6-Fold Balanced", "odds": "5.62", "combined_prob": "22.8%", "legs": "Sevilla 1X, Galatasaray Over 1.5, Benfica Win, Arsenal Win, Dortmund Over 2.5, PSG Over 1.5"},
    {"tier": "9-Fold High Yield Slate", "odds": "14.28", "combined_prob": "10.4%", "legs": "Sevilla 1X, Galatasaray Over 1.5, Benfica Win, Arsenal Win, Dortmund Over 2.5, PSG Over 1.5, Man City Win, Cruzeiro U20 Over 2.5, Real Madrid Over 2.5"}
]

BET_BUILDERS = [
    {"match": "Sevilla vs. Osasuna", "builder": "Sevilla 1X + Over 4.5 Sevilla Corners + Under 4.5 Goals", "combined_odds": 2.10, "ev_edge": "+8.40%"},
    {"match": "PSG vs. Barcelona", "builder": "Over 1.5 Goals + PSG Over 5.5 Corners + Both Teams to Score", "combined_odds": 2.85, "ev_edge": "+11.20%"},
    {"match": "Liverpool vs. Chelsea", "builder": "Over 2.5 Goals + Over 9.5 Match Corners + Salah 1+ Shot on Target", "combined_odds": 3.10, "ev_edge": "+14.50%"}
]

@app.get("/api/bankers")
def get_bankers(): return COMBO_BANKERS

@app.get("/api/folds")
def get_folds(): return FOLDS_369

@app.get("/api/bet-builders")
def get_bet_builders(): return BET_BUILDERS

@app.get("/api/goal-count")
def get_goal_count(): return GOAL_COUNT_VALUE

@app.get("/api/corners")
def get_corners(): return CORNER_PREDICTIONS

@app.get("/")
def read_root(): return FileResponse("index.html")
