# 🛒 Store Sales Agent

ML-powered sales assistant for general stores. A mobile-friendly Streamlit web app covering the whole sales funnel, with an AI advisor (GPT-4o mini via OpenRouter) on every page.

| Stage | Tool | ML method |
|---|---|---|
| Plan | Sales Forecast | Gradient Boosting (time series, 28-day backtest) |
| Understand | Customer Segments | RFM + K-Means |
| Sell more | Recommendations | Market-basket analysis (lift, confidence) |
| Retain | Churn Risk | Random Forest |
| Grow | Customer Value (CLV) | Gradient Boosting regression |
| Supply | Stock Alerts | Trend demand forecast + safety stock |
| Convert | Promotions | Price-elasticity regression + profit-floor optimizer |

## Dataset
[UCI Online Retail](https://archive.ics.uci.edu/dataset/352/online+retail). Download, unzip, and place `Online Retail.xlsx` in `data/`.

## Setup
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml   # then paste your OpenRouter key
streamlit run app.py
```
First launch takes about 1 minute (Excel parsing), then a cache file makes it fast.
Phone test on the same Wi-Fi: `streamlit run app.py --server.address 0.0.0.0` → open `http://<laptop-ip>:8501`.

## Deploy (Streamlit Community Cloud)
1. Push this repo (including `data/Online Retail.xlsx`, ~23 MB, push with git, not browser upload).
2. share.streamlit.io → New app → main file `app.py`.
3. App settings → Secrets → add `OPENROUTER_API_KEY = "..."`.

## Results on the dataset
- Forecast: ~19% error (WAPE) on the unseen last 28 days, beating a same-weekday-last-week baseline.
- Churn: AUC ≈ 0.72 on held-out customers.
- CLV: weak-to-moderate (log-R² ≈ 0.2), since only one year of history exists.
- Elasticity is observational; stock levels are simulated unless you upload a CSV (`StockCode,OnHand`).

## Structure
```
app.py            navigation
core/data.py      loading + cleaning
core/models.py    all ML models
core/llm.py       OpenRouter chat + chat panel
views/            one file per page
```
