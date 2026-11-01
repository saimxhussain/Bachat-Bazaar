import plotly.express as px
import streamlit as st

from core import models as M
from core.data import load_data
from core.llm import chat_panel

df = load_data()
st.title("👥 Customer Segments")
st.caption("Groups customers by Recency, Frequency and Monetary value (RFM) using K-Means.")

k = st.slider("Number of segments", 3, 5, 4)
r = M.rfm_segments(df, k)
rfm, summ = r["rfm"], r["summary"]

c = st.columns(2)
c[0].metric("Customers", f"{len(rfm):,}")
c[1].metric("Cluster quality (silhouette)", f"{r['silhouette']:.2f}")

st.dataframe(summ.rename(columns={"AvgSpend": "Avg spend £", "Revenue": "Revenue £", "RevenueShare": "Revenue %",
                                  "Recency": "Days since last order"}), width="stretch")

col = st.columns(2)
col[0].plotly_chart(px.pie(summ.reset_index(), names="Segment", values="Revenue", title="Revenue by segment"),
                    width="stretch")
col[1].plotly_chart(px.line(x=list(r["inertia"]), y=list(r["inertia"].values()), markers=True,
                            labels={"x": "k", "y": "Inertia"}, title="Elbow chart"), width="stretch")

st.plotly_chart(px.scatter(rfm.reset_index(), x="Recency", y="Monetary", color="Segment", log_y=True,
                           hover_data=["CustomerID", "Frequency"], title="Customers: recency vs spend"),
                width="stretch")

st.subheader("What to do with each segment")
actions = {"Champions": "Reward with early access / thank-you gifts. Never discount, they buy anyway.",
           "Loyal": "Upsell bundles and bigger baskets; nudge them toward Champion level.",
           "Promising": "Welcome offers and second-purchase incentives.",
           "At risk": "Win-back message with a modest discount before they leave.",
           "Lost": "Cheap reactivation (email/SMS) only, low expected return."}
for s in summ.index:
    st.markdown(f"- **{s}:** {actions[s]}")

chat_panel("Customer segments (RFM + KMeans):\n" + summ.to_string())
