# ==========================================================
# EDGEMETRIX — VALUE ENGINE CORE
# Auto-filter · EV calculation · Kelly staking · Quality Control
# ==========================================================
import math

# ─── STRATEGY RULES ───
MIN_EDGE = 0.04      # Bet only when model beats market by 4%+
MAX_EDGE = 0.20      # Reject suspicious edges (>20% = likely bad data)
MIN_EV = 0.02        # Minimum +2% EV to bet
KELLY_FRACTION = 0.30  # Conservative 30% Kelly
MIN_STAKE_PCT = 0.5   # 0.5% of bankroll minimum
MAX_STAKE_PCT = 4.0   # 4% of bankroll maximum

def calculate_value_decision(model_prob, devig_prob, odds):
    """
    The Heart of the System: Decide BET or SKIP
    Returns: decision dict — bet?, why?, edge%, ev%, stake%
    """
    result = {
        "bet": False,
        "reason": "",
        "edge_pct": 0.0,
        "ev_pct": 0.0,
        "stake_pct": 0.0,
        "grade": "❌"
    }

    # Safety checks
    if not all([model_prob, devig_prob, odds]) or odds <= 1.0:
        result["reason"] = "⚠️ Missing data or invalid odds"
        return result

    # Core calculations
    edge = model_prob - devig_prob
    ev = (model_prob * odds) - 1

    result["edge_pct"] = round(edge * 100, 2)
    result["ev_pct"] = round(ev * 100, 2)

    # ─── FILTERS — THE GATES ───
    if ev < MIN_EV:
        result["reason"] = f"❌ EV too low ({result['ev_pct']:.1f}%) — pass"
        return result

    if edge < MIN_EDGE:
        result["reason"] = f"⚠️ Edge too small ({result['edge_pct']:.1f}%) — not confident"
        return result

    if abs(edge) > MAX_EDGE:
        result["reason"] = f"🚩 Suspicious edge ({result['edge_pct']:.1f}%) — data check needed"
        result["grade"] = "⚠️"
        return result

    # ─── PASSED ALL GATES — CALCULATE STAKE ───
    b = odds - 1
    p = model_prob
    q = 1 - p
    kelly_raw = ((b * p) - q) / b if b > 0 else 0
    stake_pct = kelly_raw * KELLY_FRACTION

    # Clamp stake to safe limits
    stake_pct = max(MIN_STAKE_PCT / 100, min(MAX_STAKE_PCT / 100, stake_pct))

    result["bet"] = True
    result["reason"] = f"✅ VALUE FOUND · Edge +{result['edge_pct']:.1f}% · EV +{result['ev_pct']:.1f}%"
    result["stake_pct"] = round(stake_pct * 100, 2)
    result["grade"] = "🔥" if ev >= 0.08 else "✅" if ev >= 0.05 else "✓"
    return result


def rank_daily_picks(fixture_list):
    """
    Process all fixtures → filter → sort BEST VALUE FIRST
    """
    vetted_bets = []
    for fx in fixture_list:
        decision = calculate_value_decision(
            model_prob=fx.get("p_f"),
            devig_prob=fx.get("pd_devig"),
            odds=fx.get("best_odds")
        )
        fx.update(decision)
        if decision["bet"]:
            vetted_bets.append(fx)
    
    # BEST VALUE AT THE TOP — highest EV first
    vetted_bets.sort(key=lambda x: (-x["ev_pct"], -x["edge_pct"]))
    return vetted_bets


def format_pick_for_display(pick, index=1):
    """Clean dashboard-ready string"""
    return (
        f"{pick.get('grade','✓')} #{index}  {pick.get('kickoff','')}\n"
        f"⚽ {pick.get('home_team','')} v {pick.get('away_team','')}\n"
        f"   → {pick.get('selection','')}\n"
        f"🏆 {pick.get('league','')}  ·  {pick.get('market','1X2')}\n"
        f"📊 Model: {pick.get('model_prob_pct',0):.1f}%  |  Market: {pick.get('devig_prob_pct',0):.1f}%\n"
        f"📈 Edge: +{pick.get('edge_pct',0):.1f}%  |  EV: +{pick.get('ev_pct',0):.1f}%\n"
        f"💰 Odds: {pick.get('odds',0):.2f}  |  Stake: £{pick.get('stake_pct',0):.2f}\n"
        f"────────────────────────────────────────────────────"
    )
