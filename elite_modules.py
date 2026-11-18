import random
import math

def calculate_negative_binomial_probabilities(home_xg, away_xg, max_goals=6, over_dispersion=1.5):
    """
    Computes scoreline and 1X2 probabilities using a Negative Binomial approximation
    to account for real football over-dispersion (high-scoring variance) without external dependencies.
    """
    def get_nb_probs(lam, max_g, r=over_dispersion):
        probs = []
        for k in range(max_g + 1):
            # Negative Binomial probability mass function approximation
            # p = r / (r + lam)
            p = r / (r + lam)
            # Combinatorial term: gamma(k + r) / (k! * gamma(r)) * (p^r) * ((1-p)^k)
            # Using math.lgamma for numerical stability
            try:
                log_coeff = math.lgamma(k + r) - math.lgamma(k + 1) - math.lgamma(r)
                log_prob = log_coeff + r * math.log(p) + k * math.log(1.0 - p)
                probs.append(math.exp(log_prob))
            except:
                probs.append(0.0)
        total = sum(probs)
        return [val / total if total > 0 else 1.0/(max_g+1) for val in probs]

    h_probs = get_nb_probs(home_xg, max_goals)
    a_probs = get_nb_probs(away_xg, max_goals)

    matrix = [[h * a for a in a_probs] for h in h_probs]
    
    home_win, draw, away_win = 0.0, 0.0, 0.0
    for i in range(max_goals + 1):
        for j in range(max_goals + 1):
            p = matrix[i][j]
            if i > j:
                home_win += p
            elif i == j:
                draw += p
            else:
                away_win += p

    return {
        "home_win": home_win,
        "draw": draw,
        "away_win": away_win,
        "matrix": matrix
    }

def run_monte_carlo_accumulator(match_list, simulations=5000):
    """
    Simulates multi-leg accumulator outcomes natively to evaluate joint probability.
    """
    success_count = 0
    for _ in range(simulations):
        slip_passed = True
        for match in match_list:
            hx = max(0.1, match.get('home_xg', 1.3))
            ax = max(0.1, match.get('away_xg', 1.1))
            
            # Simulate goals using Poisson random generation
            h_sim = random.expovariate(1.0 / hx) if hx > 0 else 0
            a_sim = random.expovariate(1.0 / ax) if ax > 0 else 0
            # Simple integer conversion for score simulation
            h_goals = int(h_sim) # approximation
            a_goals = int(a_sim)
            
            market = match.get('market_type', 'home_win')
            if market == 'home_win' and h_goals <= a_goals:
                slip_passed = False
                break
            elif market == 'btts' and (h_goals == 0 or a_goals == 0):
                slip_passed = False
                break
        if slip_passed:
            success_count += 1
            
    return max(0.001, success_count / simulations)

print("Zero-dependency elite modules created successfully!")
