import sqlite3, json, math, os, datetime

WEIGHTS_FILE = "engine_weights.json"
EVO_LOG_FILE = "evolution_log.json"

DEFAULT_GENOME = {
    "generation": 1,
    "mod_weight_base": 0.40,
    "home_adv_scale": 1.00,
    "rho_offset": 0.00,
    "alpha_scale": 1.00,
    "min_ev_pct": 4.5,
    "best_brier": 0.2500,
    "sample_size": 0
}

def load_genome():
    if os.path.exists(WEIGHTS_FILE):
        try:
            g = json.load(open(WEIGHTS_FILE, encoding="utf-8"))
            merged = dict(DEFAULT_GENOME)
            merged.update(g)
            return merged
        except Exception:
            pass
    return dict(DEFAULT_GENOME)

def _collect_settled():
    rows = []
    for db in ("syndicate_ledger.db", "clv_audit.db", "edgemetrix_history.db"):
        if not os.path.exists(db): continue
        c = sqlite3.connect(db)
        for (tb,) in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall():
            cols = [r[1] for r in c.execute(f"PRAGMA table_info({tb})").fetchall()]
            if "status" in cols or "is_correct" in cols:
                for r in c.execute(f"SELECT * FROM {tb} ORDER BY rowid ASC").fetchall():
                    d = dict(zip(cols, r))
                    st = str(d.get("status", "")).upper()
                    won = 1 if st == "WON" or d.get("is_correct") == 1 else (0 if st == "LOST" or d.get("is_correct") == 0 else None)
                    if won is not None:
                        odds = max(1.05, float(d.get("odds") or d.get("price") or 1.90))
                        prob = float(str(d.get("true_prob") or d.get("win_prob") or d.get("confidence") or 0.58).replace("%", ""))
                        if prob > 1.0: prob /= 100.0
                        rows.append({"won": won, "odds": odds, "prob": max(0.05, min(0.95, prob)), "mkt_p": min(0.95, 1.0 / odds)})
        c.close()
    return rows

def _logit_blend(mkt_p, mod_p, w):
    mp = max(0.02, min(0.98, mkt_p))
    dp = max(0.02, min(0.98, mod_p))
    z = (1.0 - w) * math.log(mp / (1.0 - mp)) + w * math.log(dp / (1.0 - dp))
    return 1.0 / (1.0 + math.exp(-z))

def run_evolution_cycle():
    genome = load_genome()
    settled = _collect_settled()
    n = len(settled)
    if n < 25:
        genome["sample_size"] = n
        json.dump(genome, open(WEIGHTS_FILE, "w", encoding="utf-8"), indent=2)
        return {"status": "ACCUMULATING_DATA", "settled_count": n, "needed": 25 - n, "genome": genome}

    best_w = genome["mod_weight_base"]
    best_brier = 999.0
    for cand_w in [0.25, 0.30, 0.35, 0.40, 0.45]:
        brier = sum((_logit_blend(r["mkt_p"], r["prob"], cand_w) - r["won"]) ** 2 for r in settled) / n
        if brier < best_brier:
            best_brier = brier
            best_w = cand_w

    step_w = round(genome["mod_weight_base"] + 0.10 * (best_w - genome["mod_weight_base"]), 4)
    prev_brier = float(genome.get("best_brier", 0.25))

    if n > genome.get("sample_size", 0) + 15 and best_brier > prev_brier + 0.015:
        action = "ROLLBACK_GUARD_TRIGGERED"
        genome["min_ev_pct"] = min(6.0, round(genome["min_ev_pct"] + 0.25, 2))
    else:
        action = "EVOLVED_GENERATION"
        genome["generation"] = int(genome.get("generation", 1)) + 1
        genome["mod_weight_base"] = step_w
        genome["best_brier"] = round(best_brier, 4)
        genome["sample_size"] = n
        if best_brier < 0.215:
            genome["min_ev_pct"] = max(4.5, round(genome["min_ev_pct"] - 0.10, 2))

    json.dump(genome, open(WEIGHTS_FILE, "w", encoding="utf-8"), indent=2)
    log = json.load(open(EVO_LOG_FILE, encoding="utf-8")) if os.path.exists(EVO_LOG_FILE) else []
    log.append({"ts": datetime.datetime.utcnow().isoformat() + "Z", "action": action, "genome": genome})
    json.dump(log[-50:], open(EVO_LOG_FILE, "w", encoding="utf-8"), indent=2)
    return {"status": action, "genome": genome}

if __name__ == "__main__":
    print(json.dumps(run_evolution_cycle(), indent=2))
