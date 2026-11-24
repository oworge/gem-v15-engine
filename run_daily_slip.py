import json, pathlib
from datetime import datetime, timezone
import app

BANKROLL_GBP = 500.0

def build_daily_3fold():
    with app.app.test_client() as client:
        resp = client.get("/api/tab-picks?tab=daily_picks")
        payload = resp.get_json(silent=True) or {}

    rows = next((v for v in payload.values() if isinstance(v, list)), []) if isinstance(payload, dict) else (payload if isinstance(payload, list) else [])
    eligible = [r for r in rows if isinstance(r, dict) and r.get("fixture") and r.get("pk")]

    rank_order = {"CORE_EDGE": 0, "LOW_EDGE": 1, "CHECK_ODDS": 2, "NO_EDGE": 3}
    eligible.sort(key=lambda r: (rank_order.get(str(r.get("ev_flag")), 9), -float(r.get("ev") or -99), -float(r.get("prob") or 0)))

    legs = []
    used_fixtures = set()
    used_league_slots = set()
    for r in eligible:
        fx = str(r.get("fixture"))
        if fx in used_fixtures:
            continue
        slot_key = f"{r.get('league')}|{r.get('date_label')}|{r.get('ko')}"
        if slot_key in used_league_slots and len(eligible) > 6:
            continue
        legs.append(r)
        used_fixtures.add(fx)
        used_league_slots.add(slot_key)
        if len(legs) == 3:
            break

    if len(legs) < 3:
        for r in eligible:
            if str(r.get("fixture")) not in used_fixtures:
                legs.append(r)
                used_fixtures.add(str(r.get("fixture")))
                if len(legs) == 3:
                    break

    combined_odds = 1.0
    combined_prob = 1.0
    for lg in legs:
        combined_odds *= float(lg.get("odds") or 1.0)
        combined_prob *= (float(lg.get("prob") or 0.0) / 100.0)

    combined_odds = round(combined_odds, 2)
    combined_prob_pct = round(combined_prob * 100.0, 1)
    edge_ev_pct = round(((combined_prob * combined_odds) - 1.0) * 100.0, 2)
    stake_pct = 2.0 if edge_ev_pct >= 5.0 else (1.5 if edge_ev_pct > 0 else 1.0)
    stake_gbp = round(BANKROLL_GBP * (stake_pct / 100.0), 2)

    slip = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "engine_version": "GEM-V15-DC-9.8",
        "format": "Diversified 3-Fold Accumulator",
        "bankroll_gbp": BANKROLL_GBP,
        "recommended_stake_gbp": stake_gbp,
        "stake_pct": stake_pct,
        "combined_odds": combined_odds,
        "combined_model_prob_pct": combined_prob_pct,
        "combined_ev_pct": edge_ev_pct,
        "potential_return_gbp": round(stake_gbp * combined_odds, 2),
        "legs": [
            {
                "leg": idx + 1,
                "date_label": r.get("date_label"),
                "ko": r.get("ko"),
                "fixture": r.get("fixture"),
                "league": r.get("league"),
                "selection": r.get("pk"),
                "odds": r.get("odds"),
                "model_prob_pct": r.get("prob"),
                "ev_pct": r.get("ev"),
                "ev_flag": r.get("ev_flag"),
                "model_note": r.get("model_note"),
            }
            for idx, r in enumerate(legs)
        ],
    }

    pathlib.Path("daily_auto_slip.json").write_text(json.dumps(slip, indent=2), encoding="utf-8")
    print(json.dumps(slip, indent=2))
    return slip

if __name__ == "__main__":
    build_daily_3fold()


# === GEM V15-DC-13.4 AUTO-EXPAND ALL MARKETS INTO MAIN FEED ===
def _gem_auto_expand_main_feed():
    import json as _j, pathlib as _pl, re as _re
    from all_markets_engine import build_fixture_markets as _bfm
    target = {"1", "2", "BTTS_Y", "O25", "U25", "ESN", "DNB1", "DNB2", "HT_X", "HTFT_1_1", "1X", "X2", "O15"}
    for fn in ("dashboard_picks.json", "daily_bookie_beater_slip.json", "static/daily_bookie_beater_slip.json"):
        p = _pl.Path(fn)
        if not p.exists():
            continue
        try:
            raw = _j.loads(p.read_text(encoding="utf-8", errors="ignore"))
            is_l = isinstance(raw, list)
            rows = raw if is_l else (raw.get("picks") or raw.get("slip") or raw.get("matches") or [])
            if any("[" in str(r.get("market") or "") for r in rows if isinstance(r, dict)):
                continue
            seen, bases = set(), []
            for r in rows:
                if isinstance(r, dict):
                    fx = str(r.get("fixture") or r.get("match") or "").strip()
                    if fx and fx not in seen:
                        seen.add(fx)
                        bases.append(r)
            out = []
            for b in bases:
                m = _re.search(r"(\d+\.\d+)", " ".join(str(b.get(k) or "") for k in ("xg", "note", "reason", "market")))
                txg = float(m.group(1)) if m else 2.35
                lh, la = round(max(0.45, txg * 0.56), 2), round(max(0.35, txg * 0.44), 2)
                for mk in _bfm(lh, la):
                    if (mk["code"] in target or mk["code"].startswith("CS_")) and mk["prob"] >= 14.0:
                        fair = float(mk["fair_odds"])
                        odds = round(fair * 1.045, 2)
                        ev = round(((mk["prob"] / 100.0) * odds - 1.0) * 100.0, 1)
                        nr = dict(b)
                        nr["market"] = f"{mk['label']} [{mk['group']}]"
                        nr["pk"] = nr["market"]
                        nr["odds"] = odds
                        nr["prob"] = mk["prob"]
                        nr["ev"] = ev
                        nr["ev_flag"] = "CORE_EDGE" if ev >= 4.0 else "LOW_EDGE"
                        out.append(nr)
            if out:
                if is_l:
                    p.write_text(_j.dumps(out, indent=2), encoding="utf-8")
                else:
                    k = "picks" if "picks" in raw else ("slip" if "slip" in raw else "matches")
                    raw[k] = out
                    p.write_text(_j.dumps(raw, indent=2), encoding="utf-8")
        except Exception:
            pass

try:
    _gem_auto_expand_main_feed()
except Exception:
    pass
