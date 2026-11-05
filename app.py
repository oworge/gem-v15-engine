from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EDGEMETRIX V300</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            background: #0b0f19;
            color: #f1f5f9;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 700px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid #1e293b;
        }
        h1 {
            color: #38bdf8;
            font-size: 26px;
            font-weight: 800;
            margin-bottom: 8px;
        }
        .status {
            color: #4ade80;
            font-size: 14px;
            font-weight: 600;
        }
        .card {
            background: #1e293b;
            border-radius: 14px;
            padding: 24px;
            margin-bottom: 20px;
            border: 1px solid #334155;
        }
        .card h2 {
            color: #e2e8f0;
            font-size: 18px;
            margin-bottom: 18px;
            padding-bottom: 10px;
            border-bottom: 1px solid #334155;
        }
        .match {
            background: #0f172a;
            border-radius: 10px;
            padding: 16px;
            margin-bottom: 14px;
            border-left: 3px solid #38bdf8;
        }
        .match-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }
        .teams {
            font-weight: 700;
            font-size: 15px;
        }
        .time {
            color: #94a3b8;
            font-size: 12px;
        }
        .league {
            color: #94a3b8;
            font-size: 12px;
            margin-bottom: 12px;
        }
        .market {
            background: #1e293b;
            border-radius: 8px;
            padding: 12px;
            margin-top: 8px;
            border: 1px solid #334155;
        }
        .market-name {
            font-weight: 600;
            font-size: 14px;
            margin-bottom: 4px;
        }
        .market-details {
            display: flex;
            justify-content: space-between;
            font-size: 13px;
        }
        .odds {
            color: #fbbf24;
            font-weight: 600;
        }
        .edge {
            color: #4ade80;
            font-weight: 700;
        }
        
        /* Mobile/Tablet Fix */
        @media (max-width: 600px) {
            body { padding: 12px; }
            .card { padding: 16px; }
            h1 { font-size: 22px; }
            .match-header { flex-direction: column; align-items: flex-start; gap: 4px; }
            .market-details { flex-direction: column; gap: 2px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚽ EDGEMETRIX V300 DASHBOARD</h1>
            <p class="status">● ONLINE — Flask & Render Active</p>
        </div>

        <div class="card">
            <h2>📊 Daily Value Picks — 05 Nov 2026</h2>

            <div class="match">
                <div class="match-header">
                    <span class="teams">AC Milan vs Ferencváros</span>
                    <span class="time">17:45 GMT</span>
                </div>
                <div class="league">UEFA Europa League</div>
                <div class="market">
                    <div class="market-name">Over 1.5 Goals & Milan Double Chance</div>
                    <div class="market-details">
                        <span class="odds">Odds: 1.42</span>
                        <span>Probability: 77.0%</span>
                        <span class="edge">Edge: +3.2%</span>
                    </div>
                </div>
                <div class="market">
                    <div class="market-name">Both Teams To Score — Yes</div>
                    <div class="market-details">
                        <span class="odds">Odds: 1.72</span>
                        <span>Probability: 62.0%</span>
                        <span class="edge">Edge: +1.8%</span>
                    </div>
                </div>
            </div>

            <div class="match">
                <div class="match-header">
                    <span class="teams">Bayer Leverkusen vs Marseille</span>
                    <span class="time">20:00 GMT</span>
                </div>
                <div class="league">UEFA Europa League</div>
                <div class="market">
                    <div class="market-name">Over 1.5 Goals</div>
                    <div class="market-details">
                        <span class="odds">Odds: 1.35</span>
                        <span>Probability: 80.0%</span>
                        <span class="edge">Edge: +5.4%</span>
                    </div>
                </div>
                <div class="market">
                    <div class="market-name">Leverkusen Win</div>
                    <div class="market-details">
                        <span class="odds">Odds: 1.42</span>
                        <span>Probability: 76.0%</span>
                        <span class="edge">Edge: +5.0%</span>
                    </div>
                </div>
            </div>

            <div class="match">
                <div class="match-header">
                    <span class="teams">Real Sociedad vs Lyon</span>
                    <span class="time">17:45 GMT</span>
                </div>
                <div class="league">UEFA Europa League</div>
                <div class="market">
                    <div class="market-name">Over 1.5 Goals</div>
                    <div class="market-details">
                        <span class="odds">Odds: 1.30</span>
                        <span>Probability: 81.0%</span>
                        <span class="edge">Edge: +4.2%</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
