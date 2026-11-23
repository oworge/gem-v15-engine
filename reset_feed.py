import json
from datetime import datetime, timezone

data = {
    "ko": None,
    "lg": None,
    "feed_date": datetime.now(timezone.utc).isoformat(),
    "data": []
}
with open("last_good_feed.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
print("✅ Feed reset to empty — restart your app")
