import numpy as np
import pandas as pd


def equal_weights(tickers):
    """Return equal weights for the given tickers."""
    n = len(tickers)
    if n == 0:
        raise ValueError("Ticker list is empty, cannot build weights.")
    w = np.ones(n, dtype=float) / n
    return pd.Series(w, index=tickers)


def normalize_weights(raw_weights, tickers):
    """Normalize raw weights so that they sum to 1."""
    if len(raw_weights) != len(tickers):
        raise ValueError("raw_weights and tickers must have the same length.")

    s = pd.Series(raw_weights, index=tickers, dtype=float)
    total = s.sum()

    if total == 0:
        raise ValueError("Sum of weights is zero, cannot normalize.")

    return s / total


def clip_and_normalize(raw_weights, tickers, min_weight=0.0, max_weight=1.0):
    """Clip weights between [min_weight, max_weight] and normalize them."""
    if len(raw_weights) != len(tickers):
        raise ValueError("raw_weights and tickers must have the same length.")

    s = pd.Series(raw_weights, index=tickers, dtype=float)
    s_clipped = s.clip(lower=min_weight, upper=max_weight)

    total = s_clipped.sum()
    if total == 0:
        raise ValueError("Sum of weights after clipping is zero, cannot normalize.")

    return s_clipped / total
