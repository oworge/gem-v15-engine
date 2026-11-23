# ==========================================================
# DASHBOARD ENGINE — Creates league tabs from picks
# ==========================================================

LEAGUE_FILTERS = {
    "All Vetted": lambda p: True,
    "UK Leagues": lambda p: any(x in str(p.get("league","")) for x in ["England", "Scotland", "Wales", "Northern Ireland"]),
    "Europe": lambda p: any(x in str(p.get("league","")) for x in ["France", "Italy", "Germany", "Spain", "Netherlands", "Portugal"]),
    "France": lambda p: "France" in str(p.get("league","")),
    "Italy": lambda p: "Italy" in str(p.get("league","")),
    "Germany": lambda p: "Germany" in str(p.get("league","")),
    "Spain": lambda p: "Spain" in str(p.get("league","")),
    "The rest of the world": lambda p: any(x in str(p.get("league","")) for x in ["USA", "Brazil", "Mexico", "Japan", "Australia"]),
    "Bet Builder": lambda p: "Both Teams" in str(p.get("selection","")) or "Over" in str(p.get("selection",""))
}

def generate_dashboard_tabs(all_picks):
    tabs = {}
    for tab_name, filter_fn in LEAGUE_FILTERS.items():
        tabs[tab_name] = [p for p in all_picks if filter_fn(p)]
    
    # Special curated tabs
    tabs["Perfect Value"] = [p for p in all_picks if p.get("ev_pct",0) >= 5.0][:12]
    tabs["Today's Picks"] = all_picks[:8]
    tabs["Likely"] = [p for p in all_picks if p.get("model_prob_pct", 50) >= 65]
    tabs["Value"] = [p for p in all_picks if 3.0 <= p.get("ev_pct", 0) <= 10.0]
    
    return {
        "bets_found": len(all_picks),
        "tabs": tabs
    }
