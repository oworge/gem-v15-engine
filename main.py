from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from datetime import datetime

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/fixtures")
async def get_fixtures():
    # Active, upcoming unplayed match slate for the current active matchday
    active_slate = [
        {"leg": 1, "match": "Chelsea vs Newcastle", "selection": "Chelsea Win", "market": "1X2", "odds": 1.75},
        {"leg": 2, "match": "Crystal Palace vs Liverpool", "selection": "Liverpool Win", "market": "1X2", "odds": 1.50},
        {"leg": 3, "match": "West Ham vs Manchester United", "selection": "Over 2.5 Goals", "market": "Total Goals", "odds": 1.70},
        {"leg": 4, "match": "Real Madrid vs Barcelona", "selection": "Over 1.5 Goals", "market": "Goals", "odds": 1.22},
        {"leg": 5, "match": "Inter Milan vs Juventus", "selection": "Inter Milan Win or Draw", "market": "Double Chance", "odds": 1.30},
        {"leg": 6, "match": "Monaco vs Lyon", "selection": "Both Teams to Score", "market": "BTTS", "odds": 1.65},
        {"leg": 7, "match": "Ajax vs Feyenoord", "selection": "Over 2.5 Goals", "market": "Total Goals", "odds": 1.60},
        {"leg": 8, "match": "Benfica vs Porto", "selection": "Benfica Win or Draw", "market": "Double Chance", "odds": 1.28},
        {"leg": 9, "match": "Sporting CP vs Braga", "selection": "Sporting CP Win", "market": "1X2", "odds": 1.55}
    ]
    
    return {
        "status": "success",
        "timestamp": datetime.utcnow().isoformat(),
        "slate": active_slate,
        "accumulators": {
            "six_fold": {"legs": "1-6", "odds": 8.15, "stake": 10.0, "return": 81.50},
            "nine_fold": {"legs": "1-9", "odds": 36.42, "stake": 5.0, "return": 182.10}
        }
    }
