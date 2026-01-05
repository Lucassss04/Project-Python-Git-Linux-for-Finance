import datetime as dt
import numpy as np
import pandas as pd
import streamlit as st

from data import load_yahoo_data
from metrics import compute_performance_metrics


def format_timestamp_utc(ts: dt.datetime | None) -> str:
    if ts is None:
        return "-"
    return ts.strftime("%Y-%m-%d %H:%M:%S")


def render_portfolio(universe_by_category: dict, auto_refresh: bool):
    st.subheader("Portfolio – Equal-weight / Custom")

    all_categories = list(universe_by_category.keys())

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
        return

    current_universe = {}
    for cat in selected_categories:
        current_universe.update(universe_by_category[cat])

    default_selection = list(current_universe.keys())[:3]
    selected_labels = st.multiselect(
        "Select portfolio assets:",
        list(current_universe.keys()),
        default=default_selection,
    )

    if len(selected_labels) < 2:
        st.warning("Select at least two assets to build a portfolio.")
        return

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

    do_refresh = st.button("Refresh portfolio data") or auto_refresh

    if not do_refresh:
        st.info("Click 'Refresh portfolio data' or enable auto-refresh to load data.")
        return

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
            st.warning(f"No valid data for {label}. It will be excluded from the portfolio.")
            continue

        returns_dict[label] = df["return"]
        prices_dict[label] = df["price"]

    if len(returns_dict) < 2:
        st.error("Not enough valid series to build the portfolio.")
        return

    returns = pd.concat(returns_dict, axis=1).dropna()
    asset_list = list(returns.columns)

    st.markdown("### Portfolio allocation")

    allocation_mode = st.radio(
        "Allocation mode:",
        ["Equal-weight", "Custom weights"],
        horizontal=True,
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
            st.warning("Total weight is 0. Falling back to equal-weight allocation.")
            weights = np.array([1.0 / len(asset_list)] * len(asset_list))
        else:
            weights = np.array(custom_weights) / total_w

    weights_series = pd.Series(weights, index=asset_list)
    st.dataframe(weights_series.rename("Weight"))

    rebalance_freq = st.selectbox(
        "Rebalancing frequency",
        options=["Daily", "Weekly", "Monthly"],
        index=0,
    )

    weights_df = pd.DataFrame(index=returns.index, columns=asset_list, dtype=float)

    if rebalance_freq == "Daily":
        for col in asset_list:
            weights_df[col] = weights_series[col]
    elif rebalance_freq == "Weekly":
        current_w = weights_series.copy()
        for date in returns.index:
            if date.weekday() == 0:
                current_w = weights_series.copy()
            weights_df.loc[date] = current_w
    else:
        current_month = None
        current_w = weights_series.copy()
        for date in returns.index:
            month_id = (date.year, date.month)
            if current_month != month_id:
                current_month = month_id
                current_w = weights_series.copy()
            weights_df.loc[date] = current_w

    portfolio_returns = (returns * weights_df).sum(axis=1)
    portfolio_equity = (1 + portfolio_returns).cumprod()

    st.session_state.last_update_portfolio = dt.datetime.utcnow()

    initial_nav = 100.0
    current_nav = float(initial_nav * portfolio_equity.iloc[-1])

    today_port_ret = portfolio_returns.loc[
        portfolio_returns.index.date == portfolio_returns.index[-1].date()
    ]
    day_ret_pct = float(today_port_ret.sum()) if not today_port_ret.empty else 0.0
    day_pnl_value = current_nav * day_ret_pct

    pk1, pk2, pk3 = st.columns(3)
    pk1.metric("Portfolio NAV", f"{current_nav:,.2f}", f"{day_pnl_value:,.2f}")
    pk2.metric("Portfolio cumulative return", f"{portfolio_equity.iloc[-1] - 1:.2%}")
    pk3.metric("Last update (UTC)", format_timestamp_utc(st.session_state.last_update_portfolio))

    st.subheader("Equity curves – assets vs portfolio")
    chart_df = pd.DataFrame(index=returns.index)
    for col in returns.columns:
        chart_df[col] = (1 + returns[col]).cumprod()
    chart_df["Portfolio"] = portfolio_equity
    st.line_chart(chart_df)

    st.subheader("Return correlation matrix")
    corr = returns.corr()
    st.dataframe(corr.style.background_gradient(cmap="RdBu_r", vmin=-1, vmax=1))

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

