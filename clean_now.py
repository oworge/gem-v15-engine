import json
from datetime import datetime, timezone
import shutil

# Step 1: Backup
shutil.copy("last_good_feed.json", "last_good_feed.backup.json")
print("✅ Backup saved")

# Step 2: Load feed
with open("last_good_feed.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"📋 Feed date: {data.get('feed_date', 'unknown')}")
print(f"📋 League: {data.get('lg', 'unknown')}")

# Step 3: Get picks from the 'data' key
picks = data.get("data", [])
print(f"📊 Total picks loaded: {len(picks)}")

if not picks:
    print("⚠️ No picks in feed right now — your engine hasn't generated any yet today")
    print("💡 Run your engine first, then run this script again")
    exit()

# Step 4: Clean them
now = datetime.now(timezone.utc)
cleaned = []
removed = {"old": 0, "empty": 0, "zero_ev": 0}

for p in picks:
    ev = p.get("ev")
    odds = p.get("odds")
    model_p = p.get("p")
    
    # Remove missing values
    if (ev in [None, "", "undefined"] or 
        odds in [None, "", "undefined"] or 
        not model_p or str(model_p).strip() in ["", "%", "undefined"]):
        removed["empty"] += 1
        continue
    
    # Remove zero/negative EV
    try:
        if float(ev) <= 0:
            removed["zero_ev"] += 1
            continue
    except:
        removed["empty"] += 1
        continue
    
    # Remove old games
    try:
        date_str = str(p.get("fixture_date", p.get("feed_date", "")))
        time_str = str(p.get("ko", "23:59"))
        if "T" in date_str:
            date_part = date_str.split("T")[0]
        else:
            date_part = date_str
        dt_str = f"{date_part} {time_str}"
        game_time = datetime.strptime(dt_str, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
        if game_time < now:
            removed["old"] += 1
            continue
    except:
        pass
    
    cleaned.append(p)

# Step 5: Write back — SAME structure
data["data"] = cleaned
data["last_cleaned"] = now.isoformat()

with open("last_good_feed.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

# Summary
print("\n" + "=" * 50)
print("   🧹 DASHBOARD CLEANED")
print("=" * 50)
print(f"📊 Total picks:      {len(picks)}")
print(f"🗑️ Old games:        {removed['old']}")
print(f"🗑️ Empty values:     {removed['empty']}")
print(f"🗑️ Zero/Negative EV: {removed['zero_ev']}")
print(f"✅ Showing now:      {len(cleaned)}")

if cleaned:
    print("\n🔥 YOUR VALUE PICKS:")
    for i, pick in enumerate(cleaned[:6], 1):
        print(f"   #{i} {pick.get('f','')}")
        print(f"      {pick.get('pk','')}  @ {pick.get('odds',0)}  EV +{pick.get('ev',0)}%")
else:
    print("\n📌 No value bets right now.")
    print("💡 Run your engine to generate fresh picks, then run this again.")

print("\n👉 Refresh your dashboard page!\n")
