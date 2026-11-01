import numpy as np
import plotly.express as px
import streamlit as st

from core import models as M
from core.data import load_data
from core.llm import chat_panel

df = load_data()
st.title("💎 Customer Lifetime Value")
st.caption("Predicts how much each customer will spend over the next 12 months, so you know who deserves your effort.")

m = M.customer_models(df, 90)
s, cv = m["scores"], m["clv"]
s = s.assign(tier=np.select([s.clv_12m >= s.clv_12m.quantile(.9), s.clv_12m >= s.clv_12m.quantile(.7)],
                            ["VIP (top 10%)", "Gold (next 20%)"], "Standard"))

top20 = s.monetary.sort_values(ascending=False).head(int(len(s) * .2)).sum() / s.monetary.sum()
c = st.columns(3)
c[0].metric("Predicted 12-month value (all customers)", f"£{s.clv_12m.sum():,.0f}")
c[1].metric("Top 20% of customers = ", f"{top20:.0%} of revenue", help="Pareto / 80-20 rule")
c[2].metric("Model error (MAE, 90 days)", f"£{cv['mae']:,.0f}")

tiers = s.groupby("tier").agg(Customers=("clv_12m", "size"), AvgCLV=("clv_12m", "mean"), TotalCLV=("clv_12m", "sum")).round(0)
st.dataframe(tiers, width="stretch")
st.plotly_chart(px.histogram(s[s.clv_12m > 0], x="clv_12m", nbins=40, log_y=True, color="tier",
                             title="Predicted 12-month value per customer"), width="stretch")

st.subheader("Top 20 customers by predicted value")
top = s.sort_values("clv_12m", ascending=False).head(20)[["frequency", "monetary", "recency", "clv_12m"]].round(0)
st.dataframe(top.rename(columns={"frequency": "Orders", "monetary": "Spent so far £", "recency": "Days since order",
                                 "clv_12m": "Predicted 12m £"}), width="stretch")
st.caption("Method: Gradient Boosting predicts spend in the next 90 days from past behaviour; ×365/90 gives the "
           "12-month estimate. Estimate only, since the data covers just one year.")

chat_panel("Customer lifetime value model:\n" + tiers.to_string() + f"\nTop 20% of customers = {top20:.0%} of revenue.\n"
           "Top customers:\n" + top.head(8).to_string())
