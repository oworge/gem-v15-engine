@echo off
cd /d C:\Users\georg\gem-v15-live
py sync_live_odds.py
py run_daily_slip.py
