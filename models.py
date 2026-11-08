import math

def poisson_probability(lmbda, k):
    try:
        return (math.exp(-lmbda) * (lmbda ** k)) / math.factorial(k)
    except Exception:
        return 0.0

def gavin_browne_correct_score(home_lambda, away_lambda):
    best_score = "1 - 1"
    max_prob = 0.0
    for h in range(4):
        for a in range(4):
            prob = poisson_probability(home_lambda, h) * poisson_probability(away_lambda, a)
            if h > a and (h - a) <= 2:
                prob *= 1.05
            elif h == a and h <= 1:
                prob *= 1.03
            if prob > max_prob:
                max_prob = prob
                best_score = f"{h} - {a}"
    model_cs_odds = round(1.0 / max(max_prob, 0.05), 2)
    return best_score, model_cs_odds

def calculate_universal_market_prediction(home_att, away_def, away_att, home_def, market_type, market_odds):
    try:
        home_lambda = max(0.5, home_att * away_def * 1.35)
        away_lambda = max(0.5, away_att * home_def * 1.20)
        
        home_win_prob = sum(poisson_probability(home_lambda, h) * poisson_probability(away_lambda, a) for h in range(5) for a in range(5) if h > a)
        draw_prob = sum(poisson_probability(home_lambda, h) * poisson_probability(away_lambda, a) for h in range(5) for a in range(5) if h == a)
        away_win_prob = sum(poisson_probability(home_lambda, h) * poisson_probability(away_lambda, a) for h in range(5) for a in range(5) if h < a)
        btts_prob = (1 - poisson_probability(home_lambda, 0)) * (1 - poisson_probability(away_lambda, 0))
        over_25_prob = 1 - sum(poisson_probability(home_lambda, h) * poisson_probability(away_lambda, a) for h in range(3) for a in range(3) if (h + a) < 3)
        over_15_prob = 1.0 - (poisson_probability(home_lambda, 0) * poisson_probability(away_lambda, 0) + poisson_probability(home_lambda, 1) * poisson_probability(away_lambda, 0) + poisson_probability(home_lambda, 0) * poisson_probability(away_lambda, 1))
        
        m_lower = market_type.lower()
        if "btts" in m_lower or "both teams" in m_lower:
            true_prob = btts_prob
        elif "over 2.5" in m_lower:
            true_prob = over_25_prob
        elif "over 1.5" in m_lower:
            true_prob = over_15_prob
        elif "double chance" in m_lower:
            true_prob = max(home_win_prob + draw_prob, draw_prob + away_win_prob)
        elif "home win" in m_lower:
            true_prob = home_win_prob
        elif "away win" in m_lower:
            true_prob = away_win_prob
        else:
            true_prob = max(home_win_prob, 0.55)
            
        adjusted_prob = min(0.95, true_prob * 1.03)
        implied_prob = 1.0 / market_odds
        ev_margin = ((adjusted_prob - implied_prob) / implied_prob) * 100
        best_score, cs_odds = gavin_browne_correct_score(home_lambda, away_lambda)
        return round(home_lambda, 2), round(away_lambda, 2), best_score, round(ev_margin, 1), round(btts_prob * 100, 1), adjusted_prob, cs_odds
    except Exception:
        return 1.25, 1.10, "1 - 1", 5.0, 55.0, 0.76, 7.50

def calculate_fractional_kelly(odds, true_prob, fraction=0.25):
    b = odds - 1.0
    q = 1.0 - true_prob
    full_kelly = (b * true_prob - q) / b
    safe_stake = max(0.0, full_kelly * fraction)
    return round(safe_stake * 100, 2)

def calculate_million_target_progress(current_bankroll, target=1000000):
    if current_bankroll <= 0:
        return 0.0, 0
    progress_pct = round((current_bankroll / target) * 100, 2)
    cycles_needed = math.ceil(math.log(target / current_bankroll) / math.log(1.03)) if current_bankroll < target else 0
    return progress_pct, cycles_needed
