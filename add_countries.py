import pathlib

dg = pathlib.Path("data_generator.py")
code = dg.read_text(encoding="utf-8-sig").replace("\ufeff", "")

country_helper = """
LEAGUE_COUNTRY_MAP = {
    "soccer_epl": "England",
    "soccer_efl_champ": "England",
    "soccer_england_efl_cup": "England",
    "soccer_spain_la_liga": "Spain",
    "soccer_germany_bundesliga": "Germany",
    "soccer_italy_serie_a": "Italy",
    "soccer_france_ligue_one": "France",
    "soccer_brazil_campeonato": "Brazil",
    "soccer_argentina_primera_division": "Argentina",
    "soccer_colombia_primera_a": "Colombia",
    "soccer_usa_mls": "United States",
    "soccer_mexico_ligamx": "Mexico",
}

def attach_country_to_picks(picks):
    for p in picks:
        sport_key = str(p.get("sport_key", "")).lower()
        comp = str(p.get("comp", ""))
        match_name = str(p.get("match", ""))
        country = p.get("country") or LEAGUE_COUNTRY_MAP.get(sport_key)

        if not country:
            if "Colombia" in comp or "Millonarios" in match_name or "Nacional" in match_name:
                country = "Colombia"
            elif "Salvador" in comp or "Águila" in match_name:
                country = "El Salvador"
            elif "Czech" in match_name:
                country = "Czech Republic"
            elif "San Marino" in match_name:
                country = "San Marino"
            elif "Côte d'Ivoire" in match_name or "Ivory Coast" in match_name:
                country = "Côte d'Ivoire"
            elif "Barbados" in match_name:
                country = "Barbados"
            elif "Cayman" in match_name:
                country = "Cayman Islands"
            elif "Bonaire" in match_name:
                country = "Bonaire"
            elif " vs. " in match_name:
                country = match_name.split(" vs. ")[0].strip()
            else:
                country = "Global / International"

        p["country"] = country
        if country not in comp:
            p["comp"] = f"{comp} | Venue: {country}" if comp else f"Venue: {country}"
    return picks

if "get_global_daily_picks" in globals() and "_orig_country_picks" not in globals():
    _orig_country_picks = get_global_daily_picks
    def get_global_daily_picks(*args, **kwargs):
        return attach_country_to_picks(_orig_country_picks(*args, **kwargs))
"""

if "_orig_country_picks" not in code:
    dg.write_text(code + "\n" + country_helper, encoding="utf-8")
    print("COUNTRY TAGGING INSTALLED")
else:
    print("COUNTRY TAGGING ALREADY INSTALLED")
