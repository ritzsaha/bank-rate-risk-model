import pandas as pd
from pathlib import Path

def load_balance_sheet(path=None):
    if path is None:
        path = Path(__file__).resolve().parent.parent / "model" / "balance_sheet.csv"
    return pd.read_csv(path)