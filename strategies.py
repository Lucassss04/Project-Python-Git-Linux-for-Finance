import pandas as pd


def moving_average_strategy(
    data: pd.DataFrame, short_window: int = 20, long_window: int = 50
) -> pd.DataFrame:
    """
    Stratégie simple : long quand MA courte > MA longue, sinon cash.
    Renvoie un DataFrame avec colonnes de MAs, position et strategy_return.
    """
    df = data.copy()
    df["ma_short"] = df["price"].rolling(short_window).mean()
    df["ma_long"] = df["price"].rolling(long_window).mean()
    df["signal"] = 0
    df.loc[df["ma_short"] > df["ma_long"], "signal"] = 1
    df["position"] = df["signal"].shift(1).fillna(0)
    df["strategy_return"] = df["position"] * df["return"]
    return df


def momentum_strategy(
    data: pd.DataFrame, lookback: int = 60
) -> pd.DataFrame:
    """
    Stratégie momentum très simple :
    - calcule le rendement sur 'lookback' jours
    - long si ce rendement est > 0, cash sinon.
    """
    df = data.copy()
    df["mom"] = df["price"].pct_change(lookback)
    df["signal"] = 0
    df.loc[df["mom"] > 0, "signal"] = 1
    df["position"] = df["signal"].shift(1).fillna(0)
    df["strategy_return"] = df["position"] * df["return"]
    return df
