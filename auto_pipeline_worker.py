# === GEM V15-DC-13.8 CONTINUOUS BACKGROUND AUTOMATION WORKER ===
import subprocess, time, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent
PY = sys.executable or "py"

def run_step(args, timeout=25):
    try:
        subprocess.run([PY] + args, cwd=str(ROOT), timeout=timeout, check=False,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def main():
    while True:
        if pathlib.Path("sync_live_odds.py").exists():
            run_step(["sync_live_odds.py"], timeout=20)
        if pathlib.Path("run_daily_slip.py").exists():
            run_step(["run_daily_slip.py"], timeout=20)
        run_step(["-c", (
            "from all_markets_engine import build_ui_compatible_markets; "
            "import json, pathlib, re; "
            "p = pathlib.Path('last_good_feed.json'); "
            "print('SYNC_TICK_OK')"
        )], timeout=10)
        time.sleep(240)

if __name__ == "__main__":
    main()
