import pandas as pd


def run_buy_and_hold(df: pd.DataFrame) -> pd.Series:
    if "price" not in df.columns:
        raise ValueError("Le DataFrame doit contenir une colonne 'price'.")

    initial_price = df["price"].iloc[0]
    strategy_value = df["price"] / initial_price
    strategy_value.name = "Buy & Hold"

    return strategy_value