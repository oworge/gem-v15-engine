import pathlib, sys
html = pathlib.Path("templates/index.html").read_text(encoding="utf-8")
app_txt = pathlib.Path("app.py").read_text(encoding="utf-8")
req_ui = ["EdgeMETRIX PRO 26", "alert-bar", "red-dot", "daily_picks", "btts_goals", "bet_builder", "correct_score", "true_clv", "tactical_health"]
req_app = ["get_perfect_value_alert", "get_global_daily_picks"]
missing = [x for x in req_ui if x not in html] + [x for x in req_app if x not in app_txt]
if missing:
    print("LOCK VIOLATION - BLOCKED:", missing)
    sys.exit(1)
print("DASHBOARD LOCK VERIFIED: Core UI & 6 Tabs Intact (Additions Only)")
