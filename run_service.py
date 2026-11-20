#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CapitalTrain Unified Cloud Runner (Web + Telegram Bot)
Runs both the Web Server (serve_6060) and Telegram Bot (telegram_bot_runner)
concurrently on Render.com.
"""

import os
import sys
import threading
import time

# Ensure UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

def run_telegram_bot():
    """Runs the Telegram Bot in a resilient background thread."""
    print("🚀 [Telegram Bot] Initializing unified bot worker...", flush=True)
    time.sleep(2)  # Give web server a head start to bind port
    try:
        import telegram_bot_runner
        telegram_bot_runner.main()
    except Exception as e:
        print(f"⚠️ [Telegram Bot Error]: {e}", flush=True)
        # Attempt to revive bot if it crashes
        while True:
            time.sleep(5)
            try:
                print("🔄 [Telegram Bot] Restarting bot worker...", flush=True)
                import telegram_bot_runner
                telegram_bot_runner.main()
            except Exception as ex:
                print(f"⚠️ [Telegram Bot Crash]: {ex}", flush=True)

def run_web_server():
    """Runs the Web Server listening on Render PORT."""
    import serve_6060
    port = int(os.environ.get("PORT", 6060))
    print(f"🌐 [Web Server] Starting CapitalTrain Web Server on port {port}...", flush=True)
    serve_6060.socketserver.TCPServer.allow_reuse_address = True
    with serve_6060.socketserver.TCPServer(("", port), serve_6060.CustomHandler) as httpd:
        print(f"✅ [Web Server] Serving at http://0.0.0.0:{port}", flush=True)
        httpd.serve_forever()

if __name__ == "__main__":
    print("==================================================", flush=True)
    print("🚆 Starting CapitalTrain Unified Cloud Service", flush=True)
    print("==================================================", flush=True)
    
    # 1. Start Telegram Bot in background daemon thread
    bot_thread = threading.Thread(target=run_telegram_bot, daemon=True, name="TelegramBotWorker")
    bot_thread.start()

    # 2. Start Web Server in main thread (binds Render PORT immediately)
    run_web_server()
