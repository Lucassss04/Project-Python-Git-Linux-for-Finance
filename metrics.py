import numpy as np
import pandas as pd


def compute_performance_metrics(returns: pd.Series, rf: float = 0.0) -> dict:
    """Métriques standard : rendement cumulé, vol, Sharpe, max drawdown, VaR 95%."""
    returns = returns.dropna()

    # Rendement cumulé
    cum_return = (1 + returns).prod() - 1

    # Volatilité annualisée
    ann_vol = returns.std() * np.sqrt(252)

    # Sharpe annualisé
    if ann_vol > 0:
        excess_ret = returns.mean() - rf / 252
        sharpe = (excess_ret / returns.std()) * np.sqrt(252)
    else:
        sharpe = np.nan

    # Max drawdown
    equity_curve = (1 + returns).cumprod()
    running_max = equity_curve.cummax()
    drawdown = equity_curve / running_max - 1.0
    max_dd = drawdown.min()

    # VaR historique 95 % (quantile 5 % des rendements)
    var_95 = np.percentile(returns, 5)

    return {
        "cum_return": cum_return,
        "ann_vol": ann_vol,
        "sharpe": sharpe,
        "max_dd": max_dd,
        "var_95": var_95,
    }
