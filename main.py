from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from datetime import datetime

app = FastAPI()

HTML_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>GEM V15.0 ENGINE</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: sans-serif; background: #121212; color: #fff; padding: 20px; max-width: 800px; margin: auto; }
        .card { background: #1e1e1e; padding: 15px; margin-bottom: 10px; border-radius: 8px; border-left: 4px solid #00ff88; }
        .acc-box { background: #1e1e1e; padding: 15px; margin-bottom: 15px; border-radius: 8px; border: 1px solid #00ff88; }
    </style>
</head>
<body>
    <h1 style="color:#00ff88;">GEM V15.0 ENGINE</h1>
    <p>QUANTITATIVE ACCUMULATOR PIPELINE</p>
    <div id="acc-container"></div>
    <h2>Selected Slate (9 Legs)</h2>
    <div id="fixtures-container">Loading slate...</div>
    <script>
        async function fetchFixtures() {
            const container = document.getElementById('fixtures-container');
            const accContainer = document.getElementById('acc-container');
            try {
                const response = await fetch('/api/fixtures?v=' + new Date().getTime());
                const result = await response.json();

                accContainer.innerHTML = \
                    <div class="acc-box">
                        <h3 style="color:#00ff88; margin-top:0;">? 6-FOLD ACCUMULATOR</h3>
                        <p>Legs: <b>\</b> | Combined Odds: <b>\</b></p>
                        <p>Recommended Stake: <b>£\</b> ? Est Return: <b>£\</b></p>
                    </div>
                    <div class="acc-box">
                        <h3 style="color:#00ff88; margin-top:0;">?? 9-FOLD ACCUMULATOR (FULL SLATE)</h3>
                        <p>Legs: <b>\</b> | Combined Odds: <b>\</b></p>
                        <p>Recommended Stake: <b>£\</b> ? Est Return: <b>£\</b></p>
                    </div>
                \;

                container.innerHTML = result.slate.map(item => \
                    <div class="card">
                        <b>Leg \: \</b><br/>
                        Selection: <span style="color:#00ff88;">\</span> (\) @ \
                    </div>
                \).join('');
            } catch (err) {
                container.innerHTML = 'Error fetching slate.';
            }
        }
        fetchFixtures();
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def read_index():
    return HTML_CONTENT

@app.get("/api/fixtures")
async def get_fixtures():
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
        "updated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "slate": active_slate,
        "accumulators": {
            "six_fold": {"legs": "1-6", "odds": 8.15, "stake": 10.0, "return": 81.50},
            "nine_fold": {"legs": "1-9", "odds": 36.42, "stake": 5.0, "return": 182.10}
        }
    }
