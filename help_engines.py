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


def forebet_math_signal(
    xg_home: float,
    xg_away: float,
    dc_prob: float,
    market_label: str = "Over 2.5 Match Goals",
    forebet_prob: Optional[float] = None,
    forebet_score: Optional[str] = None,
) -> dict:
    """Forebet pure-math model: mathematical scoreline and probability without human bias."""
    pg = predigoal_predict(xg_home, xg_away, market_label)
    math_p = float(forebet_prob) if (forebet_prob is not None and 0.0 < float(forebet_prob) < 1.0) else (
        0.55 * float(dc_prob) + 0.45 * pg["predigoal_prob"]
    )
    return {
        "forebet_score": forebet_score or pg["predicted_score"],
        "forebet_prob": round(max(0.03, min(0.96, math_p)), 4),
        "pure_math_mode": True,
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
    forebet_prob: Optional[float] = None,
    olbg_prob: Optional[float] = None,
    betmines_prob: Optional[float] = None,
    football_ai_prob: Optional[float] = None,
    sofascore_prob: Optional[float] = None,
    tipstrr_prob: Optional[float] = None,
    pure_math_prob: Optional[float] = None,
    weights_override: Optional[dict[str, float]] = None,
) -> dict:
    """Blend all available predictive engines with clean fallbacks and zero filtering."""
    weighted_sources: list[tuple[Optional[float], float, str]] = [
        (dc_prob, 0.30, "dixon_coles"),
        (forebet_prob, 0.14, "forebet"),
        (opta_prob, 0.14, "opta"),
        (predigoal_prob, 0.12, "predigoal"),
        (kalshi_prob, 0.08, "kalshi"),
        (sportsbook_prob, 0.06, "sportsbook"),
        (football_ai_prob, 0.04, "football_ai"),
        (betmines_prob, 0.03, "betmines"),
        (sofascore_prob, 0.02, "sofascore"),
        (olbg_prob, 0.01, "olbg"),
        (tipstrr_prob, 0.01, "tipstrr"),
        (pure_math_prob, 0.10, "pure_math"),
    ]

    w_map = weights_override or {}
    parts: list[tuple[float, float, str]] = []
    for val, weight, name in weighted_sources:
        eff_w = float(w_map.get(name, weight))
        if val is not None and 0.0 < float(val) < 1.0:
            parts.append((max(0.02, min(0.98, float(val))), max(0.005, eff_w), name))

    if not parts:
        parts.append((max(0.02, min(0.98, float(dc_prob))), 1.0, "dixon_coles"))

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


def _clamp_prob(p: float, lo: float = 0.02, hi: float = 0.98) -> float:
    return max(lo, min(hi, float(p)))


def pure_math_strategy(
    prob: float,
    decimal_odds: float,
    anchor_prob: Optional[float] = None,
    shrinkage: float = 0.25,
    kelly_fraction: float = 0.25,
    max_stake_pct: float = 2.0,
) -> dict:
    """Pure mathematical strategy: logit shrinkage, EV, breakeven prob, and fractional Kelly."""
    p_raw = _clamp_prob(prob, 0.05, 0.95)
    odds_val = max(1.05, float(decimal_odds or 1.80))
    breakeven_p = 1.0 / odds_val

    ref_p = _clamp_prob(anchor_prob if anchor_prob is not None else breakeven_p, 0.05, 0.95)
    lam = max(0.0, min(0.80, float(shrinkage)))

    logit_p = math.log(p_raw / (1.0 - p_raw))
    logit_ref = math.log(ref_p / (1.0 - ref_p))
    shrunk_logit = ((1.0 - lam) * logit_p) + (lam * logit_ref)
    p_math = 1.0 / (1.0 + math.exp(-shrunk_logit))
    p_math = _clamp_prob(p_math, 0.05, 0.95)

    ev_decimal = (p_math * odds_val) - 1.0
    raw_kelly = ev_decimal / max(0.05, odds_val - 1.0)
    adj_kelly_pct = max(0.0, min(float(max_stake_pct), raw_kelly * float(kelly_fraction) * 100.0))

    return {
        "pure_math_prob": round(p_math, 4),
        "breakeven_prob": round(breakeven_p, 4),
        "ev_pct": round(ev_decimal * 100.0, 2),
        "raw_kelly_pct": round(max(0.0, raw_kelly * 100.0), 2),
        "recommended_stake_pct": round(adj_kelly_pct, 2),
        "shrinkage_applied": lam,
    }


def power_devig(implied_probs: list[float]) -> list[float]:
    """Power-method overround removal: finds k such that sum(p_i ** k) == 1.0."""
    cleaned = [_clamp_prob(p, 0.01, 0.99) for p in (implied_probs or []) if p is not None]
    if not cleaned:
        return []
    if len(cleaned) == 1:
        return [round(min(0.95, cleaned[0] * 0.95), 4)]
    total = sum(cleaned)
    if abs(total - 1.0) < 1e-6:
        return [round(p, 4) for p in cleaned]

    lo, hi = 0.5, 3.0
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        s = sum(p ** mid for p in cleaned)
        if s > 1.0:
            lo = mid
        else:
            hi = mid
    k = 0.5 * (lo + hi)
    denom = sum(p ** k for p in cleaned) or 1.0
    return [round((p ** k) / denom, 4) for p in cleaned]


def sharp_soft_edge(
    model_prob: float,
    soft_odds: float,
    sharp_prob: Optional[float] = None,
) -> dict:
    """Compute true edge over soft book odds and devigged sharp baseline."""
    p_m = _clamp_prob(model_prob, 0.05, 0.95)
    o_s = max(1.05, float(soft_odds or 1.80))
    soft_implied = 1.0 / o_s
    edge_soft_pct = ((p_m * o_s) - 1.0) * 100.0
    anchor = _clamp_prob(sharp_prob, 0.05, 0.95) if sharp_prob is not None else min(0.95, soft_implied * 0.95)
    edge_sharp_pct = (p_m - anchor) * 100.0
    return {
        "soft_implied_prob": round(soft_implied, 4),
        "sharp_anchor_prob": round(anchor, 4),
        "edge_vs_soft_pct": round(edge_soft_pct, 2),
        "edge_vs_sharp_pct": round(edge_sharp_pct, 2),
    }
