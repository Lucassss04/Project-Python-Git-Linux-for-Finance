import datetime as dt
import numpy as np
import pandas as pd
import streamlit as st

from data import load_yahoo_data
from metrics import compute_performance_metrics
from strategies import moving_average_strategy, momentum_strategy


def format_timestamp_utc(ts: dt.datetime | None) -> str:
    if ts is None:
        return "-"
    return ts.strftime("%Y-%m-%d %H:%M:%S")


def render_single_asset(universe: dict, auto_refresh: bool):
    st.subheader("Single Asset – Buy & Hold vs MA vs Momentum")

    # Asset selection
    col_left, col_right = st.columns([2, 1])
    with col_left:
        asset_label = st.selectbox("Choose an asset:", list(universe.keys()))
    with col_right:
        st.info("Later: watchlists, sector filters, etc.")

    ticker = universe[asset_label]

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
        short_w = st.number_input(...)
        long_w = st.number_input(...)
    with col2:
        lookback_mom = st.number_input(...)


    if short_w >= long_w:
        st.warning("Short MA window must be strictly smaller than Long MA window.")
        st.stop()


    do_refresh = st.button("Load / refresh data", type="primary") or auto_refresh


    if not do_refresh:
        st.info("Click 'Load / refresh data' or enable auto-refresh to load data.")
        return

    with st.spinner("Downloading data..."):
        try:
            data = load_yahoo_data(ticker, start, end)
        except Exception:
            data = None

    if data is None:
        st.error("No data received for this asset and period.")
        return

    st.session_state.last_update_single = dt.datetime.utcnow()
    st.success(f"Data loaded: {len(data)} observations.")

    # KPIs
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

    # Tabs
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

    # Metrics
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

