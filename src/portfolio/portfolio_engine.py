import numpy as np
import pandas as pd


def compute_portfolio_returns(returns_df, weights, rebalancing="daily"):
    """
    Compute portfolio returns with different rebalancing rules.

    Parameters
    ----------
    returns_df : pd.DataFrame
        Asset returns, one column per asset, index = dates.
    weights : list / array / pd.Series
        Target weights for each asset (will be normalised to sum to 1).
    rebalancing : str
        "daily"     -> rebalance every day (constant weights, classical formula)
        "none"      -> buy and hold, no rebalancing
        "monthly"   -> rebalance at the beginning of each new month
        "quarterly" -> rebalance at the beginning of each new quarter

    Returns
    -------
    pd.Series
        Portfolio returns time series.
    """

    # Align weights with returns_df columns
    if isinstance(weights, pd.Series):
        w = weights.reindex(returns_df.columns).astype(float)
    else:
        w = pd.Series(weights, index=returns_df.columns, dtype=float)

    # Normalise weights
    w = w.fillna(0.0)
    if w.sum() == 0:
        # Fallback equal weights if everything is zero
        w = pd.Series(1.0 / len(returns_df.columns), index=returns_df.columns)
    else:
        w = w / w.sum()

    mode = (rebalancing or "daily").lower()

    # Case 1: daily rebalancing (original behaviour)
    if mode == "daily":
        # Each day: r_p(t) = sum_i w_i * r_i(t)
        portfolio_returns = (returns_df * w).sum(axis=1)
        return portfolio_returns

    # Other modes: simulate asset values and rebalance on given dates
    # Start from initial capital = 1
    asset_values = w.copy()  # allocation of 1 unit of capital
    portfolio_values = pd.Series(index=returns_df.index, dtype=float)

    # Configure rebalancing frequency
    if mode == "none":
        freq = None
    elif mode == "monthly":
        freq = "M"
    elif mode == "quarterly":
        freq = "Q"
    else:
        # Unknown mode -> fallback to no rebalancing
        freq = None

    last_period = None

    for date, row in returns_df.iterrows():
        # Apply asset returns for this day (ignore NaN returns)
        asset_values = asset_values * (1.0 + row.fillna(0.0))
        total_value = asset_values.sum()
        portfolio_values.at[date] = total_value

        # No rebalancing: continue
        if freq is None:
            continue

        # Determine the current period (month or quarter)
        period = date.to_period(freq)

        if last_period is None:
            last_period = period
        elif period != last_period:
            # New period -> rebalance asset_values back to target weights
            asset_values = total_value * w
            last_period = period

    # Convert portfolio values into returns
    portfolio_returns = portfolio_values.pct_change().dropna()
    return portfolio_returns

def compute_cumulative_value(portfolio_returns, initial_value=100.0):
    """Compute cumulative portfolio value starting from initial_value."""
    cum_value = (1 + portfolio_returns).cumprod() * initial_value
    cum_value.name = "portfolio_value"
    return cum_value


def portfolio_stats(portfolio_returns, periods_per_year=252):
    """Compute annual return, annual volatility and approximate Sharpe ratio."""
    mean_daily = portfolio_returns.mean()
    vol_daily = portfolio_returns.std()

    mean_annual = mean_daily * periods_per_year
    vol_annual = vol_daily * np.sqrt(periods_per_year)
    if vol_annual == 0:
        sharpe = np.nan
    else:
        sharpe = mean_annual / vol_annual

    stats = {
        "Annual return (%)": mean_annual * 100,
        "Annual volatility (%)": vol_annual * 100,
        "Sharpe (approx)": sharpe,
    }

    return pd.DataFrame(stats, index=["Portfolio"])
