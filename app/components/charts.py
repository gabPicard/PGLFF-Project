import plotly.graph_objects as go
import pandas as pd


def price_and_strategy_chart(
    df_price: pd.DataFrame,
    strategy_series: pd.Series | None = None,
    title: str = "Prix et stratégie",
):

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df_price.index,
            y=df_price["price"],
            name="Prix",
            mode="lines",
        )
    )

    if strategy_series is not None:
        price_norm = df_price["price"] / df_price["price"].iloc[0]
        strat_norm = strategy_series / strategy_series.iloc[0]

        fig.add_trace(
            go.Scatter(
                x=df_price.index,
                y=price_norm,
                name="Prix normalisé",
                mode="lines",
                line=dict(dash="dot"),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=strategy_series.index,
                y=strat_norm,
                name=str(strategy_series.name or "Stratégie"),
                mode="lines",
            )
        )

    fig.update_layout(title=title, xaxis_title="Date", yaxis_title="Valeur")
    return fig
