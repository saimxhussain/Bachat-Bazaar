import pandas as pd
import plotly.express as px
import streamlit as st

from core import models as M
from core.data import load_data
from core.llm import chat_panel

df = load_data()
names = M.product_names(df)
dem = M.product_demand(df)

st.title("📦 Stock Alerts")
st.caption("Forecasts demand for your 60 best sellers and tells you what to reorder before you run out.")

c = st.columns(3)
lead = c[0].slider("Supplier lead time (days)", 1, 21, 7)
level = c[1].select_slider("Service level", [0.90, 0.95, 0.98], 0.95)
cover = c[2].slider("Order enough for (days)", 7, 45, 14)
z = {0.90: 1.28, 0.95: 1.65, 0.98: 2.05}[level]

template = pd.DataFrame({"StockCode": dem.index, "Product": [names[i] for i in dem.index],
                         "OnHand": M.demo_stock(dem).values})
up = st.file_uploader("Upload your real stock (CSV with columns StockCode, OnHand). Demo stock is used until then.", type="csv")
stock = M.demo_stock(dem)
if up is not None:
    u = pd.read_csv(up, dtype={"StockCode": str})
    stock = u.set_index("StockCode").OnHand
    st.success(f"Using your stock file ({len(u)} rows).")
else:
    st.download_button("Download CSV template (demo stock)", template.to_csv(index=False).encode(), "stock_template.csv")

plan = M.reorder_plan(dem, stock, lead, z, cover)
plan.insert(0, "Product", [names[i] for i in plan.index])
counts = plan.status.value_counts()
m = st.columns(3)
m[0].metric("🔴 Stock-out risk", counts.get("Stock-out risk", 0))
m[1].metric("🟠 Reorder now", counts.get("Reorder now", 0))
m[2].metric("🟢 OK", counts.get("OK", 0))

alerts = plan[plan.status != "OK"].sort_values("days_cover")
view = alerts[["Product", "status", "on_hand", "days_cover", "reorder_point", "order_qty"]]
st.dataframe(view.rename(columns={"on_hand": "On hand", "days_cover": "Days of cover",
                                  "reorder_point": "Reorder point", "order_qty": "Order qty"}), width="stretch")
st.plotly_chart(px.bar(plan.sort_values("days_cover").head(15), x="days_cover", y="Product", color="status",
                       orientation="h", title="Lowest days of cover",
                       color_discrete_map={"Stock-out risk": "#d62728", "Reorder now": "#ff7f0e", "OK": "#2ca02c"}),
                width="stretch")
st.caption("Demand = 12-week linear trend (kept within 0.5-2x the average). Safety stock = z × demand volatility × √lead time.")

chat_panel(f"Stock alerts (lead time {lead} days, service level {level:.0%}). Counts: {counts.to_dict()}.\n"
           + view.head(10).to_string())
