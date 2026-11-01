from pathlib import Path

import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@st.cache_data(show_spinner="Loading dataset (first run takes ~1 min)...")
def load_data() -> pd.DataFrame:
    cache = DATA_DIR / "retail_clean.pkl"
    if cache.exists():
        try:
            return pd.read_pickle(cache)
        except Exception:
            cache.unlink()

    files = list(DATA_DIR.glob("*.xlsx"))
    if not files:
        st.error("Put 'Online Retail.xlsx' inside the data/ folder.")
        st.stop()

    df = pd.read_excel(files[0])
    df["InvoiceNo"] = df.InvoiceNo.astype(str)
    df["StockCode"] = df.StockCode.astype(str)
    df = df[~df.InvoiceNo.str.startswith("C")]                 # drop cancellations
    df = df[(df.Quantity > 0) & (df.Quantity < 10000) & (df.UnitPrice > 0)]  # drop bad rows + the 74k-unit order that was cancelled
    df = df[df.StockCode.str.match(r"^\d{5}")]                 # real products only (no POST, M, D...)
    df = df[df.InvoiceDate < "2011-12-09"]                     # last day is partial
    df = df.dropna(subset=["Description"]).copy()
    df["Description"] = df.Description.str.strip().str.title()
    df["Revenue"] = df.Quantity * df.UnitPrice
    df["Date"] = df.InvoiceDate.dt.normalize()
    df = df.reset_index(drop=True)
    df.to_pickle(cache)
    return df
