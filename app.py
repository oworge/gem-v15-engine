from flask import Flask, render_template, request

app = Flask(__name__)

def get_master_slate():
    return [
        {
            "id": 1, "home": "Manchester United", "away": "Aston Villa",
            "league": "English Premier League", "date": "Sun, Nov 8, 2026", "time": "16:30 GMT",
            "market": "Over 1.5 Goals", "odds": 1.35, "ev": "+6.2%", "rating": "10/10",
            "builder": ["Over 1.5 Match Goals", "Bruno Fernandes 1+ Shots on Target", "John McGinn 2+ Fouls Committed", "Marcus Rashford 1+ Fouls Won", "Aston Villa Over 1.5 Cards"],
            "builder_odds": 4.85, "correct_score": "2 - 1", "cs_odds": "7.50"
        },
        {
            "id": 2, "home": "Atlético Madrid", "away": "Barcelona",
            "league": "Spanish La Liga", "date": "Sun, Nov 8, 2026", "time": "20:00 GMT",
            "market": "Double Chance: X2", "odds": 1.42, "ev": "+5.8%", "rating": "10/10",
            "builder": ["Double Chance X2", "Under 3.5 Match Goals", "Gavi 2+ Fouls Committed", "Lamine Yamal 1+ Fouls Won", "Over 4.5 Cards"],
            "builder_odds": 5.20, "correct_score": "1 - 1", "cs_odds": "6.80"
        },
        {
            "id": 3, "home": "Fiorentina", "away": "Juventus",
            "league": "Italian Serie A", "date": "Sun, Nov 8, 2026", "time": "19:45 GMT",
            "market": "Double Chance: X2", "odds": 1.38, "ev": "+5.1%", "rating": "10/10",
            "builder": ["Double Chance X2", "Under 2.5 Goals", "Manuel Locatelli 2+ Fouls Committed", "Moise Kean 1+ Shots on Target", "Over 3.5 Cards"],
            "builder_odds": 5.10, "correct_score": "0 - 1", "cs_odds": "6.50"
        },
        {
            "id": 4, "home": "Bayer Leverkusen", "away": "Borussia Dortmund",
            "league": "German Bundesliga", "date": "Sun, Nov 8, 2026", "time": "17:30 GMT",
            "market": "BTTS - Yes", "odds": 1.65, "ev": "+7.4%", "rating": "10/10",
            "builder": ["BTTS - Yes", "Over 2.5 Goals", "Florian Wirtz 1+ Shots on Target", "Julian Brandt 1+ Fouls Won", "Granit Xhaka 2+ Fouls Committed"],
            "builder_odds": 4.50, "correct_score": "2 - 2", "cs_odds": "11.00"
        },
        {
            "id": 5, "home": "AC Milan", "away": "Napoli",
            "league": "Italian Serie A", "date": "Sun, Nov 8, 2026", "time": "19:45 GMT",
            "market": "BTTS & Over 2.5", "odds": 2.10, "ev": "+8.2%", "rating": "10/10",
            "builder": ["BTTS & Over 2.5", "Christian Pulisic 1+ Shots on Target", "Khvicha Kvaratskhelia 2+ Fouls Won", "Stanislav Lobotka 2+ Fouls Committed", "Over 3.5 Cards"],
            "builder_odds": 6.75, "correct_score": "2 - 1", "cs_odds": "8.50"
        },
        {
            "id": 6, "home": "Arsenal", "away": "Chelsea",
            "league": "English Premier League", "date": "Mon, Nov 9, 2026", "time": "15:00 GMT",
            "market": "Home Win", "odds": 1.85, "ev": "+6.4%", "rating": "10/10",
            "builder": ["Arsenal Win", "Bukayo Saka 1+ Shots on Target", "Cole Palmer 1+ Fouls Won", "Moises Caicedo 2+ Fouls Committed", "Arsenal Over 5.5 Corners"],
            "builder_odds": 5.40, "correct_score": "2 - 0", "cs_odds": "8.00"
        },
        {
            "id": 7, "home": "Real Madrid", "away": "Valencia",
            "league": "Spanish La Liga", "date": "Mon, Nov 9, 2026", "time": "21:00 GMT",
            "market": "Real Madrid Win", "odds": 1.45, "ev": "+5.9%", "rating": "10/10",
            "builder": ["Real Madrid Win", "Kylian Mbappé 2+ Shots on Target", "Jude Bellingham 1+ Fouls Won", "Pepelu 2+ Fouls Committed", "Real Madrid Most Corners"],
            "builder_odds": 4.10, "correct_score": "3 - 1", "cs_odds": "9.50"
        },
        {
            "id": 8, "home": "Bayern Munich", "away": "RB Leipzig",
            "league": "German Bundesliga", "date": "Mon, Nov 9, 2026", "time": "18:30 GMT",
            "market": "Over 2.5 Goals", "odds": 1.55, "ev": "+6.8%", "rating": "10/10",
            "builder": ["Over 2.5 Goals", "Harry Kane 2+ Shots on Target", "Xavi Simons 1+ Fouls Won", "Joshua Kimmich 2+ Fouls Committed", "BTTS - Yes"],
            "builder_odds": 4.60, "correct_score": "3 - 2", "cs_odds": "14.00"
        },
        {
            "id": 9, "home": "Paris Saint-Germain", "away": "Marseille",
            "league": "French Ligue 1", "date": "Tue, Nov 10, 2026", "time": "20:45 GMT",
            "market": "PSG Win & Over 1.5", "odds": 1.78, "ev": "+7.1%", "rating": "10/10",
            "builder": ["PSG Win & Over 1.5", "Ousmane Dembélé 1+ Shots on Target", "Mason Greenwood 2+ Fouls Won", "Vitinha 2+ Fouls Committed", "Over 3.5 Cards"],
            "builder_odds": 5.80, "correct_score": "3 - 0", "cs_odds": "12.00"
        },
        {
            "id": 10, "home": "Inter Milan", "away": "Lazio",
            "league": "Italian Serie A", "date": "Tue, Nov 10, 2026", "time": "15:00 GMT",
            "market": "Inter Win", "odds": 1.62, "ev": "+6.5%", "rating": "10/10",
            "builder": ["Inter Win", "Lautaro Martínez 1+ Shots on Target", "Mattia Zaccagni 1+ Fouls Won", "Nicolò Barella 2+ Fouls Committed", "Under 4.5 Cards"],
            "builder_odds": 4.90, "correct_score": "2 - 0", "cs_odds": "7.00"
        },
        {
            "id": 11, "home": "Feyenoord", "away": "PSV Eindhoven",
            "league": "Dutch Eredivisie", "date": "Wed, Nov 11, 2026", "time": "14:30 GMT",
            "market": "BTTS - Yes", "odds": 1.50, "ev": "+5.5%", "rating": "9.8/10",
            "builder": ["BTTS - Yes", "Over 2.5 Goals", "Santiago Giménez 1+ Shots on Target", "Joey Veerman 2+ Fouls Committed", "Over 3.5 Cards"],
            "builder_odds": 4.30, "correct_score": "2 - 2", "cs_odds": "10.50"
        },
        {
            "id": 12, "home": "Benfica", "away": "Sporting CP",
            "league": "Portuguese Primeira Liga", "date": "Wed, Nov 11, 2026", "time": "21:30 GMT",
            "market": "Under 3.5 Goals", "odds": 1.38, "ev": "+4.9%", "rating": "9.7/10",
            "builder": ["Under 3.5 Goals", "Orkun Kökçü 2+ Fouls Committed", "Viktor Gyökeres 1+ Shots on Target", "Morten Hjulmand 2+ Fouls Committed", "Under 10.5 Corners"],
            "builder_odds": 4.20, "correct_score": "1 - 1", "cs_odds": "6.20"
        }
    ]

@app.route('/')
def index():
    tab = request.args.get('tab', 'dailypicks')
    slate = get_master_slate()
    
    acca_legs = int(request.args.get('legs', 3))
    selected_market = request.args.get('market_filter', 'All')
    
    filtered_pool = slate if selected_market == 'All' else [f for f in slate if selected_market.lower() in f['market'].lower()]
    current_acca = filtered_pool[:acca_legs]
    
    combined_odds = 1.0
    for l in current_acca:
        combined_odds *= l['odds']
    combined_odds = round(combined_odds, 2)

    return render_template('index.html', active_tab=tab, slate=slate, current_acca=current_acca, acca_legs=acca_legs, selected_market=selected_market, combined_odds=combined_odds)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
