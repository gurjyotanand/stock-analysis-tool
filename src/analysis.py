# src/analysis.py
from src.config import openai_client, logging


def calculate_profit_loss(buy_price, current_price, quantity):
    """Calculate net profit/loss."""
    return (current_price - buy_price) * quantity


def get_ai_analysis(ticker, current_price, day_change_pct, buy_price):
    """Get AI-driven analysis and recommendations using Chatkeyboard_arrow_up OpenAI."""
    prompt = f"""
    Analyze the stock {ticker}:
    - Current price: ${current_price:.2f}
    - 1-day change: {day_change_pct:.2f}%
    - Buy price: ${buy_price:.2f}

    Gather information such as price action and technical analysis of this stock,
    also check for market sentiments quickly about this.
    Check the daily timeframe, weekly timeframe, and monthly timeframe.

    Just Provide output in format below - nothing else except below.
    - Daily Timeframe: [Bullish/Bearish]
    - Weekly Timeframe: [Bullish/Bearish]
    - Monthly Timeframe: [Bullish/Bearish]
    - Short Term [1-2 Months]: Sell/Hold/Buy
    - Long Term [3-6 months]: Sell/Hold/Buy
    - NOTE: [If buy more: According to my buy price, when should I add more?]
            [If sell: What price to sell at?]
        <keep it short, strong prediction and accurate. >
    """
    try:
        system_message = (
            "You are a leading financial analyst providing technical analysis "
            "and recommendations on stocks and crypto. Your task is to analyze "
            "the stock for promising profit."
        )
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1000,
        )
        usage = response.usage
        tokens_info = (
            f"Tokens - Prompt: {usage.prompt_tokens}, "
            f"Completion: {usage.completion_tokens}, "
            f"Total: {usage.total_tokens}"
        )
        logging.info(f"AI analysis for {ticker} completed - {tokens_info}")
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"AI analysis error for {ticker}: {str(e)}")
        return f"AI analysis unavailable: {str(e)}"
