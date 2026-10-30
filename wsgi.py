from flask import Flask, render_template_string, request
import os

app = Flask(__name__)

MASTER_DATA = {
    "bankers": [
        {"date": "Fri 30 Oct - 18:00", "fixture": "Le Havre vs Paris SG", "selection": "PSG Win", "market": "Match Result", "odds": "1.35", "ev": 7.5},
        {"date": "Fri 30 Oct - 20:00", "fixture": "Villarreal vs Espanyol", "selection": "Villarreal Win", "market": "Match Result", "odds": "1.40", "ev": 8.4}
    ],
    "dailypicks": [
        {"date": "Fri 30 Oct - 18:00", "fixture": "Le Havre vs Paris SG", "selection": "PSG Win & Over 1.5", "market": "Match Result + Goals", "odds": "1.35", "ev": 6.8}
    ]
}

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <title>EdgeMetrix Pro 26</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #07090e; color: #f3f4f6; padding: 20px; font-family: sans-serif; }
        .nav-pills .nav-link { color: #9ca3af; background: #111622; border: 1px solid #212c42; margin-right: 8px; }
        .nav-pills .nav-link.active { background-color: #1d4ed8; color: white; }
        .table-dark { background: #111622; border: 1px solid #212c42; }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="text-white fw-bold mb-3">EdgeMetrix Pro 26</h1>
        <ul class="nav nav-pills mb-4">
            <li class="nav-item"><a class="nav-link {% if active_key == 'bankers' %}active{% endif %}" href="/?slate=bankers">🏦 Bankers of the Day</a></li>
            <li class="nav-item"><a class="nav-link {% if active_key == 'dailypicks' %}active{% endif %}" href="/?slate=dailypicks">⭐ Daily Picks</a></li>
        </ul>
        <div class="card bg-dark text-white p-3 border-secondary">
            <h3>{{ slate_title }}</h3>
            <table class="table table-dark mt-3">
                <thead>
                    <tr><th>Fixture</th><th>Selection</th><th>Market</th><th>Odds</th><th>EV %</th></tr>
                </thead>
                <tbody>
                    {% for item in items %}
                    <tr>
                        <td>{{ item.fixture }}</td>
                        <td><span class="badge bg-primary">{{ item.selection }}</span></td>
                        <td>{{ item.market }}</td>
                        <td class="text-success fw-bold">{{ item.odds }}</td>
                        <td>+{{ item.ev }}%</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>"""

@app.route("/")
def home():
    slate_key = request.args.get("slate", "bankers")
    items = MASTER_DATA.get(slate_key, MASTER_DATA["bankers"])
    title = "Bankers of the Day" if slate_key == "bankers" else "Daily Value Picks"
    return render_template_string(HTML_TEMPLATE, items=items, active_key=slate_key, slate_title=title)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
