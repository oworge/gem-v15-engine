
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ACCURACY IMPROVEMENT: Exponential Time Decay
# Weight recent matches more heavily
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
import math

def exp_decay_weight(days_ago: float, half_life_days: float = 90.0) -> float:
    """
    Calculate exponential decay weight for historical data.
    Half-life 90 days = matches ~3 months ago count half as much.
    - 0 days ago → 1.00
    - 30 days ago → 0.77
    - 90 days ago → 0.50
    - 180 days ago → 0.25
    """
    return math.exp(-math.log(2) * max(0.0, days_ago) / half_life_days)
