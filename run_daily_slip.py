import app, json, pathlib

c = app.app.test_client()
for tab in ("all", "uk", "europe", "france", "italy", "german", "spain", "row", "bet_builder"):
    r = c.get(f"/api/tab-picks?min_ev=2.5&tab={tab}")
    d = r.get_json() or {}
    picks = d.get("picks") or []
    print(f"tab={tab:11s} -> status={r.status_code} | count={len(picks)} | sample={[p.get('f') for p in picks[:2]]}")

slip = c.get("/api/auto-slip").get_json() or {}
pathlib.Path("daily_auto_slip.json").write_text(json.dumps(slip, indent=2), encoding="utf-8")
print("\nDAILY AUTO SLIP SAVED:", json.dumps(slip, indent=2))
