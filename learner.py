import sqlite3
import json
import os
from datetime import datetime

WEIGHTS_FILE = 'engine_weights.json'
DEFAULT_WEIGHTS = {
    "market_weight": 0.60,
    "dc_weight": 0.40,
    "dc_rho": -0.13,
    "min_ev_pct": 3.0,
    "max_vig_pct": 7.5,
    "min_win_prob": 0.54,
    "kelly_fraction": 0.25,
    "max_stake_pct": 3.0,
    "brier_shrinkage": 0.08
}

def load_weights():
    if os.path.exists(WEIGHTS_FILE):
        try:
            data = json.load(open(WEIGHTS_FILE, 'r', encoding='utf-8'))
            merged = dict(DEFAULT_WEIGHTS)
            merged.update(data)
            return merged
        except Exception:
            pass
    save_weights(DEFAULT_WEIGHTS)
    return dict(DEFAULT_WEIGHTS)

def save_weights(weights):
    with open(WEIGHTS_FILE, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(weights, f, indent=2)

def audit_and_calibrate():
    w = load_weights()
    outcomes = []
    for db in ('syndicate_ledger.db', 'clv_audit.db'):
        if not os.path.exists(db):
            continue
        c = sqlite3.connect(db)
        for (t,) in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall():
            cols = [r[1] for r in c.execute(f"PRAGMA table_info({t})").fetchall()]
            if 'status' in cols:
                for row in c.execute(f"SELECT * FROM {t} WHERE UPPER(status) IN ('WON','LOST') ORDER BY rowid DESC LIMIT 60").fetchall():
                    d = dict(zip(cols, row))
                    y = 1.0 if str(d.get('status','')).upper() == 'WON' else 0.0
                    p_raw = d.get('true_prob') or d.get('win_prob') or d.get('model_prob') or d.get('prob') or 0.65
                    p = float(str(p_raw).replace('%',''))
                    if p > 1.0:
                        p /= 100.0
                    outcomes.append((min(0.95, max(0.05, p)), y))
        c.close()

    if len(outcomes) >= 8:
        brier = sum((p - y) ** 2 for p, y in outcomes) / len(outcomes)
        avg_pred = sum(p for p, _ in outcomes) / len(outcomes)
        avg_hit = sum(y for _, y in outcomes) / len(outcomes)
        # If overconfident (predicted > actual hit rate), lean harder into sharp market consensus
        if (avg_pred - avg_hit) > 0.05 or brier > 0.23:
            w['market_weight'] = round(min(0.75, w['market_weight'] + 0.03), 3)
            w['dc_weight'] = round(1.0 - w['market_weight'], 3)
            w['min_ev_pct'] = round(min(5.0, w['min_ev_pct'] + 0.25), 2)
            save_weights(w)
    return w
