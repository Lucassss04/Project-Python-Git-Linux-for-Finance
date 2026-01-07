# Project: Python, Git, Linux for Finance

**Live app:** https://quant-portfolio.streamlit.app/

Interactive dashboard for **single-asset strategy backtesting** and **multi-asset portfolio analytics**, built for the *Python / Git / Linux for Finance* course project (ESILV).

**Authors:** Lucas Stalter (Quant A — Single Asset) & Christian Yu (Quant B — Portfolio).

---

## Project goals

This project aims to deliver a professional workflow that:
- Retrieves financial data from a dynamic source and updates frequently.
- Displays the current value of chosen assets and key analytics in an interactive dashboard.
- Implements quantitative strategies and portfolio simulations.
- Auto-refreshes the dashboard every ~5 minutes.
- Produces an end-of-day report generated at a fixed time (8pm) via cron, stored locally on the VM.
- Uses a clean GitHub workflow (separate branches per module + pull requests + conflict resolution).

---

## Features

### Quant A — Single Asset (Univariate module)
Focus: one asset at a time (e.g., ENGI, EUR/USD, gold).

- Strategy backtests:
  - Buy & Hold
  - Moving Average crossover
  - Momentum
- Interactive controls:
  - Analysis period (date range)
  - Strategy parameters (MA windows, momentum lookback)
- Outputs:
  - Equity curves (price + cumulative strategy performance)
  - Performance & risk metrics (e.g., Sharpe ratio, max drawdown, historical 95% VaR)

### Quant B — Portfolio (Multivariate module)
Focus: multi-asset portfolio analytics (at least 3 assets).

- Portfolio construction:
  - Select assets by category (equities/indices, FX, crypto, commodities)
  - Equal-weight or custom weights
  - Rebalancing frequency: daily / weekly / monthly
- Outputs:
  - Equity curves (assets vs portfolio)
  - Correlation matrix
  - Portfolio performance & risk metrics (volatility, Sharpe, max drawdown, VaR)

---

## Data source

Market prices are retrieved from Yahoo Finance via the `yfinance` Python package (through `data.py`).
Data is converted into:
- `price` series
- `return` series (daily returns)

---

## Repository structure

```text
.
├── app.py                      # Main Streamlit entrypoint (navigation + refresh + universe)
├── pages/
│   ├── single_asset.py         # Quant A module UI + logic
│   └── portfolio.py            # Quant B module UI + logic
├── data.py                     # Data loading utilities (Yahoo Finance)
├── strategies.py               # Strategy implementations (MA, momentum, etc.)
├── metrics.py                  # Risk/performance metrics (Sharpe, max DD, VaR, etc.)
├── daily_report.py             # Daily report generator script
├── daily_report_log.txt        # Example output log (generated locally)
├── requirements.txt            # Python dependencies
└── README.md

```

## Linux VM deployment (GCP)

This project is also deployed on a hosted Linux VM (Google Compute Engine) to satisfy the course requirement to run the app on a Linux server and keep it accessible during the evaluation week.

### Install & run
```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git cron

git clone https://github.com/Lucassss04/Project-Python-Git-Linux-for-Finance.git
cd Project-Python-Git-Linux-for-Finance

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run Streamlit on the VM (persistent)
nohup .venv/bin/streamlit run app.py --server.address 0.0.0.0 --server.port 8501 > streamlit.log 2>&1 &


