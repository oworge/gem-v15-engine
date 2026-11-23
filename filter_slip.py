# ==========================================================
# DIRECT PIPELINE — Reads from your engine, writes to your slip file
# ==========================================================
import json
from datetime import datetime, timezone

print("=" * 55)
print("   🔥 EDGEMETRIX — FILTERING VALUE PICKS")
print("=" * 55)

# ─── 1. Load your raw slip data ───
INPUT_FILE = "daily_bookie_beater_slip.json"
OUTPUT_FILE = "daily_bookie_beater_slip.json"  # Overwrite the slip file

try:
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"✅ Loaded {INPUT_FILE}")
except FileNotFoundError:
    print(f"⚠️ {INPUT_FILE} not found — checking daily_auto_slip.json...")
    INPUT_FILE = "daily_auto_slip.json"
    OUTPUT_FILE = "daily_bookie_beater_slip.json"
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"✅ Loaded {INPUT_FILE}")

# ─── 2. Extract picks list ───
picks = []
if isinstance(data, dict):
    for key in ["picks", "bets", "data", "slip", "items"]:
        if key in data and isinstance(data[key], list):
            picks = data[key]
            break
    if not picks:
        # Assume the dict itself is the list container
        picks = data
else:
    picks = data

if not isinstance(picks, list):
    picks = []

print(f"📊 Total picks loaded: {len(picks)}")

# ─── 3. Value filter — LOWERED thresholds to match your feed's +15.5% EV ───
def is_value(item):
    try:
        ev = float(item.get("ev", item.get("ev_percent", 0)))
        # Your feed shows +15.5% — so keep anything positive
        if ev <= 0:
            return False
        return True
    except:
        return True  # Keep if we can't tell

value_picks = [p for p in picks if is_value(p)]
removed = len(picks) - len(value_picks)

print(f"✅ Value bets kept: {len(value_picks)}")
print(f"🗑️ Non-value removed: {removed}")

# ─── 4. Save back in SAME format ───
if isinstance(data, dict):
    output = data.copy()
    for key in output:
        if isinstance(output[key], list) and len(output[key]) == len(picks):
            output[key] = value_picks
            break
    output["generated"] = datetime.now(timezone.utc).isoformat()
    output["total"] = len(value_picks)
else:
    output = value_picks

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2)

# ─── Summary ───
print("\n" + "=" * 55)
print("   ✅ SLIP FILE UPDATED — DASHBOARD WILL READ IT")
print("=" * 55)

if value_picks:
    print("\n🔥 YOUR VALUE PICKS:")
    for i, pick in enumerate(value_picks[:8], 1):
        f_text = pick.get('f', pick.get('home_away', pick.get('match', 'Match')))
        ev = pick.get('ev', pick.get('ev_percent', '?'))
        sel = pick.get('pk', pick.get('selection', ''))
        print(f"   #{i} EV +{ev}% | {f_text}")
        if sel:
            print(f"      → {sel}")
        print()
else:
    print("\n📌 No value bets today.")

print(f"📂 File saved: {OUTPUT_FILE}")
print("👉 Refresh your dashboard — check the 'Value' tab or slip panel!\n")
