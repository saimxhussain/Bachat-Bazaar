import plotly.graph_objects as go
import streamlit as st

from core import models as M
from core import theme
from core.data import load_data
from core.llm import chat_panel

df = load_data()
theme.header("forecast", "Sales Forecast", "Predicts daily revenue so you can plan staff, stock and promotions.")

horizon = st.slider("Days to forecast", 7, 30, 14)
r = M.sales_forecast(df, horizon)

c = st.columns(3)
c[0].metric("Forecast total", f"£{r['forecast'].sum():,.0f}")
c[1].metric("Test error (WAPE)", f"{r['wape']:.1%}", help="Error on the last 28 days, which the model never saw")
c[2].metric("Beats naive baseline by", f"{1 - r['mae'] / r['mae_naive']:.0%}",
            help="Naive = same weekday last week")

h = r["history"].iloc[-90:]
fig = go.Figure()
fig.add_scatter(x=h.index, y=h.values, name="Actual", line=dict(color="#C9C5F5"))
fig.add_scatter(x=r["backtest"].index, y=r["backtest"].predicted, name="Backtest (unseen)", line=dict(dash="dot"))
fig.add_scatter(x=r["forecast"].index, y=r["forecast"].values, name="Forecast", line=dict(width=3))
fig.update_layout(title="Daily revenue", yaxis_title="£", legend=dict(orientation="h"))
st.plotly_chart(fig, width="stretch")

f = r["forecast"]
st.write(f"**Best day:** {f.idxmax():%a %d %b} (£{f.max():,.0f}) · **Quietest trading day:** "
         f"{f[f > 5000].idxmin():%a %d %b} (£{f[f > 5000].min():,.0f})")
with st.expander("How it works"):
    st.write("Gradient Boosting on calendar features (weekday, month), lag-1/7/14 sales and rolling 7/28-day "
             "averages. Forecasts are made one day at a time, feeding each prediction back in.")

chat_panel(f"Revenue forecast next {horizon} days: £{f.sum():,.0f}. Daily: "
           + ", ".join(f"{d:%a %d %b} £{v:,.0f}" for d, v in f.items())
           + f". Last 28 days model error {r['wape']:.1%}.")
