from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>EDGEMETRIX V300</title>
        <style>
            body { background: #0b0f19; color: white; font-family: sans-serif; padding: 20px; text-align: center; }
            h1 { color: #38bdf8; }
            .card { background: #1e293b; padding: 25px; border-radius: 12px; max-width: 450px; margin: 20px auto; border: 1px solid #334155; }
            .ok { color: #4ade80; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>⚽ EDGEMETRIX V300 DASHBOARD</h1>
        <div class="card">
            <p class="ok">✅ LIVE — Connected</p>
            <p>Flask + Render Active</p>
            <hr style="border: none; border-top: 1px solid #334155; margin: 20px 0;">
            <h3>📊 Today's Picks</h3>
            <p><strong>AC Milan vs Ferencvaros</strong><br>
            Over 1.5 Goals — Odds: 1.42<br>
            <span class="ok">Edge: +3.2%</span></p>
            <p><strong>Bayer Leverkusen vs Marseille</strong><br>
            Leverkusen Win — Odds: 1.42<br>
            <span class="ok">Edge: +4.1%</span></p>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
