import os
import time
import logging
from datetime import datetime, timedelta
import pytz
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from polygon import RESTClient
import requests
from ratelimit import limits, sleep_and_retry
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()  # This loads the .env file

# Configuration
SHEET_NAME = "stock-sheet-gurjyot"  # Name of your Google Sheet
WORKSHEET_NAME = "Sheet1"
LOG_FILE = "stock_analysis.log"

# API-KEYS
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
google_creds_json = os.getenv("GOOGLE_CREDS_JSON")

# LOADING CREDENTIALS JSON
creds_dict = json.loads(google_creds_json)


# Polygon rate limit: 5 calls per minute
CALLS_PER_MINUTE = 5
PERIOD = 60  # seconds

# Setup logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s")


# Initialize Google Sheets
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).worksheet(WORKSHEET_NAME)

# Initialize OpenAI
client = OpenAI(
    api_key=os.getenv(OPENAI_API_KEY)
)


# Initialize Polygon client
polygon_client = RESTClient(api_key=POLYGON_API_KEY)


@sleep_and_retry
@limits(calls=CALLS_PER_MINUTE, period=PERIOD)
def get_stock_data(ticker):
    """Fetch stock data from Polygon.io."""
    try:
        # Get current date and previous day for 1-day change
        end_date = datetime.today()
        start_date = end_date - timedelta(days=2)
        aggs = polygon_client.get_aggs(
            ticker=ticker,
            multiplier=1,
            timespan="day",
            from_=start_date.strftime("%Y-%m-%d"),
            to=end_date.strftime("%Y-%m-%d"),
            limit=2
        )
        if len(aggs) >= 2:
            prev_close = aggs[-2].close
            curr_close = aggs[-1].close
            current_price = curr_close
            day_change_pct = ((curr_close - prev_close) / prev_close) * 100
        else:
            current_price = aggs[-1].close if aggs else 0.0
            day_change_pct = 0.0
        logging.info(
            f"Fetched data for {ticker}: price={current_price}, "
            f"change={day_change_pct}%")
        return current_price, day_change_pct
    except Exception as e:
        logging.error(f"Error fetching data for {ticker}: {str(e)}")
        raise


def calculate_profit_loss(buy_price, current_price, quantity):
    """Calculate net profit/loss."""
    return (current_price - buy_price) * quantity


def get_ai_analysis(ticker, current_price, day_change_pct, buy_price):
    """Get AI-driven analysis and recommendations using ChatGPT."""
    prompt = f"""
    Analyze the stock {ticker}:
    - Current price: ${current_price:.2f}
    - 1-day change: {day_change_pct:.2f}%
    - Buy price: ${buy_price:.2f}

    Gather information such as price action and
    technical analysis of this stock,
    also check for market sentiments quicky about this.
    Check the daily timeframe, weekly timeframe. and monthly time frame.

    Just Provide output in format below - nothing else except below.
    - Daily Timeframe: [Bullish/Bearish]
    - Weekly Timeframe: [Bullish/Bearish]
    - Mothly Timeframe: [Bullish/Bearish]
    - Short Term [1-2 Months]: Sell/Hold/Buy
    - Long Term [3-6 months]: Sell/Hold/Buy
    - NOTE: [If buy more: According to my buy price, when should I add more?]
            [If sell: What price to sell at?]
        <keep it short, strong prediction and acurate. >
    """
    try:
        system_message = (
            "You are a leading financial analyst providing technical analysis "
            "and recommendations on stocks and crypto You task is to analyze "
            "the stock for promising profit."
        )

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000
        )
        usage = response.usage
        tokens_info = (f"Tokens - Prompt: {usage.prompt_tokens}, "
                       f"Completion: {usage.completion_tokens}, "
                       f"Total: {usage.total_tokens}")
        logging.info(f"AI analysis for {ticker} completed - {tokens_info}")
        return response.choices[0].message.content

    except Exception as e:
        logging.error(f"AI analysis error for {ticker}: {str(e)}")
        return f"AI analysis unavailable: {str(e)}"


@sleep_and_retry
@limits(calls=CALLS_PER_MINUTE, period=PERIOD)
def send_telegram_message(message):
    """Send message to Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            logging.error(
                f"Telegram API error: {response.status_code} - {response.text}"
                f" - {response.text}"
                )
            return False
        logging.info("Telegram message sent successfully")
        return True
    except Exception as e:
        logging.error(f"Failed to send Telegram message: {str(e)}")
        return False


def main():
    """Main function to process stock data and send Telegram update."""
    et_tz = pytz.timezone("America/New_York")
    current_time = datetime.now(et_tz)
    date_str = current_time.strftime("%Y-%m-%d %I:%M %p ET")
    logging.info(f"Starting stock analysis at {date_str}")

    # Read portfolio from Google Sheet
    try:
        records = sheet.get_all_records()
        if not records:
            message = "Error: No data found in Google Sheet."
            send_telegram_message(message)
            logging.error(message)
            return
    except Exception as e:
        message = f"Error reading Google Sheet: {str(e)}"
        send_telegram_message(message)
        logging.error(message)
        return

    # Process stocks in batches to respect Polygon rate limits
    message = f"📊 *USD Stock Update ({date_str})*\n\n"
    batch_size = CALLS_PER_MINUTE - 1  # Reserve 1 call for Telegram
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        for record in batch:
            ticker = record["Ticker"].upper()
            buy_price = float(record["BuyInPrice"])
            quantity = float(record["Quantity"])
            try:
                current_price, day_change_pct = get_stock_data(ticker)
                profit_loss = calculate_profit_loss(
                    buy_price, current_price, quantity)
                ai_analysis = get_ai_analysis(
                    ticker, current_price, day_change_pct, buy_price)
                pl_emoji = "🟢 " if profit_loss >= 0 else "🔴 "
                message += f"""\n💸 *{ticker}*
- Price: `${current_price:.2f}` ({day_change_pct:+.2f}%)
- Qty: `{quantity} @ ${buy_price:.2f}`
- *P/L:* {pl_emoji}{'+' if profit_loss >= 0 else ''}${profit_loss:.2f}

🧠 *AI View*
{ai_analysis}

"""
                message += "\n────────────\n"

            except Exception as e:
                message += f"**{ticker}**: Error fetching data: {str(e)}\n\n"
        if i + batch_size < len(records):
            logging.info(
                f"Batch completed, waiting {PERIOD} seconds for rate limit")
            time.sleep(PERIOD)

    # Send Telegram message
    print(message)
    if not send_telegram_message(message):
        print("Failed to send Telegram message.")


if __name__ == "__main__":
    main()
