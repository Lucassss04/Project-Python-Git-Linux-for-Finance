import streamlit as st
from streamlit_autorefresh import st_autorefresh

from pages.single_asset import render_single_asset
from pages.portfolio import render_portfolio


# ----------------- Global config -----------------
st.set_page_config(
    page_title="Quant Portfolio Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

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


# ----------------- Navigation state -----------------
if "page" not in st.session_state:
    st.session_state.page = "Home"


def go_home():
    st.session_state.page = "Home"


def go_single_asset():
    st.session_state.page = "Single Asset"


def go_portfolio():
    st.session_state.page = "Portfolio"


# ----------------- Sidebar + refresh -----------------
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
    
    "Engie (ENGI)": "ENGI.PA",
    "CAC 40": "^FCHI",
    "EURUSD": "EURUSD=X",
    "Bitcoin": "BTC-USD",
    "Ethereum": "ETH-USD",
    "Solana": "SOL-USD",
    "WTI Crude Oil": "CL=F",
    "Natural Gas": "NG=F",
}

UNIVERSE_BY_CATEGORY = {
    "Equities / Indices": {
        "Engie (ENGI)": "ENGI.PA",
        "CAC 40": "^FCHI",
    },
    "Forex": {"EURUSD": "EURUSD=X"},
    "Crypto": {
        "Bitcoin": "BTC-USD",
        "Ethereum": "ETH-USD",
        "Solana": "SOL-USD",
    },
    "Commodities": {
        "WTI Crude Oil": "CL=F",
        "Natural Gas": "NG=F",
    },
    "Mixed (all types)": UNIVERSE,
}


# ----------------- Pages -----------------
if st.session_state.page == "Home":
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

    st.markdown("### What this dashboard offers")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(
            "- Single-asset analysis with live market data.\n"
            "- Buy & Hold, Moving Average and Momentum backtests.\n"
            "- Strategy parameter controls."
        )
    with col2:
        st.write(
            "- Multi-asset portfolios.\n"
            "- Equal-weight or custom weights.\n"
            "- Rebalancing and correlation matrix."
        )
    with col3:
        st.write(
            "- Risk metrics (vol, Sharpe, max DD, VaR).\n"
            "- Automated daily report script."
        )

elif st.session_state.page == "Single Asset":
    render_single_asset(UNIVERSE, auto_refresh)

elif st.session_state.page == "Portfolio":
    render_portfolio(UNIVERSE_BY_CATEGORY, auto_refresh)

#
