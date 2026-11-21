import math
from typing import Optional


def _poisson_pmf(k: int, lam: float) -> float:
    lam = max(0.05, float(lam))
    return math.exp(-lam) * (lam ** k) / math.factorial(k)


def predigoal_predict(
    xg_home: float,
    xg_away: float,
    market_label: str = "Over 2.5 Match Goals",
) -> dict:
    """Predigoal predictive layer: most-likely scoreline, goal-line probs, and market signal."""
    lh = max(0.20, min(4.50, float(xg_home or 1.35)))
    la = max(0.20, min(4.50, float(xg_away or 1.15)))

    best_score = "1-1"
    best_p = -1.0
    under_35 = 0.0
    over_25 = 0.0
    over_15 = 0.0
    btts_yes = 0.0

    for h in range(0, 6):
        ph = _poisson_pmf(h, lh)
        for a in range(0, 6):
            pa = _poisson_pmf(a, la)
            p = ph * pa
            if p > best_p:
                best_p = p
                best_score = f"{h}-{a}"
            tot = h + a
            if tot <= 3:
                under_35 += p
            if tot >= 3:
                over_25 += p
            if tot >= 2:
                over_15 += p
            if h >= 1 and a >= 1:
                btts_yes += p

    total_xg = round(lh + la, 2)
    m_low = (market_label or "").lower()
    if "btts yes" in m_low:
        m_prob = btts_yes
    elif "btts no" in m_low:
        m_prob = 1.0 - btts_yes
    elif "over 2.5" in m_low:
        m_prob = over_25
    elif "under 2.5" in m_low:
        m_prob = 1.0 - over_25
    elif "over 1.5" in m_low:
        m_prob = over_15
    elif "under 3.5" in m_low:
        m_prob = under_35
    else:
        m_prob = over_25 if total_xg >= 2.65 else over_15

    return {
        "predicted_score": best_score,
        "score_prob": round(max(0.03, min(0.65, best_p)), 4),
        "total_xg": total_xg,
        "over_15_prob": round(max(0.10, min(0.96, over_15)), 4),
        "over_25_prob": round(max(0.08, min(0.92, over_25)), 4),
        "under_35_prob": round(max(0.10, min(0.95, under_35)), 4),
        "btts_yes_prob": round(max(0.08, min(0.92, btts_yes)), 4),
        "predigoal_prob": round(max(0.05, min(0.95, m_prob)), 4),
    }


def opta_signal(
    xg_home: float,
    xg_away: float,
    dc_prob: float,
    opta_xg_home: Optional[float] = None,
    opta_xg_away: Optional[float] = None,
    opta_prob: Optional[float] = None,
) -> dict:
    """Opta shot-quality & xG layer with clean fallback to Dixon-Coles rates."""
    oh = float(opta_xg_home) if opta_xg_home is not None else float(xg_home or 1.35)
    oa = float(opta_xg_away) if opta_xg_away is not None else float(xg_away or 1.15)
    oh = max(0.15, min(4.50, oh))
    oa = max(0.15, min(4.50, oa))

    if opta_prob is not None and 0.0 < float(opta_prob) < 1.0:
        p_out = float(opta_prob)
    else:
        # Slight xG-ratio adjustment around Dixon-Coles baseline
        base_xg = max(0.40, float(xg_home or 1.35) + float(xg_away or 1.15))
        opta_xg = oh + oa
        delta = max(-0.08, min(0.08, (opta_xg - base_xg) * 0.05))
        p_out = float(dc_prob) + delta

    return {
        "opta_xg_home": round(oh, 3),
        "opta_xg_away": round(oa, 3),
        "opta_xg_total": round(oh + oa, 2),
        "opta_prob": round(max(0.03, min(0.96, p_out)), 4),
    }


def sportsbook_implied_prob(
    decimal_odds: Optional[float],
    overround_haircut: float = 0.945,
) -> Optional[float]:
    """Convert sportsbook decimal odds into devigged implied win/market probability."""
    if decimal_odds is None:
        return None
    try:
        odds_val = float(decimal_odds)
    except (TypeError, ValueError):
        return None
    if odds_val <= 1.01:
        return None
    haircut = max(0.85, min(1.0, float(overround_haircut)))
    implied = (1.0 / odds_val) * haircut
    return round(max(0.03, min(0.95, implied)), 4)


def blend_probabilities(
    dc_prob: float,
    kalshi_prob: Optional[float] = None,
    scoreai_prob: Optional[float] = None,
    predigoal_prob: Optional[float] = None,
    opta_prob: Optional[float] = None,
    sportsbook_prob: Optional[float] = None,
    weights: tuple[float, float, float, float, float, float] = (
        0.35,
        0.15,
        0.10,
        0.15,
        0.15,
        0.10,
    ),
) -> dict:
    """Blend Dixon-Coles, Kalshi, ScoreAI, Predigoal, Opta, and Sportsbook probabilities."""
    w_dc, w_k, w_s, w_p, w_o, w_sb = weights
    parts: list[tuple[float, float, str]] = []

    p_dc = max(0.02, min(0.98, float(dc_prob)))
    parts.append((p_dc, w_dc, "dixon_coles"))

    candidates = [
        (kalshi_prob, w_k, "kalshi"),
        (scoreai_prob, w_s, "scoreai"),
        (predigoal_prob, w_p, "predigoal"),
        (opta_prob, w_o, "opta"),
        (sportsbook_prob, w_sb, "sportsbook"),
    ]
    for val, weight, name in candidates:
        if val is not None and 0.0 < float(val) < 1.0:
            parts.append((max(0.02, min(0.98, float(val))), weight, name))

    total_w = sum(w for _, w, _ in parts)
    blended_prob = sum(p * w for p, w, _ in parts) / total_w
    sources_used = [name for _, _, name in parts]

    probs_only = [p for p, _, _ in parts]
    spread_pct = round((max(probs_only) - min(probs_only)) * 100.0, 1)

    return {
        "blended_prob": round(blended_prob, 4),
        "sources_used": sources_used,
        "consensus_spread_pct": spread_pct,
    }
