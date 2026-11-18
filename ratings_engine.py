import sqlite3, math

DB = "team_ratings.db"

def init_ratings():
    c = sqlite3.connect(DB)
    c.execute("CREATE TABLE IF NOT EXISTS ratings (team TEXT PRIMARY KEY, elo REAL DEFAULT 1500.0, att REAL DEFAULT 1.0, def REAL DEFAULT 1.0, sigma REAL DEFAULT 0.18, matches INTEGER DEFAULT 0)")
    c.commit(); c.close()

def get_team(team):
    init_ratings()
    c = sqlite3.connect(DB)
    row = c.execute("SELECT elo, att, def, sigma, matches FROM ratings WHERE team=?", (team,)).fetchone()
    if not row:
        c.execute("INSERT INTO ratings (team) VALUES (?)", (team,))
        c.commit()
        row = (1500.0, 1.0, 1.0, 0.18, 0)
    c.close()
    return {"elo": row[0], "att": row[1], "def": row[2], "sigma": row[3], "matches": row[4]}

def update_match_ratings(home, away, hg, ag, k=24.0):
    h, a = get_team(home), get_team(away)
    exp_h = 1.0 / (1.0 + 10.0 ** ((a["elo"] - (h["elo"] + 55.0)) / 400.0))
    act_h = 1.0 if hg > ag else (0.5 if hg == ag else 0.0)
    mov = math.log(abs(hg - ag) + 1.0) + 1.0
    delta = k * mov * (act_h - exp_h)

    h_elo, a_elo = round(h["elo"] + delta, 2), round(a["elo"] - delta, 2)
    h_att = round(max(0.45, min(2.10, h["att"] * 0.92 + (hg / max(0.55, a["def"] * 1.32)) * 0.08)), 4)
    h_def = round(max(0.45, min(2.10, h["def"] * 0.92 + (ag / max(0.55, a["att"] * 1.32)) * 0.08)), 4)
    a_att = round(max(0.45, min(2.10, a["att"] * 0.92 + (ag / max(0.55, h["def"] * 1.32)) * 0.08)), 4)
    a_def = round(max(0.45, min(2.10, a["def"] * 0.92 + (hg / max(0.55, h["att"] * 1.32)) * 0.08)), 4)
    h_sig = round(max(0.05, h["sigma"] * 0.96), 4)
    a_sig = round(max(0.05, a["sigma"] * 0.96), 4)

    c = sqlite3.connect(DB)
    c.execute("UPDATE ratings SET elo=?, att=?, def=?, sigma=?, matches=matches+1 WHERE team=?", (h_elo, h_att, h_def, h_sig, home))
    c.execute("UPDATE ratings SET elo=?, att=?, def=?, sigma=?, matches=matches+1 WHERE team=?", (a_elo, a_att, a_def, a_sig, away))
    c.commit(); c.close()
    return {"home_elo": h_elo, "away_elo": a_elo}

def get_elo_xg_prior(home, away, base_avg=1.30, home_adv=1.12):
    h, a = get_team(home), get_team(away)
    elo_edge = max(0.75, min(1.35, 1.0 + ((h["elo"] - a["elo"]) / 1600.0)))
    lh = max(0.25, min(3.20, h["att"] * a["def"] * base_avg * home_adv * elo_edge))
    la = max(0.25, min(3.20, a["att"] * h["def"] * base_avg / elo_edge))
    uncertainty = round((h["sigma"] + a["sigma"]) / 2.0, 4)
    return round(lh, 3), round(la, 3), uncertainty
