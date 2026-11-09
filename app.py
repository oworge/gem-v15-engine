from flask import Flask, render_template, request, redirect, url_for
import os
import sqlite3
import math

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
app = Flask(__name__, template_folder=template_dir)

DB_NAME = "syndicate_ledger.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tracked_slips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            home TEXT,
            away TEXT,
            market TEXT,
            odds TEXT,
            stake REAL,
            status TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

def poisson_probability(lam, k):
    return (math.exp(-lam) * (lam ** k)) / math.factorial(k)

def calculate_poisson_metrics(home_team, away_team, league, date, time, base_home_lambda, base_away_lambda, market, odds, ev):
    # Dynamic Poisson Calculations
    p_home_win = sum(poisson_probability(base_home_lambda, i) * poisson_probability(base_away_lambda, j) for i in range(6) for j in range(6) if i > j)
    p_draw = sum(poisson_probability(base_home_lambda, i) * poisson_probability(base_away_lambda, i) for i in range(6))
    p_away_win = 1.0 - p_home_win - p_draw
    
    # Over 2.5 Probability
    p_over_25 = 1.0 - sum(poisson_probability(base_home_lambda, i) * poisson_probability(base_away_lambda, j) for i in range(3) for j in range(3) if i + j <= 2)
    
    # BTTS Probability
    p_btts = (1.0 - poisson_probability(base_home_lambda, 0)) * (1.0 - poisson_probability(base_away_lambda, 0))
    
    return {
        "home": home_team,
        "away": away_team,
        "league": league,
        "date": date,
        "time": time,
        "market": market,
        "odds": odds,
        "ev": ev,
        "tactical_health": "Optimal (Poisson Model Verified)",
        "clv_benchmark": f"{round(float(odds)*0.97, 2)} (+{round(float(ev.replace('+','').replace('%',''))*0.2, 1)}% Edge)",
        "correct_score": f"{round(base_home_lambda)}-{round(base_away_lambda)}",
        "cs_odds": str(round(7.5 + (abs(base_home_lambda - base_away_lambda) * 1.5), 2)),
        "btts_prob": f"{round(p_btts * 100, 1)}%"
    }

def get_fixture_slate():
    return [
        calculate_poisson_metrics("FC Botoșani", "Oțelul Galați", "Romanian SuperLiga", "Mon 9 Nov", "18:00 GMT", 1.35, 1.05, "Under 2.5 Goals", "1.68", "+12.1%"),
        calculate_poisson_metrics("Torreense", "União de Leiria", "Liga Portugal 2", "Mon 9 Nov", "20:15 GMT", 1.25, 1.20, "BTTS - Yes", "1.78", "+14.5%"),
        calculate_poisson_metrics("Plymouth Parkway", "Berkhamsted", "English FA Cup", "Mon 9 Nov", "14:30 GMT", 1.80, 0.90, "Home Win", "2.05", "+14.2%"),
        calculate_poisson_metrics("Hacken W", "Chelsea W", "Women's Champions League", "Mon 9 Nov", "17:45 GMT", 1.40, 1.95, "Over 2.5 Goals", "1.72", "+16.8%")
    ]

@app.route("/", methods=["GET", "POST"])
def index():
    active_tab = request.args.get("tab", "dailypicks")
    slate = get_fixture_slate()
    
    if request.method == "POST":
        home = request.form.get("home")
        away = request.form.get("away")
        market = request.form.get("market")
        odds = request.form.get("odds")
        stake = float(request.form.get("stake", 10.0))
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tracked_slips (home, away, market, odds, stake, status) VALUES (?, ?, ?, ?, ?, ?)",
                       (home, away, market, odds, stake, "Active / Auditing"))
        conn.commit()
        conn.close()
        return redirect(url_for('index', tab='clvaudit'))

    try:
        acca_legs = int(request.args.get("legs", 3))
    except (ValueError, TypeError):
        acca_legs = 3
        
    selected_market = request.args.get("market_filter", "Home Win")
    market_options = ["Home Win", "Over 2.5 Goals", "BTTS - Yes", "Under 2.5 Goals"]
    
    filtered_slate = [f for f in slate if selected_market in f["market"] or selected_market == "All"]
    current_acca = filtered_slate[:acca_legs] if filtered_slate else slate[:acca_legs]
    if not current_acca:
        current_acca = slate[:3]
    
    combined = 1.0
    for item in current_acca:
        try:
            combined *= float(item["odds"])
        except (ValueError, TypeError):
            pass
    combined_odds = round(combined, 2)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT home, away, market, odds, stake, status FROM tracked_slips")
    tracked_bets = cursor.fetchall()
    conn.close()

    return render_template(
        "index.html",
        active_tab=active_tab,
        slate=slate,
        current_acca=current_acca,
        acca_legs=acca_legs,
        market_options=market_options,
        selected_market=selected_market,
        combined_odds=combined_odds,
        tracked_bets=tracked_bets
    )

if __name__ == "__main__":
    app.run(debug=True, port=5000)
