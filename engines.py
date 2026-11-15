from poisson_engine import calculate_from_xg

def devig_1x2(odds_h, odds_d=3.40, odds_a=4.20):
    inv_h = 1.0 / max(1.02, float(odds_h))
    inv_d = 1.0 / max(1.02, float(odds_d))
    inv_a = 1.0 / max(1.02, float(odds_a))
    overround = inv_h + inv_d + inv_a
    return inv_h / overround, inv_d / overround, inv_a / overround, round((overround - 1.0) * 100, 2)

class EngineSuite:
    def run_all_engines(self, match_id, home, away, region, xg_home=1.65, xg_away=1.05, odds=1.85, odds_draw=3.50, odds_away=4.10):
        dc = calculate_from_xg(xg_home, xg_away)
        model_h = dc["home_win_pct"] / 100.0
        model_1x = dc["dc_1x_pct"] / 100.0

        mkt_h, mkt_d, mkt_a, vig_pct = devig_1x2(odds, odds_draw, odds_away)

        # Blend 60% sharp devigged market prior + 40% Dixon-Coles xG posterior
        true_prob = (0.60 * mkt_h) + (0.40 * model_h)
        fair_odds = round(1.0 / max(0.05, true_prob), 2)
        ev_dec = (true_prob * float(odds)) - 1.0
        ev_pct = round(ev_dec * 100, 2)

        # Quarter-Kelly sizing capped at 3.0% bankroll
        b = max(0.01, float(odds) - 1.0)
        full_kelly = max(0.0, ((b * true_prob) - (1.0 - true_prob)) / b)
        q_kelly_pct = round(min(3.0, full_kelly * 0.25 * 100), 2)

        # Strict institutional gate: low vig (<=7.5%), positive EV (>=3.0%), realistic win prob (>=54%)
        is_approved = (vig_pct <= 7.5) and (ev_pct >= 3.0) and (true_prob >= 0.54)
        conf_pct = round(true_prob * 100, 1)

        return {
            "consensus_score": f"{conf_pct}%",
            "true_prob": round(true_prob, 4),
            "fair_odds": fair_odds,
            "ev_pct": ev_pct,
            "kelly_pct": q_kelly_pct,
            "overround_pct": vig_pct,
            "is_approved": is_approved,
            "consensus_status": f"VERIFIED +EV ({ev_pct:+.1f}%)" if is_approved else f"REJECTED (EV {ev_pct:+.1f}% | Vig {vig_pct}%)",
            "dixon_coles": dc,
            "value_king": {
                "source": "Dixon-Coles + No-Vig Blend",
                "confidence_score": round(true_prob, 4),
                "ev_percentage": f"{ev_pct:+.1f}%",
                "rating": "Perfect Value" if is_approved else "No Edge"
            }
        }

ENGINES = EngineSuite()
