import datetime as dt

import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf


@st.cache_data(show_spinner=False, ttl=300)
def load_yahoo_data(ticker: str, start, end):
    """
    Download daily data from Yahoo Finance and return a DataFrame
    with columns: price, return.
    """
    try:
        df = yf.download(
            ticker,
            start=start,
            end=end,
            auto_adjust=True,
            progress=False,
        )
    except Exception:
        return None

    if df is None or df.empty:
        return None

    df = df[["Close"]].rename(columns={"Close": "price"})
    df["return"] = df["price"].pct_change()
    df = df.dropna()

    return df
#