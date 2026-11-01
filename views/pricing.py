import numpy as np
import plotly.graph_objects as go
import streamlit as st

from core import models as M
from core.data import load_data
from core.llm import chat_panel

df = load_data()
names = M.product_names(df)
el, pooled = M.price_elasticity(df)

st.title("🏷️ Promotions")
st.caption("Estimates how sensitive each product is to price, then finds discounts that grow sales without wrecking profit.")

c = st.columns(2)
cost = c[0].slider("Cost as % of price", 30, 85, 55, help="Your dataset has no costs, so set your typical margin here.") / 100
tol = c[1].slider("Profit I'm willing to give up for growth", 0, 30, 10, help="0% = discounts must not reduce profit") / 100

plan = M.promo_plan(el, cost, tol)
plan.insert(0, "Product", [names[i] for i in plan.index])
act = plan[plan.discount > 0]

m = st.columns(3)
m[0].metric("Products worth discounting", f"{len(act)} / {len(plan)}")
m[1].metric("Extra revenue / week", f"£{act.revenue_gain.sum():,.0f}")
m[2].metric("Profit change / week", f"£{act.profit_change.sum():,.0f}")

st.subheader("Best promotions")
show = act.sort_values("revenue_gain", ascending=False).head(20)[["Product", "price", "elasticity", "discount",
                                                                 "unit_lift", "revenue_gain", "profit_change"]]
st.dataframe(show.assign(discount=(show.discount * 100).round().astype(int).astype(str) + "%",
                         unit_lift=(show.unit_lift * 100).round().astype(int).astype(str) + "%").round(2),
             width="stretch", hide_index=True)

st.subheader("Try one product")
pick = st.selectbox("Product", list(plan.index), format_func=lambda i: f"{names[i]} ({i})")
row = el.loc[pick]
d = np.linspace(0, 0.3, 31)
u, rev, prof = M.simulate(row.price, row.weekly_units, row.elasticity, cost, d)
fig = go.Figure()
fig.add_scatter(x=d * 100, y=rev, name="Revenue £/week")
fig.add_scatter(x=d * 100, y=prof, name="Profit £/week")
fig.update_layout(xaxis_title="Discount %", title=f"Elasticity {row.elasticity:.2f} ({row.source})", legend=dict(orientation="h"))
st.plotly_chart(fig, width="stretch")

st.caption("Elasticity comes from log-log regression of weekly units on weekly price (retail-sized sales only), "
           "shrunk toward the store-wide estimate. It is observational, so treat results as ideas to test, not guarantees.")

chat_panel(f"Promotion planner (cost {cost:.0%} of price, profit tolerance {tol:.0%}). Store-wide elasticity {pooled:.2f}.\n"
           + show.head(8).round(2).to_string(index=False))
