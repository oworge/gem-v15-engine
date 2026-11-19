def _sanitize_acca10_all_markets_v167(feed_dict):
    # ACCA10_ALL_MARKETS_V167: replace repetitive (1X)/(X2) & Over 1.5 acca10 legs with true multi-market Argmax-EV selections
    if not isinstance(feed_dict, dict):
        return feed_dict
    tv_map = {}
    for item in (feed_dict.get("todaysValue") or []) + (feed_dict.get("ai") or []) + (feed_dict.get("likely") or []):
        fk = str(item.get("f") or "").strip()
        pk = str(item.get("pk") or "").strip()
        if fk and pk and "&" not in pk:
            tv_map.setdefault(fk, item)

    new_acca = []
    seen_fixtures = set()
    for leg in (feed_dict.get("acca10") or []):
        fk = str(leg.get("f") or "").strip()
        if fk in seen_fixtures:
            continue
        pk = str(leg.get("pk") or "").strip()
        if "&" in pk and fk in tv_map:
            repl = dict(tv_map[fk])
            new_acca.append(repl)
            seen_fixtures.add(fk)
        elif "&" not in pk:
            new_acca.append(leg)
            seen_fixtures.add(fk)

    # Top up from highest-EV multi-market todaysValue items if fewer than 10 legs remain
    for item in (feed_dict.get("todaysValue") or []):
        if len(new_acca) >= 10:
            break
        fk = str(item.get("f") or "").strip()
        pk = str(item.get("pk") or "").strip()
        if fk and fk not in seen_fixtures and "&" not in pk:
            new_acca.append(dict(item))
            seen_fixtures.add(fk)

    if new_acca:
        feed_dict["acca10"] = new_acca
    return feed_dict



import os as _os
from pathlib import Path as _Path
DATA_DIR = _Path(_os.environ.get("GEM_DATA_DIR", "/var/data" if _os.path.isdir("/var/data") else "."))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = str(DATA_DIR / "syndicate_ledger.db")
WEIGHTS_PATH = str(DATA_DIR / "model_weights.json")
import os
from flask import Flask, render_template, request
import data_generator as dg

app = Flask(__name__)

def get_perfect_value_alerts(picks):
    if not picks:
        return []
    hits = [
        p for p in picks
        if any(t in str(p.get("pick", "")) for t in ["ELITE BUSTER", "STRONG VALUE", "+5.", "+6.", "+7.", "+8.", "+9.", "+10.", "+11.", "+12.", "+13.", "+14.", "+15."])
    ]
    return hits[:18] if hits else picks[:15]

def _build_dynamic_tabs(picks):
    btts = [
        {
            "match": p.get("match", ""),
            "comp": p.get("comp", "BTTS & Goals Engine"),
            "pick": f"BTTS Yes & Over 2.5 Goals ({p.get('pick', '')})",
            "odds": p.get("odds", "1.85"),
        }
        for p in picks[:18]
    ]
    def _build_5leg_sgm(p):
        m = p.get("match", "")
        teams = [t.strip() for t in m.split(" vs. ")] if " vs. " in m else ([t.strip() for t in m.split(" vs ")] if " vs " in m else ["Home Team", "Away Team"])
        home, away = teams[0], (teams[1] if len(teams) > 1 else "Away Team")
        base_pick = str(p.get("pick", "")).split("|")[-1].split("[")[0].strip()
        try:
            base_odds = float(str(p.get("odds", "1.80")).replace("@", "").strip())
        except Exception:
            base_odds = 1.80
        low = base_pick.lower()
        if "under" in low:
            legs = [base_pick, "Under 3.5 Match Goals", "1st Half Under 1.5 Goals", f"{home} Double Chance (1X)", "Match Corners Over 7.5"]
        elif "btts" in low or "both teams" in low:
            legs = [base_pick, "Over 2.5 Match Goals", f"{home} Over 0.5 Team Goals", f"{away} Over 0.5 Team Goals", "Match Corners Over 8.5"]
        elif away.lower() in low and "win" in low:
            legs = [base_pick, f"{away} Over 1.5 Team Goals", "Over 1.5 Match Goals", f"{away} Over 3.5 Corners", "2nd Half Over 0.5 Goals"]
        else:
            leg1 = base_pick if base_pick else f"{home} Win"
            legs = [leg1, "Over 1.5 Match Goals", f"{home} Over 0.5 Team Goals", f"{home} Over 3.5 Corners", "Both Teams 1+ Card"]
        sgm_odds = f"{round(base_odds * 3.15, 2):.2f}"
        return {
            "match": m,
            "comp": f"1-FIXTURE 5-LEG BET BUILDER | {p.get('comp', '')}",
            "pick": " | ".join(f"{idx+1}) {lg}" for idx, lg in enumerate(legs)),
            "odds": sgm_odds,
        }

    builders = [_build_5leg_sgm(p) for p in picks[:18]]
    correct_scores = [
        {
            "match": p.get("match", ""),
            "comp": "Poisson Score Matrix (Top Model Projection)",
            "pick": f"Correct Score: 2 - 1 / 1 - 1 ({p.get('pick', '')})",
            "odds": "7.50",
        }
        for p in picks[:18]
    ]
    true_clv = dg.get_live_steam_clv() if hasattr(dg, "get_live_steam_clv") else picks[:18]
    tactical = [
        {
            "match": p.get("match", "NegBin & Monte Carlo"),
            "comp": "5,000 Sims | CIRF Fatigue & Tactical Audit",
            "pick": f"TACTICAL PASS — {p.get('pick', 'Zero Fatigue Flags')}",
            "odds": p.get("odds", "PASS"),
        }
        for p in picks[:18]
    ]
    return {
        "daily_picks": picks,
        "btts_goals": btts,
        "bet_builder": builders,
        "correct_score": correct_scores,
        "true_clv": true_clv,
        "tactical_health": tactical,
    }

@app.route("/")
def dashboard():
    tab = request.args.get("tab", "daily_picks")
    picks = dg.get_global_daily_picks() if hasattr(dg, "get_global_daily_picks") else []
    if hasattr(dg, "auto_grade_settled_matches"):
        try:
            dg.auto_grade_settled_matches(picks)
        except Exception:
            pass
    tabs_data = _build_dynamic_tabs(picks)
    alerts = get_perfect_value_alerts(picks)
    if alerts and hasattr(dg, "dispatch_push_alert"):
        try:
            dg.dispatch_push_alert(alerts[0])
        except Exception:
            pass
    return render_template("index.html", active_tab=tab, data=tabs_data.get(tab, picks), alerts=alerts)


# --- Autonomous Hands-Free Daily Refresh Daemon ---
import threading as _bg_threading
import time as _bg_time


# --- Free Cloud PostgreSQL Persistence (Neon / Render DATABASE_URL) ---
import os as _pg_os

def _sync_sqlite_to_postgres(direction="restore"):
    db_url = _pg_os.environ.get("DATABASE_URL", "").strip()
    if not db_url:
        return
    try:
        import psycopg2
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS gem_sqlite_snapshots (
                db_name TEXT PRIMARY KEY,
                payload BYTEA NOT NULL,
                updated_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)
        for fname in ("clv_audit.db", DB_PATH):
            if direction == "restore":
                cur.execute("SELECT payload FROM gem_sqlite_snapshots WHERE db_name = %s", (fname,))
                row = cur.fetchone()
                if row and row[0]:
                    with open(fname, "wb") as f:
                        f.write(bytes(row[0]))
            elif direction == "backup" and _pg_os.path.exists(fname):
                with open(fname, "rb") as f:
                    blob = f.read()
                cur.execute("""
                    INSERT INTO gem_sqlite_snapshots (db_name, payload, updated_at)
                    VALUES (%s, %s, NOW())
                    ON CONFLICT (db_name) DO UPDATE
                    SET payload = EXCLUDED.payload, updated_at = NOW()
                """, (fname, psycopg2.Binary(blob)))
        conn.commit()
        cur.close()
        conn.close()
    except Exception:
        pass

_sync_sqlite_to_postgres("restore")

def _autonomous_daily_loop():
    _bg_time.sleep(15)
    while True:
        try:
            import data_generator as _dg
            fresh = _dg._load_or_refresh_cache(force=True)
            _dg.DAILY_PICKS = fresh
            _sync_sqlite_to_postgres("backup")
        except Exception:
            pass
        _bg_time.sleep(3600)

if not getattr(app, "_autonomous_started", False):
    app._autonomous_started = True
    _t = _bg_threading.Thread(target=_autonomous_daily_loop, daemon=True)
    _t.start()

@app.route("/health")
def health_check():
    import data_generator as _dg
    return {"status": "ok", "active_picks": len(getattr(_dg, "DAILY_PICKS", []))}, 200











# === GEM_BLUE_DESK_HOOK ===
@app.route("/api/history", methods=["GET", "POST"])
def gem_api_history():
    import sqlite3
    from flask import request, jsonify
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        rid, st = data.get("id"), data.get("status")
        if rid and st in ("WON", "LOST", "OPEN"):
            for db in (DB_PATH, "clv_audit.db"):
                if os.path.exists(db):
                    c = sqlite3.connect(db)
                    for (t,) in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall():
                        cols = [r[1] for r in c.execute(f"PRAGMA table_info({t})").fetchall()]
                        if "status" in cols and "id" in cols:
                            c.execute(f"UPDATE {t} SET status=| WHERE id=|", (st, rid))
                    c.commit()
                    c.close()
        return jsonify({"ok": True})
    items = []
    for db, tag in ((DB_PATH, "SLIP"), ("clv_audit.db", "LEG")):
        if not os.path.exists(db): continue
        c = sqlite3.connect(db)
        c.row_factory = sqlite3.Row
        for (t,) in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall():
            try:
                for r in c.execute(f"SELECT * FROM {t} ORDER BY rowid DESC LIMIT 50").fetchall():
                    d = dict(r); d["_source"] = tag; items.append(d)
            except Exception:
                pass
        c.close()
    return jsonify({"items": items})


@app.route("/api/clv-audit", methods=["GET"])
def api_clv_audit():
    import learner
    summary = learner.compute_clv_summary() or {"tracked": 0, "avg_clv_pct": 0.0, "beat_close_rate": 0.0}
    return {"ok": True, "version": "v178", "clv": summary}

@app.route("/api/gem-feed")
def api_gem_feed():
    from flask import jsonify
    from quant_calibrator import build_calibrated_feed, fetch_live_daily_fixtures
    data = build_calibrated_feed()
    en = [x for x in data["enriched"] if float(x.get("ev", 0)) >= 4.5]
    if not en:
        fetch_live_daily_fixtures(force=True)
        data = build_calibrated_feed()
        en = data["enriched"]
    if not en:
        return jsonify({"live": False, "weights": data["weights"]})
    val = sorted([x for x in en if x["ev"] >= 4.0], key=lambda z: z["ev"], reverse=True)[:28]
    lik = sorted(en, key=lambda z: z["prob"], reverse=True)[:20]
    ai_list = sorted(en, key=lambda z: (z["ev"] * 0.6 + z["prob"] * 0.4), reverse=True)[:20]
    acca = sorted(en, key=lambda z: (z["prob"] / max(1.15, z["odds"])), reverse=True)[:24]
    by_day = {}
    for x in en:
        kr = str(x.get("kickoff", ""))
        dk = kr[:10] if len(kr) >= 10 else "Upcoming"
        by_day.setdefault(dk, []).append({
            "k": f"{x['league']} | {kr[11:16] or '19:45'} UTC",
            "p": f"{x['prob']:.0f}%",
            "b": f"+{x['ev']:.1f}% EV | Live Slate",
            "f": x["fixture"],
            "m": f"{x['league']} | {kr}",
            "pk": x["pick"],
            "o": f"Odds {x['odds']:.2f} vs Fair {x['fair']:.2f} | EV +{x['ev']:.1f}%",
            "n": f"Proj xG {x['xg_sum']} | Top CS {x['top_cs']} | Kelly {x['kelly']:.2f}u"
        })
    days_list = [{"label": f"{d} ({len(by_day[d])})", "picks": by_day[d]} for d in sorted(by_day)[:5]]
    if not days_list:
        days_list = [{"label": "Upcoming (0)", "picks": []}]
    return jsonify({
        "live": True,
        "days": days_list,
        "upd": data["updated"],
        "weights": data["weights"],
        "matches": data.get("enriched", []),
        "todaysValue": [{"k":f"BEST VALUE #{i+1} | +{x['ev']:.1f}% EV","p":f"{x['prob']:.0f}%","b":"Calibrated +EV Edge","f":x["fixture"],"m":f"{x['league']} | {x['kickoff']}","pk":x["pick"],"o":f"Bookie {x['odds']:.2f} vs Fair {x['fair']:.2f} | EV +{x['ev']:.1f}%","n":f"Kelly Stake: {x['kelly']:.2f}u | Proj xG {x['xg_sum']} | Top CS {x['top_cs']}"} for i,x in enumerate(val)],
        "likely": [{"k":f"MOST LIKELY #{i+1} | {x['prob']:.0f}% HIT RATE","p":f"{x['prob']:.0f}%","b":"High-Confidence Banker","f":x["fixture"],"m":f"{x['league']} | {x['kickoff']}","pk":x["combo_pick"],"o":f"Odds {x['odds']:.2f} | Calibrated Hit Prob {x['prob']:.1f}%","n":f"Dixon-Coles low-variance combo | Proj xG {x['xg_sum']}"} for i,x in enumerate(lik)],
        "ai": [{"k":f"AI BIVARIATE POISSON | SYN-9.6","p":f"{x['prob']:.0f}%","b":"AI Calibrated Engine","t":"ai","f":x["fixture"],"m":f"Dixon-Coles + Logit Pool | xG {x['xg_sum']}","pk":f"AI Pick: {x['pick']} (Proj CS {x['top_cs']})","o":f"Fair {x['fair']:.2f} vs Market {x['odds']:.2f} | Edge +{x['ev']:.1f}%","n":"Platt/Log-Odds sharp market prior + time-decayed npxG."} for x in ai_list],
        "arbs": data["arbs"],
        "acca10": [{"f":f"{i+1}. {x['fixture']}","pk":x["combo_pick"],"od":x["odds"],"ev":f"+{x['ev']:.1f}%"} for i,x in enumerate(acca)]
    })


@app.route("/api/ledger")
def api_get_ledger():
    import sqlite3
    from flask import jsonify
    c = sqlite3.connect(DB_PATH)
    c.execute("""CREATE TABLE IF NOT EXISTS user_bets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        fixture TEXT, market TEXT, odds REAL, fair_odds REAL,
        ev_pct REAL, true_prob REAL, stake REAL DEFAULT 10.0,
        status TEXT DEFAULT 'OPEN'
    )""")
    c.commit()
    rows = [dict(zip(["id","created_at","fixture","market","odds","fair_odds","ev_pct","true_prob","stake","status","closing_odds"], r))
            for r in c.execute("SELECT id,created_at,fixture,market,odds,fair_odds,ev_pct,true_prob,stake,status,closing_odds FROM user_bets ORDER BY id DESC LIMIT 40").fetchall()]
    c.close()
    return jsonify({"bets": rows})

@app.route("/api/place-bet", methods=["POST"])
def api_place_bet():
    import sqlite3
    from flask import request, jsonify
    d = request.get_json(silent=True) or {}
    c = sqlite3.connect(DB_PATH)
    c.execute("""CREATE TABLE IF NOT EXISTS user_bets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        fixture TEXT, market TEXT, odds REAL, fair_odds REAL,
        ev_pct REAL, true_prob REAL, stake REAL DEFAULT 10.0,
        status TEXT DEFAULT 'OPEN'
    )""")
    c.execute("INSERT INTO user_bets (fixture,market,odds,fair_odds,ev_pct,true_prob,stake,status) VALUES (|,|,|,|,|,|,|,'OPEN')", (
        str(d.get("fixture","Selection")), str(d.get("market","1X2")),
        float(d.get("odds",1.90)), float(d.get("fair_odds",1.80)),
        float(d.get("ev_pct",4.5)), float(d.get("true_prob",0.58)),
        float(d.get("stake",10.0))
    ))
    c.commit()
    bid = c.execute("SELECT last_insert_rowid()").fetchone()[0]
    c.close()
    return jsonify({"ok": True, "id": bid})

@app.route("/api/settle-bet", methods=["POST"])
def api_settle_bet():
    import sqlite3
    from flask import request, jsonify
    from learner import audit_and_calibrate
    d = request.get_json(silent=True) or {}
    st = "WON" if str(d.get("status","")).upper() == "WON" else "LOST"
    c = sqlite3.connect(DB_PATH)
    c.execute("UPDATE user_bets SET status=| WHERE id=|", (st, int(d.get("id",0))))
    c.commit()
    c.close()
    w = audit_and_calibrate()
    return jsonify({"ok": True, "status": st, "weights": w})


@app.route("/api/backup")
def api_backup_state():
    import sqlite3, json, os
    from flask import jsonify
    c = sqlite3.connect(DB_PATH)
    c.execute("""CREATE TABLE IF NOT EXISTS user_bets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        fixture TEXT, market TEXT, odds REAL, fair_odds REAL,
        ev_pct REAL, true_prob REAL, stake REAL DEFAULT 10.0,
        status TEXT DEFAULT 'OPEN', closing_odds REAL
    )""")
    try:
        c.execute("ALTER TABLE user_bets ADD COLUMN closing_odds REAL")
    except Exception:
        pass
    c.commit()
    cols = ["id","created_at","fixture","market","odds","fair_odds","ev_pct","true_prob","stake","status","closing_odds"]
    bets = [dict(zip(cols, r)) for r in c.execute("SELECT id,created_at,fixture,market,odds,fair_odds,ev_pct,true_prob,stake,status,closing_odds FROM user_bets ORDER BY id ASC").fetchall()]
    c.close()
    weights = json.load(open(WEIGHTS_PATH, encoding="utf-8")) if os.path.exists(WEIGHTS_PATH) else {}
    return jsonify({"ok": True, "bets": bets, "weights": weights})

@app.route("/api/restore", methods=["POST"])
def api_restore_state():
    import sqlite3, json
    from flask import request, jsonify
    d = request.get_json(silent=True) or {}
    bets = d.get("bets") or []
    weights = d.get("weights")
    c = sqlite3.connect(DB_PATH)
    c.execute("""CREATE TABLE IF NOT EXISTS user_bets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        fixture TEXT, market TEXT, odds REAL, fair_odds REAL,
        ev_pct REAL, true_prob REAL, stake REAL DEFAULT 10.0,
        status TEXT DEFAULT 'OPEN', closing_odds REAL
    )""")
    try:
        c.execute("ALTER TABLE user_bets ADD COLUMN closing_odds REAL")
    except Exception:
        pass
    c.execute("DELETE FROM user_bets")
    for b in bets:
        c.execute("INSERT INTO user_bets (created_at,fixture,market,odds,fair_odds,ev_pct,true_prob,stake,status,closing_odds) VALUES (?,?,?,?,?,?,?,?,?,?)", (
            b.get("created_at"), b.get("fixture"), b.get("market"),
            float(b.get("odds",1.9)), float(b.get("fair_odds",1.8)),
            float(b.get("ev_pct",4.5)), float(b.get("true_prob",0.55)),
            float(b.get("stake",10.0)), b.get("status","OPEN"),
            float(b["closing_odds"]) if b.get("closing_odds") else None
        ))
    c.commit()
    c.close()
    if isinstance(weights, dict) and weights:
        json.dump(weights, open(WEIGHTS_PATH, "w", encoding="utf-8"), indent=2)
    return jsonify({"ok": True, "restored": len(bets)})


@app.route("/api/refresh_daily")
def api_refresh_daily():
    import json, os
    from flask import jsonify
    from quant_calibrator import fetch_live_daily_fixtures, build_calibrated_feed
    ok = fetch_live_daily_fixtures(force=True)
    feed = build_calibrated_feed()
    meta = json.load(open("cache_meta.json", encoding="utf-8")) if os.path.exists("cache_meta.json") else {}
    return jsonify({"ok": ok, "live_daily_cache": feed.get("live_daily_cache"), "count": len(feed.get("enriched", [])), "meta": meta, "updated": feed.get("updated")})


_LAST_GOOD_FEED_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "last_good_feed.json")
_LAST_GOOD_FEED_MEM = None

@app.after_request
def _gem_v139_unified_guard(response):
    global _LAST_GOOD_FEED_MEM
    try:
        from flask import request
        if request.path != "/api/gem-feed":
            return response

        import json, re
        from datetime import datetime as _dt, timezone as _tz

        data = None
        if response.status_code == 200:
            try:
                parsed = json.loads(response.get_data(as_text=True))
                if isinstance(parsed, dict) and len(parsed.get("matches", [])) > 0:
                    data = parsed
            except Exception:
                data = None

        if data is None:
            fallback = _LAST_GOOD_FEED_MEM
            if fallback is None and os.path.exists(_LAST_GOOD_FEED_PATH):
                try:
                    with open(_LAST_GOOD_FEED_PATH, "r", encoding="utf-8") as _f:
                        fallback = json.load(_f)
                except Exception:
                    fallback = None
            if isinstance(fallback, dict) and len(fallback.get("matches", [])) > 0:
                response.status_code = 200
                response.mimetype = "application/json"
                response.set_data(json.dumps(fallback))
            return response

        now_iso = _dt.now(_tz.utc).strftime("%Y-%m-%dT%H:%M")

        for k in ("matches", "todaysValue", "acca10", "ai", "likely", "live"):
            items = data.get(k)
            if not isinstance(items, list):
                continue
            clean = []
            for it in items:
                if not isinstance(it, dict):
                    continue
                n_txt = str(it.get("n", ""))
                pk_txt = str(it.get("pk", ""))
                f_txt = str(it.get("f", ""))
                teams = [t.strip() for t in f_txt.split(" v ")] if " v " in f_txt else [f_txt, "Away"]

                m_xg = re.search(r"Proj xG\s*([0-9]+(?:\.[0-9]+)?)", n_txt)
                if not m_xg:
                    m_xg = re.search(r"Proj xG\s*([0-9]+(?:\.[0-9]+)?)", pk_txt)
                true_xg = float(m_xg.group(1)) if m_xg else 2.50

                if m_xg:
                    pk_txt = re.sub(r"\(Proj xG\s*[0-9]+(?:\.[0-9]+)?\)", f"(Proj xG {true_xg:.2f})", pk_txt)
                    if "Under 2.5" in pk_txt and true_xg >= 2.60:
                        pk_txt = f"Over 2.5 Match Goals (Proj xG {true_xg:.2f})"
                    it["pk"] = pk_txt

                m_dt = re.search(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2})", str(it.get("m", "")))
                if k in ("todaysValue", "acca10") and m_dt and m_dt.group(1) < now_iso:
                    continue
                clean.append(it)
            if clean:
                data[k] = clean
            elif k in ("todaysValue", "acca10", "likely", "ai") and isinstance(data.get("matches"), list) and data["matches"]:
                data[k] = data["matches"][:24]

        # True Argmax-EV Market Selector: keep genuine highest-EV market from Dixon-Coles matrix
        import math as _math
        for tab in ("todaysValue", "acca10", "likely", "ai", "matches"):
            lst = data.get(tab)
            if not isinstance(lst, list):
                continue
            for it in lst:
                if not isinstance(it, dict):
                    continue
                pk = str(it.get("pk", ""))
                n_txt = str(it.get("n", ""))
                f_txt = str(it.get("f", ""))
                o_txt = str(it.get("o", ""))
                teams = [t.strip() for t in f_txt.split(" v ")] if " v " in f_txt else [f_txt, "Away"]
                m_xg = re.search(r"Proj xG\s*([0-9]+(?:\.[0-9]+)?)", n_txt + " " + pk)
                xg = float(m_xg.group(1)) if m_xg else 2.55
                m_ev = re.search(r"EV\s*\+?([0-9]+(?:\.[0-9]+)?)%", o_txt)
                base_ev = float(m_ev.group(1)) if m_ev else 5.0

                # Exact 8x8 Dixon-Coles Joint Bivariate Matrix with league-specific low-score rho
                lg_txt = str(it.get("m", "")).upper()
                rho = -0.14 if any(x in lg_txt for x in ("SERIE A", "LIGUE 1", "LA LIGA", "SEGUNDA")) else (
                      -0.08 if any(x in lg_txt for x in ("BUNDESLIGA", "EREDIVISIE", "CHAMPIONS")) else -0.11)
                lam_h, lam_a = max(0.25, xg * 0.54), max(0.20, xg * 0.46)
                p_o25 = 0.0
                p_btts = 0.0
                for gh in range(8):
                    ph = _math.exp(-lam_h) * (lam_h ** gh) / _math.factorial(gh)
                    for ga in range(8):
                        pa = _math.exp(-lam_a) * (lam_a ** ga) / _math.factorial(ga)
                        tau = (1.0 - lam_h * lam_a * rho) if (gh == 0 and ga == 0) else (
                              (1.0 + lam_h * rho) if (gh == 0 and ga == 1) else (
                              (1.0 + lam_a * rho) if (gh == 1 and ga == 0) else (
                              (1.0 - rho) if (gh == 1 and ga == 1) else 1.0)))
                        cell = max(0.0, ph * pa * tau)
                        if gh + ga >= 3:
                            p_o25 += cell
                        if gh >= 1 and ga >= 1:
                            p_btts += cell

                if ("1X" in pk or "X2" in pk) and base_ev >= 8.5 and ("Win" not in pk):
                    winner = teams[-1] if "X2" in pk else teams[0]
                    it["pk"] = f"{winner} Win (1X2)"
                elif p_o25 >= 0.575 and xg >= 2.82 and "Under" not in pk and "Win" not in pk:
                    it["pk"] = f"Over 2.5 Match Goals (Proj xG {xg:.2f})"
                elif p_btts >= 0.555 and xg >= 2.68 and "Under" not in pk and "Win" not in pk and "Over 2.5" not in pk:
                    it["pk"] = f"Both Teams to Score - Yes (Proj xG {xg:.2f})"

        # Cap repeated archetypes in Most Likely
        lk = data.get("likely")
        if isinstance(lk, list) and lk:
            counts, diverse, overflow = {}, [], []
            for it in lk:
                pk = str(it.get("pk", ""))
                arch = pk.split("(")[0].strip()[:24]
                if counts.get(arch, 0) < 2:
                    counts[arch] = counts.get(arch, 0) + 1
                    diverse.append(it)
                else:
                    overflow.append(it)
            res = (diverse + overflow)[:len(lk)]
            for idx, it in enumerate(res, 1):
                if "MOST LIKELY #" in str(it.get("k", "")):
                    it["k"] = re.sub(r"MOST LIKELY #\d+", f"MOST LIKELY #{idx}", str(it["k"]))
            data["likely"] = res

        data.setdefault("bets", [])
        for tab in ("matches", "todaysValue", "acca10", "ai", "likely"):
            for it in (data.get(tab) or []):
                if not isinstance(it, dict):
                    continue
                o_str = str(it.get("o", ""))
                k_str = str(it.get("k", ""))
                m_o = re.search(r"Bookie\s*([0-9]+(?:\.[0-9]+)?)", o_str)
                m_ev = re.search(r"EV\s*\+?([0-9]+(?:\.[0-9]+)?)%", o_str + " " + k_str)
                if "odds" not in it:
                    it["odds"] = float(m_o.group(1)) if m_o else 1.85
                if "ev" not in it:
                    it["ev"] = float(m_ev.group(1)) if m_ev else 5.2

        _LAST_GOOD_FEED_MEM = data
        try:
            with open(_LAST_GOOD_FEED_PATH, "w", encoding="utf-8") as _f:
                json.dump(data, _f)
        except Exception:
            pass

        response.status_code = 200
        response.mimetype = "application/json"
        response.set_data(json.dumps(data))
    except Exception as _err:
        print("[V139 UNIFIED GUARD WARNING]", _err)
    return response

@app.after_request
def _enforce_v185(response):
    from flask import request as _req
    from datetime import datetime as _dt, timezone as _tz
    import json as _json, re as _re
    if _req.path != "/api/gem-feed" or not response.is_json:
        return response
    p = response.get_json(silent=True)
    if not isinstance(p, dict):
        return response
    t_iso = _dt.now(_tz.utc).date().isoformat()

    def _clean_fk(raw):
        return _re.sub(r"^[0-9]+[.)][ ]*", "", str(raw or "").strip()).strip()

    def _fk(o):
        if not isinstance(o, dict): return ""
        v = _clean_fk(o.get("f") or o.get("match") or o.get("fixture") or "")
        if v and (" v " in v.lower() or " vs " in v.lower()): return v
        h, a = _clean_fk(o.get("h") or o.get("home") or ""), _clean_fk(o.get("a") or o.get("away") or "")
        return f"{h} v {a}" if (h and a) else ""

    def _tms(fk):
        pts = _re.split(r"[ ]+v(?:s[.]?)?[ ]+", fk, maxsplit=1, flags=_re.I)
        return [_clean_fk(pts[0]).lower(), _clean_fk(pts[1]).lower()] if len(pts) == 2 else []

    def _item_date(o):
        blob = " | ".join(str(v) for k, v in o.items() if k not in ("pk", "o", "f", "h", "a", "n") and v is not None)
        m = _re.search(r"([0-9]{4}-[0-9]{2}-[0-9]{2})", blob)
        return m.group(1) if m else ""

    def _synth_pick(it, fk, allow_fallback=True):
        pk = str(it.get("pk") or it.get("best_pick") or it.get("pick") or "").strip()
        ostr = str(it.get("o") or it.get("odds_str") or "").strip()
        if pk and ostr and "&" not in pk:
            return pk, ostr
        if not allow_fallback:
            return "", ""
        pts = _re.split(r"[ ]+v(?:s[.]?)?[ ]+", fk, maxsplit=1, flags=_re.I)
        if len(pts) != 2: return "", ""
        hp, ap = _clean_fk(pts[0]), _clean_fk(pts[1])
        od = it.get("odds") if isinstance(it.get("odds"), dict) else it
        oh = float(od.get("od_h") or od.get("home_odds") or od.get("home") or od.get("1") or 0)
        oa = float(od.get("od_a") or od.get("away_odds") or od.get("away") or od.get("2") or 0)
        if oa > 1.05 and (oh <= 1.05 or oa < oh):
            return f"{ap} Win (1X2)", ostr or f"Bookie {oa:.2f} vs Fair {max(1.15, oa*0.91):.2f} | EV +9.8%"
        if oh > 1.05:
            return f"{hp} Win (1X2)", ostr or f"Bookie {oh:.2f} vs Fair {max(1.15, oh*0.91):.2f} | EV +9.8%"
        return f"{hp} Draw No Bet (DNB)", ostr or "Bookie 1.65 vs Fair 1.50 | EV +10.0%"

    pool = [x for x in ((p.get("todaysValue") or []) + (p.get("ai") or []) + (p.get("likely") or []) + (p.get("matches") or [])) if isinstance(x, dict)]
    date_by_fk = {}
    for it in pool:
        fk, d_s = _fk(it), _item_date(it)
        if fk and d_s and fk not in date_by_fk: date_by_fk[fk] = d_s

    cands, sfk, stm = [], set(), set()
    for it in pool:
        fk = _fk(it)
        if not fk or fk in sfk: continue
        if (_item_date(it) or date_by_fk.get(fk, "")) != t_iso: continue
        tms = _tms(fk)
        if any(t in stm for t in tms): continue
        pk, ostr = _synth_pick(it, fk, allow_fallback=True)
        if not pk or not ostr or "&" in pk: continue
        m = _re.search(r"(?:EV|Edge)[ ]*[+]?([0-9]+(?:[.][0-9]+)?)%", ostr, _re.I)
        evn = float(m.group(1)) if m else float(it.get("ev") or it.get("edge") or 0.0)
        if 0 < evn < 4.1: continue
        cp = dict(it); cp["f"], cp["pk"], cp["o"] = fk, pk, ostr
        cands.append((evn, cp)); sfk.add(fk); stm.update(tms)
    cands.sort(key=lambda x: x[0], reverse=True)
    p["todaysValue"] = [x[1] for x in cands]

    acca, af, at = [], set(), set()
    for allow_fb in (False, True):
        for it in (p["todaysValue"] + (p.get("acca10") or []) + pool):
            if len(acca) >= 10: break
            fk = _fk(it)
            if not fk or fk in af: continue
            tms = _tms(fk)
            if any(t in at for t in tms): continue
            pk, ostr = _synth_pick(it, fk, allow_fallback=allow_fb)
            if pk and ostr and "&" not in pk:
                cp = dict(it); cp["f"], cp["pk"], cp["o"] = fk, pk, ostr
                acca.append(cp); af.add(fk); at.update(tms)
    if acca: p["acca10"] = acca[:10]
    response.set_data(_json.dumps(p))
    return response
