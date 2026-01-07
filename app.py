import datetime as dt
from predictions import predict_future_prices
import numpy as np
import pandas as pd
import streamlit as st

from data import load_yahoo_data
from metrics import compute_performance_metrics
from strategies import moving_average_strategy, momentum_strategy

from streamlit_autorefresh import st_autorefresh


# ----------------- Global config -----------------
st.set_page_config(
    page_title="Quant Portfolio Dashboard",
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

st.title("Quant Portfolio Dashboard")

# ----------------- Navigation -----------------
if "page" not in st.session_state:
    st.session_state.page = "Home"


def go_home():
    st.session_state.page = "Home"


def go_single_asset():
    st.session_state.page = "Single Asset"


def go_portfolio():
    st.session_state.page = "Portfolio"


# ----------------- Navigation + Refresh -----------------
if "page" not in st.session_state:
    st.session_state.page = "Home"

def go_home():
    st.session_state.page = "Home"

def go_single_asset():
    st.session_state.page = "Single Asset"

def go_portfolio():
    st.session_state.page = "Portfolio"


auto_refresh = True
refresh_mins = 5

with st.sidebar:
    st.header("Navigation")
    st.button("Home", on_click=go_home, use_container_width=True)
    st.button("Single Asset", on_click=go_single_asset, use_container_width=True)
    st.button("Portfolio", on_click=go_portfolio, use_container_width=True)
    st.markdown("---")
    st.caption("Python / Git / Linux for Finance – ESILV")

    st.markdown("### Refresh")
    auto_refresh = st.toggle("Auto-refresh", value=True)
    refresh_mins = st.number_input(
        "Refresh interval (minutes)", min_value=1, max_value=60, value=5
    )

if auto_refresh:
    st_autorefresh(interval=int(refresh_mins * 60 * 1000), key="auto_refresh")


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


def format_timestamp_utc(ts: dt.datetime | None) -> str:
    if ts is None:
        return "-"
    return ts.strftime("%Y-%m-%d %H:%M:%S")


# ----------------- Pages content -----------------
# ========== HOME ==========
if st.session_state.page == "Home":
    # Hero section (no duplicate title)
    st.markdown(
        """
        <div style="padding: 0.5rem 0 1.5rem 0;">
            <p style="font-size: 0.95rem; color: #5c6370; margin-bottom: 0.5rem;">
                Single-asset and multi-asset analytics for portfolio managers and quantitative teams.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    hero_col1, hero_col2 = st.columns([2, 1])

    with hero_col1:
        st.markdown(
            """
            <p style="font-size: 0.95rem; color: #4b4f58;">
            This dashboard delivers a professional workflow for market data retrieval, backtesting
            and portfolio risk monitoring. Navigate between the Single Asset module and the
            Multi-Asset Portfolio module to explore trading strategies and portfolio construction.
            </p>
            """,
            unsafe_allow_html=True,
        )

        cta_col1, cta_col2 = st.columns(2)
        with cta_col1:
            if st.button("Open Single Asset module", use_container_width=True):
                go_single_asset()
        with cta_col2:
            if st.button("Open Portfolio module", use_container_width=True):
                go_portfolio()

    with hero_col2:
        st.info(
            "Project developed as part of the **Python / Git / Linux for Finance** course.\n\n"
            "**Authors:** Lucas STALTER and Christian YU\n"
            "**Program:** Master 1 – Ingénierie Financière, ESILV (Paris – La Défense)"
        )

    st.markdown("---")

    # Key value propositions
    st.markdown("### 🚀 What this dashboard offers")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### 🎯 Market & strategies")
        st.write(
            "- Single-asset analysis with live market data.\n"
            "- Buy & Hold, Moving Average and Momentum backtests.\n"
            "- Flexible parameters (lookback windows, analysis horizon)."
        )

    with col2:
        st.markdown("#### 📊 Portfolio analytics")
        st.write(
            "- Multi-asset equal-weight or custom-weight portfolios.\n"
            "- Rebalancing by frequency (daily, weekly, monthly).\n"
            "- Correlation matrix and diversified equity curves."
        )

    with col3:
        st.markdown("#### 🧮 Risk & reporting")
        st.write(
            "- Cumulative return, annualized volatility and Sharpe ratio.\n"
            "- Maximum drawdown and historical 95% Value-at-Risk.\n"
            "- Automated daily report script on benchmark index."
        )

    st.markdown("---")

    # Usage guide
    st.markdown("### 📌 How to use the platform")
    st.write(
        "1. **Single Asset module:** select an instrument, choose the analysis period and compare Buy & Hold, "
        "Moving Average and Momentum strategies on the same equity curve.\n"
        "2. **Portfolio module:** build a multi-asset portfolio, choose equal or custom weights and a "
        "rebalancing frequency, then analyse diversification and risk metrics.\n"
        "3. Adjust strategy parameters, export tables if needed and use the daily report for an end-of-day "
        "quantitative summary."
    )

# ========== SINGLE ASSET ==========
elif st.session_state.page == "Single Asset":
    st.subheader("Single Asset – Buy & Hold vs MA vs Momentum")

    # Asset selection
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

    do_refresh = st.button("Load / refresh data", type="primary") or auto_refresh

    if do_refresh:
        with st.spinner("Downloading data..."):
            try:
                data = load_yahoo_data(ticker, start, end)
            except Exception:
                data = None

        if data is None:
            st.error("No data received for this asset and period.")
        else:
            st.session_state.last_update_single = dt.datetime.utcnow()
            st.success(f"Data loaded: {len(data)} observations.")

            # === KPIs row – Single Asset ===
            last_price = float(data["price"].iloc[-1])
            today_returns = data["return"].loc[data.index.date == data.index[-1].date()]
            day_ret = float(today_returns.sum()) if not today_returns.empty else 0.0
            cum_bh = (1 + data["return"]).cumprod().iloc[-1] - 1

            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric(
                label="Last price",
                value=f"{last_price:,.2f}",
                delta=f"{day_ret:.2%}",
                help="Last available close and today's return.",
            )
            kpi2.metric(
                label="Cumulative return (Buy & Hold)",
                value=f"{cum_bh:.2%}",
                help="Total return of a passive Buy & Hold position over the selected period.",
            )
            kpi3.metric(
                label="Last update (UTC)",
                value=format_timestamp_utc(st.session_state.last_update_single),
                help="Time when data was last refreshed.",
            )

            # Strategies
            ma_df = moving_average_strategy(data, short_window=short_w, long_window=long_w)
            mom_df = momentum_strategy(data, lookback=lookback_mom)

            # Tabs: charts and data
            chart_tab, table_tab = st.tabs(["Charts", "Raw data"])

            with chart_tab:
                st.subheader("Price and strategies")
                chart_df = pd.DataFrame(index=data.index)
                chart_df["Price"] = data["price"]
                chart_df["Buy & Hold"] = (1 + data["return"]).cumprod()
                chart_df["MA Strategy"] = (1 + ma_df["strategy_return"]).cumprod()
                chart_df["Momentum Strategy"] = (1 + mom_df["strategy_return"]).cumprod()
                st.line_chart(chart_df)
                st.markdown("---")
            st.subheader(" Prediction")
            
            show_pred = st.checkbox("Show Price Prediction (Linear Regression)", value=False)
            
            if show_pred:
                days_pred = st.slider("Forecast Horizon (days)", 10, 90, 30)
                
                pred_df, trend_slope = predict_future_prices(data, days_ahead=days_pred)
                
                trend_str = "Positive" if trend_slope > 0 else "Negative"
                st.info(f"Model Trend: **{trend_str}** (Slope: {trend_slope:.4f})")
                
                future_chart = pd.DataFrame({
                    "Predicted Price": pred_df["Predicted Price"]
                })
                st.line_chart(future_chart)
                
                with st.expander("See Prediction Data"):
                    st.dataframe(pred_df)

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


# ========== PORTFOLIO ==========
elif st.session_state.page == "Portfolio":
    st.subheader("Portfolio – Equal-weight / Custom")

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
                    try:
                        df = load_yahoo_data(tkr, start, end)
                    except Exception:
                        df = None

                if df is None or df.empty:
                    st.warning(
                        f"No valid data for {label}. It will be excluded from the portfolio."
                    )
                    continue

                returns_dict[label] = df["return"]
                prices_dict[label] = df["price"]

            if len(returns_dict) < 2:
                st.error("Not enough valid series to build the portfolio.")
            else:
                returns = pd.concat(returns_dict, axis=1).dropna()
                prices = pd.concat(prices_dict, axis=1).reindex(returns.index)

                asset_list = list(returns.columns)

                # ---------- Allocation block ----------
                st.markdown("### Portfolio allocation")

                allocation_mode = st.radio(
                    "Allocation mode:",
                    ["Equal-weight", "Custom weights"],
                    horizontal=True,
                    help="Choose between equal weights or custom user-defined weights.",
                )

                if allocation_mode == "Equal-weight":
                    n = returns.shape[1]
                    weights = np.array([1.0 / n] * n)
                else:
                    st.write("Set custom weights (they must sum to 100%).")
                    custom_weights = []
                    for asset in asset_list:
                        w = st.slider(
                            f"Weight for {asset}",
                            min_value=0.0,
                            max_value=100.0,
                            value=float(100.0 / len(asset_list)),
                            step=1.0,
                        )
                        custom_weights.append(w)

                    total_w = sum(custom_weights)
                    if total_w == 0:
                        st.warning(
                            "Total weight is 0. Falling back to equal-weight allocation."
                        )
                        n = len(asset_list)
                        weights = np.array([1.0 / n] * n)
                    else:
                        weights = np.array(custom_weights) / total_w

                weights_series = pd.Series(weights, index=asset_list)
                st.dataframe(weights_series.rename("Weight"))

                # ---------- Rebalancing frequency ----------
                rebalance_freq = st.selectbox(
                    "Rebalancing frequency",
                    options=["Daily", "Weekly", "Monthly"],
                    index=0,
                    help="How often portfolio weights are reset to target weights.",
                )

                weights_df = pd.DataFrame(
                    index=returns.index, columns=asset_list, dtype=float
                )

                if rebalance_freq == "Daily":
                    for col in asset_list:
                        weights_df[col] = weights_series[col]
                elif rebalance_freq == "Weekly":
                    # Rebalance every Monday
                    current_w = weights_series.copy()
                    for date in returns.index:
                        if date.weekday() == 0:  # Monday
                            current_w = weights_series.copy()
                        weights_df.loc[date] = current_w
                else:  # Monthly
                    current_month = None
                    current_w = weights_series.copy()
                    for date in returns.index:
                        month_id = (date.year, date.month)
                        if current_month != month_id:
                            current_month = month_id
                            current_w = weights_series.copy()
                        weights_df.loc[date] = current_w

                weights_df = weights_df.astype(float)

                portfolio_returns = (returns * weights_df).sum(axis=1)
                portfolio_equity = (1 + portfolio_returns).cumprod()

                # ---------- KPIs row – Portfolio ----------
                st.session_state.last_update_portfolio = dt.datetime.utcnow()

                initial_nav = 100.0
                current_nav = float(initial_nav * portfolio_equity.iloc[-1])

                today_port_ret = portfolio_returns.loc[
                    portfolio_returns.index.date
                    == portfolio_returns.index[-1].date()
                ]
                day_ret_pct = (
                    float(today_port_ret.sum()) if not today_port_ret.empty else 0.0
                )
                day_pnl_value = current_nav * day_ret_pct

                pk1, pk2, pk3 = st.columns(3)
                pk1.metric(
                    label="Portfolio NAV",
                    value=f"{current_nav:,.2f}",
                    delta=f"{day_pnl_value:,.2f}",
                    help="Reference NAV starts at 100; delta is today's PnL.",
                )
                pk2.metric(
                    label="Portfolio cumulative return",
                    value=f"{portfolio_equity.iloc[-1] - 1:.2%}",
                    help="Total return of the portfolio since the start of the period.",
                )
                pk3.metric(
                    label="Last update (UTC)",
                    value=format_timestamp_utc(st.session_state.last_update_portfolio),
                    help="Time when portfolio data was last refreshed.",
                )

                # ---------- Charts ----------
                st.subheader("Equity curves – assets vs portfolio")

                chart_df = pd.DataFrame(index=returns.index)
                for col in returns.columns:
                    chart_df[col] = (1 + returns[col]).cumprod()
                chart_df["Portfolio"] = portfolio_equity
                st.line_chart(chart_df)

                # ---------- Correlation ----------
                st.subheader("Return correlation matrix")
                corr = returns.corr()
                st.dataframe(
                    corr.style.background_gradient(cmap="RdBu_r", vmin=-1, vmax=1)
                )

                # ---------- Metrics ----------
                st.subheader("Performance and risk metrics – Portfolio")
                port_metrics = compute_performance_metrics(portfolio_returns)

                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("Cumulative return", f"{port_metrics['cum_return']:.2%}")
                    st.metric(
                        "Daily 95% VaR",
                        f"{port_metrics['var_95']:.2%}",
                        help="Historical 95% Value-at-Risk on daily portfolio returns.",
                    )
                with c2:
                    st.metric(
                        "Annualized volatility",
                        f"{port_metrics['ann_vol']:.2%}",
                        help="Annualized standard deviation of portfolio daily returns.",
                    )
                with c3:
                    st.metric(
                        "Sharpe ratio",
                        f"{port_metrics['sharpe']:.2f}",
                        help="Excess portfolio return per unit of volatility.",
                    )
                    st.metric(
                        "Maximum drawdown",
                        f"{port_metrics['max_dd']:.2%}",
                        help="Largest peak-to-trough loss of the portfolio over the period.",
                    )
