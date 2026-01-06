import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import streamlit as st

# Allow imports like "from src.data.fetch_yf import get_history"
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))
from streamlit_autorefresh import st_autorefresh
from src.data.fetch_yf import get_history
from src.portfolio.weights import equal_weights, normalize_weights
from src.portfolio.portfolio_engine import (
    compute_portfolio_returns,
    compute_cumulative_value,
    portfolio_stats,
)
from src.portfolio.correlations import compute_correlation_matrix


def get_price_data_multi(tickers, period="1y", interval="1d"):
    """
    Download price history for multiple tickers and build a price DataFrame.

    Returns
    -------
    prices : pd.DataFrame
        Price time series with one column per valid ticker.
    invalid_tickers : list
        List of tickers for which no data could be fetched.
    """
    dfs = []
    invalid_tickers = []

    for t in tickers:
        try:
            df_t = get_history(t, period=period, interval=interval)

            # If no data, mark as invalid and skip
            if df_t is None or df_t.empty:
                invalid_tickers.append(t)
                continue

            # In get_history, the column is "price" -> rename to ticker symbol
            df_t = df_t.rename(columns={"price": t})
            dfs.append(df_t)

        except Exception as e:
            invalid_tickers.append(t)
            st.warning(f"Could not download data for {t}: {e}")

    if not dfs:
        # No valid ticker at all
        return pd.DataFrame(), invalid_tickers

    prices = pd.concat(dfs, axis=1)
    prices = prices.dropna(how="all")

    # Ensure columns are simple strings (no MultiIndex)
    if isinstance(prices.columns, pd.MultiIndex):
        prices.columns = [
            str(col[0]) if isinstance(col, tuple) else str(col)
            for col in prices.columns
        ]
    else:
        prices.columns = [str(c) for c in prices.columns]

    return prices, invalid_tickers


def compute_returns(price_df):
    """Compute simple returns from price DataFrame."""
    # fill_method=None to avoid the FutureWarning
    returns = price_df.pct_change(fill_method=None).dropna()
    return returns


def run(config=None):
    """Main Streamlit page for the multi-asset portfolio (Quant B)."""
    st_autorefresh(interval=300000, key="data_refresher")
    #refresh every 5 minutes
    st.toast(f"Data updated at {datetime.now().strftime('%H:%M:%S')}", icon="🔄")
    st.title("Multi-Asset Portfolio")

    # Default values (can be overridden by config.yaml if you want)
    default_tickers = ["AAPL", "MSFT", "GLD"]
    default_period = "1y"
    default_interval = "1d"
    initial_value = 100.0
    periods_per_year = 252

    if config is not None and "portfolio" in config:
        cfg = config["portfolio"]
        default_tickers = cfg.get("default_tickers", default_tickers)
        default_period = cfg.get("period", default_period)
        default_interval = cfg.get("interval", default_interval)
        initial_value = cfg.get("initial_value", initial_value)
        periods_per_year = cfg.get("periods_per_year", periods_per_year)

    st.write(
        "Simulate a portfolio with several assets, choose custom weights, "
        "and analyze its overall performance."
    )

    # ---- 1) Tickers and history settings ----
    st.subheader("1) Assets and history settings")

    tickers_str = st.text_input(
        "Tickers (comma-separated)",
        value=", ".join(default_tickers),
    )
    tickers = [t.strip().upper() for t in tickers_str.split(",") if t.strip()]

    col1, col2 = st.columns(2)
    with col1:
        period = st.selectbox(
            "History period (yfinance period)",
            ["3mo", "6mo", "1y", "2y", "5y", "10y"],
            index=2,
        )
    with col2:
        interval = st.selectbox(
            "Interval",
            ["1d", "1wk", "1mo"],
            index=0,
        )

    if len(tickers) == 0:
        st.warning("Please add at least one ticker.")
        return

    # Fetch market data immediately so we know which tickers are valid
    price_df, invalid_tickers = get_price_data_multi(
        tickers, period=period, interval=interval
    )

    if invalid_tickers:
        st.warning(
            "No data found for the following tickers, they were ignored: "
            + ", ".join(invalid_tickers)
        )

    if price_df.empty:
        st.error("No valid data fetched for any ticker. Please adjust the tickers.")
        return

    valid_tickers = list(price_df.columns)

    # ---- 2) Portfolio allocation ----
    st.subheader("2) Portfolio allocation")

    cols = st.columns(len(valid_tickers))
    raw_weights = []
    for col, t in zip(cols, valid_tickers):
        with col:
            w = st.slider(
                f"Weight {t}",
                min_value=0.0,
                max_value=1.0,
                value=1.0 / len(valid_tickers),
                step=0.05,
            )
            raw_weights.append(w)

    if sum(raw_weights) == 0:
        st.info("All weights are zero. Using equal weights on valid tickers.")
        weights = equal_weights(valid_tickers)
    else:
        weights = normalize_weights(raw_weights, valid_tickers)

    st.write("Normalized weights (valid tickers only):", weights.round(3).to_dict())

    # ---- 3) Strategy settings ----
    st.subheader("3) Strategy settings")

    strategy_label = st.selectbox(
        "Rebalancing frequency",
        [
            "Daily (constant weights)",
            "Monthly rebalancing",
            "Quarterly rebalancing",
            "None (buy and hold)",
        ],
        index=0,
    )

    strategy_map = {
        "Daily (constant weights)": "daily",
        "Monthly rebalancing": "monthly",
        "Quarterly rebalancing": "quarterly",
        "None (buy and hold)": "none",
    }
    rebalancing_freq = strategy_map[strategy_label]

    # ---- 4) Market data ----
    st.subheader("4) Market data")

    price_df_for_plot = price_df.copy()
    if isinstance(price_df_for_plot.columns, pd.MultiIndex):
        price_df_for_plot.columns = [
            str(col[0]) if isinstance(col, tuple) else str(col)
            for col in price_df_for_plot.columns
        ]
    else:
        price_df_for_plot.columns = [str(c) for c in price_df_for_plot.columns]

    st.line_chart(price_df_for_plot)

    # ---- 5) Portfolio performance ----
    st.subheader("5) Portfolio performance")

    returns_df = compute_returns(price_df)

    # Try to use rebalancing parameter if backend supports it,
    # otherwise fall back to the old signature.
    try:
        portfolio_returns = compute_portfolio_returns(
            returns_df, weights, rebalancing=rebalancing_freq
        )
    except TypeError:
        portfolio_returns = compute_portfolio_returns(returns_df, weights)

    cum_value = compute_cumulative_value(portfolio_returns, initial_value=initial_value)
    stats_df = portfolio_stats(portfolio_returns, periods_per_year=periods_per_year)

    st.line_chart(cum_value)

    st.markdown("Portfolio statistics")
    st.dataframe(
        stats_df.style.format(
            {
                "Annual return (%)": "{:.2f}",
                "Annual volatility (%)": "{:.2f}",
                "Sharpe (approx)": "{:.2f}",
            }
        )
    )

    # ---- 6) Diversification effect ----
    st.subheader("6) Diversification effect")

    # Annualized volatility of each asset
    asset_vol_annual = returns_df.std() * (periods_per_year ** 0.5)

    # Align weights with returns_df columns
    if isinstance(weights, pd.Series):
        w_aligned = weights.reindex(returns_df.columns).fillna(0.0)
    else:
        w_aligned = pd.Series(weights, index=returns_df.columns).fillna(0.0)

    # Normalize weights (safety)
    if w_aligned.sum() == 0:
        w_aligned = pd.Series(1.0 / len(returns_df.columns), index=returns_df.columns)
    else:
        w_aligned = w_aligned / w_aligned.sum()

    # Weighted average asset volatility (annualized, decimal)
    weighted_avg_vol = float((w_aligned * asset_vol_annual).sum())

    # Portfolio annual volatility (decimal)
    portfolio_vol = float(portfolio_returns.std() * (periods_per_year ** 0.5))

    # Volatility reduction due to diversification (in %)
    if weighted_avg_vol > 0:
        vol_reduction_pct = (weighted_avg_vol - portfolio_vol) / weighted_avg_vol * 100.0
    else:
        vol_reduction_pct = 0.0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Weighted avg asset vol (%)", f"{weighted_avg_vol * 100:.2f}")
    with col2:
        st.metric("Portfolio vol (%)", f"{portfolio_vol * 100:.2f}")
    with col3:
        st.metric("Vol reduction (%)", f"{vol_reduction_pct:.2f}")

    # ---- 7) Correlation matrix ----
    st.subheader("7) Correlation between assets")

    corr_df = compute_correlation_matrix(returns_df)
    st.dataframe(corr_df.style.background_gradient(cmap="coolwarm"))

    with st.expander("Show first portfolio daily returns"):
        st.dataframe(portfolio_returns.to_frame().head())


if __name__ == "__main__":
    # Run with:  streamlit run pages/Portfolio.py
    run()
