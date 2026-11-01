import streamlit as st

from core import models as M
from core import theme
from core.data import load_data
from core.llm import chat_panel

df = load_data()
names = M.product_names(df)
model = M.basket_model(df)

theme.header("recommend", "Product Recommendations", "Market-basket analysis: what do customers buy together? Use it for bundles and cross-sell.")

pairs = M.top_pairs(model, names, 15)
st.subheader("Top bundle ideas")
st.dataframe(pairs.assign(Lift=pairs.Lift.round(1)), width="stretch", hide_index=True)
st.caption("Lift = how many times more likely two products are bought together than by chance.")

st.subheader("Cross-sell for one product")
options = {f"{names[c]} ({c})": c for c in model["codes"]}
pick = st.selectbox("Product", list(options), index=0)
rec = M.recommend(model, names, options[pick], k=8)
st.dataframe(rec.assign(Confidence=(rec.Confidence * 100).round(1).astype(str) + "%", Lift=rec.Lift.round(1)),
             width="stretch", hide_index=True)
if len(rec):
    st.info(f"Tip: when someone adds **{pick.split(' (')[0]}**, suggest **{rec.iloc[0].Product}** "
            f"({rec.iloc[0].Confidence:.0%} of buyers also bought it).")

chat_panel("Top product pairs bought together:\n" + pairs.head(8).round(1).to_string(index=False)
           + f"\nSelected product {pick}; recommendations:\n" + rec.round(2).to_string(index=False))
