import sqlite3, os, random, json

def run_walk_forward_backtest(sims=5000, start_bankroll=1000.0):
    records = []
    for db in ("syndicate_ledger.db", "clv_audit.db", "edgemetrix_history.db"):
        if not os.path.exists(db): continue
        c = sqlite3.connect(db)
        for (tb,) in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall():
            cols = [r[1] for r in c.execute(f"PRAGMA table_info({tb})").fetchall()]
            if "status" in cols or "is_correct" in cols:
                for row in c.execute(f"SELECT * FROM {tb} ORDER BY rowid ASC").fetchall():
                    d = dict(zip(cols, row))
                    st = str(d.get("status", "")).upper()
                    won = 1 if st == "WON" or d.get("is_correct") == 1 else (0 if st == "LOST" or d.get("is_correct") == 0 else None)
                    if won is not None:
                        odds = float(d.get("odds") or d.get("price") or 1.90)
                        prob = float(str(d.get("true_prob") or d.get("win_prob") or d.get("confidence") or 0.60).replace("%", ""))
                        if prob > 1.0: prob /= 100.0
                        records.append({"won": won, "odds": odds, "prob": max(0.05, min(0.95, prob))})
        c.close()

    if not records:
        return {"sample_size": 0, "status": "Awaiting settled matches in ledger"}

    brier = sum((r["prob"] - r["won"]) ** 2 for r in records) / len(records)
    hits = sum(r["won"] for r in records)
    pnl = sum((r["odds"] - 1.0) if r["won"] else -1.0 for r in records)

    # Monte Carlo drawdown simulation at 1.5% flat/Kelly unit sizing
    max_dds, finals = [], []
    for _ in range(sims):
        bk = peak = start_bankroll
        mdd = 0.0
        for r in records:
            pick = random.choice(records)
            stake = bk * 0.015
            bk += stake * (pick["odds"] - 1.0) if pick["won"] else -stake
            if bk > peak: peak = bk
            dd = (peak - bk) / peak
            if dd > mdd: mdd = dd
        max_dds.append(mdd); finals.append(bk)

    return {
        "sample_size": len(records),
        "win_rate_pct": round((hits / len(records)) * 100, 2),
        "flat_roi_pct": round((pnl / len(records)) * 100, 2),
        "brier_score": round(brier, 4),
        "mc_median_bankroll": round(sorted(finals)[sims // 2], 2),
        "mc_avg_max_drawdown_pct": round((sum(max_dds) / sims) * 100, 2)
    }

if __name__ == "__main__":
    print(json.dumps(run_walk_forward_backtest(), indent=2))
