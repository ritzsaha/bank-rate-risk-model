import numpy as np
import pandas as pd
from sklearn.decomposition import PCA

COLS = ["2yr", "3yr", "5yr", "7yr", "10yr"]

def yield_changes(yields, cols=COLS):
    """Daily change in each yield, in percentage points."""
    return yields[cols].diff().dropna()

def fit_pca(changes):
    pca = PCA().fit(changes)
    c = pca.components_
    if c[0].sum() < 0: c[0] *= -1             # level: all maturities move up together
    if c[1][-1] < c[1][0]: c[1] *= -1         # slope: the long end moves more than the short end
    if c[2][2] < 0: c[2] *= -1                # curvature: the middle (5yr) moves up
    return pca

def pc_shock(pca, i, n_sigma=1.0, horizon_days=250, keys=(2, 3, 5, 7, 10)):
    """Shock in percentage points at each key for an n_sigma move in component i over a year."""
    size = n_sigma * np.sqrt(horizon_days) * np.sqrt(pca.explained_variance_[i])
    return pd.Series(pca.components_[i] * size, index=list(keys))