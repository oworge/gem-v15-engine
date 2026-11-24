# === GEM V15-DC-13.3 PERMANENT ALL-MARKETS ENGINE ===
import math
import json
import pathlib
import re

MARKET_GROUPS = [
    "ALL",
    "1X2",
    "BTTS",
    "O/U 2.5",
    "ESN",
    "DNB",
    "1H Draw",
    "HT/FT",
    "Correct Score",
    "DC/O1.5",
]

def _poisson_pmf(k, lam):
    lam = max(0.05, float(lam))
    return (math.exp(-lam) * (lam ** k)) / math.factorial(k)

def build_fixture_markets(lh, la, rho=-0.065):
    lh = max(0.35, min(3.60, float(lh)))
    la = max(0.25, min(3.40, float(la)))
    max_g = 7
    pmf_h = [_poisson_pmf(i, lh) for i in range(max_g + 1)]
    pmf_a = [_poisson_pmf(j, la) for j in range(max_g + 1)]

    grid = {}
    for i in range(max_g + 1):
        for j in range(max_g + 1):
            p = pmf_h[i] * pmf_a[j]
            if i == 0 and j == 0:
                p *= max(0.05, 1.0 - (lh * la * rho))
            elif i == 1 and j == 0:
                p *= max(0.05, 1.0 + (la * rho))
            elif i == 0 and j == 1:
                p *= max(0.05, 1.0 + (lh * rho))
            elif i == 1 and j == 1:
                p *= max(0.05, 1.0 - rho)
            grid[(i, j)] = max(0.0, p)

    total_p = sum(grid.values()) or 1.0
    for k in grid:
        grid[k] /= total_p

    p1 = sum(p for (i, j), p in grid.items() if i > j)
    px = sum(p for (i, j), p in grid.items() if i == j)
    p2 = sum(p for (i, j), p in grid.items() if i < j)
    po15 = sum(p for (i, j), p in grid.items() if (i + j) >= 2)
    po25 = sum(p for (i, j), p in grid.items() if (i + j) >= 3)
    pu25 = 1.0 - po25
    pbtts_y = sum(p for (i, j), p in grid.items() if i >= 1 and j >= 1)
    pbtts_n = 1.0 - pbtts_y
    pesn = max(0.01, p1 + p2)
    decisive_denom = max(0.01, p1 + p2)
    pdnb1 = p1 / decisive_denom
    pdnb2 = p2 / decisive_denom
    p1hx = math.exp(-0.44 * (lh + la)) * sum(
        _poisson_pmf(k, 0.44 * lh) * _poisson_pmf(k, 0.44 * la)
        for k in range(5)
    )
    top_cs = sorted(grid.items(), key=lambda x: x[1], reverse=True)[:3]

    markets = [
        {"group": "1X2", "code": "1", "label": "Home Win (1)", "prob": round(p1 * 100, 1), "fair_odds": round(1.0 / max(0.02, p1), 2)},
        {"group": "1X2", "code": "X", "label": "Draw (X)", "prob": round(px * 100, 1), "fair_odds": round(1.0 / max(0.02, px), 2)},
        {"group": "1X2", "code": "2", "label": "Away Win (2)", "prob": round(p2 * 100, 1), "fair_odds": round(1.0 / max(0.02, p2), 2)},
        {"group": "ESN", "code": "ESN", "label": "Either Side to Win (ESN / 12)", "prob": round(pesn * 100, 1), "fair_odds": round(1.0 / max(0.02, pesn), 2)},
        {"group": "DNB", "code": "DNB1", "label": "Home Draw No Bet (DNB 1)", "prob": round(pdnb1 * 100, 1), "fair_odds": round(1.0 / max(0.02, pdnb1), 2)},
        {"group": "DNB", "code": "DNB2", "label": "Away Draw No Bet (DNB 2)", "prob": round(pdnb2 * 100, 1), "fair_odds": round(1.0 / max(0.02, pdnb2), 2)},
        {"group": "BTTS", "code": "BTTS_Y", "label": "Both Teams to Score - Yes", "prob": round(pbtts_y * 100, 1), "fair_odds": round(1.0 / max(0.02, pbtts_y), 2)},
        {"group": "BTTS", "code": "BTTS_N", "label": "Both Teams to Score - No", "prob": round(pbtts_n * 100, 1), "fair_odds": round(1.0 / max(0.02, pbtts_n), 2)},
        {"group": "O/U 2.5", "code": "O25", "label": "Over 2.5 Match Goals", "prob": round(po25 * 100, 1), "fair_odds": round(1.0 / max(0.02, po25), 2)},
        {"group": "O/U 2.5", "code": "U25", "label": "Under 2.5 Match Goals", "prob": round(pu25 * 100, 1), "fair_odds": round(1.0 / max(0.02, pu25), 2)},
        {"group": "1H Draw", "code": "HT_X", "label": "1st Half Draw (HT X)", "prob": round(p1hx * 100, 1), "fair_odds": round(1.0 / max(0.02, p1hx), 2)},
        {"group": "HT/FT", "code": "HTFT_1_1", "label": "HT/FT: Home / Home (1/1)", "prob": round((p1 * 0.62) * 100, 1), "fair_odds": round(1.0 / max(0.02, p1 * 0.62), 2)},
        {"group": "HT/FT", "code": "HTFT_X_1", "label": "HT/FT: Draw / Home (X/1)", "prob": round((p1 * 0.28) * 100, 1), "fair_odds": round(1.0 / max(0.02, p1 * 0.28), 2)},
        {"group": "DC/O1.5", "code": "1X", "label": "Home or Draw (1X)", "prob": round((p1 + px) * 100, 1), "fair_odds": round(1.0 / max(0.02, p1 + px), 2)},
        {"group": "DC/O1.5", "code": "X2", "label": "Draw or Away (X2)", "prob": round((px + p2) * 100, 1), "fair_odds": round(1.0 / max(0.02, px + p2), 2)},
        {"group": "DC/O1.5", "code": "O15", "label": "Over 1.5 Match Goals", "prob": round(po15 * 100, 1), "fair_odds": round(1.0 / max(0.02, po15), 2)},
    ]
    for (ci, cj), cp in top_cs:
        markets.append({
            "group": "Correct Score",
            "code": f"CS_{ci}_{cj}",
            "label": f"Correct Score {ci}-{cj}",
            "prob": round(cp * 100, 1),
            "fair_odds": round(1.0 / max(0.01, cp), 2),
        })
    return markets

def load_all_unlocked_fixtures():
    fixtures = []
    seen = set()
    for fn in ("dashboard_picks.json", "static/daily_bookie_beater_slip.json", "daily_bookie_beater_slip.json"):
        p = pathlib.Path(fn)
        if not p.exists():
            continue
        try:
            raw = json.loads(p.read_text(encoding="utf-8", errors="ignore"))
            rows = raw if isinstance(raw, list) else (raw.get("picks") or raw.get("slip") or raw.get("matches") or [])
            for r in rows:
                if not isinstance(r, dict):
                    continue
                fx = str(r.get("fixture") or r.get("match") or "").strip()
                if not fx or fx in seen:
                    continue
                seen.add(fx)
                blob = " ".join(str(r.get(k) or "") for k in ("xg", "note", "reason", "market", "pk"))
                m = re.search(r"(\d+\.\d+)", blob)
                tot_xg = float(m.group(1)) if m else 2.35
                lh = round(max(0.45, tot_xg * 0.56), 2)
                la = round(max(0.35, tot_xg * 0.44), 2)
                fixtures.append({
                    "fixture": fx,
                    "league": r.get("league") or "Global Football Slate",
                    "ko": r.get("ko") or r.get("kickoff") or "TBD",
                    "lh": lh,
                    "la": la,
                    "markets": build_fixture_markets(lh, la),
                })
        except Exception:
            continue
    return fixtures
