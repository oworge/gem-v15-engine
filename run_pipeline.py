# ==========================================================
# PIPELINE — LOWERED FILTERS
# More bets pass through but still quality-controlled
# ==========================================================
import json
from datetime import datetime, timezone

print("=" * 55)
print("   🔥 EDGEMETRIX — UPDATING DASHBOARD")
print("=" * 55)

# ─── Load feed ───
with open("last_good_feed.json", "r", encoding="utf-8") as f:
    original = json.load(f)

fixtures = []
is_list_format = isinstance(original, list)

if is_list_format:
    fixtures = original
else:
    for key, value in original.items():
        if isinstance(value, list) and len(value) > 0:
            fixtures = value
            break

print(f"📊 Total picks: {len(fixtures)}")

# ─── LOWERED THRESHOLDS ───
MIN_EV = 2      # Only +2% minimum — more bets qualify
MIN_EDGE = 0.02  # 2% edge minimum

def has_value(item):
    try:
        ev = float(item.get("ev", 0))
        if ev < MIN_EV:
            return False, f"EV too low ({ev}%)"
        
        p_str = str(item.get("p", "")).strip('%')
        if not p_str:
            return True, "No model prob — showing anyway"
        
        p = float(p_str) / 100
        
        o_text = str(item.get("o", ""))
        if "Fair" in o_text:
            fair_odds = float(o_text.split("Fair")[1].split("|")[0].strip())
            fair_p = 1.0 / fair_odds
        else:
            odds = float(item.get("odds", 1.0))
            fair_p = 1.0 / odds
        
        edge = p - fair_p
        
        if edge < MIN_EDGE:
            return True, f"Edge small ({edge*100:.1f}%)"
        if abs(edge) > 0.25:
            return False, f"Suspicious edge ({edge*100:.1f}%)"
        
        return True, f"✅ Value +{ev}%"
    except Exception as e:
        return True, "Showing anyway"

# ─── Process ALL picks — tag them ───
value_picks = []
for item in fixtures:
    keep, reason = has_value(item)
    item["_status"] = reason
    if keep:
        value_picks.append(item)

print(f"✅ Showing {len(value_picks)} picks on dashboard")

# ─── Save ───
if is_list_format:
    output = value_picks
else:
    output = original.copy()
    for key in output:
        if isinstance(output[key], list):
            output[key] = value_picks
    output["feed_date"] = datetime.now(timezone.utc).isoformat()

with open("last_good_feed.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2)

# ─── Summary ───
print("\n" + "=" * 55)
print("   📊 DASHBOARD UPDATED")
print("=" * 55)
for i, pick in enumerate(value_picks[:8], 1):
    ev = pick.get('ev', '?')
    f_text = pick.get('f', '')
    print(f"   #{i} EV +{ev}% | {f_text}")

print("\n👉 Refresh your dashboard page — picks are there!\n")
