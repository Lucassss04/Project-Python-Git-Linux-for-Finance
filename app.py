import datetime as dt

import numpy as np
import pandas as pd
import streamlit as st

from data import load_yahoo_data
from metrics import compute_performance_metrics
from strategies import moving_average_strategy

# ----------------- Config globale -----------------
st.set_page_config(
    page_title="Quant Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Petit CSS pour alléger le fond et élargir la sidebar
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
    "Prototype de plateforme pour analyse single asset et, plus tard, portefeuille."
)

# ----------------- Navigation -----------------
if "page" not in st.session_state:
    st.session_state.page = "Accueil"


def go_home():
    st.session_state.page = "Accueil"


def go_single_asset():
    st.session_state.page = "Module A : Single Asset"


def go_portfolio():
    st.session_state.page = "Module B (Portfolio)"


with st.sidebar:
    st.header("Navigation")
    st.button("Accueil", on_click=go_home, use_container_width=True)
    st.button("Module A (Single Asset)", on_click=go_single_asset, use_container_width=True)
    st.button("Module B (Portfolio)", on_click=go_portfolio, use_container_width=True)
    st.markdown("---")
    st.caption("Projet Python / Git / Linux – ESILV")

# ----------------- Contenu des pages -----------------
if st.session_state.page == "Accueil":
    st.subheader("Accueil")
    st.write(
        "Cette application a pour objectif de fournir un tableau de bord quantitatif "
        "pour analyser un actif unique (Module A) puis un portefeuille multi-actifs "
        "(Module B), avec indicateurs de performance et de risque."
    )

elif st.session_state.page == "Module A : Single Asset":
    st.subheader("Module A : Single Asset – Prototype")

    # Choix de l'actif
    tickers = {
        "TotalEnergies (TTE)": "TTE.PA",
        "Engie (ENGI)": "ENGI.PA",
        "CAC 40": "^FCHI",
        "EURUSD": "EURUSD=X",
        "Bitcoin": "BTC-USD",
    }
    col_left, col_right = st.columns([2, 1])
    with col_left:
        asset_label = st.selectbox("Choisir un actif :", list(tickers.keys()))
    with col_right:
        st.info("Plus tard : filtre par liste watchlist, secteur, etc.")

    ticker = tickers[asset_label]

    # Période
    default_end = dt.date.today()
    default_start = default_end - dt.timedelta(days=365)

    date_range = st.date_input(
        "Période d'analyse",
        value=(default_start, default_end),
        max_value=default_end,
    )

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start, end = date_range
    else:
        start = default_start
        end = date_range

    st.write(f"Ticker sélectionné : **{ticker}**")

    # Paramètres de stratégie (dans un expander pour le visuel)
    with st.expander("Paramètres de la stratégie moyenne mobile"):
        col_s, col_l = st.columns(2)
        with col_s:
            short_w = st.number_input(
                "MA courte (jours)", min_value=5, max_value=100, value=20
            )
        with col_l:
            long_w = st.number_input(
                "MA longue (jours)", min_value=10, max_value=250, value=50
            )

    if st.button("Charger / mettre à jour les données", type="primary"):
        with st.spinner("Téléchargement des données..."):
            data = load_yahoo_data(ticker, start, end)

        if data is None:
            st.error("Aucune donnée reçue pour cette période / cet actif.")
        else:
            st.success(f"Données chargées : {len(data)} observations.")

            strat_df = moving_average_strategy(
                data, short_window=short_w, long_window=long_w
            )

            # Layout : graphique en haut, métriques en dessous
            chart_tab, table_tab = st.tabs(["Graphiques", "Données brutes"])

            with chart_tab:
                st.subheader("Prix & Stratégies")

                chart_df = pd.DataFrame(index=strat_df.index)
                chart_df["Prix"] = strat_df["price"]
                chart_df["Buy & Hold"] = (1 + strat_df["return"]).cumprod()
                chart_df["Stratégie MA"] = (1 + strat_df["strategy_return"]).cumprod()
                st.line_chart(chart_df)

            with table_tab:
                st.subheader("Dernières observations")
                st.dataframe(strat_df[["price", "return", "strategy_return"]].tail())

            # Métriques
            st.subheader("Métriques de performance et de risque")

            metrics_bh = compute_performance_metrics(strat_df["return"])
            metrics_ma = compute_performance_metrics(strat_df["strategy_return"])

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### Buy & Hold")
                st.metric("Rendement cumulé", f"{metrics_bh['cum_return']:.2%}")
                st.metric("Vol annualisée", f"{metrics_bh['ann_vol']:.2%}")
                st.metric("Sharpe", f"{metrics_bh['sharpe']:.2f}")
                st.metric("Max drawdown", f"{metrics_bh['max_dd']:.2%}")
                st.metric("VaR 95% (quotidienne)", f"{metrics_bh['var_95']:.2%}")

            with col2:
                st.markdown("### Stratégie MA")
                st.metric("Rendement cumulé", f"{metrics_ma['cum_return']:.2%}")
                st.metric("Vol annualisée", f"{metrics_ma['ann_vol']:.2%}")
                st.metric("Sharpe", f"{metrics_ma['sharpe']:.2f}")
                st.metric("Max drawdown", f"{metrics_ma['max_dd']:.2%}")
                st.metric("VaR 95% (quotidienne)", f"{metrics_ma['var_95']:.2%}")

elif st.session_state.page == "Module B (Portfolio)":
    st.subheader("Module B : Portfolio")
    st.write(
        "À implémenter : sélection multi-actifs, pondérations, courbe de portefeuille, "
        "corrélations et métriques globales."
    )

