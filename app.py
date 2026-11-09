import os
from flask import Flask, render_template, request

app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    active_tab = request.args.get('tab', 'dailypicks')
    daily_picks = [
        {'match': 'Arsenal vs Chelsea', 'league': 'Premier League', 'market': 'Home Win', 'odds': '1.85', 'ev': '+8.4%'}
    ]
    btts_slate = [
        {'match': 'Torreense vs Uniao de Leiria', 'league': 'Liga Portugal 2', 'market': 'BTTS - Yes', 'odds': '1.78'}
    ]
    acca_legs = [
        {'match': 'Arsenal vs Chelsea', 'market': 'Home Win', 'odds': '1.85'}
    ]
    return render_template('index.html', active_tab=active_tab, daily_picks=daily_picks, btts_slate=btts_slate, acca_legs=acca_legs)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
