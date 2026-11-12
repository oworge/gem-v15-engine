import math
import random
from flask import Flask, render_template_string, jsonify
from elite_modules import calculate_negative_binomial_probabilities, run_monte_carlo_accumulator

app = Flask(__name__)

CURRENT_FIXTURES = [
    {
        "id": 1,
        "match": "Turkiye vs. Belgium",
        "competition": "UEFA Nations League",
        "market_type": "home_win",
        "home_xg": 1.52,
        "away_xg": 1.38,
        "selection": "Over 1.5 Goals",
        "odds": "3/4 (1.75)"
    },
    {
        "id": 2,
        "match": "England vs. Croatia",
        "competition": "UEFA Nations League",
        "market_type": "home_win",
        "home_xg": 1.65,
        "away_xg": 0.95,
        "selection": "England (Double Chance 1X)",
        "odds": "1/14 (1.07)"
    },
    {
        "id": 3,
        "match": "Italy vs. France",
        "competition": "UEFA Nations League",
        "market_type": "home_win",
        "home_xg": 1.45,
        "away_xg": 1.50,
        "selection": "Over 1.5 Goals",
        "odds": "4/5 (1.80)"
    }
]

@app.route('/')
def dashboard():
    evaluated_matches = []
    for f in CURRENT_FIXTURES:
        nb_res = calculate_negative_binomial_probabilities(f['home_xg'], f['away_xg'])
        evaluated_matches.append({
            "match": f['match'],
            "competition": f['competition'],
            "selection": f['selection'],
            "odds": f['odds'],
            "model_prob": f"{round(nb_res['home_win'] * 100, 1)}%"
        })
    
    joint_prob = run_monte_carlo_accumulator(CURRENT_FIXTURES, simulations=1000)

    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>EDGEMETRIX V15.0 PRO</title>
        <style>
            body { background-color: #0f172a; color: #f8fafc; font-family: monospace; padding: 20px; }
            h1 { color: #38bdf8; text-transform: uppercase; letter-spacing: 2px; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; background: #1e293b; }
            th, td { padding: 12px; border: 1px solid #334155; text-align: left; }
            th { background: #0284c7; color: white; }
            .badge { background: #22c55e; color: black; padding: 4px 8px; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>EDGEMETRIX V15.0 PRO ? SYNNDICATE DASHBOARD</h1>
        <p>Status: <span class="badge">ACTIVE PRODUCTION MODE</span></p>
        <hr style="border-color: #334155;">
        <h2>Live Automated Accumulator Slate</h2>
        <table>
            <tr>
                <th>Match</th>
                <th>Competition</th>
                <th>Selection</th>
                <th>Odds</th>
                <th>Model Prob</th>
            </tr>
            {% for m in matches %}
            <tr>
                <td>{{ m.match }}</td>
                <td>{{ m.competition }}</td>
                <td>{{ m.selection }}</td>
                <td>{{ m.odds }}</td>
                <td>{{ m.model_prob }}</td>
            </tr>
            {% endfor %}
        </table>
        <p style="margin-top: 20px;"><strong>Monte Carlo Joint Probability:</strong> {{ (joint_prob * 100) | round(1) }}% | <strong>Status:</strong> LOCK & STACK</p>
    </body>
    </html>
    """
    return render_template_string(html_template, matches=evaluated_matches, joint_prob=joint_prob)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
