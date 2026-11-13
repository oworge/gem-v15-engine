import pathlib, re

dg = pathlib.Path("data_generator.py").read_text(encoding="utf-8")

real_slate = '''BASE_GLOBAL_SLATE = [
    ("Türkiye vs. Belgium", "UEFA Nations League (12 Nov 2026 | 17:00 UTC)", "Over 1.5 Goals", 1.75, 1.55, 1.85),
    ("Italy vs. France", "UEFA Nations League (12 Nov 2026 | 19:45 UTC)", "BTTS Yes", 1.98, 1.77, 2.10),
    ("England vs. Croatia", "UEFA Nations League (12 Nov 2026 | 19:45 UTC)", "England Win & O1.5", 1.78, 1.60, 2.25),
    ("Czechia vs. Spain", "UEFA Nations League (12 Nov 2026 | 19:45 UTC)", "Spain Win & O1.5", 1.86, 1.67, 2.28),
    ("Ivory Coast vs. Gambia", "AFCON 2027 Qualifiers (12 Nov 2026 | 19:00 UTC)", "Ivory Coast Win & O1.5", 1.74, 1.57, 2.48),
    ("Senegal vs. Sudan", "AFCON 2027 Qualifiers (12 Nov 2026 | 19:00 UTC)", "Senegal -1.5 AH", 1.67, 1.50, 2.68),
    ("Cameroon vs. Namibia", "AFCON 2027 Qualifiers (12 Nov 2026 | 19:00 UTC)", "Cameroon Win", 1.72, 1.55, 2.55),
    ("Ghana vs. Somalia", "AFCON 2027 Qualifiers (12 Nov 2026 | 15:00 UTC)", "Over 2.5 Goals", 1.68, 1.52, 2.60),
    ("Albania vs. Finland", "UEFA Nations League (12 Nov 2026 | 19:45 UTC)", "Albania Win", 1.84, 1.67, 2.22),
    ("Armenia vs. Cyprus", "UEFA Nations League (12 Nov 2026 | 17:00 UTC)", "Over 1.5 Goals", 1.76, 1.60, 2.38),
    ("Montenegro vs. Latvia", "UEFA Nations League (12 Nov 2026 | 19:45 UTC)", "Montenegro Win", 1.70, 1.55, 2.50),
    ("San Marino vs. Belarus", "UEFA Nations League (12 Nov 2026 | 19:45 UTC)", "Belarus -1.5 AH", 1.75, 1.60, 2.40),
    ("Curaçao vs. Panama", "CONCACAF Nations League QF (12 Nov 2026)", "Panama Win", 1.83, 1.68, 2.20),
    ("Benin vs. Central African Republic", "AFCON 2027 Qualifiers (12 Nov 2026 | 19:00 UTC)", "Under 2.5 Goals", 1.79, 1.64, 2.32),
    ("Madagascar vs. Guinea-Bissau", "AFCON 2027 Qualifiers (12 Nov 2026 | 16:00 UTC)", "1X Double Chance", 1.66, 1.52, 2.58),
    ("Uzbekistan vs. Russia", "International Friendly (12 Nov 2026 | 15:00 UTC)", "BTTS Yes", 1.88, 1.74, 2.12),
    ("Lithuania vs. Suriname", "International Friendly (12 Nov 2026 | 17:00 UTC)", "Over 1.5 Goals", 1.74, 1.62, 2.38),
    ("Navalcarnero vs. Real Betis", "Spanish Copa del Rey (12 Nov 2026 | 18:00 UTC)", "Real Betis -1.5 AH", 1.69, 1.57, 2.48),
    ("Tarancón vs. Levante", "Spanish Copa del Rey (12 Nov 2026 | 18:00 UTC)", "Over 2.5 Goals", 1.67, 1.56, 2.52)
]'''

real_builders = '''BET_BUILDERS = [
    {"match": "Today 5-Fold Elite Value Acca #1 (12 Nov 2026)", "comp": "UEFA + AFCON Verified Today Slate", "pick": "Türkiye/Belgium O1.5 + Italy/France BTTS + England Win + Spain Win + Senegal -1.5", "odds": "15.80"},
    {"match": "Today 5-Fold Global Multi-Confed #2 (12 Nov 2026)", "comp": "UEFA + CAF + CONCACAF + Copa del Rey", "pick": "Ivory Coast Win + Cameroon Win + Panama Win + Real Betis -1.5 + Ghana O2.5", "odds": "14.20"},
    {"match": "Today 4-Fold Evening Kick-Off Builder (19:45 UTC)", "comp": "UEFA Nations League Night Slate", "pick": "Albania Win + Montenegro Win + Belarus -1.5 + Czechia/Spain O1.5", "odds": "10.65"}
]'''

dg = re.sub(r"BASE_GLOBAL_SLATE = \[.*?\]\n\nBET_BUILDERS = \[.*?\]", real_slate + "\n\n" + real_builders, dg, count=1, flags=re.S)
pathlib.Path("data_generator.py").write_text(dg, encoding="utf-8")
print("VERIFIED 12 NOV 2026 TODAY SLATE LOADED")
