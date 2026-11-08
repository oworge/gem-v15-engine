# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import csv, os
from models import calculate_million_target_progress
from api import fetch_live_global_fixtures

app = Flask(__name__)

LEDGER_FILE = "bankroll_ledger.csv"
FOOTBALL_DATA_KEY = os.environ.get("FOOTBALL_DATA_KEY", "e10a0006eda94810a953a275036a7654")
API_URL = "https://api.football-data.org/v4/matches"

MARKET_OPTIONS = [
    "All Markets", "Over 1.5 Goals", "Over 2.5 Goals", 
    "BTTS - Yes", "Home Win", "Away Win", "Under 2.5 Goals", "Double Chance"
]

def init_ledger():
    if not os.path.exists(LEDGER_FILE):
        with open(LEDGER_FILE, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "Fixture", "Market", "Odds", "EV_%", "Kelly_Stake_%", "Result"])

def log_trade(fixture, market, odds, ev, stake):
    init_ledger()
    with open(LEDGER_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), fixture, market, odds, ev, stake, "PENDING"])

@app.route("/")
def index():
    tab = request.args.get("tab", "accagenerator")
    bankroll = float(request.args.get("bankroll", 1000.0))
    acca_legs = min(10, max(2, int(request.args.get("legs", 4))))
    selected_market = request.args.get("market_filter", "All Markets")
    
    slate = fetch_live_global_fixtures(bankroll, FOOTBALL_DATA_KEY, API_URL)

    if selected_market != "All Markets":
        filtered_pool = [f for f in slate if selected_market.lower() in f["market"].lower()]
    else:
        filtered_pool = slate

    if len(filtered_pool) < acca_legs:
        filtered_pool = slate

    current_acca = filtered_pool[:acca_legs]
    
    try:
        combined_odds = 1.0
        for item in current_acca:
            combined_odds *= item["odds"]
        combined_odds = round(combined_odds, 2)
    except Exception:
        combined_odds = 1.0

    progress_pct, cycles_left = calculate_million_target_progress(bankroll)

    return render_template(
        "index.html",
        active_tab=tab,
        slate=slate,
        current_acca=current_acca,
        acca_legs=acca_legs,
        selected_market=selected_market,
        market_options=MARKET_OPTIONS,
        combined_odds=combined_odds,
        bankroll=bankroll,
        progress_pct=progress_pct,
        cycles_left=cycles_left
    )

@app.route("/submit_acca", methods=["POST"])
def submit_acca():
    summary_fixture = request.form.get("summary_fixture", "Custom Accumulator")
    summary_market = request.form.get("summary_market", "Multi-Leg Acca")
    odds = float(request.form.get("combined_odds", 1.0))
    stake_pct = request.form.get("stake_pct", "2.0%")
    
    log_trade(summary_fixture, summary_market, odds, "+12.5%", stake_pct)
    return redirect(url_for("index", tab="accagenerator", submitted="true"))

if __name__ == "__main__":
    init_ledger()
    app.run(debug=True, host="0.0.0.0", port=5000)
