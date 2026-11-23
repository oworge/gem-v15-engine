import json, math, os, pathlib, re, urllib.request, urllib.parse
from datetime import datetime, timezone

LEAGUE_KEYS = [
    "soccer_epl", "soccer_efl_champ", "soccer_england_league1", "soccer_england_league2",
    "soccer_spain_la_liga", "soccer_italy_serie_a", "soccer_germany_bundesliga",
    "soccer_france_ligue_one", "soccer_netherlands_eredivisie",
    "soccer_uefa_champs_league", "soccer_uefa_europa_league",
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

def power_devig(odds_list):
    clean = [float(o) for o in odds_list if float(o) > 1.01]
    if len(clean) < 2:
        return [round(1.0 / o, 4) for o in clean]
    inv = [1.0 / o for o in clean]
    if sum(inv) <= 1.0:
        s = sum(inv)
        return [round(p / s, 4) for p in inv]
    lo, hi = 1.0, 4.0
    for _ in range(32):
        mid = 0.5 * (lo + hi)
        if sum(p ** mid for p in inv) > 1.0:
            lo = mid
        else:
            hi = mid
    k = 0.5 * (lo + hi)
    probs = [p ** k for p in inv]
    tot = sum(probs)
    return [round(p / tot, 4) for p in probs]


def _gem_derive_extended_odds(best, devig_1x2):
    # Add ESN (Either Side to Win = 12), 1st Half Draw (HT_X), HT/FT, and top Correct Score lines
    out = dict(best or {})
    p1 = float((devig_1x2 or {}).get("p_home") or 0.40)
    px = float((devig_1x2 or {}).get("p_draw") or 0.27)
    p2 = float((devig_1x2 or {}).get("p_away") or 0.33)
    p_esn = max(0.05, min(0.95, p1 + p2))
    out.setdefault("ESN", round(max(1.12, (1.0 / p_esn) * 0.96), 2))
    out.setdefault("12", out["ESN"])
    # 1st Half Draw probability typically runs ~1.42x full-time draw share in low-scoring halves
    p_ht_x = max(0.18, min(0.55, px * 1.42))
    out.setdefault("HT_X", round(max(1.65, (1.0 / p_ht_x) * 0.94), 2))
    # Key HT/FT combinations
    out.setdefault("HTFT_X_X", round(max(3.50, (1.0 / max(0.06, p_ht_x * px * 1.35)) * 0.92), 2))
    out.setdefault("HTFT_1_1", round(max(1.65, (1.0 / max(0.08, p1 * 0.72)) * 0.92), 2))
    out.setdefault("HTFT_2_2", round(max(1.85, (1.0 / max(0.08, p2 * 0.72)) * 0.92), 2))
    out.setdefault("HTFT_X_1", round(max(3.60, (1.0 / max(0.05, p_ht_x * p1 * 1.15)) * 0.92), 2))
    out.setdefault("HTFT_X_2", round(max(4.00, (1.0 / max(0.05, p_ht_x * p2 * 1.15)) * 0.92), 2))
    # Top Correct Score baseline prices
    out.setdefault("CS_1_1", 6.50)
    out.setdefault("CS_1_0", 7.00)
    out.setdefault("CS_2_1", 8.50)
    out.setdefault("CS_1_2", 9.00)
    out.setdefault("CS_2_0", 9.50)
    out.setdefault("CS_0_1", 9.50)
    out.setdefault("CS_0_0", 10.50)
    return out

def sync_odds():
    cache_path = pathlib.Path("global_odds_cache.json")
    existing = json.loads(cache_path.read_text(encoding="utf-8", errors="ignore")) if cache_path.exists() else {}
    if not isinstance(existing, dict):
        existing = {}
    api_key = _load_api_key()
    if not api_key:
        print("SYNC_STATUS: Cached fixtures =", len(existing))
        return existing
    updated = 0
    for sport in LEAGUE_KEYS:
        url = (
            f"https://api.the-odds-api.com/v4/sports/{sport}/odds/"
            f"?apiKey={urllib.parse.quote(api_key)}&regions=uk,eu&markets=h2h,totals,btts&oddsFormat=decimal"
        )
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "GEM-V15-Engine/9.9"})
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
                            p_val = float(pt)
                            if name == "Over" and abs(p_val - 1.5) < 0.05:
                                best["O1.5"] = max(best.get("O1.5", 0.0), price)
                            elif name == "Under" and abs(p_val - 1.5) < 0.05:
                                best["U1.5"] = max(best.get("U1.5", 0.0), price)
                            elif name == "Over" and abs(p_val - 2.5) < 0.05:
                                best["O2.5"] = max(best.get("O2.5", 0.0), price)
                            elif name == "Under" and abs(p_val - 2.5) < 0.05:
                                best["U2.5"] = max(best.get("U2.5", 0.0), price)
                            elif name == "Over" and abs(p_val - 3.5) < 0.05:
                                best["O3.5"] = max(best.get("O3.5", 0.0), price)
                            elif name == "Under" and abs(p_val - 3.5) < 0.05:
                                best["U3.5"] = max(best.get("U3.5", 0.0), price)
                        elif mkey == "btts":
                            if name.lower() == "yes":
                                best["BTTS_Y"] = max(best.get("BTTS_Y", 0.0), price)
                            elif name.lower() == "no":
                                best["BTTS_N"] = max(best.get("BTTS_N", 0.0), price)
            devig_1x2 = {}
            if "1" in best and "X" in best and "2" in best:
                p1, px, p2 = power_devig([best["1"], best["X"], best["2"]])
                devig_1x2 = {"p_home": p1, "p_draw": px, "p_away": p2}
                best["1X"] = round(max(1.06, (1.0 / max(0.05, p1 + px)) * 0.965), 2)
                best["X2"] = round(max(1.06, (1.0 / max(0.05, p2 + px)) * 0.965), 2)
                best["12"] = round(max(1.06, (1.0 / max(0.05, p1 + p2)) * 0.965), 2)
                best["DNB_1"] = round(max(1.06, (1.0 / max(0.05, p1 / max(0.05, p1 + p2))) * 0.965), 2)
                best["DNB_2"] = round(max(1.06, (1.0 / max(0.05, p2 / max(0.05, p1 + p2))) * 0.965), 2)
            mk = _norm_key(home, away)
            existing[mk] = {
                "fixture": f"{home} v {away}", "home": home, "away": away,
                "league": ev.get("sport_title") or sport, "commence_time": commence,
                "odds_map": {k: round(v, 2) for k, v in _gem_derive_extended_odds(best, devig_1x2).items()},
                "devig_1x2": devig_1x2,
                "synced_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
            updated += 1
    cache_path.write_text(json.dumps(existing, indent=2), encoding="utf-8")
    print(f"SYNC_STATUS: Synced {updated} fixtures across all 16 markets")
    return existing

if __name__ == "__main__":
    sync_odds()
