import os, csv, io, json, time, urllib.request

FD_CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "football_data_cache.json")
FD_DIVS = ["E0", "E1", "E2", "E3", "SC0", "SP1", "I1", "D1", "F1", "N1", "P1", "B1"]

ALIASES = {
    "man city": "manchester city", "man united": "manchester united", "man utd": "manchester united",
    "nottm forest": "nottingham forest", "sheff utd": "sheffield united", "sheff wed": "sheffield wednesday",
    "wolves": "wolverhampton wanderers", "newcastle": "newcastle united", "west ham": "west ham united",
    "tottenham": "tottenham hotspur", "spurs": "tottenham hotspur", "brighton": "brighton and hove albion",
    "leicester": "leicester city", "leeds": "leeds united", "ipswich": "ipswich town",
    "inter": "internazionale", "milan": "ac milan", "ath madrid": "atletico madrid",
    "ath bilbao": "athletic club", "betis": "real betis", "sociedad": "real sociedad",
    "ein frankfurt": "eintracht frankfurt", "mgladbach": "borussia monchengladbach",
    "leverkusen": "bayer leverkusen", "dortmund": "borussia dortmund", "bayern munich": "bayern munchen",
    "paris sg": "paris saint germain", "psg": "paris saint germain", "st etienne": "saint etienne",
    "sp lisbon": "sporting cp", "porto": "fc porto", "benfica": "sl benfica"
}

def _norm(name):
    s = re.sub(r"[^a-z0-9 ]+", " ", str(name or "").lower()).strip()
    s = re.sub(r"\s+", " ", s)
    return ALIASES.get(s, s)

def sync_football_data(force=False):
    if not force and os.path.exists(FD_CACHE):
        try:
            age = time.time() - os.path.getmtime(FD_CACHE)
            if age < 43200:
                return json.load(open(FD_CACHE, encoding="utf-8"))
        except Exception:
            pass

    teams = {}
    sharp_edges = []
    seasons = ["2627", "2526"]
    for div in FD_DIVS:
        rows = []
        for sz in seasons:
            url = f"https://www.football-data.co.uk/mmz4281/{sz}/{div}.csv"
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                txt = urllib.request.urlopen(req, timeout=8).read().decode("utf-8", errors="ignore")
                rdr = list(csv.DictReader(io.StringIO(txt)))
                if len(rdr) >= 10:
                    rows = rdr
                    break
            except Exception:
                continue

        for r in rows[-180:]:
            ht, at = _norm(r.get("HomeTeam")), _norm(r.get("AwayTeam"))
            if not ht or not at:
                continue
            try:
                hg, ag = int(float(r["FTHG"])), int(float(r["FTAG"]))
                for tm, gf, ga, is_h in ((ht, hg, ag, True), (at, ag, hg, False)):
                    d = teams.setdefault(tm, {"hgf": 0.0, "hga": 0.0, "hn": 0, "agf": 0.0, "aga": 0.0, "an": 0})
                    if is_h:
                        d["hgf"] += gf; d["hga"] += ga; d["hn"] += 1
                    else:
                        d["agf"] += gf; d["aga"] += ga; d["an"] += 1
            except Exception:
                pass
            try:
                psh, b365h = float(r.get("PSH") or 0), float(r.get("B365H") or 0)
                if psh > 1.2 and b365h > 1.2:
                    sharp_edges.append(round((b365h / psh - 1.0) * 100.0, 2))
            except Exception:
                pass

    ratings = {}
    for tm, d in teams.items():
        h_att = ((d["hgf"] + 4.2) / (d["hn"] + 3.0)) / 1.42
        h_def = ((d["hga"] + 3.4) / (d["hn"] + 3.0)) / 1.15
        a_att = ((d["agf"] + 3.4) / (d["an"] + 3.0)) / 1.15
        a_def = ((d["aga"] + 4.2) / (d["an"] + 3.0)) / 1.42
        ratings[tm] = {
            "h_att": round(max(0.55, min(1.85, h_att)), 3),
            "h_def": round(max(0.55, min(1.85, h_def)), 3),
            "a_att": round(max(0.55, min(1.85, a_att)), 3),
            "a_def": round(max(0.55, min(1.85, a_def)), 3),
            "gp": d["hn"] + d["an"]
        }

    payload = {
        "source": "football-data.co.uk",
        "updated": int(time.time()),
        "teams": ratings,
        "avg_pin_b365_spread": round(sum(sharp_edges) / max(1, len(sharp_edges)), 2) if sharp_edges else 2.4
    }
    try:
        json.dump(payload, open(FD_CACHE, "w", encoding="utf-8"))
    except Exception:
        pass
    return payload

def get_fixture_xg(home_name, away_name, base_lh=1.38, base_la=1.18):
    fd = sync_football_data(force=False)
    tms = fd.get("teams", {})
    hr = tms.get(_norm(home_name))
    ar = tms.get(_norm(away_name))
    if not hr and not ar:
        return base_lh, base_la, False
    h_att = hr["h_att"] if hr else 1.0
    h_def = hr["h_def"] if hr else 1.0
    a_att = ar["a_att"] if ar else 1.0
    a_def = ar["a_def"] if ar else 1.0
    lh = round(max(0.45, min(3.40, base_lh * h_att * a_def)), 2)
    la = round(max(0.40, min(3.10, base_la * a_att * h_def)), 2)
    return lh, la, True
