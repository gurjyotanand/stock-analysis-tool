import requests
from datetime import datetime, timedelta
from ratelimit import limits, sleep_and_retry
from src.config import ALPHA_VANTAGE_API_KEY, CALLS_PER_MINUTE, PERIOD, logging

BASE_URL = "https://www.alphavantage.co/query"

@sleep_and_retry
@limits(calls=CALLS_PER_MINUTE, period=PERIOD)
def get_stock_data(ticker, type):
    """Fetch stock data from Alpha Vantage."""
    try:
        ticker = ticker.upper()
        type = type.lower()
        #print(type)

        if type == "stock":
        # API parameters for daily time series
            params = {
                "function": "TIME_SERIES_DAILY",
                "symbol": ticker,
                "apikey": ALPHA_VANTAGE_API_KEY,
                "outputsize": "compact"  # Get recent data only
            }

        else:
             #print("CRYPTO")
             params = {
                "function": "DIGITAL_CURRENCY_DAILY",
                "symbol": ticker,
                "apikey": ALPHA_VANTAGE_API_KEY,
                "market": "USD",  # Assuming USD market for crypto
                "outputsize": "compact"  # Get recent data only
            }

        
        # Make API request
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()  # Raise exception for bad status codes
        data = response.json()
        #print(data)
        
        # Check for API errors
        if "Error Message" in data:
            logging.error(f"API Error for {ticker}: {data['Error Message']}")
            raise Exception(f"API Error: {data['Error Message']}")
        if "Note" in data:
            logging.error(f"API Limit Reached for {ticker}: {data['Note']}")
            raise Exception(f"API Limit Reached: {data['Note']}")
        if ("Time Series (Daily)" not in data) and ("Time Series (Digital Currency Daily)" not in data):
            logging.error(f"No daily time series data available for {ticker}.")
            raise Exception("No daily time series data available.")
        
        # Get daily time series data
        if type == "stock":
            daily_data = data["Time Series (Daily)"]
        else:
            daily_data = data["Time Series (Digital Currency Daily)"]

        available_dates = sorted(daily_data.keys(), reverse=True)
        
        # Ensure we have at least one day of data
        if not available_dates:
            logging.error(f"No trading data available for {ticker}.")
            raise Exception("No trading data available.")
        
        # Get current price (most recent close)
        current_price = float(daily_data[available_dates[0]]["4. close"])
        day_change_pct = 0.0
        
        #Get daily high and daily low
        daily_high = float(daily_data[available_dates[0]]["2. high"])
        daily_low = float(daily_data[available_dates[0]]["3. low"])

        # Calculate day change if we have previous day's data
        if len(available_dates) >= 2:
            curr_close = float(daily_data[available_dates[0]]["4. close"])
            prev_close = float(daily_data[available_dates[1]]["4. close"])
            day_change_pct = ((curr_close - prev_close) / prev_close) * 100
        
        logging.info(
            f"Fetched data for {ticker}: price={current_price}, change={day_change_pct}%"
        )
        return current_price, day_change_pct, daily_high, daily_low
    
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data for {ticker}: {str(e)}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error for {ticker}: {str(e)}")
        raise