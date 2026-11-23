@echo off
title EDGEMETRIX ? Beat the Bookie
echo.
echo ========================================
echo   EDGEMETRIX ? DAILY VALUE SCAN
echo   Finding value bets...
echo ========================================
echo.
cd /d "C:\Users\georg\gem-v15-live"
python generate_daily.py
echo.
echo ========================================
echo   ? DONE ? Value bets found!
echo ========================================
echo.
pause
