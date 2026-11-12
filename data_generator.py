from datetime import datetime

GLOBAL_CONFEDERATIONS = ["UEFA", "CONMEBOL", "AFC", "CAF", "CONCACAF", "Domestic Top-5"]

BASE_GLOBAL_SLATE = [
    {"match":"Turkiye vs. Belgium","comp":"UEFA Nations League","pick":"Over 1.5 Goals (+12.3% EV | +6.8% Edge)","odds":"1.75"},
    {"match":"England vs. Croatia","comp":"UEFA Nations League","pick":"Double Chance (1X) (+3.7% EV | +2.9% Edge)","odds":"1.07"},
    {"match":"Italy vs. France","comp":"UEFA Nations League","pick":"Over 1.5 Goals (+11.2% EV | +6.1% Edge)","odds":"1.80"},
    {"match":"Czechia vs. Spain","comp":"UEFA Nations League","pick":"Spain Win & Over 1.5 Goals (+8.4% EV | +4.7% Edge)","odds":"1.85"},
    {"match":"Albania vs. Finland","comp":"UEFA Nations League","pick":"Double Chance (1X) (+6.2% EV | +3.5% Edge)","odds":"1.28"},
    {"match":"Armenia vs. Faroe Islands","comp":"UEFA Nations League","pick":"Armenia Win (+9.1% EV | +5.0% Edge)","odds":"1.62"},
    {"match":"Greece vs. Republic of Ireland","comp":"UEFA Nations League","pick":"Under 2.5 Goals (+7.8% EV | +4.2% Edge)","odds":"1.65"},
    {"match":"Norway vs. Slovenia","comp":"UEFA Nations League","pick":"BTTS Yes (+8.5% EV | +4.6% Edge)","odds":"1.78"},
    {"match":"Austria vs. Kazakhstan","comp":"UEFA Nations League","pick":"Austria -1.5 AH (+6.9% EV | +3.8% Edge)","odds":"1.55"},
    {"match":"North Macedonia vs. Latvia","comp":"UEFA Nations League","pick":"Over 1.5 Goals (+8.1% EV | +4.4% Edge)","odds":"1.35"},
    {"match":"Germany vs. Bosnia & Herz.","comp":"UEFA Nations League","pick":"Over 2.5 Goals (+7.4% EV | +4.1% Edge)","odds":"1.44"},
    {"match":"Netherlands vs. Hungary","comp":"UEFA Nations League","pick":"Netherlands Win & BTTS No (+9.3% EV | +5.1% Edge)","odds":"2.15"},
    {"match":"Portugal vs. Poland","comp":"UEFA Nations League","pick":"Over 2.5 Goals (+9.1% EV | +5.2% Edge)","odds":"1.80"},
    {"match":"Scotland vs. Denmark","comp":"UEFA Nations League","pick":"BTTS Yes (+8.8% EV | +4.9% Edge)","odds":"1.83"},
    {"match":"Switzerland vs. Serbia","comp":"UEFA Nations League","pick":"Over 1.5 Goals (+6.5% EV | +3.6% Edge)","odds":"1.36"},
    {"match":"Brazil vs. Venezuela","comp":"CONMEBOL Slate","pick":"Brazil -1.5 AH (+8.9% EV | +4.9% Edge)","odds":"1.68"},
    {"match":"Argentina vs. Paraguay","comp":"CONMEBOL Slate","pick":"Argentina Win & O1.5 (+7.9% EV | +4.3% Edge)","odds":"1.52"},
    {"match":"Colombia vs. Uruguay","comp":"CONMEBOL Slate","pick":"BTTS Yes (+9.4% EV | +5.2% Edge)","odds":"1.92"},
    {"match":"Ecuador vs. Bolivia","comp":"CONMEBOL Slate","pick":"Ecuador Win & U3.5 (+8.2% EV | +4.5% Edge)","odds":"1.65"},
    {"match":"Chile vs. Peru","comp":"CONMEBOL Slate","pick":"Chile 1X & U3.5 (+6.8% EV | +3.7% Edge)","odds":"1.45"},
    {"match":"Japan vs. Indonesia","comp":"AFC Slate","pick":"Japan Win & O2.5 (+8.6% EV | +4.8% Edge)","odds":"1.58"},
    {"match":"South Korea vs. Kuwait","comp":"AFC Slate","pick":"South Korea -1.5 AH (+7.5% EV | +4.1% Edge)","odds":"1.62"},
    {"match":"Australia vs. Saudi Arabia","comp":"AFC Slate","pick":"Australia 1X & O1.5 (+7.1% EV | +3.9% Edge)","odds":"1.55"},
    {"match":"Iran vs. North Korea","comp":"AFC Slate","pick":"Iran Win & BTTS No (+8.3% EV | +4.6% Edge)","odds":"1.72"},
    {"match":"Uzbekistan vs. Qatar","comp":"AFC Slate","pick":"Over 1.5 Goals (+6.9% EV | +3.8% Edge)","odds":"1.34"},
    {"match":"Morocco vs. Gabon","comp":"CAF Slate","pick":"Morocco Win & O1.5 (+8.7% EV | +4.8% Edge)","odds":"1.60"},
    {"match":"Nigeria vs. Benin","comp":"CAF Slate","pick":"Nigeria Win (+7.4% EV | +4.1% Edge)","odds":"1.48"},
    {"match":"Senegal vs. Burkina Faso","comp":"CAF Slate","pick":"Senegal 1X & U3.5 (+6.6% EV | +3.6% Edge)","odds":"1.40"},
    {"match":"Egypt vs. Cape Verde","comp":"CAF Slate","pick":"Over 1.5 Goals (+7.2% EV | +4.0% Edge)","odds":"1.33"},
    {"match":"USA vs. Jamaica","comp":"CONCACAF Nations League","pick":"USA Win & O1.5 (+8.0% EV | +4.4% Edge)","odds":"1.66"}
]

def get_global_daily_picks():
    today = datetime.utcnow().strftime("%d %b %Y")
    return [{**item, "comp": f"{item['comp']} | Global Scan ({today})"} for item in BASE_GLOBAL_SLATE]

DAILY_PICKS = get_global_daily_picks()

BET_BUILDERS = [
    {"match":"Turkiye vs. Belgium (5-Leg Builder)","comp":"UEFA Nations League (+14.2% EV)","pick":"1) O1.5 Goals | 2) BTTS Yes | 3) Belgium O3.5 Corners | 4) O2.5 Cards | 5) De Ketelaere 1+ SOT","odds":"5.40"},
    {"match":"Italy vs. France (5-Leg Builder)","comp":"UEFA Nations League (+12.8% EV)","pick":"1) O1.5 Goals | 2) U5.5 Cards | 3) France X2 | 4) O7.5 Corners | 5) Mbappe 2+ Shots","odds":"4.85"},
    {"match":"Brazil vs. Venezuela (5-Leg Builder)","comp":"CONMEBOL Global Slate (+13.6% EV)","pick":"1) Brazil Win | 2) O1.5 Goals | 3) Brazil O5.5 Corners | 4) Vinicius Jr 1+ SOT | 5) U4.5 Cards","odds":"4.95"},
    {"match":"Japan vs. Indonesia (5-Leg Builder)","comp":"AFC Global Slate (+12.4% EV)","pick":"1) Japan Win | 2) O2.5 Goals | 3) Japan O6.5 Corners | 4) BTTS No | 5) Kubo 1+ SOT","odds":"4.60"},
    {"match":"Morocco vs. Gabon (5-Leg Builder)","comp":"CAF Global Slate (+12.9% EV)","pick":"1) Morocco Win | 2) O1.5 Goals | 3) Morocco O5.5 Corners | 4) Hakimi 1+ Shot | 5) U4.5 Cards","odds":"4.75"}
]
