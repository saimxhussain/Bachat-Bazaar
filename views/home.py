import plotly.express as px
import streamlit as st

from core import models as M
from core.data import load_data
from core.llm import ask, chat_panel

df = load_data()
names = M.product_names(df)

st.title("🛒 Store Sales Agent")
st.caption("From forecast to promotion: 7 ML tools that cover the whole sales funnel.")

c = st.columns(4)
c[0].metric("Revenue", f"£{df.Revenue.sum():,.0f}")
c[1].metric("Orders", f"{df.InvoiceNo.nunique():,}")
c[2].metric("Customers", f"{df.CustomerID.nunique():,}")
c[3].metric("Products", f"{df.StockCode.nunique():,}")

monthly = df.groupby(df.Date.dt.to_period("M").astype(str)).Revenue.sum().reset_index()
st.plotly_chart(px.bar(monthly, x="Date", y="Revenue", title="Monthly revenue"), width="stretch")

st.markdown("""
| Funnel stage | Tool | ML method |
|---|---|---|
| Plan | 📈 Sales Forecast | Gradient Boosting (time series) |
| Understand | 👥 Customer Segments | RFM + K-Means |
| Sell more | 🛍️ Recommendations | Market-basket (lift) |
| Retain | ⚠️ Churn Risk | Random Forest |
| Grow | 💎 Customer Value | Gradient Boosting regression |
| Supply | 📦 Stock Alerts | Trend demand forecast + safety stock |
| Convert | 🏷️ Promotions | Price elasticity regression |
""")


def full_context():
    f = M.sales_forecast(df, 14)
    last = f["history"].iloc[-14:].sum()
    seg = M.rfm_segments(df, 4)["summary"][["Customers", "AvgSpend", "RevenueShare"]]
    s = M.customer_models(df, 90)["scores"]
    risk = s.sort_values("value_at_risk", ascending=False).head(5)[["recency", "monetary", "churn_prob"]].round(2)
    dem = M.product_demand(df)
    plan = M.reorder_plan(dem, M.demo_stock(dem))
    alerts = plan[plan.status != "OK"].sort_values("days_cover").head(6)
    alerts = alerts.assign(product=[names[i] for i in alerts.index])[["product", "days_cover", "order_qty", "status"]]
    pairs = M.top_pairs(M.basket_model(df), names, 4)
    el, _ = M.price_elasticity(df)
    promo = M.promo_plan(el).sort_values("revenue_gain", ascending=False).head(4)
    promo = promo.assign(product=[names[i] for i in promo.index])[["product", "discount", "unit_lift", "revenue_gain"]].round(2)
    return (f"Next 14 days forecast revenue: £{f['forecast'].sum():,.0f} (last 14 days: £{last:,.0f}).\n"
            f"Segments:\n{seg.to_string()}\nHighest value-at-risk customers (churn probability):\n{risk.to_string()}\n"
            f"Stock alerts (demo stock):\n{alerts.to_string()}\nBundle ideas:\n{pairs.to_string(index=False)}\n"
            f"Best promotions (weekly £ gain):\n{promo.to_string(index=False)}")


if st.button("✨ Generate this week's action plan", type="primary"):
    with st.spinner("Running all models and asking the AI..."):
        ctx = full_context()
        st.session_state["ctx_home"] = ctx
        st.session_state["plan"] = ask([{"role": "user", "content":
            "Write this week's action plan for the owner: 5 prioritized actions covering forecast, "
            "VIP/at-risk customers, bundles, restocking and promotions. Use the numbers."}], ctx)
if "plan" in st.session_state:
    st.markdown(st.session_state["plan"])

chat_panel(st.session_state.get("ctx_home", f"Store totals: revenue £{df.Revenue.sum():,.0f}, "
                                              f"{df.CustomerID.nunique()} customers. Press the action-plan button for full model output."))
