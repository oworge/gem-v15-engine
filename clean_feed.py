# ==========================================================
# clean_feed.py — Feed Data Cleaner Module
# Remove old games, missing values, and non-positive EV picks
# ==========================================================
from datetime import datetime, timezone

def clean_feed_data(data):
    """
    Apply 3 filters to feed data:
    1. Remove games that have already kicked off
    2. Remove picks with missing/undefined values
    3. Keep only positive EV bets
    """
    picks = []

    # Extract the list of picks
    if isinstance(data, dict):
        for key in ["picks", "bets", "data", "slip", "items"]:
            if key in data and isinstance(data[key], list):
                picks = data[key]
                break
        if not picks:
            return data  # Can't find list — return unchanged
    else:
        picks = data if isinstance(data, list) else []

    if not picks:
        return data

    now = datetime.now(timezone.utc)
    cleaned = []

    for item in picks:
        # ─── FILTER 1: Skip old games ───
        try:
            date_str = str(item.get("fixture_date", item.get("date", "")))
            time_str = str(item.get("ko", "23:59"))
            date_part = date_str.split("T")[0] if "T" in date_str else date_str
            dt_str = f"{date_part} {time_str}"
            game_time = datetime.strptime(dt_str, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
            if game_time < now:
                continue  # Game kicked off — skip
        except:
            pass  # Keep if we can't parse the date

        # ─── FILTER 2: Skip picks with missing/undefined values ───
        ev = item.get("ev")
        odds = item.get("odds")
        p_val = item.get("p")

        if ev in [None, "", 0, "0", "undefined"]:
            continue
        if odds in [None, "", 0, "undefined"]:
            continue
        if not p_val or str(p_val).strip() in ["", "%", "undefined"]:
            continue

        # ─── FILTER 3: Skip zero/negative EV ───
        try:
            if float(ev) <= 0:
                continue
        except:
            continue

        # Passed ALL filters — keep this pick
        cleaned.append(item)

    # Rebuild in the SAME format we received
    if isinstance(data, dict):
        for key in data:
            if isinstance(data[key], list) and len(data[key]) == len(picks):
                data[key] = cleaned
                break
        data["last_cleaned"] = now.isoformat()
        data["filter_summary"] = {
            "original_count": len(picks),
            "cleaned_count": len(cleaned)
        }
        return data
    else:
        return cleaned
