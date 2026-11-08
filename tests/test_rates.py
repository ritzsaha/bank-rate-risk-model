from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from src.rates import COLS, yield_changes, fit_pca, pc_shock

@pytest.fixture
def setup():
    path = Path(__file__).resolve().parent.parent / "data" / "yields.csv"
    dy = yield_changes(pd.read_csv(path, index_col="date", parse_dates=True))
    return dy, fit_pca(dy)

def test_changes_clean(setup):
    dy, _ = setup
    assert dy.shape[1] == 5 and not dy.isna().any().any()

def test_variance_ratios(setup):
    _, pca = setup
    r = pca.explained_variance_ratio_
    assert r.sum() == pytest.approx(1.0)
    assert (np.diff(r) <= 0).all()

def test_components_orthonormal(setup):
    _, pca = setup
    c = pca.components_
    assert c @ c.T == pytest.approx(np.eye(5), abs=1e-8)

def test_sign_convention(setup):
    _, pca = setup
    c = pca.components_
    assert c[0].sum() > 0 and c[1][-1] > c[1][0] and c[2][2] > 0

def test_shock_scaling(setup):
    _, pca = setup
    assert pc_shock(pca, 0, 2).tolist() == pytest.approx((2 * pc_shock(pca, 0, 1)).tolist())
    assert pc_shock(pca, 1, -1).tolist() == pytest.approx((-pc_shock(pca, 1, 1)).tolist())

def test_reconstruction(setup):
    dy, pca = setup
    rebuilt = pca.inverse_transform(pca.transform(dy))
    assert rebuilt == pytest.approx(dy.values, abs=1e-8)