import math
from ratings_engine import get_elo_xg_prior

LEAGUE_PRIORS = {
    "NATIONS_LEAGUE": (2.25, -0.16, 0.08),
    "INTERNATIONAL": (2.25, -0.16, 0.08),
    "SEGUNDA": (2.22, -0.16, 0.09),
    "SERIE_A": (2.55, -0.14, 0.07),
    "LA_LIGA": (2.52, -0.14, 0.07),
    "PREMIER_LEAGUE": (2.82, -0.12, 0.06),
    "BUNDESLIGA": (3.12, -0.09, 0.05),
    "EREDIVISIE": (3.08, -0.09, 0.05),
    "DEFAULT": (2.60, -0.13, 0.07)
}

def get_league_prior(league_key):
    k = str(league_key or "DEFAULT").upper().replace(" ", "_")
    for name, vals in LEAGUE_PRIORS.items():
        if name in k: return vals
    return LEAGUE_PRIORS["DEFAULT"]

def cap_npxg(val):
    return round(max(0.25, min(3.20, float(val))), 3)

def apply_context_multipliers(lh, la, rest_diff=0, home_shock=1.0, away_shock=1.0):
    rest_adj = max(-0.09, min(0.09, float(rest_diff) * 0.03))
    return cap_npxg(lh * (1.0 + rest_adj) * float(home_shock)), cap_npxg(la * (1.0 - rest_adj) * float(away_shock))

def estimate_decayed_xg(recent_matches, league_key="DEFAULT", home="Home", away="Away", home_adv=1.12, xi=0.0065):
    avg_g, _, _ = get_league_prior(league_key)
    base_avg = avg_g / 2.0
    elo_h, elo_a, _ = get_elo_xg_prior(home, away, base_avg=base_avg, home_adv=home_adv)
    if not recent_matches:
        return elo_h, elo_a
    w_sum = h_gf = h_ga = a_gf = a_ga = 0.0
    for m in recent_matches:
        w = math.exp(-xi * max(0.0, float(m.get("days_ago", 7))))
        h_gf += w * cap_npxg(m.get("home_gf", base_avg))
        h_ga += w * cap_npxg(m.get("home_ga", base_avg))
        a_gf += w * cap_npxg(m.get("away_gf", base_avg))
        a_ga += w * cap_npxg(m.get("away_ga", base_avg))
        w_sum += w
    if w_sum <= 0:
        return elo_h, elo_a
    form_h = cap_npxg(((h_gf / w_sum) * (a_ga / w_sum) / base_avg) * home_adv)
    form_a = cap_npxg(((a_gf / w_sum) * (h_ga / w_sum) / base_avg))
    return round(0.55 * form_h + 0.45 * elo_h, 3), round(0.55 * form_a + 0.45 * elo_a, 3)

def dixon_coles_tau(h, a, lh, la, rho=-0.13):
    if h == 0 and a == 0: return max(0.01, 1.0 - (lh * la * rho))
    if h == 0 and a == 1: return max(0.01, 1.0 + (lh * rho))
    if h == 1 and a == 0: return max(0.01, 1.0 + (la * rho))
    if h == 1 and a == 1: return max(0.01, 1.0 - rho)
    return 1.0

def nb_pmf(mu, k, alpha=0.07):
    if alpha <= 0.001:
        return (math.exp(-mu) * (mu ** k)) / math.factorial(k)
    r = 1.0 / alpha
    p = r / (r + mu)
    coeff = math.exp(math.lgamma(k + r) - math.lgamma(k + 1) - math.lgamma(r))
    return coeff * (p ** r) * ((1.0 - p) ** k)

def calculate_from_xg(home_exp, away_exp, rho=-0.13, league_key=None):
    alpha = 0.07
    if league_key:
        _, rho, alpha = get_league_prior(league_key)
    lh, la = cap_npxg(home_exp), cap_npxg(away_exp)
    grid, tot = {}, 0.0
    for h in range(9):
        for a in range(9):
            p = nb_pmf(lh, h, alpha) * nb_pmf(la, a, alpha) * dixon_coles_tau(h, a, lh, la, rho)
            grid[(h, a)] = p; tot += p
    hw = dr = aw = o15 = o25 = u25 = btts = 0.0
    for (h, a), rp in grid.items():
        p = rp / tot if tot > 0 else 0.0
        if h > a: hw += p
        elif h == a: dr += p
        else: aw += p
        if (h + a) >= 2: o15 += p
        if (h + a) >= 3: o25 += p
        else: u25 += p
        if h >= 1 and a >= 1: btts += p
    return {
        "home_win_pct": round(hw * 100, 2), "draw_pct": round(dr * 100, 2), "away_win_pct": round(aw * 100, 2),
        "dc_1x_pct": round((hw + dr) * 100, 2), "dc_x2_pct": round((aw + dr) * 100, 2),
        "over_15_pct": round(o15 * 100, 2), "over_25_pct": round(o25 * 100, 2), "under_25_pct": round(u25 * 100, 2),
        "btts_pct": round(btts * 100, 2), "expected_home_goals": lh, "expected_away_goals": la
    }
