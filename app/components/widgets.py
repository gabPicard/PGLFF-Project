import streamlit as st


def select_asset():
    return st.text_input("Ticker (ex: AAPL, MSFT, BTC-USD)", value="AAPL").upper()



def select_period():
    return st.selectbox(
        "Period:",
        ["1mo", "3mo", "6mo", "1y", "5y", "max"],
        index=3,
    )


def select_interval():
    return st.selectbox(
        "Interval:",
        ["1d", "1wk"],
        index=0,
    )


def select_strategy():
    return st.radio(
        "Strategy:",
        ["Buy & Hold", "Momentum", "Mean Reversion"],
        index=0,
        horizontal=True,
    )


def momentum_period_slider(default: int = 20):
    return st.slider("Moving average period (days):", min_value=3, max_value=100, value=default)
