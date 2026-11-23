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
