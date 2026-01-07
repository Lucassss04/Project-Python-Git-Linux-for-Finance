# 📈 Quantitative Portfolio Management Dashboard

**Course:** Python / Git / Linux for Finance (ESILV)
**Authors:** Lucas Stalter (Quant A) & Christian Yu (Quant B)
**Live App:** https://quant-portfolio.streamlit.app/

---

## 📖 Executive Summary

This project is a production-ready quantitative research platform built to bridge the gap between raw market data and actionable investment insights. Deployed on a **Linux (GCP)** infrastructure, the application simulates a professional asset management workflow, featuring a **Univariate Backtesting Engine** and a **Multivariate Portfolio Optimizer**.

The dashboard allows Portfolio Managers to:
1.  **Backtest Active Strategies:** Compare Moving Average and Momentum strategies against a Buy & Hold benchmark.
2.  **Construct Multi-Asset Portfolios:** Simulate diversification effects across Equities, Forex, Crypto, and Commodities.
3.  **Monitor Risk Real-Time:** Track Value at Risk (VaR), Volatility, and Drawdowns dynamically.
4.  **Automate Reporting:** Receive daily index performance logs generated via automated server-side scripts (Cron).

---

## 👥 Division of Responsibilities

This project adheres to a strict separation of concerns to simulate a collaborative Git workflow:

| Module | Developer | Responsibilities |
| :--- | :--- | :--- |
| **Quant A**<br>(Single Asset) | **Lucas Stalter** | **Backtesting Engine:** Implementation of Moving Average (Short/Long) and Momentum strategies.<br>**Univariate Analytics:** Equity curves, trade signal logic, and single-asset risk metrics. |
| **Quant B**<br>(Portfolio) | **Christian Yu** | **Portfolio Construction:** Cross-asset correlation matrices, weighting algorithms (Equal vs. Custom).<br>**Simulation:** Rebalancing logic (Daily/Weekly/Monthly) and aggregate portfolio NAV tracking. |

---

## ⚙️ Functional Architecture

### 1. Data Ingestion Layer (`data.py`)
- **Source:** Yahoo Finance API (`yfinance`).
- **Processing:** Fetches adjusted closing prices (`auto_adjust=True`) to account for dividends and splits.
- **Optimization:** Implements intelligent caching (`ttl=300s`) to minimize API latency and handle rate limits gracefully.

### 2. Algorithmic Strategies (`strategies.py`)
- **Moving Average Crossover:**
  - *Logic:* Long signal generated when $MA_{short} > MA_{long}$.
  - *Parameters:* Fully customizable windows (e.g., 20-day vs 50-day).
- **Momentum:**
  - *Logic:* Long signal generated when $Return_{t-lookback} > 0$.
  - *Parameters:* Customizable lookback period (e.g., 60 days).

### 3. Portfolio Engine (`portfolio.py`)
- **Universe:** Dynamic filtering by asset class (Indices, Crypto, Commodities, Forex).
- **Weighting Schemes:**
  - *Equal-Weight:* $w_i = 1/N$
  - *Custom:* User-defined weights $\sum w_i = 100\%$ via interactive sliders.
- **Rebalancing:** Simulates periodic re-alignment of weights (Daily, Weekly, Monthly) to mitigate drift.

---

## 🧮 Financial Methodology

Risk metrics are calculated in `metrics.py` following industry standards:

1.  **Cumulative Return:**
    $$R_{cum} = \prod (1 + r_t) - 1$$
2.  **Annualized Volatility:**
    $$\sigma_{ann} = \sigma_{daily} \times \sqrt{252}$$
3.  **Sharpe Ratio:**
    $$Sharpe = \frac{\bar{R}_p - R_f}{\sigma_p}$$
    *(Assuming $R_f \approx 0$ for simplified excess return calculation)*.
4.  **Maximum Drawdown:**
    $$MaxDD = \min \left( \frac{Price_t}{Peak_t} - 1 \right)$$
5.  **Value at Risk (VaR 95%):**
    The 5th percentile of the historical return distribution ($P(R < VaR) = 0.05$).

---

## ☁️ Linux Server Deployment & Automation

The project satisfies the requirement for continuous 24/7 deployment on a Linux Virtual Machine.

### 1. Environment Setup
The application is hosted on a Google Compute Engine VM (Debian/Ubuntu).
# System dependencies
sudo apt update && sudo apt install python3-venv git cron

# Repository setup
git clone [https://github.com/Lucassss04/Project-Python-Git-Linux-for-Finance.git](https://github.com/Lucassss04/Project-Python-Git-Linux-for-Finance.git)
cd Project-Python-Git-Linux-for-Finance

# Virtual Environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

2. Persistent Execution

We use nohup to background the process, ensuring the dashboard remains active after the SSH session terminates.

nohup .venv/bin/streamlit run app.py --server.port 8501 > streamlit.log 2>&1 &

3. Automated Cron Job

A dedicated script (daily_report.py) generates a daily performance log for the CAC 40.

Crontab Configuration: To schedule the report daily at 20:00 (8 PM), run crontab -e and append:

0 20 * * * cd /home/your_user/Project-Python-Git-Linux-for-Finance && .venv/bin/python daily_report.py >> cron.log 2>&1

Output: Reports are appended to daily_report_log.txt.

Repository Structure

.
├── app.py                      # Main entry point (Streamlit Navigation & Config)
├── data.py                     # Data ingestion wrapper (yfinance)
├── metrics.py                  # Financial formulas (Sharpe, Vol, VaR, DD)
├── strategies.py               # Trading logic (MA, Momentum)
├── daily_report.py             # Automation script for Cron jobs
├── daily_report_log.txt        # Persistent log file for daily reports
├── requirements.txt            # Python dependencies
├── README.md                   # Documentation
└── pages/
    ├── single_asset.py         # [Quant A] UI & Logic
    └── portfolio.py            # [Quant B] UI & Logic

Local Installation

    Clone the repository:

git clone [https://github.com/Lucassss04/Project-Python-Git-Linux-for-Finance.git](https://github.com/Lucassss04/Project-Python-Git-Linux-for-Finance.git)

Install dependencies:

pip install -r requirements.txt

Launch the dashboard:

streamlit run app.py