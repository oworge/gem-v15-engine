import math
from poisson_engine import calculate_from_xg, estimate_decayed_xg, apply_context_multipliers
from ratings_engine import get_elo_xg_prior

def power_devig(odds_list):
    clean = [max(1.02, float(o)) for o in odds_list if o and float(o) > 1.01]
    if len(clean) < 2: return [1.0 / clean[0]], 0.0
    overround = sum(1.0 / o for o in clean)
    lo, hi = 0.5, 2.5
    for _ in range(35):
        mid = 0.5 * (lo + hi)
        if sum((1.0 / o) ** mid for o in clean) > 1.0: lo = mid
        else: hi = mid
    k = 0.5 * (lo + hi)
    probs = [(1.0 / o) ** k for o in clean]
    tot = sum(probs)
    return [p / tot for p in probs], round((overround - 1.0) * 100, 2)

class EngineSuite:
    def score_parlay(self, legs, corr_discount=0.97):
        if len(legs) != 3: return {"approved": False, "ev_pct": 0.0}
        cp, co = corr_discount, 1.0
        for l in legs:
            cp *= float(l["true_prob"]); co *= float(l["odds"])
        ev = round(((cp * co) - 1.0) * 100, 2)
        return {"approved": ev >= 4.5, "combined_prob_pct": round(cp * 100, 2), "combined_odds": round(co, 2), "ev_pct": ev}

    def run_all_engines(self, match_id, home, away, region, xg_home=None, xg_away=None, odds=1.90, odds_draw=3.50, odds_away=4.00, open_odds=None, recent_matches=None, league_key="DEFAULT", rest_diff=0, home_shock=1.0, away_shock=1.0, over_25_odds=None, under_25_odds=None, btts_yes_odds=None):
        _, _, sigma = get_elo_xg_prior(home, away)
        if xg_home is None or xg_away is None:
            xg_home, xg_away = estimate_decayed_xg(recent_matches, league_key=league_key, home=home, away=away)
        xg_home, xg_away = apply_context_multipliers(xg_home, xg_away, rest_diff=rest_diff, home_shock=home_shock, away_shock=away_shock)
        dc = calculate_from_xg(xg_home, xg_away, league_key=league_key)

        mkt_probs, vig_pct = power_devig([odds, odds_draw, odds_away])
        mkt_h, mkt_d, mkt_a = mkt_probs[0], mkt_probs[1], mkt_probs[2]

        steam_drift = ((float(odds) - float(open_odds)) / float(open_odds) * 100.0) if open_odds and float(open_odds) > 1.01 else 0.0
        steam_ok = steam_drift <= 3.5

        # Full multi-market evaluation ranked by Sharpe-adjusted EV
        markets = [
            ("Home Win", dc["home_win_pct"] / 100.0, mkt_h, float(odds)),
            ("Away Win", dc["away_win_pct"] / 100.0, mkt_a, float(odds_away)),
            ("Double Chance 1X", dc["dc_1x_pct"] / 100.0, min(0.95, mkt_h + mkt_d), round(1.0 / max(0.10, (mkt_h + mkt_d) * 1.04), 2)),
            ("Double Chance X2", dc["dc_x2_pct"] / 100.0, min(0.95, mkt_a + mkt_d), round(1.0 / max(0.10, (mkt_a + mkt_d) * 1.04), 2))
        ]
        if over_25_odds and under_25_odds:
            ou_p, _ = power_devig([over_25_odds, under_25_odds])
            markets.append(("Over 2.5 Goals", dc["over_25_pct"] / 100.0, ou_p[0], float(over_25_odds)))
            markets.append(("Under 2.5 Goals", dc["under_25_pct"] / 100.0, ou_p[1], float(under_25_odds)))
        if btts_yes_odds:
            markets.append(("BTTS Yes", dc["btts_pct"] / 100.0, 1.0 / (float(btts_yes_odds) * 1.05), float(btts_yes_odds)))

        best = None
        for label, mod_p, mkt_p, m_odds in markets:
            tp = (0.60 * mkt_p) + (0.40 * mod_p)
            ev_dec = (tp * m_odds) - 1.0
            ev_pct = round(ev_dec * 100, 2)
            std = math.sqrt(max(0.01, tp * (1.0 - tp))) * m_odds
            sharpe = ev_dec / std
            if best is None or sharpe > best["sharpe"]:
                best = {"market": label, "tp": tp, "odds": m_odds, "ev": ev_pct, "sharpe": sharpe}

        tp, m_odds, ev_pct = best["tp"], best["odds"], best["ev"]
        fair_odds = round(1.0 / max(0.05, tp), 2)
        b = max(0.01, m_odds - 1.0)
        q_kelly = round(min(2.5, max(0.0, ((b * tp) - (1.0 - tp)) / b) * 0.25 * 100), 2)

        # Higher uncertainty (sigma) tightens required EV slightly
        req_ev = round(4.5 + max(0.0, (sigma - 0.14) * 10.0), 2)
        is_approved = steam_ok and (vig_pct <= 7.5) and (ev_pct >= req_ev) and (tp >= 0.54)
        return {
            "consensus_score": f"{round(tp * 100, 1)}%",
            "best_market": best["market"],
            "true_prob": round(tp, 4),
            "fair_odds": fair_odds,
            "ev_pct": ev_pct,
            "required_ev_pct": req_ev,
            "kelly_pct": q_kelly,
            "overround_pct": vig_pct,
            "is_approved": is_approved,
            "consensus_status": f"VERIFIED {best['market']} ({ev_pct:+.1f}% EV)" if is_approved else f"REJECTED (EV {ev_pct:+.1f}% < {req_ev}%)",
            "dixon_coles": dc
        }

ENGINES = EngineSuite()
