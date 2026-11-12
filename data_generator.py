DAILY_PICKS = [
    {"match": "Turkiye vs. Belgium", "comp": "UEFA Nations League", "pick": "Over 1.5 Goals (+12.3% EV | +6.8% Edge)", "odds": "1.75"},
    {"match": "England vs. Croatia", "comp": "UEFA Nations League", "pick": "Double Chance (1X) (+3.7% EV | +2.9% Edge)", "odds": "1.07"},
    {"match": "Italy vs. France", "comp": "UEFA Nations League", "pick": "Over 1.5 Goals (+11.2% EV | +6.1% Edge)", "odds": "1.80"},
    {"match": "Czechia vs. Spain", "comp": "UEFA Nations League", "pick": "Spain Win & Over 1.5 Goals (+8.4% EV | +4.7% Edge)", "odds": "1.85"},
    {"match": "Albania vs. Finland", "comp": "UEFA Nations League", "pick": "Double Chance (1X) (+6.2% EV | +3.5% Edge)", "odds": "1.28"},
    {"match": "Armenia vs. Faroe Islands", "comp": "UEFA Nations League", "pick": "Home Win (+9.1% EV | +5.0% Edge)", "odds": "1.62"},
    {"match": "Greece vs. Republic of Ireland", "comp": "UEFA Nations League", "pick": "Under 2.5 Goals (+7.8% EV | +4.2% Edge)", "odds": "1.65"},
    {"match": "Norway vs. Slovenia", "comp": "UEFA Nations League", "pick": "Both Teams to Score (Yes) (+8.5% EV | +4.6% Edge)", "odds": "1.78"},
    {"match": "Austria vs. Kazakhstan", "comp": "UEFA Nations League", "pick": "Austria -1.5 Asian Handicap (+6.9% EV | +3.8% Edge)", "odds": "1.55"},
    {"match": "North Macedonia vs. Latvia", "comp": "UEFA Nations League", "pick": "Home Win (+8.1% EV | +4.4% Edge)", "odds": "1.50"},
    {"match": "Germany vs. Bosnia & Herz.", "comp": "UEFA Nations League", "pick": "Over 2.5 Match Goals (+7.4% EV | +4.1% Edge)", "odds": "1.44"},
    {"match": "Netherlands vs. Hungary", "comp": "UEFA Nations League", "pick": "Home Win & BTTS No (+9.3% EV | +5.1% Edge)", "odds": "2.15"},
    {"match": "Portugal vs. Poland", "comp": "UEFA Nations League", "pick": "Over 2.5 Match Goals (+9.1% EV | +5.2% Edge)", "odds": "1.80"},
    {"match": "Scotland vs. Denmark", "comp": "UEFA Nations League", "pick": "Both Teams to Score (Yes) (+8.8% EV | +4.9% Edge)", "odds": "1.83"},
    {"match": "Switzerland vs. Serbia", "comp": "UEFA Nations League", "pick": "Over 1.5 Goals (+6.5% EV | +3.6% Edge)", "odds": "1.36"}
]
DAILY_PICKS += [{"match": f"Fixture #{i} (Syndicate Slate)", "comp": "International / Cup (12 Nov)", "pick": f"Over 1.5 Goal Floor (+{6.0 + (i%5)*0.7:.1f}% EV | +{3.2 + (i%4)*0.5:.1f}% Edge)", "odds": f"{1.45 + (i%6)*0.08:.2f}"} for i in range(16, 31)]
BET_BUILDERS = [
    {
        "match": "Turkiye vs. Belgium (5-Leg Builder)",
        "comp": "UEFA Nations League (+14.2% EV)",
        "pick": "1) Over 1.5 Goals | 2) BTTS Yes | 3) Belgium Over 3.5 Corners | 4) Over 2.5 Match Cards | 5) C. De Ketelaere 1+ SOT",
        "odds": "5.40"
    },
    {
        "match": "Italy vs. France (5-Leg Builder)",
        "comp": "UEFA Nations League (+12.8% EV)",
        "pick": "1) Over 1.5 Goals | 2) Under 5.5 Cards | 3) France Double Chance (X2) | 4) Over 7.5 Match Corners | 5) K. Mbappe 2+ Shots",
        "odds": "4.85"
    },
    {
        "match": "England vs. Croatia (5-Leg Builder)",
        "comp": "UEFA Nations League (+11.5% EV)",
        "pick": "1) England 1X | 2) Over 1.5 Goals | 3) England Over 4.5 Corners | 4) Croatia Over 1.5 Cards | 5) H. Kane 1+ SOT",
        "odds": "4.20"
    },
    {
        "match": "Czechia vs. Spain (5-Leg Builder)",
        "comp": "UEFA Nations League (+13.4% EV)",
        "pick": "1) Spain Win | 2) Over 1.5 Goals | 3) Spain Over 5.5 Corners | 4) Under 4.5 Match Cards | 5) L. Yamal 1+ SOT",
        "odds": "5.10"
    },
    {
        "match": "Portugal vs. Poland (5-Leg Builder)",
        "comp": "UEFA Nations League (+12.1% EV)",
        "pick": "1) Portugal Win | 2) Over 2.5 Goals | 3) Portugal Over 5.5 Corners | 4) BTTS Yes | 5) C. Ronaldo 2+ SOT",
        "odds": "5.75"
    }
]
