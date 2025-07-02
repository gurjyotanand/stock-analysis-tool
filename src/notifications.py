# src/notifications.py
import requests
from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, logging
from ratelimit import limits, sleep_and_retry
from src.config import CALLS_PER_MINUTE, PERIOD


@sleep_and_retry
@limits(calls=CALLS_PER_MINUTE, period=PERIOD)
def send_telegram_message(message):
    print("Sending tm")
    """Send message to Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload)
        print(response.text)
        print(response.status_code)
        if response.status_code != 200:
            logging.error(
                f"Telegram API error: {response.status_code} - {response.text}"
            )
            return False
        logging.info("Telegram message sent successfully")
        return True
    except Exception as e:
        logging.error(f"Failed to send Telegram message: {str(e)}")
        return False
