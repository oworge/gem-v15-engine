import pathlib, sqlite3, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import learner

def test_compute_clv_summary_math():
    tmp_db = pathlib.Path(tempfile.gettempdir()) / "gem_clv_regression.db"
    if tmp_db.exists():
        tmp_db.unlink()
    orig_db = learner.DB_PATH
    try:
        learner.DB_PATH = str(tmp_db)
        conn = sqlite3.connect(tmp_db)
        conn.execute(
            "CREATE TABLE odds_snapshots (fixture TEXT, market TEXT, open_odds REAL, last_odds REAL, updated_at TEXT, PRIMARY KEY (fixture, market))"
        )
        conn.executemany(
            "INSERT INTO odds_snapshots (fixture, market, open_odds, last_odds, updated_at) VALUES (?, ?, ?, ?, ?)",
            [
                ("Team A v Team B", "Home Win", 2.10, 1.90, "2026-11-20T18:00:00Z"),
                ("Team C v Team D", "Over 2.5", 1.80, 1.95, "2026-11-20T18:05:00Z"),
            ],
        )
        conn.commit()
        conn.close()

        res = learner.compute_clv_summary()
        assert res["tracked"] == 2
        assert res["avg_clv_pct"] == 1.42
        assert res["beat_close_rate"] == 50.0
    finally:
        learner.DB_PATH = orig_db
        if tmp_db.exists():
            tmp_db.unlink()

if __name__ == "__main__":
    test_compute_clv_summary_math()
    print("OK: test_clv_summary.py")
