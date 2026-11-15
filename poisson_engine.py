import math

def poisson_pmf(lmbda, k):
    if lmbda <= 0:
        return 1.0 if k == 0 else 0.0
    return (math.exp(-lmbda) * (lmbda ** k)) / math.factorial(k)

def dixon_coles_tau(h, a, lh, la, rho=-0.13):
    if h == 0 and a == 0:
        return max(0.01, 1.0 - (lh * la * rho))
    elif h == 0 and a == 1:
        return max(0.01, 1.0 + (lh * rho))
    elif h == 1 and a == 0:
        return max(0.01, 1.0 + (la * rho))
    elif h == 1 and a == 1:
        return max(0.01, 1.0 - rho)
    return 1.0

def calculate_match_probabilities(home_attack, away_defense, away_attack, home_defense, league_avg_goals=2.65, rho=-0.13):
    home_exp = max(0.25, home_attack * away_defense * (league_avg_goals / 2.0))
    away_exp = max(0.25, away_attack * home_defense * (league_avg_goals / 2.0))
    return calculate_from_xg(home_exp, away_exp, rho=rho)

def calculate_from_xg(home_exp, away_exp, rho=-0.13):
    grid = {}
    total_p = 0.0
    for h in range(9):
        for a in range(9):
            p = poisson_pmf(home_exp, h) * poisson_pmf(away_exp, a) * dixon_coles_tau(h, a, home_exp, away_exp, rho)
            grid[(h, a)] = p
            total_p += p

    home_win = draw = away_win = over_15 = over_25 = btts = 0.0
    for (h, a), raw_p in grid.items():
        p = raw_p / total_p if total_p > 0 else 0.0
        if h > a:
            home_win += p
        elif h == a:
            draw += p
        else:
            away_win += p
        if (h + a) >= 2:
            over_15 += p
        if (h + a) >= 3:
            over_25 += p
        if h >= 1 and a >= 1:
            btts += p

    return {
        "home_win_pct": round(home_win * 100, 2),
        "draw_pct": round(draw * 100, 2),
        "away_win_pct": round(away_win * 100, 2),
        "dc_1x_pct": round((home_win + draw) * 100, 2),
        "dc_x2_pct": round((away_win + draw) * 100, 2),
        "over_15_pct": round(over_15 * 100, 2),
        "over_25_pct": round(over_25 * 100, 2),
        "btts_pct": round(btts * 100, 2),
        "expected_home_goals": round(home_exp, 2),
        "expected_away_goals": round(away_exp, 2)
    }
