import sqlite3
import json
import os
from datetime import datetime

DB_FILE = 'edgemetrix_history.db'
WEIGHTS_FILE = 'engine_weights.json'

# Default feature weights if none are optimized yet
DEFAULT_WEIGHTS = {
    "form_weight": 0.40,
    "xg_weight": 0.30,
    "h2h_weight": 0.15,
    "home_advantage": 0.15
}

def init_engine_db():
    """Initializes the SQLite database for tracking predictions and outcomes."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            match_id TEXT PRIMARY KEY,
            fixture_date TEXT,
            home_team TEXT,
            away_team TEXT,
            predicted_outcome TEXT,
            confidence REAL,
            weights_snapshot TEXT,
            actual_result TEXT DEFAULT NULL,
            is_correct INTEGER DEFAULT NULL,
            audited_at TEXT DEFAULT NULL
        )
    ''')
    conn.commit()
    conn.close()
    
    # Initialize weights file if it doesn't exist
    if not os.path.exists(WEIGHTS_FILE):
        save_weights(DEFAULT_WEIGHTS)

def load_weights():
    """Loads the current active feature weights for the prediction model."""
    if os.path.exists(WEIGHTS_FILE):
        with open(WEIGHTS_FILE, 'r') as f:
            return json.load(f)
    return DEFAULT_WEIGHTS

def save_weights(weights):
    """Saves updated weights to disk."""
    with open(WEIGHTS_FILE, 'w') as f:
        json.dump(weights, f, indent=4)

def log_prediction(match_id, home, away, predicted_outcome, confidence):
    """Logs a new prediction to memory with the weights active at that moment."""
    init_engine_db()
    current_weights = load_weights()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR IGNORE INTO predictions 
        (match_id, fixture_date, home_team, away_team, predicted_outcome, confidence, weights_snapshot)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        str(match_id), 
        datetime.utcnow().strftime('%Y-%m-%d'), 
        home, 
        away, 
        predicted_outcome, 
        confidence, 
        json.dumps(current_weights)
    ))
    conn.commit()
    conn.close()

def audit_and_evolve(fetch_result_func):
    """
    Audits past pending predictions against real results and adjusts weights 
    based on historical accuracy trends.
    """
    init_engine_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT match_id, predicted_outcome FROM predictions WHERE actual_result IS NULL")
    pending = cursor.fetchall()
    
    audited_count = 0
    for match_id, predicted in pending:
        # fetch_result_func should query your external API for the match status & winner ('HOME', 'AWAY', 'DRAW')
        result_data = fetch_result_func(match_id)
        
        if result_data and result_data.get('status') in ['FT', 'AET', 'PEN']:
            actual = result_data.get('winner')
            is_correct = 1 if predicted == actual else 0
            
            cursor.execute('''
                UPDATE predictions 
                SET actual_result = ?, is_correct = ?, audited_at = ?
                WHERE match_id = ?
            ''', (actual, is_correct, datetime.utcnow().isoformat(), match_id))
            audited_count += 1
            
    conn.commit()
    conn.close()
    
    if audited_count > 0:
        optimize_weights_from_history()

def optimize_weights_from_history():
    """
    Analyzes historical performance and performs a micro-adjustment 
    to weights to favor metrics that are performing better.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Get last 50 audited predictions
    cursor.execute("SELECT is_correct, weights_snapshot FROM predictions WHERE is_correct IS NOT NULL ORDER BY audited_at DESC LIMIT 50")
    history = cursor.fetchall()
    conn.close()
    
    if len(history) < 10:
        return # Need a small sample size before shifting weights
        
    weights = load_weights()
    
    # Calculate rolling accuracy
    correct_count = sum([row[0] for row in history])
    accuracy = correct_count / len(history)
    
    # Adaptive tuning mechanism: 
    # If accuracy drops below 60%, introduce a slight variance/rebalance toward xG and recent form
    if accuracy < 0.60:
        weights["xg_weight"] = min(0.50, weights["xg_weight"] + 0.02)
        weights["form_weight"] = max(0.20, weights["form_weight"] - 0.02)
        save_weights(weights)
from learner import log_prediction, audit_and_evolve, load_weights

# Inside your route where predictions/slips are generated:
@app.route('/generate-slip', methods=['POST'])
def generate_slip():
    # ... your prediction logic using active weights ...
    active_weights = load_weights()
    
    # Example logging loop for each match included in the slip
    for match in selected_matches:
        log_prediction(
            match_id=match['id'],
            home=match['home_team'],
            away=match['away_team'],
            predicted_outcome=match['prediction'],
            confidence=match['confidence']
        )
    
    return render_template('slip.html', matches=selected_matches)

# Optional: Trigger an audit check whenever the dashboard loads or via background cron
@app.before_first_request
def run_background_audit():
    try:
        # Pass your existing API fetching function here
        audit_and_evolve(fetch_match_result_from_api)
    except Exception as e:
        print(f"Audit routine skipped: {e}")