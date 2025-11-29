import datetime as dt
import yfinance as yf
import pandas as pd


def load_yahoo_data(ticker: str, start: dt.date, end: dt.date) -> pd.DataFrame | None:
    """Télécharge les prix quotidiens via yfinance et calcule les rendements simples."""
    data = yf.download(ticker, start=start, end=end)

    if data.empty:
        return None

    # Certaines séries (FX, indices) n'ont pas 'Adj Close'
    if "Adj Close" in data.columns:
        price_col = "Adj Close"
    else:
        price_col = "Close"

    data = data[[price_col]].rename(columns={price_col: "price"})
    data["return"] = data["price"].pct_change()
    data["equity_bh"] = (1 + data["return"]).cumprod()
    return data

