import json, os, pathlib, re, urllib.request, urllib.parse
from datetime import datetime, timezone

LEAGUE_KEYS = [
    "soccer_epl",
    "soccer_efl_champ",
    "soccer_england_league1",
    "soccer_england_league2",
    "soccer_spain_la_liga",
    "soccer_italy_serie_a",
    "soccer_germany_bundesliga",
    "soccer_france_ligue_one",
    "soccer_netherlands_eredivisie",
    "soccer_uefa_champs_league",
    "soccer_uefa_europa_league",
]

def _norm_key(home, away):
    raw = f"{home} v {away}".lower().strip()
    raw = re.sub(r"[^a-z0-9\s]", "", raw)
    return re.sub(r"\s+", " ", raw).strip()

def _load_api_key():
    key = os.environ.get("THE_ODDS_API_KEY", "").strip()
    if key:
        return key
    env_p = pathlib.Path(".env")
    if env_p.exists():
        for line in env_p.read_text(encoding="utf-8", errors="ignore").splitlines():
            if line.strip().startswith("THE_ODDS_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""

def sync_odds():
    cache_path = pathlib.Path("global_odds_cache.json")
    existing = {}
    if cache_path.exists():
        try:
            loaded = json.loads(cache_path.read_text(encoding="utf-8", errors="ignore"))
            if isinstance(loaded, dict):
                existing = loaded
        except Exception:
            existing = {}

    api_key = _load_api_key()
    if not api_key:
        print("SYNC_STATUS: No THE_ODDS_API_KEY set; preserving existing global_odds_cache.json entries:", len(existing))
        return existing

    updated = 0
    for sport in LEAGUE_KEYS:
        url = (
            f"https://api.the-odds-api.com/v4/sports/{sport}/odds/"
            f"?apiKey={urllib.parse.quote(api_key)}&regions=uk,eu&markets=h2h,totals&oddsFormat=decimal"
        )
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "GEM-V15-Engine/9.5"})
            with urllib.request.urlopen(req, timeout=12) as resp:
                events = json.loads(resp.read().decode("utf-8"))
        except Exception:
            continue

        for ev in events or []:
            home = str(ev.get("home_team") or "").strip()
            away = str(ev.get("away_team") or "").strip()
            commence = str(ev.get("commence_time") or "").strip()
            if not home or not away:
                continue
            best = {}
            for bm in ev.get("bookmakers") or []:
                for mkt in bm.get("markets") or []:
                    mkey = mkt.get("key")
                    for out in mkt.get("outcomes") or []:
                        name = str(out.get("name") or "")
                        price = float(out.get("price") or 0.0)
                        pt = out.get("point")
                        if price <= 1.02:
                            continue
                        if mkey == "h2h":
                            if name == home:
                                best["1"] = max(best.get("1", 0.0), price)
                            elif name == away:
                                best["2"] = max(best.get("2", 0.0), price)
                            elif name.lower() == "draw":
                                best["X"] = max(best.get("X", 0.0), price)
                        elif mkey == "totals" and pt is not None:
                            if name == "Over" and abs(float(pt) - 1.5) < 0.05:
                                best["O1.5"] = max(best.get("O1.5", 0.0), price)
                            elif name == "Over" and abs(float(pt) - 2.5) < 0.05:
                                best["O2.5"] = max(best.get("O2.5", 0.0), price)
            if "1" in best and "X" in best:
                dc_1x = 1.0 / ((1.0 / best["1"]) + (1.0 / best["X"]))
                best["1X"] = round(max(1.06, dc_1x * 0.96), 2)
            if "2" in best and "X" in best:
                dc_x2 = 1.0 / ((1.0 / best["2"]) + (1.0 / best["X"]))
                best["X2"] = round(max(1.06, dc_x2 * 0.96), 2)

            mk = _norm_key(home, away)
            existing[mk] = {
                "fixture": f"{home} v {away}",
                "home": home,
                "away": away,
                "league": ev.get("sport_title") or sport,
                "commence_time": commence,
                "odds_map": {k: round(v, 2) for k, v in best.items()},
                "synced_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
            updated += 1

    cache_path.write_text(json.dumps(existing, indent=2), encoding="utf-8")
    print(f"SYNC_STATUS: Synced {updated} live fixtures into global_odds_cache.json (total cached: {len(existing)})")
    return existing

if __name__ == "__main__":
    sync_odds()
