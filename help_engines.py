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


def blend_probabilities(
    dc_prob: float,
    kalshi_prob: Optional[float] = None,
    scoreai_prob: Optional[float] = None,
    predigoal_prob: Optional[float] = None,
    weights: tuple[float, float, float, float] = (0.45, 0.20, 0.15, 0.20),
) -> dict:
    """Blend Dixon-Coles, Kalshi, ScoreAI, and Predigoal probabilities with safe fallbacks."""
    w_dc, w_k, w_s, w_p = weights
    parts: list[tuple[float, float, str]] = []

    p_dc = max(0.02, min(0.98, float(dc_prob)))
    parts.append((p_dc, w_dc, "dixon_coles"))

    if kalshi_prob is not None and 0.0 < float(kalshi_prob) < 1.0:
        parts.append((max(0.02, min(0.98, float(kalshi_prob))), w_k, "kalshi"))

    if scoreai_prob is not None and 0.0 < float(scoreai_prob) < 1.0:
        parts.append((max(0.02, min(0.98, float(scoreai_prob))), w_s, "scoreai"))

    if predigoal_prob is not None and 0.0 < float(predigoal_prob) < 1.0:
        parts.append((max(0.02, min(0.98, float(predigoal_prob))), w_p, "predigoal"))

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
