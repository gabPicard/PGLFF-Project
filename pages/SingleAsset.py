import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

from app.components.widgets import (
    select_asset,
    select_period,
    select_interval,
    select_strategy,
    momentum_period_slider,
)
from app.components.charts import price_and_strategy_chart

from src.data.fetch_yf import get_history
from src.strategies.buy_and_hold import run_buy_and_hold
from src.strategies.momentum import run_momentum
from src.strategies.mean_reversion import run_mean_reversion
from src.evaluation.backtesting import backtest

st.set_page_config(
    page_title="Analysis of a single asset (Quant A)",
    page_icon="📈",
    layout="wide",
)

count = st_autorefresh(interval=300000, limit=None, key="single_asset_refresh")

st.title("Analysis of a single asset (Quant A)")

st.toast(f"Data updated - {datetime.now().strftime('%H:%M:%S')}")

with st.sidebar:
    st.header("Parameters")
    ticker = select_asset()
    period = select_period()
    interval = select_interval()
    strategy_name = select_strategy()

    ma_period = None
    mr_period = None
    mr_threshold = None

    if strategy_name == "Momentum":
        ma_period = momentum_period_slider(default=20)

    elif strategy_name == "Mean Reversion":
        mr_period = st.slider("MA Period (mean reversion)", 5, 60, 20)
        mr_threshold = st.slider("Threshold (%)", 1, 10, 2) / 100


try:
    with st.spinner("Downloading data..."):
        df = get_history(ticker, period=period, interval=interval)
        if df is None or df.empty:
            st.error(f"No data available for {ticker} with period '{period}' and interval '{interval}'.")
            st.stop()
except Exception as e:
    st.error(f"Error downloading data: {e}")
    st.stop()

st.subheader(f"History of {ticker}")

col_top_left, col_top_right = st.columns(2)

col_top_left.write(
    f"Downloaded period: {df.index.min().date()} → {df.index.max().date()}"
)
col_top_right.write(f"Number of points: {len(df)}")

if strategy_name == "Buy & Hold":
    strategy_series = run_buy_and_hold(df)
elif strategy_name == "Momentum":
    strategy_series = run_momentum(df, period=ma_period)
else:
    strategy_series = run_mean_reversion(df, period=mr_period, threshold=mr_threshold)

results = backtest(strategy_series)

st.subheader("📊 Performance Indicators")

m1, m2, m3, m4 = st.columns(4)

m1.metric(
    "Total Return",
    f"{results['total_return']*100:,.2f} %",
)
m2.metric(
    "Annualized Volatility",
    f"{results['annual_vol']*100:,.2f} %",
)
m3.metric(
    "Sharpe (approx.)",
    f"{results['sharpe']:.2f}",
)
m4.metric(
    "Max drawdown",
    f"{results['max_drawdown']*100:,.2f} %",
)

st.subheader("📉 Price and Strategy")

fig = price_and_strategy_chart(df, strategy_series, title=f"{ticker} - {strategy_name}")
st.plotly_chart(fig, use_container_width=True)

with st.expander("View raw data"):
    st.dataframe(df.tail(20))