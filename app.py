import datetime as dt

import numpy as np
import pandas as pd
import streamlit as st

from data import load_yahoo_data
from metrics import compute_performance_metrics
from strategies import moving_average_strategy, momentum_strategy

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
    "Prototype de plateforme pour analyse single asset et portefeuille multi-actifs."
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

# ----------------- Univers d'actifs -----------------
UNIVERSE = {
    # Actions / indices
    "TotalEnergies (TTE)": "TTE.PA",     # TotalEnergies [finance:TotalEnergies SE]
    "Engie (ENGI)": "ENGI.PA",          # Engie [finance:Engie SA]
    "CAC 40": "^FCHI",                  # CAC 40 [finance:CAC 40]

    # Forex
    "EURUSD": "EURUSD=X",

    # Crypto
    "Bitcoin": "BTC-USD",               # Bitcoin [finance:Bitcoin]
    "Ethereum": "ETH-USD",              # Ethereum [finance:Ethereum]
    "Solana": "SOL-USD",                # Solana [finance:Solana]

    # Commodities (Yahoo Finance tickers)
    "Gold (XAUUSD)": "XAUUSD=X",
    "WTI Crude Oil": "CL=F",
    "Natural Gas": "NG=F",
}

UNIVERSE_BY_CATEGORY = {
    "Actions / Indices": {
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
    "Mix (tous types)": UNIVERSE,
}

# ----------------- Contenu des pages -----------------
if st.session_state.page == "Accueil":
    st.subheader("Accueil")

    # Bloc d'intro
    st.markdown(
        """
        Bienvenue sur le **Quant Dashboard**.  
        Cette application a été développée dans le cadre du projet *Python / Git / Linux for Finance* 
        pour fournir un environnement d'analyse quantitatif proche d'un outil professionnel.
        """,
        unsafe_allow_html=False,
    )

    st.markdown("---")

    # 3 colonnes de "cartes" de fonctionnalités
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🎯 Objectif")
        st.write(
            "- Centraliser l'analyse d'un actif ou d'un portefeuille.\n"
            "- Visualiser les performances dans le temps.\n"
            "- Suivre en direct l'impact de différentes stratégies."
        )

    with col2:
        st.markdown("### 🧱 Architecture")
        st.write(
            "- **Module A** : analyse single asset (prix, Buy & Hold, MA, momentum).\n"
            "- **Module B** : portefeuille multi‑actifs égal‑pondéré.\n"
            "- **Back‑end** : Python / yfinance / pandas / numpy."
        )

    with col3:
        st.markdown("### 📊 Indicateurs clés")
        st.write(
            "- Rendement cumulé et volatilité annualisée.\n"
            "- Sharpe ratio, max drawdown.\n"
            "- VaR historique 95 % sur rendements journaliers."
        )

    st.markdown("---")

    # Section "Comment utiliser le dashboard ?"
    st.markdown("### 🚀 Comment utiliser le dashboard ?")
    st.write(
        "1. **Module A (Single Asset)** – choisis un actif, une période, puis compare les stratégies "
        "Buy & Hold, moyenne mobile et momentum sur la même courbe.\n"
        "2. **Module B (Portfolio)** – sélectionne plusieurs actifs, construis un portefeuille "
        "égal‑pondéré et observe sa performance globale et sa matrice de corrélation.\n"
        "3. Ajuste les paramètres (fenêtres de moyennes mobiles, lookback momentum, période d'analyse) "
        "pour tester différents scénarios de marché."
    )

    # Section "Perspectives"
    st.markdown("### 🔧 Pistes d'amélioration")
    st.write(
        "Le projet pourra ensuite être enrichi avec :\n"
        "- optimisation des poids de portefeuille (min‑variance, max Sharpe),\n"
        "- ajout de nouvelles stratégies de trading,\n"
        "- déploiement sur un serveur Linux (PythonAnywhere) pour une disponibilité 24/7."
    )

elif st.session_state.page == "Module A : Single Asset":
    st.subheader("Module A : Single Asset – Buy & Hold vs MA vs Momentum")

    # Choix de l'actif (dans tout l'univers)
    col_left, col_right = st.columns([2, 1])
    with col_left:
        asset_label = st.selectbox("Choisir un actif :", list(UNIVERSE.keys()))
    with col_right:
        st.info("Plus tard : filtres par liste watchlist, secteur, etc.")

    ticker = UNIVERSE[asset_label]

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

    # Paramètres des stratégies
    with st.expander("Paramètres des stratégies"):
        col1, col2 = st.columns(2)
        with col1:
            short_w = st.number_input(
                "MA courte (jours)", min_value=5, max_value=100, value=20
            )
            long_w = st.number_input(
                "MA longue (jours)", min_value=10, max_value=250, value=50
            )
        with col2:
            lookback_mom = st.number_input(
                "Lookback momentum (jours)", min_value=10, max_value=252, value=60
            )

    if st.button("Charger / mettre à jour les données", type="primary"):
        with st.spinner("Téléchargement des données..."):
            data = load_yahoo_data(ticker, start, end)

        if data is None:
            st.error("Aucune donnée reçue pour cette période / cet actif.")
        else:
            st.success(f"Données chargées : {len(data)} observations.")

            # Stratégies
            ma_df = moving_average_strategy(
                data, short_window=short_w, long_window=long_w
            )
            mom_df = momentum_strategy(data, lookback=lookback_mom)

            # Graphiques
            chart_tab, table_tab = st.tabs(["Graphiques", "Données brutes"])

            with chart_tab:
                st.subheader("Prix & Stratégies")

                chart_df = pd.DataFrame(index=data.index)
                chart_df["Prix"] = data["price"]
                chart_df["Buy & Hold"] = (1 + data["return"]).cumprod()
                chart_df["Stratégie MA"] = (1 + ma_df["strategy_return"]).cumprod()
                chart_df["Stratégie Momentum"] = (1 + mom_df["strategy_return"]).cumprod()
                st.line_chart(chart_df)

            with table_tab:
                st.subheader("Dernières observations")

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

            # Métriques de performance / risque
            st.subheader("Métriques de performance et de risque")

            metrics_bh = compute_performance_metrics(data["return"])
            metrics_ma = compute_performance_metrics(ma_df["strategy_return"])
            metrics_mom = compute_performance_metrics(mom_df["strategy_return"])

            col_bh, col_ma, col_mom = st.columns(3)

            with col_bh:
                st.markdown("### Buy & Hold")
                st.metric("Rendement cumulé", f"{metrics_bh['cum_return']:.2%}")
                st.metric("Vol annualisée", f"{metrics_bh['ann_vol']:.2%}")
                st.metric("Sharpe", f"{metrics_bh['sharpe']:.2f}")
                st.metric("Max drawdown", f"{metrics_bh['max_dd']:.2%}")
                st.metric("VaR 95% (quotidienne)", f"{metrics_bh['var_95']:.2%}")

            with col_ma:
                st.markdown("### Stratégie MA")
                st.metric("Rendement cumulé", f"{metrics_ma['cum_return']:.2%}")
                st.metric("Vol annualisée", f"{metrics_ma['ann_vol']:.2%}")
                st.metric("Sharpe", f"{metrics_ma['sharpe']:.2f}")
                st.metric("Max drawdown", f"{metrics_ma['max_dd']:.2%}")
                st.metric("VaR 95% (quotidienne)", f"{metrics_ma['var_95']:.2%}")

            with col_mom:
                st.markdown("### Stratégie Momentum")
                st.metric("Rendement cumulé", f"{metrics_mom['cum_return']:.2%}")
                st.metric("Vol annualisée", f"{metrics_mom['ann_vol']:.2%}")
                st.metric("Sharpe", f"{metrics_mom['sharpe']:.2f}")
                st.metric("Max drawdown", f"{metrics_mom['max_dd']:.2%}")
                st.metric("VaR 95% (quotidienne)", f"{metrics_mom['var_95']:.2%}")

elif st.session_state.page == "Module B (Portfolio)":
    st.subheader("Module B : Portfolio – Prototype égal-pondéré")

    # --- 1) Choix d'une ou plusieurs catégories ---
    all_categories = list(UNIVERSE_BY_CATEGORY.keys())

    col_cat, col_help = st.columns([2, 1])
    with col_cat:
        selected_categories = st.multiselect(
            "Catégories d'actifs :",
            all_categories,
            default=all_categories,  # par défaut : tout l'univers
        )
    with col_help:
        st.caption(
            "Tu peux combiner plusieurs catégories (ex : Crypto + Commodities) "
            "puis choisir les actifs dans l'union des catégories."
        )

    if not selected_categories:
        st.warning("Sélectionne au moins une catégorie d'actifs.")
    else:
        # --- 2) Univers filtré = union des catégories choisies ---
        current_universe = {}
        for cat in selected_categories:
            current_universe.update(UNIVERSE_BY_CATEGORY[cat])

        # --- 3) Sélection multi-actifs dans cet univers combiné ---
        default_selection = list(current_universe.keys())[:3]
        selected_labels = st.multiselect(
            "Sélectionner les actifs du portefeuille :",
            list(current_universe.keys()),
            default=default_selection,
        )

        if len(selected_labels) < 2:
            st.warning("Sélectionne au moins deux actifs pour construire un portefeuille.")
        else:
            default_end = dt.date.today()
            default_start = default_end - dt.timedelta(days=365)

            date_range = st.date_input(
                "Période d'analyse (portefeuille)",
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
                with st.spinner(f"Téléchargement {label} ({tkr})..."):
                    df = load_yahoo_data(tkr, start, end)
                if df is None:
                    st.error(f"Aucune donnée pour {label}.")
                    continue
                returns_dict[label] = df["return"]
                prices_dict[label] = df["price"]

            if len(returns_dict) < 2:
                st.error("Pas assez de séries valides pour construire le portefeuille.")
            else:
                returns = pd.concat(returns_dict, axis=1).dropna()
                prices = pd.concat(prices_dict, axis=1).reindex(returns.index)

                n = returns.shape[1]
                weights = np.array([1.0 / n] * n)
                weight_series = pd.Series(weights, index=returns.columns)

                st.markdown("### Poids du portefeuille (égal-pondéré)")
                st.dataframe(weight_series.rename("Poids"))

                portfolio_returns = (returns * weights).sum(axis=1)
                portfolio_equity = (1 + portfolio_returns).cumprod()

                st.subheader("Courbes d'equity – actifs vs portefeuille")

                chart_df = pd.DataFrame(index=returns.index)
                for col in returns.columns:
                    chart_df[col] = (1 + returns[col]).cumprod()
                chart_df["Portefeuille"] = portfolio_equity
                st.line_chart(chart_df)

                st.subheader("Matrice de corrélation des rendements")
                corr = returns.corr()
                st.dataframe(
                    corr.style.background_gradient(cmap="RdBu_r", vmin=-1, vmax=1)
                )

                st.subheader("Métriques de performance et de risque – Portefeuille")
                port_metrics = compute_performance_metrics(portfolio_returns)

                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("Rendement cumulé", f"{port_metrics['cum_return']:.2%}")
                    st.metric("VaR 95% (quotidienne)", f"{port_metrics['var_95']:.2%}")
                with c2:
                    st.metric("Vol annualisée", f"{port_metrics['ann_vol']:.2%}")
                with c3:
                    st.metric("Sharpe", f"{port_metrics['sharpe']:.2f}")
                    st.metric("Max drawdown", f"{port_metrics['max_dd']:.2%}")
