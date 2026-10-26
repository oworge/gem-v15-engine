from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import os
app = FastAPI()
@app.get("/api/fixtures")
def get_fixtures():
    slate_data = [
        {"leg": 1, "match": "PSG vs. Lyon", "selection": "PSG Double Chance (1X) & Over 1.5 Goals", "odds": 1.45, "time": "20:00 GMT", "status": "UPCOMING"},
        {'leg': 2, 'match': 'Sevilla vs. Osasuna', 'selection': 'Over 1.5 Goals', 'odds': 1.38, 'time': '20:00 GMT', 'status': 'UPCOMING'},
        {"leg": 3, "match": "Galatasaray vs. Fenerbahce", "selection": "Over 1.5 Goals", "odds": 1.30, "time": "17:00 GMT", "status": "UPCOMING'},
        {"leg": 4, "match": "Bayern Munich vs. Dortmund", "selection": "Over 2.5 Goals", "odds": 1.40, "time": "17:30 GMT", "status": "UPCOMING'},
        {"leg": 5, "match": "Inter Milan vs. Juventus", "selection": "Inter Double Chance (1X)", "odds": 1.35, "time": "19:45 GMT", "status": "UPCOMING"},
        {"leg": 6, "match": "Real Madrid vs. Atletico Madrid", "selection": "Over 1.5 Goals", "odds": 1.28, "time": "20:00 GMT", "status": "UPCOMING"},
        {'leg': 7, 'match': 'Arsenal vs. Chelsea', 'selection': 'Arsenal Double Chance (1X)', 'odds': 1.32, 'time': '16:30 GMT', 'status': 'UPCOMING'},
        {"leg": 8, "match": "Barcelona vs. Athletic Bilbao", "selection": "Over 1.5 Goals", "odds": 1.25, "time": "20:00 GMT", "status": "UPCOMING'},
        {"leg": 9, "match": "Ajax vs. PSVEindhoven", "selection": "Over 1.5 Goals", "odds": 1.22, "time": "13:30 GMT", "status": "UPCOMING"}
    ]
    three_odds = round(1.45 * 1.38 * 1.30, 2)
    six_odds = round(three_odds * 1.40 * 1.35 * 1.28, 2)
    nine_odds = round(six_odds * 1.32 * 1.25 * 1.22, 2)
    return {
        "status": "success",
        "accumulators": {
            "three_fold": {"odds": three_odds},
            "six_fold": {"odds": six_odds},
            "nine_fold": {"odds": nine_odds}
        },
        "slate": slate_data
    }
@app.get("/", response_class=HTMLResponse)
def read_root():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(base_dir, "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()