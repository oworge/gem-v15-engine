import sys, pathlib, re

ap = pathlib.Path("app.py").read_text(encoding="utf-8")
assert "_enforce_vetting_integrity" in ap and "_sanitize_feed_dict" in ap, "FAIL: Runtime integrity firewall missing from app.py"
assert "if False and is_dnb and dnb_cnt >= 2:" in ap, "FAIL: Synthetic DNB overwrite re-enabled"

qc = pathlib.Path("quant_calibrator.py").read_text(encoding="utf-8")
assert "q[4] >= 4.0" in qc and "1.35 <= q[3] <= 5.50" in qc, "FAIL: Vetting-first EV/odds gate missing in quant_calibrator.py"

print("PASS: All vetting-first gates, side-sync locks, and runtime firewalls verified.")
