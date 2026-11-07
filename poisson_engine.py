import math

def factorial(n):
    if n == 0 or n == 1:
        return 1
    return math.factorial(n)

def poisson_probability(lmbda, k):
    """Calculates the probability of k events occurring given expected lambda."""
    return (math.exp(-lmbda) * (lmbda ** k)) / factorial(k)

def calculate_match_probabilities(home_attack, away_defense, away_attack, home_defense, league_avg_goals=2.75):
    """
    Calculates exact win/draw/loss probabilities using Poisson Distribution.
    """
    # 1. Calculate Expected Goals (xG) for the fixture
    home_exp_goals = home_attack * away_defense * (league_avg_goals / 2)
    away_exp_goals = away_attack * home_defense * (league_avg_goals / 2)
    
    home_win_prob = 0.0
    draw_prob = 0.0
    away_win_prob = 0.0
    
    # 2. Iterate through realistic scorelines (0 to 6 goals for each team)
    for h in range(7):
        for a in range(7):
            p_home = poisson_probability(home_exp_goals, h)
            p_away = poisson_probability(away_exp_goals, a)
            match_score_prob = p_home * p_away
            
            if h > a:
                home_win_prob += match_score_prob
            elif h == a:
                draw_prob += match_score_prob
            else:
                away_win_prob += match_score_prob
                
    return {
        "home_win_pct": round(home_win_prob * 100, 2),
        "draw_pct": round(draw_prob * 100, 2),
        "away_win_pct": round(away_win_prob * 100, 2),
        "expected_home_goals": round(home_exp_goals, 2),
        "expected_away_goals": round(away_exp_goals, 2)
    }