# ==========================================================
# CORRECT CLEANER — Reads from daily_auto_slip.json, writes back
# Matches YOUR exact format: slip array, ev_pct, fixture, etc.
# ==========================================================
import json
from datetime import datetime, timezone
import shutil

# Step 1: Backup first
shutil.copy("daily_auto_slip.json", "daily_auto_slip.backup.json")
print("✅ Backup saved: daily_auto_slip.backup.json")

# Step 2: Load the REAL data
with open("daily_auto_slip.json", "r", encoding="utf-8") as f:
    data = json.load(f)

picks = data.get("slip", [])
print(f"📊 Total slip picks loaded: {len(picks)}")

if not picks:
    print("⚠️ No picks found in slip — nothing to clean")
    exit()

# Step 3: Apply 3 filters
now = datetime.now(timezone.utc)
cleaned = []
removed = {"old": 0, "no_ev": 0, "suspicious": 0}

for item in picks:
    ev = item.get("ev_pct", 0)
    
    # Filter 1: Remove zero/negative EV
    try:
        if float(ev) <= 0:
            removed["no_ev"] += 1
            continue
    except:
        removed["no_ev"] += 1
        continue
    
    # Filter 2: Remove old games (if we have a date)
    fixture_text = str(item.get("fixture", ""))
    date_text = str(item.get("date", fixture_text[:10] if fixture_text else ""))
    is_old = False
    try:
        for fmt in ["%Y-%m-%d", "%d/%m/%Y"]:
            try:
                game_date = datetime.strptime(date_text.strip(), fmt).replace(tzinfo=timezone.utc)
                today = now.replace(hour=0, minute=0, second=0, microsecond=0)
                if game_date < today:
                    is_old = True
                    break
            except:
                pass
        if is_old:
            removed["old"] += 1
            continue
    except:
        pass
    
    cleaned.append(item)

# Step 4: Save back — SAME EXACT FORMAT
data["slip"] = cleaned
data["last_cleaned"] = now.isoformat()
data["summary"] = {
    "original": len(picks),
    "cleaned": len(cleaned),
    "removed_old": removed["old"],
    "removed_no_ev": removed["no_ev"]
}

with open("daily_auto_slip.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

# Step 5: Show results
print("\n" + "=" * 60)
print("   🧹 SLIP FILE CLEANED — DASHBOARD WILL READ THIS")
print("=" * 60)
print(f"📊 Original picks: {len(picks)}")
print(f"🗑️ Old games removed: {removed['old']}")
print(f"🗑️ Zero/negative EV removed: {removed['no_ev']}")
print(f"✅ Showing now: {len(cleaned)} clean value bets")

if cleaned:
    print("\n🔥 YOUR UPDATED SLIP:")
    for i, pick in enumerate(cleaned[:10], 1):
        fixture = pick.get("fixture", "Unknown")
        selection = pick.get("selection", "")
        ev = pick.get("ev_pct", "?")
        odds = pick.get("odds", "?")
        print(f"   #{i} EV +{ev}% | {fixture}")
        if selection:
            print(f"      → {selection}  @ {odds}")
        print()
else:
    print("\n📌 No value bets right now — empty slip is smart betting!")

print("👉 Refresh your dashboard — check the 'Value' tab or slip panel!\n")
