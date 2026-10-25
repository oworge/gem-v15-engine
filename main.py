from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from datetime import datetime

app = FastAPI()

@app.get("/manifest.json")
async def manifest():
    return {"name": "GEM V15.0 Engine", "short_name": "GEM V15", "start_url": "/", "display": "standalone", "background_color": "#121212", "theme_color": "#00ff88", "icons": []}

@app.get("/", response_class=HTMLResponse)
async def read_index(response: Response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/fixtures")
async def get_fixtures(response: Response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    active_slate = [
        {"leg": 1, "match": "Chelsea vs Newcastle", "selection": "Chelsea Win", "market": "1X2", "odds": 1.75, "status": "UPCOMING"},
        {"leg": 2, "match": "Crystal Palace vs Liverpool", "selection": "Liverpool Win", "market": "1X2", "odds": 1.50, "status": "UPCOMING"},
        {"leg": 3, "match": "West Ham vs Manchester United", "selection": "Over 2.5 Goals", "market": "Total Goals", "odds": 1.70, "status": "UPCOMING"},
        {"leg": 4, "match": "Real Madrid vs Barcelona", "selection": "Over 1.5 Goals", "market": "Goals", "odds": 1.22, "status": "UPCOMING"},
        {"leg": 5, "match": "Inter Milan vs Juventus", "selection": "Inter Milan Win or Draw", "market": "Double Chance", "odds": 1.30, "status": "UPCOMING"},
        {"leg": 6, "match": "Monaco vs Lyon", "selection": "Both Teams to Score", "market": "BTTS", "odds": 1.65, "status": "UPCOMING"},
        {"leg": 7, "match": "Ajax vs Feyenoord", "selection": "Over 2.5 Goals", "market": "Total Goals", "odds": 1.60, "status": "UPCOMING"},
        {"leg": 8, "match": "Benfica vs Porto", "selection": "Benfica Win or Draw", "market": "Double Chance", "odds": 1.28, "status": "UPCOMING"},
        {"leg": 9, "match": "Sporting CP vs Braga", "selection": "Sporting CP Win", "market": "1X2", "odds": 1.55, "status": "UPCOMING"}
    ]
    return {
        "status": "success",
        "updated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "slate": active_slate,
        "accumulators": {
            "three_fold": {"legs": "1-3", "odds": 4.46},
            "six_fold": {"legs": "1-6", "odds": 8.15},
            "nine_fold": {"legs": "1-9", "odds": 36.42}
        }
    }
