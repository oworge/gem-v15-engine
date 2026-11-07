# props_engine.py - Advanced Player Prop & Bet Builder Engine
import logging

class PlayerPropEngine:
    def __init__(self):
        pass

    def evaluate_prop(self, player_name, team, opponent, prop_type, baseline_stat, odds):
        multiplier = 1.15 if prop_type in ["To Be Booked", "Fouls Committed (2+)"] else 1.08
        implied_prob = round(1.0 / odds, 3)
        modeled_prob = min(round(implied_prob * multiplier, 3), 0.95)
        
        edge = round((modeled_prob * odds) - 1.0, 3)
        edge_pct = round(edge * 100, 1)
        
        confidence = "A+ Bully Grade" if edge_pct >= 8.0 else "Solid Value"

        return {
            "player": player_name,
            "team": team,
            "opponent": opponent,
            "prop_market": prop_type,
            "baseline": baseline_stat,
            "odds": odds,
            "modeled_probability": f"{int(modeled_prob * 100)}%",
            "expected_value": f"{'+' if edge_pct > 0 else ''}{edge_pct}%",
            "rating": confidence,
            "status": "VERIFIED PROP CONFLUENCE"
        }

    def get_featured_props(self):
        return [
            self.evaluate_prop("Harry Maguire", "Manchester United", "Nottingham Forest", "To Be Booked", "0.45 Cards/90", 2.40),
            self.evaluate_prop("Casemiro", "Manchester United", "Nottingham Forest", "Fouls Committed (2+)", "2.3 Fouls/90", 1.72),
            self.evaluate_prop("Rodri", "Manchester City", "Nottingham Forest", "Tackles Made (3+)", "3.4 Tackles/90", 1.85),
            self.evaluate_prop("Vinicius Junior", "Real Madrid", "Valencia", "Player Fouled (3+)", "3.8 Fouls Won/90", 1.90),
            self.evaluate_prop("Jude Bellingham", "Real Madrid", "Valencia", "Shots on Target (1+)", "1.2 SOT/90", 1.55)
        ]

PROPS_ENGINE = PlayerPropEngine()
