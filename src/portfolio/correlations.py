import pandas as pd


def compute_correlation_matrix(returns_df):
    """Compute correlation matrix between asset returns."""
    return returns_df.corr()
