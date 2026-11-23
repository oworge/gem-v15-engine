# ==========================================================
# EDGEMETRIX — DAILY PREDICTION GENERATOR
# Run this → Value Engine filters → Dashboard updates → You see only VALUE BETS
# ==========================================================
import sys, json
from datetime import datetime

print("=" * 55)
print("   EDGEMETRIX — VALUE ENGINE DAILY RUN")
print(f"   🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 55)

# Import our new modules
try:
    from value_engine import calculate_value_decision, rank_daily_picks, format_pick_for_display
    from dashboard_engine import generate_dashboard_tabs, save_dashboard_json
    print("✅ Modules loaded successfully")
except Exception as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# ─── LOAD TODAY'S FIXTURES ───
# Your fixture feed already updates — load from your existing data file
FIXTURES_FILE = "fixtures_today.json"

try:
    with open(FIXTURES_FILE, "r", encoding="utf-8") as f:
        fixtures = json.load(f)
    print(f"✅ Loaded {len(fixtures)} fixtures from feed")
except FileNotFoundError:
    print(f"⚠️ Fixture file not found: {FIXTURES_FILE}")
    print("💡 Waiting for fixture feed to populate...")
    fixtures = []

if not fixtures:
    print("📌 No fixtures yet — dashboard will update when feed populates")
    sys.exit(0)

# ─── RUN VALUE ENGINE ───
print("\n🔍 Scanning for value bets...")
dashboard_data = generate_dashboard_tabs(fixtures)

# ─── SUMMARY ───
tabs = dashboard_data["tabs"]
print(f"\n📊 RESULTS SUMMARY")
print(f"   Total Fixtures: {dashboard_data['total_fixtures']}")
print(f"   Value Bets Found: {dashboard_data['bets_found']}")
print(f"   Top Pick EV:  +{tabs.get('All Vetted',[{}])[0].get('ev_pct',0) if tabs.get('All Vetted') else 0:.1f}%")

for tab_name in ["All Vetted", "UK Leagues", "Perfect Value", "Today's Picks"]:
    count = len(tabs.get(tab_name, []))
    print(f"   {tab_name}: {count} picks")

# ─── SAVE FOR DASHBOARD ───
save_dashboard_json(dashboard_data)

# ─── DISPLAY TOP PICKS IN CONSOLE ───
top_picks = tabs.get("Today's Picks", [])
if top_picks:
    print("\n" + "=" * 55)
    print("   🔥 TOP PICKS — TODAY'S BEST VALUE")
    print("=" * 55 + "\n")
    for i, pick in enumerate(top_picks[:8], 1):
        print(format_pick_for_display(pick, i))
else:
    print("\n📌 No value bets found today. That's okay — quality over quantity!")

print("\n✅ DONE — Dashboard updated. Ready to beat the bookie today! 🔥\n")
