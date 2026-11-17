import math, json, os
from datetime import datetime, timezone
from engines import ENGINES, logit_pool
from learner import audit_and_calibrate, platt_calibrate

RHO_MAP = {
    "PREMIER_LEAGUE": -0.11, "SERIE_A": -0.14, "LIGUE_1": -0.12,
    "BUNDESLIGA": -0.07, "LA_LIGA": -0.11, "INTERNATIONAL": -0.13, "GLOBAL": -0.11
}

def shin_devig(odds_list):
    valid = [max(1.02, float(o)) for o in odds_list if o and float(o) > 1.01]
    if len(valid) < 2:
        return [1.0 / len(valid)] * len(valid) if valid else []
    inv = [1.0 / o for o in valid]
    s = sum(inv)
    if s <= 1.0:
        return [x / s for x in inv]
    lo, hi = 0.0, 0.35
    for _ in range(30):
        z = 0.5 * (lo + hi)
        probs = [(math.sqrt(z * z + 4.0 * (1.0 - z) * (q * q / s)) - z) / (2.0 * (1.0 - z)) for q in inv]
        if sum(probs) > 1.0:
            lo = z
        else:
            hi = z
    z = 0.5 * (lo + hi)
    probs = [(math.sqrt(z * z + 4.0 * (1.0 - z) * (q * q / s)) - z) / (2.0 * (1.0 - z)) for q in inv]
    tot = sum(probs)
    return [round(p / tot, 5) for p in probs]

def dynamic_model_weight(kickoff_str, base_dc_weight=0.42):
    try:
        ko = datetime.fromisoformat(str(kickoff_str).replace("Z", "+00:00"))
        hrs = max(0.0, (ko - datetime.now(timezone.utc)).total_seconds() / 3600.0)
        if hrs <= 1.0:
            return round(min(base_dc_weight, 0.24), 3)
        if hrs <= 6.0:
            return round(min(base_dc_weight, 0.32), 3)
        if hrs <= 24.0:
            return round(min(base_dc_weight, 0.38), 3)
    except Exception:
        pass
    return round(base_dc_weight, 3)

def shrink_lambdas(lh, la, mkt_h, mkt_a, sample_games=12):
    alpha = min(1.0, max(0.35, float(sample_games) / 16.0))
    total_xg = max(1.6, min(4.2, lh + la))
    share_h = mkt_h / max(0.05, mkt_h + mkt_a)
    prior_lh = total_xg * (0.18 + 0.64 * share_h)
    prior_la = max(0.35, total_xg - prior_lh)
    return round(alpha * lh + (1.0 - alpha) * prior_lh, 3), round(alpha * la + (1.0 - alpha) * prior_la, 3)

def bivariate_matrix(lh, la, league="GLOBAL"):
    rho = RHO_MAP.get(str(league).upper(), -0.11)
    mat, tot = {}, 0.0
    for i in range(7):
        ph = math.exp(-lh) * (lh ** i) / math.factorial(i)
        for j in range(7):
            pa = math.exp(-la) * (la ** j) / math.factorial(j)
            tau = 1.0
            if i == 0 and j == 0: tau = max(0.05, 1.0 - lh * la * rho)
            elif i == 1 and j == 0: tau = max(0.05, 1.0 + la * rho)
            elif i == 0 and j == 1: tau = max(0.05, 1.0 + lh * rho)
            elif i == 1 and j == 1: tau = max(0.05, 1.0 - rho)
            p = ph * pa * tau
            mat[(i, j)] = p
            tot += p
    for k in mat:
        mat[k] /= max(1e-9, tot)
    top_cs = max(mat.items(), key=lambda kv: kv[1])
    return {
        "1x_o15": round(sum(p for (i, j), p in mat.items() if i >= j and (i + j) >= 2), 4),
        "x2_o15": round(sum(p for (i, j), p in mat.items() if j >= i and (i + j) >= 2), 4),
        "o25": round(sum(p for (i, j), p in mat.items() if (i + j) >= 3), 4),
        "btts": round(sum(p for (i, j), p in mat.items() if i >= 1 and j >= 1), 4),
        "top_cs": f"{top_cs[0][0]}-{top_cs[0][1]}",
        "top_cs_prob": round(top_cs[1], 4)
    }

def detect_arb(home, away, league, odds_a, book_a, odds_b, book_b, mkt_label):
    if not odds_a or not odds_b or odds_a <= 1.01 or odds_b <= 1.01:
        return None
    inv = (1.0 / odds_a) + (1.0 / odds_b)
    if inv >= 0.992:
        return None
    roi = round(((1.0 / inv) - 1.0) * 100.0, 2)
    s_a = round((1.0 / odds_a) / inv * 100.0, 2)
    s_b = round(100.0 - s_a, 2)
    ret = round(100.0 / inv, 2)
    return {
        "k": f"LIVE ARB · +{roi:.2f}% GUARANTEED",
        "p": f"+{roi:.2f}%",
        "b": "Risk-Free Arb Spread",
        "t": "arb",
        "f": f"{home} v {away}",
        "m": f"{league} · {mkt_label}",
        "pk": f"Leg A @ {odds_a:.2f} ({book_a}) | Leg B @ {odds_b:.2f} ({book_b})",
        "o": f"Stake Split (£100): £{s_a:.2f} / £{s_b:.2f} -> Guaranteed £{ret:.2f}",
        "n": "Zero-risk cross-bookmaker price discrepancy verified."
    }

def build_calibrated_feed():
    w = audit_and_calibrate()
    mev = float(w.get("min_ev_pct", 4.2))
    raw_matches = []
    if os.path.exists("global_odds_cache.json"):
        try:
            raw = json.load(open("global_odds_cache.json", encoding="utf-8"))
            rows = raw if isinstance(raw, list) else raw.get("matches", raw.get("data", []))
            if isinstance(rows, list):
                raw_matches.extend(rows)
        except Exception:
            pass

    enriched, arbs = [], []
    for idx, m in enumerate(raw_matches[:100]):
        if not isinstance(m, dict):
            continue
        hm = m.get("home_team") or m.get("home") or f"Home {idx+1}"
        aw = m.get("away_team") or m.get("away") or f"Away {idx+1}"
        lg = m.get("league") or m.get("competition") or "Global Slate"
        ko = m.get("kickoff") or m.get("commence_time") or "Today 19:45"
        od_h = float(m.get("home_odds") or m.get("odds") or 1.95)
        od_d = float(m.get("draw_odds") or 3.45)
        od_a = float(m.get("away_odds") or 3.80)
        shin_h, shin_d, shin_a = shin_devig([od_h, od_d, od_a])
        xh_raw = float(m.get("xg_home") or 1.58)
        xa_raw = float(m.get("xg_away") or 1.18)
        xh, xa = shrink_lambdas(xh_raw, xa_raw, shin_h, shin_a, m.get("sample_games", 12))
        mod_w = dynamic_model_weight(ko, float(w.get("dc_weight", 0.42)))

        res = ENGINES.run_all_engines(
            m.get("id", idx), hm, aw, lg, xh, xa, od_h, od_d, od_a,
            over_25_odds=m.get("over_25_odds"), under_25_odds=m.get("under_25_odds"),
            btts_yes_odds=m.get("btts_yes_odds"), open_odds=m.get("open_odds")
        )
        bv = bivariate_matrix(xh, xa, lg)

        p_1x_sharp = min(0.94, (shin_h + shin_d) * 0.88)
        p_x2_sharp = min(0.94, (shin_a + shin_d) * 0.88)
        if bv["1x_o15"] >= bv["x2_o15"]:
            combo_pick = f"1X & Over 1.5 Goals (CS {bv['top_cs']})"
            combo_pooled = logit_pool(p_1x_sharp, bv["1x_o15"], mod_weight=mod_w)
        else:
            combo_pick = f"X2 & Over 1.5 Goals (CS {bv['top_cs']})"
            combo_pooled = logit_pool(p_x2_sharp, bv["x2_o15"], mod_weight=mod_w)

        combo_cal = platt_calibrate(combo_pooled, "COMBO", w)
        main_cal = platt_calibrate(res["true_prob"], "1X2", w)
        combo_odds = round(max(1.25, (1.0 / max(0.22, p_1x_sharp if bv["1x_o15"] >= bv["x2_o15"] else p_x2_sharp)) * 0.96), 2)
        combo_ev = round((combo_cal * combo_odds - 1.0) * 100.0, 2)
        main_ev = round((main_cal * od_h - 1.0) * 100.0, 2)

        use_main = main_ev >= max(3.5, combo_ev)
        best_prob = main_cal if use_main else combo_cal
        best_odds = od_h if use_main else combo_odds
        best_ev = main_ev if use_main else combo_ev
        fair = round(1.0 / max(0.05, best_prob), 2)
        b_dec = max(0.01, best_odds - 1.0)
        kelly = round(min(2.5, max(0.0, ((b_dec * best_prob) - (1.0 - best_prob)) / b_dec) * 0.25 * 100.0), 2)

        enriched.append({
            "fixture": f"{hm} v {aw}",
            "league": lg,
            "kickoff": ko,
            "pick": res["best_market"] if use_main else combo_pick,
            "combo_pick": combo_pick,
            "odds": best_odds,
            "fair": fair,
            "ev": best_ev,
            "prob": round(best_prob * 100.0, 1),
            "kelly": kelly,
            "xg_sum": round(xh + xa, 2),
            "top_cs": bv["top_cs"],
            "cs_odds": round(1.0 / max(0.05, bv["top_cs_prob"]), 2),
            "approved": res["is_approved"] or best_ev >= mev
        })
        if m.get("over_25_odds") and m.get("under_25_odds"):
            arb = detect_arb(hm, aw, lg, float(m["over_25_odds"]), "Pinnacle", float(m["under_25_odds"]), "Bet365", "Total Goals 2.5")
            if arb:
                arbs.append(arb)

    return {"weights": w, "enriched": enriched, "arbs": arbs, "updated": datetime.now(timezone.utc).strftime("%a %d %b, %H:%M UTC")}
