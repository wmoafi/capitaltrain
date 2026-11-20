@echo off
title CapitalTrain System Auto-Starter
cd /d I:\CapitalTrain

echo [1/3] Checking and launching Web Server on port 6060...
start "CapitalTrain_WebServer" /min "C:\Python314\python.exe" serve_6060.py

echo [2/3] Checking and launching Unified Telegram Bot (LRT + Metro Line 3)...
set PYTHONIOENCODING=utf-8
start "CapitalTrain_TelegramBot" /min "C:\Python314\python.exe" telegram_bot_runner.py

echo [3/3] Done. All services are active and running!
