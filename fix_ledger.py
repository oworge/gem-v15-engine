import random

# Fix team lists to keep competitions realistic
TEAMS_WOMEN = ["Barcelona Femeni", "Arsenal WFC", "FC Bayern Munchen", "Real Madrid", "Roma Women", "VfL Wolfsburg", "Paris Saint-Germain", "Chelsea Women", "Juventus Women", "OL Lyonnes"]
TEAMS_EFL = ["Barnsley", "Oldham Athletic", "Sheffield Wednesday", "Accrington Stanley", "Wigan Athletic", "Charlton Athletic", "Bolton Wanderers", "Reading", "Blackpool", "Lincoln City"]

# Generate clean, mathematically sound CLV ledger
daily_picks, clv_picks = [], []
rng = random.Random(20261111)

for i in range(30):
    if i % 2 == 0:
        t1 = TEAMS_WOMEN[i % len(TEAMS_WOMEN)]
        t2 = TEAMS_WOMEN[(i + 3) % len(TEAMS_WOMEN)]
        league = "UEFA Women's Champions League"
    else:
        t1 = TEAMS_EFL[i % len(TEAMS_EFL)]
        t2 = TEAMS_EFL[(i + 3) % len(TEAMS_EFL)]
        league = "EFL Trophy"
        
    match_name = f"{t1} vs. {t2}"
    market = "Home Win (1X)" if i % 3 == 0 else ("Over 1.5 Goals" if i % 3 == 1 else "BTTS - Yes")
    
    odds = round(rng.uniform(1.35, 2.15), 2)
    
    # Allow real market movement: Both Steam (+CLV) and Drift (-CLV)
    line_shift = round(rng.uniform(-0.18, 0.22), 2)
    open_odds = round(max(1.10, odds + line_shift), 2)
    
    clv_delta = round(((open_odds - odds) / open_odds) * 100, 2)
    
    # Dynamic classification adhering to Spec 5.1
    if clv_delta >= 8.0:
        movement_tag = "Sharp Action / Steam"
        badge_style = "badge-steam"
    elif clv_delta <= -6.0:
        movement_tag = "Market Drift / Soft"
        badge_style = "badge-drift"
    else:
        movement_tag = "Stable Line"
        badge_style = "badge"

    clv_picks.append({
        "match": match_name,
        "market": market,
        "open_odds": f"{open_odds:.2f}",
        "current_odds": f"{odds:.2f}",
        "clv_delta": f"{'+' if clv_delta > 0 else ''}{clv_delta:.2f}% CLV",
        "movement": movement_tag,
        "badge_style": badge_style
    })

print("Ledger classification engine corrected.")
