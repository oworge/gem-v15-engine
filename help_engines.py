from typing import Optional


def blend_probabilities(
    dc_prob: float,
    kalshi_prob: Optional[float] = None,
    scoreai_prob: Optional[float] = None,
    weights: tuple[float, float, float] = (0.55, 0.25, 0.20),
) -> dict:
    w_dc, w_k, w_s = weights
    parts: list[tuple[float, float, str]] = []

    p_dc = max(0.02, min(0.98, float(dc_prob)))
    parts.append((p_dc, w_dc, "dixon_coles"))

    if kalshi_prob is not None and 0.0 < float(kalshi_prob) < 1.0:
        parts.append((max(0.02, min(0.98, float(kalshi_prob))), w_k, "kalshi"))

    if scoreai_prob is not None and 0.0 < float(scoreai_prob) < 1.0:
        parts.append((max(0.02, min(0.98, float(scoreai_prob))), w_s, "scoreai"))

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
