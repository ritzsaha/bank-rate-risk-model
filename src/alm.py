import pandas as pd
from pathlib import Path

def load_balance_sheet(path=None):
    if path is None:
        path = Path(__file__).resolve().parent.parent / "model" / "balance_sheet.csv"
    return pd.read_csv(path)

def load_balance_sheet(path="model/balance_sheet.csv"):
    return pd.read_csv(path)

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