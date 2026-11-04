import pytest
import pandas as pd
from src.alm import (load_balance_sheet, interest_income, interest_expense,
                     nii, nim, delta_nii, delta_eve, equity, key_rate_exposure, KEYS, 
                     delta_eve_curve)

@pytest.fixture
def bs():
    return load_balance_sheet()

def test_balance_sheet_loads(bs):
    assert bs.shape == (6, 8)
    assert bs.loc[bs["side"] == "Asset", "balance"].sum() == 100

def test_interest_income(bs):
    assert interest_income(bs) == pytest.approx(4.2206, abs=1e-4)

def test_interest_expense(bs):
     assert interest_expense(bs) == pytest.approx(1.5832, abs=1e-4)

def test_nii(bs):
    assert nii(bs) == pytest.approx(2.6374, abs=1e-4)

def test_nim(bs):
    assert nim(bs) == pytest.approx(2.6374, abs=1e-4)

def test_delta_nii_up(bs):
    assert delta_nii(bs, 1) == pytest.approx(0.0835, abs=1e-4)

def test_delta_nii_down(bs):
    assert delta_nii(bs, -1) == pytest.approx(-0.0835, abs=1e-4)

def test_delta_nii_zero(bs):
    assert delta_nii(bs, 0) == pytest.approx(0.0, abs=1e-4)

def test_linear(bs):
    assert delta_nii(bs, 2) == pytest.approx(2 * delta_nii(bs, 1), abs=1e-4)
    
def test_beta_matters(bs):
    bs2 = bs.copy()
    bs2["beta"] = 1.0
    assert delta_nii(bs2, 1) == pytest.approx(-0.3015, abs=1e-4)

def test_delta_eve_positive(bs):
    assert delta_eve(bs, 1) == pytest.approx(-1.2225, abs=1e-4)

def test_delta_eve_negative(bs):
    assert delta_eve(bs, -1) == pytest.approx(1.2225, abs=1e-4)

def test_equity(bs):
    assert equity(bs) == 8

def test_delta_eve_zero(bs):
    assert delta_eve(bs, 0) == pytest.approx(0.0, abs=1e-4)

def test_delta_eve_linear(bs):
    assert delta_eve(bs, 2) == pytest.approx(2 * delta_eve(bs, 1), abs=1e-4)

def test_delta_eve_as_pp_equity(bs):
    assert delta_eve(bs, 1) / equity(bs) * 100 == pytest.approx(-15.28, abs=0.01)

def test_key_rate_exposure(bs):
    result = key_rate_exposure(bs)

    expected = pd.Series(
        [-116, 48.25, 190, 0, 0],
        index=KEYS,
        dtype=float
    )

    pd.testing.assert_series_equal(result, expected)


def test_delta_eve_curve_parallel_shock(bs):
    parallel = pd.Series(1.0, index=KEYS)

    assert delta_eve_curve(bs, parallel) == pytest.approx(-1.2225)