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
