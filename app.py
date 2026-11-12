import math
import random
from flask import Flask, render_template_string

app = Flask(__name__)

# Original fixture view configuration
CURRENT_FIXTURES = [
    {"match": "Turkiye vs. Belgium", "competition": "UEFA Nations League", "selection": "Over 1.5 Goals", "odds": "3/4 (1.75)"},
    {"match": "England vs. Croatia", "competition": "UEFA Nations League", "selection": "England (Double Chance 1X)", "odds": "1/14 (1.07)"},
    {"match": "Italy vs. France", "competition": "UEFA Nations League", "selection": "Over 1.5 Goals", "odds": "4/5 (1.80)"}
]

@app.route('/')
def dashboard():
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
        <h1>EDGEMETRIX V15.0 PRO</h1>
        <p>Status: <span class="badge">ACTIVE</span></p>
        <hr style="border-color: #334155;">
        <h2>Live Slate</h2>
        <table>
            <tr>
                <th>Match</th>
                <th>Competition</th>
                <th>Selection</th>
                <th>Odds</th>
            </tr>
            {% for m in matches %}
            <tr>
                <td>{{ m.match }}</td>
                <td>{{ m.competition }}</td>
                <td>{{ m.selection }}</td>
                <td>{{ m.odds }}</td>
            </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """
    return render_template_string(html_template, matches=CURRENT_FIXTURES)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
