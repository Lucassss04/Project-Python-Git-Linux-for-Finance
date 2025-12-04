import datetime as dt
import os
import pandas as pd  # kept if you want to extend the report later

from data import load_yahoo_data
from metrics import compute_performance_metrics

TICKER = "^FCHI"          # main index (CAC 40)
REPORT_FILE = "daily_report_log.txt"
DAYS_LOOKBACK = 252       # lookback for performance metrics


def generate_daily_report():
    end_date = dt.date.today()
    start_date = end_date - dt.timedelta(days=DAYS_LOOKBACK)

    data = load_yahoo_data(TICKER, start=start_date, end=end_date)

    if data is None or data.empty:
        log_message = (
            f"[{dt.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}] "
            f"ERROR: No data for {TICKER}."
        )
        print(log_message)
        with open(REPORT_FILE, "a") as f:
            f.write(log_message + "\n")
        return

    returns = data["return"].dropna()
    metrics = compute_performance_metrics(returns)

    last_price = float(data["price"].iloc[-1])

    report_content = f"""
--- Daily Report ({end_date}) for {TICKER} (CAC 40) ---
Closing price: {last_price:.2f}
Cumulative return ({DAYS_LOOKBACK}d): {metrics['cum_return']:.2%}
Annualized volatility: {metrics['ann_vol']:.2%}
Sharpe ratio: {metrics['sharpe']:.2f}
Maximum drawdown: {metrics['max_dd']:.2%}
Daily 95% VaR: {metrics['var_95']:.2%}

"""

    with open(REPORT_FILE, "a") as f:
        f.write(report_content)

    print(f"Report generated and saved to {REPORT_FILE}")


if __name__ == "__main__":
    generate_daily_report()
