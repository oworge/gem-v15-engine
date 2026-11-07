# alert_engine.py - Automated Telegram & Discord Syndicate Alert Dispatcher
import os
import urllib.request
import urllib.parse
import json
import logging

class SyndicateAlertDispatcher:
    def __init__(self):
        self.telegram_token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
        self.telegram_chat_id = os.environ.get('TELEGRAM_CHAT_ID', '')
        self.discord_webhook_url = os.environ.get('DISCORD_WEBHOOK_URL', '')

    def dispatch_value_alert(self, match_name, market, odds, ev_pct, confidence):
        alert_message = (
            f"🚨 *EDGEMETRIX V300 SYNDICATE ALERT* 🚨\n\n"
            f"⚽ *Fixture:* {match_name}\n"
            f"🎯 *Selection:* {market}\n"
            f"📈 *Odds:* @{odds} | *EV:* +{ev_pct}%\n"
            f"🛡️ *Grade:* {confidence}\n"
            f"⚡ *Status:* Bayesian & Poisson Verified"
        )
        
        logging.info(f"DISPATCHED ALERT: {alert_message}")

        # Dispatch to Telegram Bot API
        if self.telegram_token and self.telegram_chat_id:
            try:
                api_url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
                payload = json.dumps({
                    "chat_id": self.telegram_chat_id,
                    "text": alert_message,
                    "parse_mode": "Markdown"
                }).encode('utf-8')
                
                req = urllib.request.Request(
                    api_url,
                    data=payload,
                    headers={'Content-Type': 'application/json'}
                )
                urllib.request.urlopen(req, timeout=5)
            except Exception as e:
                logging.error(f"Telegram Alert Error: {e}")

        # Dispatch to Discord if configured
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
