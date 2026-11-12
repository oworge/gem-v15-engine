def calculate_dynamic_baselines(fixtures_data):
    league_goals = {}
    league_match_counts = {}
    team_stats = {}

    for fixture in fixtures_data:
        league = fixture.get("league", "General")
        h_team = fixture.get("home_team")
        a_team = fixture.get("away_team")
        h_goals = fixture.get("home_goals", 1.3)
        a_goals = fixture.get("away_goals", 1.1)

        league_goals[league] = league_goals.get(league, 0) + h_goals + a_goals
        league_match_counts[league] = league_match_counts.get(league, 0) + 1

        for team in [h_team, a_team]:
            if team not in team_stats:
                team_stats[team] = {"scored": 0, "conceded": 0, "matches": 0}

        team_stats[h_team]["scored"] += h_goals
        team_stats[h_team]["conceded"] += a_goals
        team_stats[h_team]["matches"] += 1

        team_stats[a_team]["scored"] += a_goals
        team_stats[a_team]["conceded"] += h_goals
        team_stats[a_team]["matches"] += 1

    league_averages = {}
    for league, total_goals in league_goals.items():
        matches = league_match_counts.get(league, 1)
        league_averages[league] = total_goals / max(matches, 1)

    adjusted_team_strengths = {}
    for team, stats in team_stats.items():
        matches = max(stats["matches"], 1)
        adjusted_team_strengths[team] = {
            "attack_strength": round(stats["scored"] / matches, 3),
            "defence_vulnerability": round(stats["conceded"] / matches, 3)
        }

    return league_averages, adjusted_team_strengths

def get_adjusted_xg(home_team, away_team, league, league_averages, team_strengths):
    lg_avg = league_averages.get(league, 2.5)
    h_data = team_strengths.get(home_team, {"attack_strength": 1.3, "defence_vulnerability": 1.0})
    a_data = team_strengths.get(away_team, {"attack_strength": 1.1, "defence_vulnerability": 1.2})

    home_xG = max(0.2, (h_data["attack_strength"] * a_data["defence_vulnerability"]) * (lg_avg / 2.0))
    away_xG = max(0.2, (a_data["attack_strength"] * h_data["defence_vulnerability"]) * (lg_avg / 2.0))

    return round(home_xG, 2), round(away_xG, 2)
print("Baselines module created successfully!")
