import streamlit as st
import pandas as pd

from components.widgets import (
    select_asset,
    select_period,
    select_interval,
    select_strategy,
    momentum_period_slider,
)
from components.charts import price_and_strategy_chart

from src.data.fetch_yf import get_history
from src.strategies.buy_and_hold import run_buy_and_hold
from src.strategies.momentum import run_momentum
from src.evaluation.backtesting import backtest

st.set_page_config(
    page_title="Analyse d'un actif",
    page_icon="📈",
    layout="wide",
)

st.title("Analyse d’un actif (Quant A)")

with st.sidebar:
    st.header("Paramètres")
    ticker = select_asset()
    period = select_period()
    interval = select_interval()
    strategy_name = select_strategy()

    ma_period = None
    if strategy_name == "Momentum":
        ma_period = momentum_period_slider(default=20)

try:
    with st.spinner("Téléchargement des données..."):
        df = get_history(ticker, period=period, interval=interval)
        if df is None or df.empty:
            st.error(f"Aucune donnée disponible pour {ticker} avec la période '{period}' et l'intervalle '{interval}'.")
            st.stop()
except Exception as e:
    st.error(f"Erreur lors du téléchargement des données : {e}")
    st.stop()

st.subheader(f"Historique de {ticker}")

col_top_left, col_top_right = st.columns(2)

col_top_left.write(
    f"Période téléchargée : {df.index.min().date()} → {df.index.max().date()}"
)
col_top_right.write(f"Nombre de points : {len(df)}")

if strategy_name == "Buy & Hold":
    strategy_series = run_buy_and_hold(df)
else:
    strategy_series = run_momentum(df, period=ma_period)

results = backtest(strategy_series)

st.subheader("📊 Indicateurs de performance")

m1, m2, m3, m4 = st.columns(4)

m1.metric(
    "Rendement total",
    f"{results['total_return']*100:,.2f} %",
)
m2.metric(
    "Volatilité annualisée",
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

st.subheader("📉 Prix et stratégie")

fig = price_and_strategy_chart(df, strategy_series, title=f"{ticker} - {strategy_name}")
st.plotly_chart(fig, use_container_width=True)

with st.expander("Voir les données brutes"):
    st.dataframe(df.tail(20))
