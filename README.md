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

Repository Structure
```
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
```
Local Installation

    Clone the repository:

git clone [https://github.com/Lucassss04/Project-Python-Git-Linux-for-Finance.git](https://github.com/Lucassss04/Project-Python-Git-Linux-for-Finance.git)

Install dependencies:

pip install -r requirements.txt

Launch the dashboard:

streamlit run app.py

---

## ☁️ Linux Server Deployment & Automation

The project is deployed on a Linux Virtual Machine (GCP/Debian) to ensure **24/7 availability** and **automated daily reporting**. The deployment strategy prioritizes stability using absolute paths, persistent background processes, and dedicated logging.

### 1. Environment Setup
The application is hosted on a Google Compute Engine VM (Debian/Ubuntu).


#### Repository setup


```bash
# 1. System dependencies
sudo apt update && sudo apt install -y git python3-venv cron

# 2. Clone repository
git clone https://github.com/Lucassss04/Project-Python-Git-Linux-for-Finance.git
cd Project-Python-Git-Linux-for-Finance

# 3. Python Virtual Environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

```

### 2. Continuous Execution (Background Process)

To keep the Streamlit dashboard running **even after the SSH session is closed**, we launch it with `nohup` and send it to the background with `&`.
`nohup` prevents the process from receiving the hangup signal (SIGHUP) when the terminal disconnects, which is why it continues running after logout. 
We also use **absolute paths** to make the command independent from the current working directory and avoid path-related issues. 

```bash
nohup /home/<USER>/Project-Python-Git-Linux-for-Finance/.venv/bin/streamlit run \
  /home/<USER>/Project-Python-Git-Linux-for-Finance/app.py \
  --server.address 0.0.0.0 --server.port 8501 \
  > /home/<USER>/Project-Python-Git-Linux-for-Finance/streamlit.log 2>&1 &
```

### 3. Automated Daily Reporting (Cron)

This project automates reporting using a cron job that executes `daily_report.py` every day at **20:00** (Paris time). The resulting market report is stored locally on the VM, satisfying the persistent reporting requirement. 

The implementation addresses the restricted context of cron (minimal environment variables, undefined working directory) by using **absolute paths**, explicit directory switching (`cd`), and redirecting all outputs to a persistent log file.

### 3.1 Timezone Configuration (Europe/Paris)
To ensure the report runs at 8 PM local time rather than UTC, we configure the system timezone:

```bash
sudo timedatectl set-timezone Europe/Paris
timedatectl  # Verify Local time matches CET/CEST
```
#### 3.2 Crontab Entry (Daily at 20:00)
We schedule the automated report by editing the user crontab (`crontab -e`) and appending the command below.

```cron
0 20 * * * cd /home/<USER>/Project-Python-Git-Linux-for-Finance && /home/<USER>/Project-Python-Git-Linux-for-Finance/.venv/bin/python /home/<USER>/Project-Python-Git-Linux-for-Finance/daily_report.py >> /home/<USER>/Project-Python-Git-Linux-for-Finance/daily_report_cron.log 2>&1
```
To check the file : 
```
tail -n 50 /home/<USER>/Project-Python-Git-Linux-for-Finance/daily_report_cron.log
```

