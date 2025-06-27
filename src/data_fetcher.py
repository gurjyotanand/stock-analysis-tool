# src/data_fetcher.py
from datetime import datetime, timedelta
from ratelimit import limits, sleep_and_retry
from src.config import polygon_client, CALLS_PER_MINUTE, PERIOD, logging


@sleep_and_retry
@limits(calls=CALLS_PER_MINUTE, period=PERIOD)
def get_stock_data(ticker):
    """Fetch stock data from Polygon.io."""
    try:
        end_date = datetime.today()
        start_date = end_date - timedelta(days=2)
        aggs = polygon_client.get_aggs(
            ticker=ticker,
            multiplier=1,
            timespan="day",
            from_=start_date.strftime("%Y-%m-%d"),
            to=end_date.strftime("%Y-%m-%d"),
            limit=2,
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
            f"Fetched data for {ticker}: price={current_price}, change={day_change_pct}%"
        )
        return current_price, day_change_pct
    except Exception as e:
        logging.error(f"Error fetching data for {ticker}: {str(e)}")
        raise
