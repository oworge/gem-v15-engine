# alert_engine.py - Automated Syndicate Alert Dispatcher
import os
import urllib.request
import json
import logging

class SyndicateAlertDispatcher:
    def __init__(self):
        # Optional environment variables for Telegram / Discord webhooks
        self.telegram_token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
        self.telegram_chat_id = os.environ.get('TELEGRAM_CHAT_ID', '')
        self.discord_webhook_url = os.environ.get('DISCORD_WEBHOOK_URL', '')

    def dispatch_value_alert(self, match_name, market, odds, ev_pct, confidence):
        alert_message = (
            f"🚨 **EDGEMETRIX V300 SYNDICATE ALERT** 🚨\n"
            f"⚽ **Fixture:** {match_name}\n"
            f"🎯 **Selection:** {market}\n"
            f"📈 **Odds:** @{odds} | **EV:** +{ev_pct}%\n"
            f"🛡️ **Grade:** {confidence}\n"
            f"⚡ Status: SHARP POISSON & BAYESIAN VERIFIED"
        )
        
        # Log to console
        logging.info(f"DISPATCHED ALERT: {alert_message}")

        # Send to Discord if webhook configured
        if self.discord_webhook_url:
            try:
                payload = json.dumps({"content": alert_message}).encode('utf-8')
                req = urllib.request.Request(
                    self.discord_webhook_url,
                    data=payload,
                    headers={'Content-Type': 'application/json'}
                )
                urllib.request.urlopen(req, timeout=5)
            except Exception as e:
                logging.error(f"Discord Alert Error: {e}")

        return alert_message

ALERT_ENGINE = SyndicateAlertDispatcher()
