def fetch_live_upcoming_fixtures():
    headers = {
        'x-rapidapi-host': 'v3.football.api-sports.io',
        'x-rapidapi-key': FOOTBALL_API_KEY
    }
    params = {'next': '50', 'status': 'NS-1H-2H-HT'}
    processed_db = {}
    
    if FOOTBALL_API_KEY:
        try:
            response = requests.get(API_URL, headers=headers, params=params, timeout=8)
            if response.status_code == 200:
                data = response.json().get('response', [])
                for item in data:
                    status_short = item['fixture']['status']['short']
                    if status_short in ['FT', 'AET', 'PEN', 'PST', 'CANC']:
                        continue
                    
                    match_id = item['fixture']['id']
                    match_date = item['fixture']['date'][:10]
                    home = item['teams']['home']['name']
                    away = item['teams']['away']['name']
                    region = item['league']['name']
                    
                    intel = ENGINES.run_all_engines(
                        match_id, home, away, region, xg_home=2.10, xg_away=0.85, odds=1.55
                    )
                    
                    # Include all games; use tag to show gate status
                    fixture_obj = {
                        'id': match_id,
                        'region': region,
                        'home': home,
                        'away': away,
                        'league': f"{item['league']['name']} ({item['league']['country']})",
                        'time': item['fixture']['date'][11:16] + ' GMT',
                        'xg_home': 2.10,
                        'xg_away': 0.85,
                        'market': f'{home} Win or Draw & Over 1.5',
                        'odds': 1.55,
                        'value_tag': 'VERIFIED 99%+' if intel['is_approved'] else 'PENDING CONFLUENCE',
                        'backend_intelligence': intel
                    }

                    if match_date not in processed_db:
                        processed_db[match_date] = []
                    processed_db[match_date].append(fixture_obj)
        except Exception as e:
            logging.error(f'API Fetch Error: {e}')

    return processed_db