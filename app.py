# Updated Value King Engine scanning all major markets for +EV
class ValueKingEngine:
    def analyze_all_markets(self, bookmaker_odds_dict, opta_probs_dict):
        """
        Scans all football betting markets (1X2, Double Chance, BTTS, Over/Under)
        and isolates the selection with the highest positive expected value (+EV).
        """
        best_selection = None
        highest_ev = -100.0

        for market, odds in bookmaker_odds_dict.items():
            true_prob = opta_probs_dict.get(market, 0.50)
            # EV Formula: (Probability * Odds) - 1
            ev_calc = round((true_prob * odds) - 1.0, 3)
            ev_pct = round(ev_calc * 100, 1)

            if ev_pct > highest_ev:
                highest_ev = ev_pct
                best_selection = {
                    'market': market,
                    'odds': odds,
                    'true_prob': true_prob,
                    'ev_percentage': f"{'+' if ev_pct > 0 else ''}{ev_pct}%",
                    'rating': "A+ Value" if ev_pct >= 8.0 else ("Solid Edge" if ev_pct > 0 else "No EV")
                }

        return best_selection