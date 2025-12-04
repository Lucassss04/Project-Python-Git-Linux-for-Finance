import datetime as dt

import numpy as np
import pandas as pd
import streamlit as st

from data import load_yahoo_data
from metrics import compute_performance_metrics
from strategies import moving_average_strategy, momentum_strategy

# ----------------- Global config -----------------
st.set_page_config(
    page_title="Quant Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Simple CSS to lighten background and widen sidebar
st.markdown(
    """
    <style>
    .stApp {background-color: #f5f7fb;}
    [data-testid="stSidebar"] > div:first-child {padding-top: 1.5rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Quant Dashboard")
st.caption(
    "Prototype platform for single-asset analysis and multi-asset portfolio analysis."
)

# ----------------- Navigation -----------------
if "page" not in st.session_state:
    st.session_state.page = "Home"


def go_home():
    st.session_state.page = "Home"


def go_single_asset():
    st.session_state.page = "Module A: Single Asset"


def go_portfolio():
    st.session_state.page = "Module B: Portfolio"


with st.sidebar:
    st.header("Navigation")
    st.button("Home", on_click=go_home, use_container_width=True)
    st.button("Module A (Single Asset)", on_click=go_single_asset, use_container_width=True)
    st.button("Module B (Portfolio)", on_click=go_portfolio, use_container_width=True)
    st.markdown("---")
    st.caption("Python / Git / Linux for Finance – ESILV")

# ----------------- Asset universe -----------------
UNIVERSE = {
    # Equities / indices
    "TotalEnergies (TTE)": "TTE.PA",
    "Engie (ENGI)": "ENGI.PA",
    "CAC 40": "^FCHI",

    # Forex
    "EURUSD": "EURUSD=X",

    # Crypto
    "Bitcoin": "BTC-USD",
    "Ethereum": "ETH-USD",
    "Solana": "SOL-USD",

    # Commodities (Yahoo Finance tickers)
    "Gold (XAUUSD)": "XAUUSD=X",
    "WTI Crude Oil": "CL=F",
    "Natural Gas": "NG=F",
}

UNIVERSE_BY_CATEGORY = {
    "Equities / Indices": {
        "TotalEnergies (TTE)": "TTE.PA",
        "Engie (ENGI)": "ENGI.PA",
        "CAC 40": "^FCHI",
    },
    "Forex": {
        "EURUSD": "EURUSD=X",
    },
    "Crypto": {
        "Bitcoin": "BTC-USD",
        "Ethereum": "ETH-USD",
        "Solana": "SOL-USD",
    },
    "Commodities": {
        "Gold (XAUUSD)": "XAUUSD=X",
        "WTI Crude Oil": "CL=F",
        "Natural Gas": "NG=F",
    },
    "Mixed (all types)": UNIVERSE,
}

# ----------------- Pages content -----------------
# ========== HOME ==========
if st.session_state.page == "Home":
    st.subheader("Home")

    # Intro block
    st.markdown(
        """
        Welcome to the **Quant Dashboard**.  
        This application was developed as part of the *Python / Git / Linux for Finance* project
        to provide a quantitative analysis environment close to a professional tool.
        """,
        unsafe_allow_html=False,
    )

    st.markdown("---")

    # 3 columns of feature "cards"
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🎯 Objective")
        st.write(
            "- Centralize the analysis of a single asset or a portfolio.\n"
            "- Visualize performance over time.\n"
            "- Monitor the impact of different strategies in real time."
        )

    with col2:
        st.markdown("### 🧱 Architecture")
        st.write(
            "- **Module A**: single-asset analysis (price, Buy & Hold, MA, momentum).\n"
            "- **Module B**: equal-weight multi-asset portfolio.\n"
            "- **Back-end**: Python / yfinance / pandas / numpy."
        )

    with col3:
        st.markdown("### 📊 Key indicators")
        st.write(
            "- Cumulative return and annualized volatility.\n"
            "- Sharpe ratio, maximum drawdown.\n"
            "- Historical 95% VaR on daily returns."
        )

    st.markdown("---")

    # "How to use" section
    st.markdown("### 🚀 How to use the dashboard")
    st.write(
        "1. **Module A (Single Asset)** – choose an asset and a period, then compare "
        "Buy & Hold, moving-average, and momentum strategies on the same chart.\n"
        "2. **Module B (Portfolio)** – select several assets, build an equal-weight "
        "portfolio, and observe its global performance and correlation matrix.\n"
        "3. Adjust parameters (moving-average windows, momentum lookback, analysis period) "
        "to test different market scenarios."
    )

    # "Future work" section
    st.markdown("### 🔧 Future improvements")
    st.write(
        "The project can later be extended with:\n"
        "- portfolio weight optimization (min-variance, max Sharpe),\n"
        "- additional trading strategies,\n"
        "- deployment on a Linux server (PythonAnywhere) for 24/7 availability."
    )

# ========== MODULE A: SINGLE ASSET ==========
elif st.session_state.page == "Module A: Single Asset":
    st.subheader("Module A: Single Asset – Buy & Hold vs MA vs Momentum")

    # Asset selection (whole universe)
    col_left, col_right = st.columns([2, 1])
    with col_left:
        asset_label = st.selectbox("Choose an asset:", list(UNIVERSE.keys()))
    with col_right:
        st.info("Later: watchlists, sector filters, etc.")

    ticker = UNIVERSE[asset_label]

    # Date range
    default_end = dt.date.today()
    default_start = default_end - dt.timedelta(days=365)

    date_range = st.date_input(
        "Analysis period",
        value=(default_start, default_end),
        max_value=default_end,
    )

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start, end = date_range
    else:
        start = default_start
        end = date_range

    st.write(f"Selected ticker: **{ticker}**")

    # Strategy parameters
    with st.expander("Strategy parameters"):
        col1, col2 = st.columns(2)
        with col1:
            short_w = st.number_input(
                "Short MA window (days)", min_value=5, max_value=100, value=20
            )
            long_w = st.number_input(
                "Long MA window (days)", min_value=10, max_value=250, value=50
            )
        with col2:
            lookback_mom = st.number_input(
                "Momentum lookback (days)", min_value=10, max_value=252, value=60
            )

    data = None  # ensure variable exists outside the button scope

    if st.button("Load / refresh data", type="primary"):
        with st.spinner("Downloading data..."):
            data = load_yahoo_data(ticker, start, end)

        if data is None:
            st.error("No data received for this asset and period.")
        else:
            st.session_state.last_update_single = dt.datetime.utcnow()

            st.success(f"Data loaded: {len(data)} observations.")

            # === Current value block – Single Asset ===
            last_price = float(data["price"].iloc[-1])
            today_returns = data["return"].loc[
                data.index.date == data.index[-1].date()
            ]
            day_ret = float(today_returns.sum()) if not today_returns.empty else 0.0
            cum_bh = (1 + data["return"]).cumprod().iloc[-1] - 1

            col_cv1, col_cv2, col_cv3 = st.columns(3)
            col_cv1.metric(
                label="Last price",
                value=f"{last_price:,.2f}",
                delta=f"{day_ret:.2%}",
                help="Last close and today's return.",
            )
            col_cv2.metric(
                label="Cumulative return (Buy & Hold)",
                value=f"{cum_bh:.2%}",
            )
            col_cv3.metric(
                label="Last update (UTC)",
                value=st.session_state.last_update_single.strftime("%Y-%m-%d %H:%M:%S"),
            )

            # Strategies
            ma_df = moving_average_strategy(
                data, short_window=short_w, long_window=long_w
            )
            mom_df = momentum_strategy(data, lookback=lookback_mom)

            # Charts
            chart_tab, table_tab = st.tabs(["Charts", "Raw data"])

            with chart_tab:
                st.subheader("Price and strategies")

                chart_df = pd.DataFrame(index=data.index)
                chart_df["Price"] = data["price"]
                chart_df["Buy & Hold"] = (1 + data["return"]).cumprod()
                chart_df["MA Strategy"] = (1 + ma_df["strategy_return"]).cumprod()
                chart_df["Momentum Strategy"] = (1 + mom_df["strategy_return"]).cumprod()
                st.line_chart(chart_df)

            with table_tab:
                st.subheader("Last observations")

                tail_df = pd.DataFrame(
                    {
                        "price": np.ravel(data["price"].to_numpy()),
                        "ret_bh": np.ravel(data["return"].to_numpy()),
                        "ret_ma": np.ravel(ma_df["strategy_return"].to_numpy()),
                        "ret_mom": np.ravel(mom_df["strategy_return"].to_numpy()),
                    },
                    index=data.index,
                )

                st.dataframe(tail_df.tail())

            # Performance / risk metrics
            st.subheader("Performance and risk metrics")

            metrics_bh = compute_performance_metrics(data["return"])
            metrics_ma = compute_performance_metrics(ma_df["strategy_return"])
            metrics_mom = compute_performance_metrics(mom_df["strategy_return"])

            col_bh, col_ma, col_mom = st.columns(3)

            with col_bh:
                st.markdown("### Buy & Hold")
                st.metric("Cumulative return", f"{metrics_bh['cum_return']:.2%}")
                st.metric("Annualized volatility", f"{metrics_bh['ann_vol']:.2%}")
                st.metric("Sharpe ratio", f"{metrics_bh['sharpe']:.2f}")
                st.metric("Maximum drawdown", f"{metrics_bh['max_dd']:.2%}")
                st.metric("Daily 95% VaR", f"{metrics_bh['var_95']:.2%}")

            with col_ma:
                st.markdown("### Moving Average Strategy")
                st.metric("Cumulative return", f"{metrics_ma['cum_return']:.2%}")
                st.metric("Annualized volatility", f"{metrics_ma['ann_vol']:.2%}")
                st.metric("Sharpe ratio", f"{metrics_ma['sharpe']:.2f}")
                st.metric("Maximum drawdown", f"{metrics_ma['max_dd']:.2%}")
                st.metric("Daily 95% VaR", f"{metrics_ma['var_95']:.2%}")

            with col_mom:
                st.markdown("### Momentum Strategy")
                st.metric("Cumulative return", f"{metrics_mom['cum_return']:.2%}")
                st.metric("Annualized volatility", f"{metrics_mom['ann_vol']:.2%}")
                st.metric("Sharpe ratio", f"{metrics_mom['sharpe']:.2f}")
                st.metric("Maximum drawdown", f"{metrics_mom['max_dd']:.2%}")
                st.metric("Daily 95% VaR", f"{metrics_mom['var_95']:.2%}")

# ========== MODULE B: PORTFOLIO ==========
elif st.session_state.page == "Module B: Portfolio":
    st.subheader("Module B: Portfolio – Equal-weight prototype")

    # --- 1) Choose one or several categories ---
    all_categories = list(UNIVERSE_BY_CATEGORY.keys())

    col_cat, col_help = st.columns([2, 1])
    with col_cat:
        selected_categories = st.multiselect(
            "Asset categories:",
            all_categories,
            default=all_categories,
        )
    with col_help:
        st.caption(
            "You can combine several categories (e.g. Crypto + Commodities) "
            "and then choose assets from the union of these categories."
        )

    if not selected_categories:
        st.warning("Select at least one asset category.")
    else:
        # --- 2) Filtered universe = union of selected categories ---
        current_universe = {}
        for cat in selected_categories:
            current_universe.update(UNIVERSE_BY_CATEGORY[cat])

        # --- 3) Multi-asset selection in this combined universe ---
        default_selection = list(current_universe.keys())[:3]
        selected_labels = st.multiselect(
            "Select portfolio assets:",
            list(current_universe.keys()),
            default=default_selection,
        )

        if len(selected_labels) < 2:
            st.warning("Select at least two assets to build a portfolio.")
        else:
            default_end = dt.date.today()
            default_start = default_end - dt.timedelta(days=365)

            date_range = st.date_input(
                "Portfolio analysis period",
                value=(default_start, default_end),
                max_value=default_end,
                key="portfolio_dates",
            )

            if isinstance(date_range, tuple) and len(date_range) == 2:
                start, end = date_range
            else:
                start = default_start
                end = date_range

            returns_dict = {}
            prices_dict = {}
            for label in selected_labels:
                tkr = current_universe[label]
                with st.spinner(f"Downloading {label} ({tkr})..."):
                    df = load_yahoo_data(tkr, start, end)
                if df is None:
                    st.error(f"No data for {label}.")
                    continue
                returns_dict[label] = df["return"]
                prices_dict[label] = df["price"]

            if len(returns_dict) < 2:
                st.error("Not enough valid series to build the portfolio.")
            else:
                returns = pd.concat(returns_dict, axis=1).dropna()
                prices = pd.concat(prices_dict, axis=1).reindex(returns.index)

                n = returns.shape[1]
                weights = np.array([1.0 / n] * n)
                weight_series = pd.Series(weights, index=returns.columns)

                st.markdown("### Portfolio weights (equal-weight)")
                st.dataframe(weight_series.rename("Weight"))

                portfolio_returns = (returns * weights).sum(axis=1)
                portfolio_equity = (1 + portfolio_returns).cumprod()

                # === Current value block – Portfolio ===
                st.session_state.last_update_portfolio = dt.datetime.utcnow()

                initial_nav = 100.0
                current_nav = float(initial_nav * portfolio_equity.iloc[-1])

                today_port_ret = portfolio_returns.loc[
                    portfolio_returns.index.date
                    == portfolio_returns.index[-1].date()
                ]
                day_ret_pct = float(today_port_ret.sum()) if not today_port_ret.empty else 0.0
                day_pnl_value = current_nav * day_ret_pct

                col_p1, col_p2, col_p3 = st.columns(3)
                col_p1.metric(
                    label="Portfolio NAV",
                    value=f"{current_nav:,.2f}",
                    delta=f"{day_pnl_value:,.2f}",
                    help="Reference NAV starts at 100; delta is today's PnL.",
                )
                col_p2.metric(
                    label="Portfolio cumulative return",
                    value=f"{portfolio_equity.iloc[-1] - 1:.2%}",
                )
                col_p3.metric(
                    label="Last update (UTC)",
                    value=st.session_state.last_update_portfolio.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                )

                st.subheader("Equity curves – assets vs portfolio")

                chart_df = pd.DataFrame(index=returns.index)
                for col in returns.columns:
                    chart_df[col] = (1 + returns[col]).cumprod()
                chart_df["Portfolio"] = portfolio_equity
                st.line_chart(chart_df)

                st.subheader("Return correlation matrix")
                corr = returns.corr()
                st.dataframe(
                    corr.style.background_gradient(cmap="RdBu_r", vmin=-1, vmax=1)
                )

                st.subheader("Performance and risk metrics – Portfolio")
                port_metrics = compute_performance_metrics(portfolio_returns)

                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("Cumulative return", f"{port_metrics['cum_return']:.2%}")
                    st.metric("Daily 95% VaR", f"{port_metrics['var_95']:.2%}")
                with c2:
                    st.metric("Annualized volatility", f"{port_metrics['ann_vol']:.2%}")
                with c3:
                    st.metric("Sharpe ratio", f"{port_metrics['sharpe']:.2f}")
                    st.metric("Maximum drawdown", f"{port_metrics['max_dd']:.2%}")
