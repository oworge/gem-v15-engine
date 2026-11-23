# ==========================================================
# COMPLETE DASHBOARD CLEANER — 3 filters in one
# 1. Remove old games that kicked off
# 2. Remove picks with missing/empty values
# 3. Keep only positive EV bets
# ==========================================================
import json
from datetime import datetime, timezone

print("=" * 55)
print("   🧹 COMPLETE DASHBOARD CLEANER")
print("=" * 55)

# ─── Load your slip file ───
try:
    with open("daily_bookie_beater_slip.json", "r", encoding="utf-8") as f:
        data = json.load(f)
except FileNotFoundError:
    with open("daily_auto_slip.json", "r", encoding="utf-8") as f:
        data = json.load(f)

# Extract picks
picks = []
if isinstance(data, dict):
    for key in ["picks", "bets", "data", "slip", "items"]:
        if key in data and isinstance(data[key], list):
            picks = data[key]
            break
    if not picks:
        picks = []
else:
    picks = data if isinstance(data, list) else []

print(f"📊 Total loaded: {len(picks)}")

# ─── FILTER 1: Remove OLD games ───
now = datetime.now(timezone.utc)
def is_future(item):
    try:
        date_str = str(item.get("fixture_date", item.get("date", "")))
        time_str = str(item.get("ko", "23:59"))
        if "T" in date_str:
            date_part = date_str.split("T")[0]
        else:
            date_part = date_str
        dt_str = f"{date_part} {time_str}"
        try:
            game_time = datetime.strptime(dt_str, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
            if game_time < now:
                return False
        except:
            pass
        return True
    except:
        return True

# ─── FILTER 2: Remove picks with MISSING/EMPTY values ───
def has_valid_values(item):
    ev = item.get("ev")
    odds = item.get("odds")
    model_p = item.get("p")
    
    # Check if values exist and aren't empty/placeholder
    if ev in [None, "", 0, "0", "undefined"]:
        return False, "Missing EV"
    if odds in [None, "", 0, "undefined"]:
        return False, "Missing odds"
    if not model_p or str(model_p).strip() in ["", "%", "undefined"]:
        return False, "Missing model prob"
    
    return True, "OK"

# ─── FILTER 3: Keep only POSITIVE EV ───
def has_positive_ev(item):
    try:
        ev = float(item.get("ev", 0))
        return ev > 0, ev
    except:
        return False, 0

# ─── APPLY ALL FILTERS ───
clean_picks = []
counts = {"old": 0, "no_value": 0, "negative_ev": 0}

for pick in picks:
    future = is_future(pick)
    valid, why = has_valid_values(pick)
    positive, ev = has_positive_ev(pick)
    
    if not future:
        counts["old"] += 1
    elif not valid:
        counts["no_value"] += 1
    elif not positive:
        counts["negative_ev"] += 1
    else:
        clean_picks.append(pick)

# ─── Save ───
if isinstance(data, dict):
    output = data.copy()
    for k in output:
        if isinstance(output[k], list) and len(output[k]) == len(picks):
            output[k] = clean_picks
            break
    output["last_cleaned"] = now.isoformat()
    output["summary"] = {
        "total_removed": sum(counts.values()),
        "old_games": counts["old"],
        "missing_values": counts["no_value"],
        "negative_ev": counts["negative_ev"],
        "showing": len(clean_picks)
    }
else:
    output = clean_picks

with open("daily_bookie_beater_slip.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2)

# ─── Summary ───
print("\n" + "=" * 55)
print("   📊 CLEANING COMPLETE")
print("=" * 55)
print(f"🗑️ Old games removed:       {counts['old']}")
print(f"🗑️ Missing values removed:   {counts['no_value']}")
print(f"🗑️ Negative/zero EV removed: {counts['negative_ev']}")
print(f"✅ Showing now:              {len(clean_picks)} clean value bets")

if clean_picks:
    print("\n🔥 YOUR CLEAN VALUE BETS:")
    for i, pick in enumerate(clean_picks[:6], 1):
        f_text = pick.get('f', '')
        ev = pick.get('ev', '?')
        odds = pick.get('odds', '?')
        ko = pick.get('ko', '')
        print(f"   #{i} {f_text}  @ {ko}  EV +{ev}%  Odds {odds}")
else:
    print("\n📌 No clean upcoming value bets right now.")
    print("💡 That's actually GOOD — only bet when the data is solid!")

print("\n👉 Refresh your dashboard — undefineds & old games are gone!\n")
