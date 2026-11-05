import pandas as pd
from pathlib import Path
import numpy as np

def load_balance_sheet(path=None):
    if path is None:
        path = Path(__file__).resolve().parent.parent / "model" / "balance_sheet.csv"

    print("Reading file:", path.resolve())

    return pd.read_csv(path)

def load_yields(path=None):
    if path is None:
        path = Path(__file__).resolve().parent.parent / "data" / "yields.csv"

    df = pd.read_csv(path, parse_dates=["date"], index_col="date")
    return df.sort_index()

def interest_income(bs):
    assets = bs[bs["side"] == "Asset"]
    return (assets["balance"] * assets["rate"]).sum() / 100      # sum of balance x rate, divided by 100

def interest_expense(bs):
    liabs = bs[bs["side"] == "Liability"]
    return (liabs["balance"] * liabs["rate"]).sum() / 100

def nii(bs):
    return interest_income(bs) - interest_expense(bs)  # NII in absolute terms

def nim(bs):
    total_assets = bs.loc[bs["side"] == "Asset", "balance"].sum()
    return nii(bs) / total_assets * 100        # NII over total assets, in percent

def delta_nii(bs, shock_pp):
    assets = bs[bs["side"] == "Asset"]
    liabs = bs[bs["side"] == "Liability"]
    asset_gain = ((assets["balance"] * assets["reprice_share"]).sum() / 100) * shock_pp/100      # sum of balance x reprice_share/100, times shock/100
    liability_cost = ((liabs["balance"] * liabs["reprice_share"] * liabs["beta"]).sum() / 100) * shock_pp/100  
    return asset_gain - liability_cost

def delta_eve(bs, shock_pp):
    assets = bs[bs["side"] == "Asset"]
    liabs = bs[bs["side"] == "Liability"]
    asset_exposure = (assets["balance"] * assets["duration"]).sum()
    liability_exposure = (liabs["balance"] * liabs["duration"]).sum()
    return -(asset_exposure - liability_exposure) * shock_pp / 100

def equity(bs):
    total_assets = bs.loc[bs["side"] == "Asset", "balance"].sum()
    total_liabs = bs.loc[bs["side"] == "Liability", "balance"].sum()
    return total_assets - total_liabs

KEYS = [2, 3, 5, 7, 10]

def key_rate_weights(duration, keys=KEYS):
    """Spread one duration over the key maturities (weights sum to 1)."""
    w = pd.Series(0.0, index=keys)
    if duration <= keys[0]:
        w[keys[0]] = 1.0
    elif duration >= keys[-1]:
        w[keys[-1]] = 1.0
    else:
        for lo, hi in zip(keys[:-1], keys[1:]):
            if lo <= duration < hi:
                w_hi = (duration - lo) / (hi - lo)        # how far the duration is from lo toward hi
                w[lo], w[hi] = 1 - w_hi, w_hi
    return w

def key_rate_exposure(bs, keys=KEYS):
    """Net exposure (assets minus liabilities) at each key, in $B x years."""
    total = pd.Series(0.0, index=keys)
    for _, row in bs.iterrows():
        sign = 1 if row["side"] == "Asset" else -1                # +1 for an asset, -1 for a liability
        total += sign * row["balance"] * row["duration"] * key_rate_weights(row["duration"], keys=keys)
    return total

def delta_eve_curve(bs, shocks, keys=KEYS):
    """shocks: a Series indexed by key, in percentage points."""
    return -(key_rate_exposure(bs, keys=keys) * shocks / 100).sum()

def tilt(keys, pivot, slope, parallel=0.0):
    """Shock at each key: parallel + slope x (key - pivot), in percentage points."""
    return pd.Series([parallel + slope * (k - pivot) for k in keys], 
                     index=keys)

def historical_shock(yields, start, end, cols=("2yr","3yr","5yr","7yr","10yr"), keys=KEYS):
    """Actual yield change between two dates, one value per key."""
    change = yields.loc[end, cols] - yields.loc[start, cols]
    return pd.Series(change.values, index=keys)