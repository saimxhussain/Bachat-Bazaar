import plotly.express as px
import streamlit as st

from core import models as M
from core import theme
from core.data import load_data
from core.llm import chat_panel

df = load_data()
theme.header("churn", "Churn Risk", "Which customers are about to stop buying, and how much money is at stake?")

horizon = st.radio("Churn = no purchase in the next…", [60, 90], index=1, horizontal=True, format_func=lambda d: f"{d} days")
m = M.customer_models(df, horizon)
s, cm = m["scores"], m["churn"]

c = st.columns(4)
c[0].metric("AUC", f"{cm['auc']:.2f}", help="1.0 = perfect, 0.5 = coin flip (tested on unseen customers)")
c[1].metric("Recall", f"{cm['recall']:.0%}", help="Share of real churners the model catches")
c[2].metric("Precision", f"{cm['precision']:.0%}")
c[3].metric("Base churn rate", f"{cm['base_rate']:.0%}")

thr = st.slider("Flag customers above churn probability", 0.3, 0.9, 0.6, 0.05)
risky = s[s.churn_prob >= thr].sort_values("value_at_risk", ascending=False)
st.metric("Customers flagged", f"{len(risky):,}", f"£{risky.value_at_risk.sum():,.0f} value at risk")

st.plotly_chart(px.histogram(s, x="churn_prob", nbins=30, title="Churn probability across all customers"),
                width="stretch")
st.subheader("Call these customers first")
show = risky.head(25)[["recency", "frequency", "monetary", "churn_prob", "value_at_risk"]].round(2)
st.dataframe(show.rename(columns={"recency": "Days since order", "frequency": "Orders", "monetary": "Spent £",
                                  "churn_prob": "Churn prob", "value_at_risk": "Value at risk £"}),
             width="stretch")
st.download_button("Download full at-risk list (CSV)", risky.round(2).to_csv().encode(), "at_risk_customers.csv")

st.plotly_chart(px.bar(m["importances"], orientation="h", title="What drives churn (feature importance)",
                       labels={"value": "importance", "index": ""}).update_layout(showlegend=False),
                width="stretch")

chat_panel(f"Churn model (Random Forest, {horizon}-day window): AUC {cm['auc']:.2f}, recall {cm['recall']:.0%}. "
           f"{len(risky)} customers above {thr:.0%} risk, £{risky.value_at_risk.sum():,.0f} value at risk.\n"
           "Top at-risk customers:\n" + show.head(8).to_string())
