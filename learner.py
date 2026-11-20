import sqlite3


import os as _os
from pathlib import Path as _Path
DATA_DIR = _Path(_os.environ.get("GEM_DATA_DIR", "/var/data" if _os.path.isdir("/var/data") else "."))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = str(DATA_DIR / "syndicate_ledger.db")
WEIGHTS_PATH = str(DATA_DIR / "model_weights.json")
import json, math, os, sqlite3

WEIGHTS_FILE = WEIGHTS_PATH
DEFAULT_WEIGHTS = {
    "dc_weight": 0.42,
    "market_weight": 0.58,
    "min_ev_pct": 4.2,
    "platt": {
        "1X2": {"a": 0.92, "b": -0.04},
        "COMBO": {"a": 0.94, "b": -0.03},
        "TOTALS": {"a": 0.91, "b": -0.02},
        "BTTS": {"a": 0.90, "b": -0.03}
    }
}

def load_weights():
    if os.path.exists(WEIGHTS_FILE):
        try:
            d = json.load(open(WEIGHTS_FILE, encoding="utf-8"))
            for k, v in DEFAULT_WEIGHTS.items():
                if k not in d:
                    d[k] = v
            return d
        except Exception:
            pass
    save_weights(DEFAULT_WEIGHTS)
    return dict(DEFAULT_WEIGHTS)

def save_weights(weights):
    with open(WEIGHTS_FILE, "w", encoding="utf-8", newline="\n") as f:
        json.dump(weights, f, indent=2)

def platt_calibrate(p, market_family="1X2", weights=None):
    w = weights or load_weights()
    params = w.get("platt", {}).get(market_family, {"a": 0.93, "b": -0.03})
    p_c = min(0.985, max(0.015, float(p)))
    logit = math.log(p_c / (1.0 - p_c))
    z = params["a"] * logit + params["b"]
    return round(1.0 / (1.0 + math.exp(-max(-12.0, min(12.0, z)))), 4)

def audit_and_calibrate():
    w = load_weights()
    outcomes = []
    for db in (DB_PATH, "clv_audit.db"):
        if not os.path.exists(db):
            continue
        c = sqlite3.connect(db)
        for (t,) in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall():
            cols = [r[1] for r in c.execute(f"PRAGMA table_info({t})").fetchall()]
            if "status" in cols:
                for row in c.execute(f"SELECT * FROM {t} WHERE UPPER(status) IN ('WON','LOST') ORDER BY rowid DESC LIMIT 100").fetchall():
                    d = dict(zip(cols, row))
                    y = 1.0 if str(d.get("status", "")).upper() == "WON" else 0.0
                    p_raw = d.get("true_prob") or d.get("win_prob") or d.get("model_prob") or d.get("prob") or 0.62
                    p = float(str(p_raw).replace("%", ""))
                    if p > 1.0:
                        p /= 100.0
                    mkt = str(d.get("market") or d.get("selection") or "1X2").upper()
                    fam = "COMBO" if ("1X" in mkt or "X2" in mkt or "O1.5" in mkt) else ("BTTS" if "BTTS" in mkt else ("TOTALS" if "OVER" in mkt or "UNDER" in mkt else "1X2"))
                    outcomes.append((min(0.95, max(0.05, p)), y, fam))
        c.close()

    if len(outcomes) >= 4:
        brier = sum((p - y) ** 2 for p, y, _ in outcomes) / len(outcomes)
        logloss = -sum(y * math.log(max(1e-6, p)) + (1.0 - y) * math.log(max(1e-6, 1.0 - p)) for p, y, _ in outcomes) / len(outcomes)
        avg_pred = sum(p for p, _, _ in outcomes) / len(outcomes)
        avg_hit = sum(y for _, y, _ in outcomes) / len(outcomes)
        w["last_brier"] = round(brier, 4)
        w["last_logloss"] = round(logloss, 4)
        w["last_sample"] = len(outcomes)
        w["realized_hit_rate"] = round(avg_hit, 4)

        # Bidirectional calibration: penalize overconfidence, reward verified outperformance
        if (avg_pred - avg_hit) > 0.04 or brier > 0.225:
            w["market_weight"] = round(min(0.78, w["market_weight"] + 0.025), 3)
            w["dc_weight"] = round(1.0 - w["market_weight"], 3)
            w["min_ev_pct"] = round(min(5.5, w["min_ev_pct"] + 0.2), 2)
        elif (avg_hit - avg_pred) > 0.05 and brier < 0.215:
            w["market_weight"] = round(max(0.48, w["market_weight"] - 0.015), 3)
            w["dc_weight"] = round(1.0 - w["market_weight"], 3)
            w["min_ev_pct"] = round(max(4.0, w["min_ev_pct"] - 0.1), 2)

        for fam in ("1X2", "COMBO", "TOTALS", "BTTS"):
            sub = [(p, y) for p, y, f in outcomes if f == fam]
            if len(sub) >= 3:
                err = (sum(y for _, y in sub) / len(sub)) - (sum(p for p, _ in sub) / len(sub))
                cur = w["platt"].get(fam, {"a": 0.93, "b": -0.03})
                cur["b"] = round(max(-0.35, min(0.25, cur["b"] + err * 0.35)), 4)
                if err < -0.05:
                    cur["a"] = round(max(0.75, cur["a"] - 0.02), 4)
                elif err > 0.06:
                    cur["a"] = round(min(1.04, cur["a"] + 0.01), 4)
                w["platt"][fam] = cur
        w.setdefault("dc_by_market", {"1X2": w["dc_weight"], "COMBO": w["dc_weight"], "TOTALS": round(min(0.55, w["dc_weight"] + 0.04), 3), "BTTS": round(min(0.55, w["dc_weight"] + 0.03), 3)})
        save_weights(w)
    return w


def track_line_velocity(fixture, market, current_odds):
    try:
        c = sqlite3.connect(DB_PATH)
        c.execute("CREATE TABLE IF NOT EXISTS odds_snapshots (fixture TEXT, market TEXT, open_odds REAL, last_odds REAL, updated_at TEXT, PRIMARY KEY (fixture, market))")
        row = c.execute("SELECT open_odds FROM odds_snapshots WHERE fixture=? AND market=?", (fixture, market)).fetchone()
        now_s = datetime.now(timezone.utc).isoformat() if "datetime" in globals() else ""
        if not row:
            c.execute("INSERT INTO odds_snapshots VALUES (?, ?, ?, ?, ?)", (fixture, market, float(current_odds), float(current_odds), now_s))
            c.commit(); c.close()
            return 0.0
        open_od = float(row[0])
        c.execute("UPDATE odds_snapshots SET last_odds=?, updated_at=? WHERE fixture=? AND market=?", (float(current_odds), now_s, fixture, market))
        c.commit(); c.close()
        return round(((1.0 / max(1.02, float(current_odds))) - (1.0 / max(1.02, open_od))) * 100.0, 2)
    except Exception:
        return 0.0


def compute_clv_summary():
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS odds_snapshots (
                fixture TEXT,
                market TEXT,
                open_odds REAL,
                last_odds REAL,
                updated_at TEXT,
                PRIMARY KEY (fixture, market)
            )
        """)
        cols = [r[1] for r in cur.execute("PRAGMA table_info(odds_snapshots)").fetchall()]
        if "last_odds" not in cols:
            cur.execute("ALTER TABLE odds_snapshots ADD COLUMN last_odds REAL")
            if "curr_odds" in cols:
                cur.execute("UPDATE odds_snapshots SET last_odds = curr_odds WHERE last_odds IS NULL")
        rows = cur.execute(
            "SELECT fixture, market, open_odds, last_odds FROM odds_snapshots WHERE open_odds > 1.01 AND last_odds > 1.01"
        ).fetchall()
        conn.close()
        if not rows:
            return {"tracked": 0, "avg_clv_pct": 0.0, "beat_close_rate": 0.0}
        clvs = [(((1.0 / float(r[3])) / (1.0 / float(r[2]))) - 1.0) * 100.0 for r in rows]
        beats = sum(1 for c in clvs if c > 0)
        return {
            "tracked": len(clvs),
            "avg_clv_pct": round(sum(clvs) / len(clvs), 2),
            "beat_close_rate": round((beats / len(clvs)) * 100.0, 1)
        }
    except Exception as exc:
        return {"tracked": 0, "avg_clv_pct": 0.0, "beat_close_rate": 0.0, "err": str(exc)}

