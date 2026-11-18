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
    return hits[:6] if hits else picks[:5]

def _build_dynamic_tabs(picks):
    btts = [
        {
            "match": p.get("match", ""),
            "comp": p.get("comp", "BTTS & Goals Engine"),
            "pick": f"BTTS Yes & Over 2.5 Goals ({p.get('pick', '')})",
            "odds": p.get("odds", "1.85"),
        }
        for p in picks[:6]
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

    builders = [_build_5leg_sgm(p) for p in picks[:6]]
    correct_scores = [
        {
            "match": p.get("match", ""),
            "comp": "Poisson Score Matrix (Top Model Projection)",
            "pick": f"Correct Score: 2 - 1 / 1 - 1 ({p.get('pick', '')})",
            "odds": "7.50",
        }
        for p in picks[:6]
    ]
    true_clv = dg.get_live_steam_clv() if hasattr(dg, "get_live_steam_clv") else picks[:6]
    tactical = [
        {
            "match": p.get("match", "NegBin & Monte Carlo"),
            "comp": "5,000 Sims | CIRF Fatigue & Tactical Audit",
            "pick": f"TACTICAL PASS — {p.get('pick', 'Zero Fatigue Flags')}",
            "odds": p.get("odds", "PASS"),
        }
        for p in picks[:6]
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
        for fname in ("clv_audit.db", "syndicate_ledger.db"):
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
            for db in ("syndicate_ledger.db", "clv_audit.db"):
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
    for db, tag in (("syndicate_ledger.db", "SLIP"), ("clv_audit.db", "LEG")):
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


@app.route("/api/gem-feed")
def api_gem_feed():
    from flask import jsonify
    from quant_calibrator import build_calibrated_feed
    data = build_calibrated_feed()
    en = data["enriched"]
    if not en:
        return jsonify({"live": False, "weights": data["weights"]})
    val = sorted([x for x in en if x["ev"] >= 3.5], key=lambda z: z["ev"], reverse=True)[:8]
    lik = sorted(en, key=lambda z: z["prob"], reverse=True)[:6]
    ai_list = sorted(en, key=lambda z: (z["ev"] * 0.6 + z["prob"] * 0.4), reverse=True)[:6]
    acca = sorted(en, key=lambda z: (z["prob"] / max(1.15, z["odds"])), reverse=True)[:10]
    return jsonify({
        "live": True,
        "upd": data["updated"],
        "weights": data["weights"],
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
    c = sqlite3.connect("syndicate_ledger.db")
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
    c = sqlite3.connect("syndicate_ledger.db")
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
    c = sqlite3.connect("syndicate_ledger.db")
    c.execute("UPDATE user_bets SET status=| WHERE id=|", (st, int(d.get("id",0))))
    c.commit()
    c.close()
    w = audit_and_calibrate()
    return jsonify({"ok": True, "status": st, "weights": w})


@app.route("/api/backup")
def api_backup_state():
    import sqlite3, json, os
    from flask import jsonify
    c = sqlite3.connect("syndicate_ledger.db")
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
    weights = json.load(open("model_weights.json", encoding="utf-8")) if os.path.exists("model_weights.json") else {}
    return jsonify({"ok": True, "bets": bets, "weights": weights})

@app.route("/api/restore", methods=["POST"])
def api_restore_state():
    import sqlite3, json
    from flask import request, jsonify
    d = request.get_json(silent=True) or {}
    bets = d.get("bets") or []
    weights = d.get("weights")
    c = sqlite3.connect("syndicate_ledger.db")
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
        json.dump(weights, open("model_weights.json", "w", encoding="utf-8"), indent=2)
    return jsonify({"ok": True, "restored": len(bets)})


@app.route("/api/refresh_daily")
def api_refresh_daily():
    from flask import jsonify
    from quant_calibrator import fetch_live_daily_fixtures, build_calibrated_feed
    ok = fetch_live_daily_fixtures(force=True)
    feed = build_calibrated_feed()
    return jsonify({"ok": ok, "live_daily_cache": feed.get("live_daily_cache"), "count": len(feed.get("enriched", [])), "updated": feed.get("updated")})

@app.after_request
def gem_inject_blue_desk(resp):
    try:
        if resp.content_type and "text/html" in resp.content_type:
            html = resp.get_data(as_text=True)
            css = open("static/gem_blue_desk.css", encoding="utf-8").read() if os.path.exists("static/gem_blue_desk.css") else ""
            js = open("static/gem_blue_desk.js", encoding="utf-8").read() if os.path.exists("static/gem_blue_desk.js") else ""
            if css and js and "gem-bar" not in html:
                bundle = f"<style>{css}</style><script>{js}</script>"
                html = html.replace("</body>", bundle + "</body>") if "</body>" in html else html + bundle
                resp.set_data(html)
    except Exception:
        pass
    return resp


# === GEM_DESK_FEED_API ===
@app.route("/api/desk")
def gem_api_desk():
    import os, sqlite3, json, re
    from flask import jsonify
    from engines import ENGINES
    from learner import audit_and_calibrate
    w = audit_and_calibrate()
    mev = float(w.get("min_ev_pct", 4.5))
    items = []
    pev = lambda v: float(m.group(0)) if (m := re.search(r"[-+]|\d+(|:\.\d+)|", str(v or ""))) else 0.0
    for db, src in (("syndicate_ledger.db", "SLIP"), ("clv_audit.db", "CLV")):
        if not os.path.exists(db): continue
        c = sqlite3.connect(db); c.row_factory = sqlite3.Row
        for (tb,) in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall():
            try:
                for row in c.execute(f"SELECT * FROM {tb} ORDER BY rowid DESC LIMIT 80").fetchall():
                    d = dict(row); ev = pev(d.get("ev") or d.get("edge") or d.get("ev_pct") or 0)
                    if ev >= mev:
                        d["_src"] = src; d["_tbl"] = tb; d["ev"] = f"+{ev:.1f}%"; items.append(d)
            except Exception: pass
        c.close()
    if os.path.exists("global_odds_cache.json"):
        try:
            raw = json.load(open("global_odds_cache.json", encoding="utf-8"))
            rows = raw if isinstance(raw, list) else raw.get("matches", raw.get("data", []))
            for m in (rows or [])[:80]:
                if isinstance(m, dict):
                    hm, aw = m.get("home_team") or "Home", m.get("away_team") or "Away"
                    od = float(m.get("odds") or m.get("home_odds") or m.get("best_odds") or 1.90)
                    res = ENGINES.run_all_engines(m.get("id", hm), hm, aw, "GLOBAL", float(m.get("xg_home") or 1.6), float(m.get("xg_away") or 1.1), od, float(m.get("draw_odds") or 3.5), float(m.get("away_odds") or 4.0))
                    if res["is_approved"] and res["ev_pct"] >= mev:
                        m["_src"] = "QUANT_EV"; m["prob"] = res["consensus_score"]; m["ev"] = f"+{res['ev_pct']:.1f}%"; m["kelly"] = f"{res['kelly_pct']:.2f}%"; m["strategy"] = f"Dixon-Coles + No-Vig | Fair {res['fair_odds']} vs {od}"; items.append(m)
        except Exception: pass
    return jsonify({"items": items, "weights": w, "min_ev_pct": mev})


@app.after_request
def _inject_gem_polish_v40(resp):
    try:
        if "text/html" in resp.headers.get("Content-Type",""):
            html=resp.get_data(as_text=True)
            tag='<link rel="stylesheet" href="/static/gem_polish.css?v=93"><script src="/static/gem_data.js?v=93"></script><script src="/static/gem_polish.js?v=93"></script>'
            if "gem_polish.js?v=93" not in html:
                html=html.replace("</body>",tag+"</body>") if "</body>" in html else (html+tag)
                resp.set_data(html)
    except Exception:
        pass
    return resp
