import pandas as pd
from .metrics import total_return, annualized_volatility, sharpe_ratio, max_drawdown


def backtest(strategy_value: pd.Series) -> dict:
    return {
        "total_return": float(total_return(strategy_value)),
        "annual_vol": float(annualized_volatility(strategy_value)),
        "sharpe": float(sharpe_ratio(strategy_value)),
        "max_drawdown": float(max_drawdown(strategy_value)),
        "final_value": float(strategy_value.iloc[-1]),
    }
