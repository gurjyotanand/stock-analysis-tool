# src/main.py
import time
from datetime import datetime
import pytz
from src.config import sheet, TEST_MODE, logging, CALLS_PER_MINUTE, PERIOD
from src.data_fetcher import get_stock_data
from src.analysis import calculate_profit_loss, get_ai_analysis
from src.notifications import send_telegram_message


def main():
    """Main function to process stock data and send Telegram update."""
    et_tz = pytz.timezone("America/New_York")
    current_time = datetime.now(et_tz)
    date_str = current_time.strftime("%Y-%m-%d %I:%M %p ET")
    logging.info(f"Starting stock analysis at {date_str}")

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

    message = f"📊 *USD Stock Update ({date_str})*\n\n"
    batch_size = CALLS_PER_MINUTE - 1
    for i in range(0, len(records), batch_size):
        batch = records[i : i + batch_size]
        for record in batch:
            ticker = record["Ticker"].upper()
            buy_price = float(record["BuyInPrice"])
            quantity = float(record["Quantity"])
            type = record["Type"].lower()
            try:
                current_price, day_change_pct, daily_high, daily_low = get_stock_data(
                    ticker, type
                )
                profit_loss = calculate_profit_loss(buy_price, current_price, quantity)
                ai_analysis = get_ai_analysis(
                    ticker, current_price, day_change_pct, buy_price
                )
                pl_emoji = "🟢 " if profit_loss >= 0 else "🔴 "
                message += f"""\n💸 *{ticker}*
- Price: `${current_price:.2f}` ({day_change_pct:+.2f}%)
- High: `${daily_high:.2f}` | 📉 Low: `${daily_low:.2f}`
- Qty: `{quantity} @ ${buy_price:.2f}`
- *P/L:* {pl_emoji}{"+" if profit_loss >= 0 else ""}${profit_loss:.2f}
\n🧠 *AI View*
{ai_analysis}

"""
                message += "\n────────────\n"
            except Exception as e:
                message += f"**{ticker}**: Error fetching data: {str(e)}\n\n"
        if i + batch_size < len(records):
            logging.info(f"Batch completed, waiting {PERIOD} seconds for rate limit")
            time.sleep(PERIOD)

    print(message)
    if TEST_MODE:
        print("Telegram message would be sent in TEST MODE.")
    else:
        if not send_telegram_message(message):
            print("Failed to send Telegram message.")


if __name__ == "__main__":
    main()
