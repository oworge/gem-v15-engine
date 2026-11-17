import json, math, os, sqlite3

WEIGHTS_FILE = "model_weights.json"
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
    for db in ("syndicate_ledger.db", "clv_audit.db"):
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

    if len(outcomes) >= 8:
        brier = sum((p - y) ** 2 for p, y, _ in outcomes) / len(outcomes)
        avg_pred = sum(p for p, _, _ in outcomes) / len(outcomes)
        avg_hit = sum(y for _, y, _ in outcomes) / len(outcomes)
        w["last_brier"] = round(brier, 4)
        w["last_sample"] = len(outcomes)
        if (avg_pred - avg_hit) > 0.04 or brier > 0.225:
            w["market_weight"] = round(min(0.78, w["market_weight"] + 0.025), 3)
            w["dc_weight"] = round(1.0 - w["market_weight"], 3)
            w["min_ev_pct"] = round(min(5.2, w["min_ev_pct"] + 0.2), 2)
        for fam in ("1X2", "COMBO", "TOTALS", "BTTS"):
            sub = [(p, y) for p, y, f in outcomes if f == fam]
            if len(sub) >= 5:
                err = (sum(y for _, y in sub) / len(sub)) - (sum(p for p, _ in sub) / len(sub))
                cur = w["platt"].get(fam, {"a": 0.93, "b": -0.03})
                cur["b"] = round(max(-0.35, min(0.25, cur["b"] + err * 0.4)), 4)
                if err < -0.05:
                    cur["a"] = round(max(0.75, cur["a"] - 0.02), 4)
                w["platt"][fam] = cur
        save_weights(w)
    return w
