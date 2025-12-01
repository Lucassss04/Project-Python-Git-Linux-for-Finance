import datetime as dt
import pandas as pd
import os

from data import load_yahoo_data
from metrics import compute_performance_metrics

TICKER = "^FCHI" 
REPORT_FILE = "daily_report_log.txt"
DAYS_LOOKBACK = 252 
TARGET_TIME = "20:00"

def generate_daily_report():
    end_date = dt.date.today()
    start_date = end_date - dt.timedelta(days=DAYS_LOOKBACK)

    data = load_yahoo_data(TICKER, start=start_date, end=end_date)

    if data is None or data.empty:
        log_message = f"[{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERROR: No data for {TICKER}."
        print(log_message)
        with open(REPORT_FILE, "a") as f:
            f.write(log_message + "\n")
        return

    returns = data["return"].dropna()
    metrics = compute_performance_metrics(returns)

    last_price = data["price"].iloc[-1]
    last_price = float(last_price)
    
    report_content = f"""
--- Daily Report ({end_date}) for {TICKER} (CAC40)---
Closing Price: {last_price:.2f}
Cumulative Return: {metrics['cum_return']:.2%}
Annualized Volatility: {metrics['ann_vol']:.2%}
Sharpe Ratio: {metrics['sharpe']:.2f}
Max Drawdown: {metrics['max_dd']:.2%}
Daily VaR 95%: {metrics['var_95']:.2%}
"""
    
    with open(REPORT_FILE, "a") as f:
        f.write(report_content)
    
    print(f"Rapport généré et sauvegardé dans {REPORT_FILE}")

if __name__ == "__main__":
    generate_daily_report()