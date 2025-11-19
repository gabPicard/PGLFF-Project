import pandas as pd


def run_momentum(df: pd.DataFrame, period: int = 20) -> pd.Series:
    if "price" not in df.columns:
        raise ValueError("Le DataFrame doit contenir une colonne 'price'.")

    df = df.copy()
    df["ma"] = df["price"].rolling(period).mean()

    df["signal"] = (df["price"] > df["ma"]).astype(int)

    df["returns"] = df["price"].pct_change()

    df["strategy_ret"] = df["signal"].shift(1) * df["returns"]

    df["strategy_value"] = (1 + df["strategy_ret"]).cumprod()
    df["strategy_value"].fillna(1.0, inplace=True)
    df["strategy_value"].name = f"Momentum_{period}"

    return df["strategy_value"]