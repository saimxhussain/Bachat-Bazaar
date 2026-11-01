import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core import images, ui
from core import models as M
from core.data import load_data
from core.llm import ask, chat_panel

df = load_data()
names = M.product_names(df)
END = df.Date.max()

# ── greeting + period picker ─────────────────────────────────────────────
left, right = st.columns([3, 1.15], vertical_alignment="bottom")
with right:
    days = st.selectbox("Period", [7, 30, 90], key="period", label_visibility="collapsed",
                        format_func=lambda d: f"{END - pd.Timedelta(days=d - 1):%b %d, %Y} – {END:%b %d, %Y}")
with left:
    ui.hello("this week" if days == 7 else f"in the last {days} days")

START = END - pd.Timedelta(days=days - 1)
cur = df[df.Date >= START]
prev = df[(df.Date >= START - pd.Timedelta(days=days)) & (df.Date < START)]
daily = cur.groupby("Date").agg(Revenue=("Revenue", "sum"), Orders=("InvoiceNo", "nunique"),
                                Customers=("CustomerID", "nunique"), Units=("Quantity", "sum"))
vs = f"vs. previous {days} days"

main, side = st.columns([3.1, 1.15], gap="large")

with main:
    # ── KPI cards ────────────────────────────────────────────────────────
    k = st.columns(4)
    with k[0]:
        ui.kpi("Total Revenue", ui.money(cur.Revenue.sum()), ui.pct_change(cur.Revenue.sum(), prev.Revenue.sum()),
               vs, "wallet", "green", daily.Revenue)
    with k[1]:
        ui.kpi("Total Orders", f"{cur.InvoiceNo.nunique():,}", ui.pct_change(cur.InvoiceNo.nunique(), prev.InvoiceNo.nunique()),
               vs, "cart", "blue", daily.Orders)
    with k[2]:
        ui.kpi("Customers", f"{cur.CustomerID.nunique():,}", ui.pct_change(cur.CustomerID.nunique(), prev.CustomerID.nunique()),
               vs, "users", "purple", daily.Customers)
    with k[3]:
        ui.kpi("Products Sold", f"{cur.Quantity.sum():,.0f}", ui.pct_change(cur.Quantity.sum(), prev.Quantity.sum()),
               vs, "box", "orange", daily.Units)

    # ── revenue overview ─────────────────────────────────────────────────
    with st.container(key="card-revenue"):
        h1, h2, h3 = st.columns([1.7, 1.9, 1], vertical_alignment="center")
        h1.html(ui.card_head("Revenue Overview", "Daily revenue performance for the selected period."))
        metric = h2.segmented_control("Metric", ["Revenue", "Orders", "Customers"], default="Revenue",
                                      key="rev_metric", label_visibility="collapsed") or "Revenue"
        gran = h3.selectbox("Granularity", ["Daily", "Weekly", "Monthly"], key="rev_gran", label_visibility="collapsed")
        freq = {"Daily": "D", "Weekly": "W", "Monthly": "MS"}[gran]
        col = {"Revenue": ("Revenue", "sum"), "Orders": ("InvoiceNo", "nunique"), "Customers": ("CustomerID", "nunique")}[metric]
        series = cur.groupby(pd.Grouper(key="Date", freq=freq))[col[0]].agg(col[1])
        series = series[series > 0]
        fmt = "£%{y:,.0f}" if metric == "Revenue" else "%{y:,.0f}"
        fig = go.Figure(go.Scatter(
            x=series.index, y=series.values, mode="lines", line=dict(color="#3B63F5", width=2.6, shape="spline", smoothing=1),
            fill="tozeroy", fillcolor="rgba(59,99,245,.13)",
            hovertemplate="%{x|%b %d, %Y}<br><b>" + fmt + "</b><extra></extra>"))
        fig.update_layout(template="bazaar", height=300, margin=dict(l=0, r=0, t=6, b=0), showlegend=False,
                          paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF", font=dict(color="#374151"))
        fig.update_xaxes(showgrid=False, tickformat="%b %d")
        fig.update_yaxes(gridcolor="#EEF0F6", rangemode="tozero", tickprefix="£" if metric == "Revenue" else "", tickformat="~s")
        st.plotly_chart(fig, width="stretch")

    # ── top products + recent orders ─────────────────────────────────────
    dem = M.product_demand(df)
    plan = M.reorder_plan(dem, M.demo_stock(dem))
    label = {"OK": "In stock", "Reorder now": "Low stock", "Stock-out risk": "Stock-out risk"}
    agg = cur.groupby("StockCode").agg(revenue=("Revenue", "sum"), units=("Quantity", "sum")).nlargest(5, "revenue")
    prev_units = prev.groupby("StockCode").Quantity.sum()
    pics = images.lookup_many(tuple(names[c] for c in agg.index))
    rows = []
    for i, (code, r) in enumerate(agg.iterrows(), 1):
        pu = prev_units.get(code, 0)
        rows.append(dict(rank=i, name=names[code], code=code, units=r.units, revenue=r.revenue,
                         stock=label.get(plan.status.get(code)), trend_pct=ui.pct_change(r.units, pu),
                         series=cur[cur.StockCode == code].groupby("Date").Revenue.sum().values, img=pics.get(names[code], "")))
    a, b = st.columns([1.6, 1])
    with a.container(key="card-top"):
        st.html(ui.card_head("Top Products", "Best performing products in this period.", "box"))
        ui.top_products(rows, "Stock levels are simulated until you upload your own on the Stock Alerts page. "
                              "Product photos are matched from the web by name and may not be exact.")
    with b.container(key="card-orders"):
        st.html(ui.card_head("Recent Orders", "Latest customer orders.", "file"))
        orders = (df.groupby("InvoiceNo").agg(total=("Revenue", "sum"), when=("InvoiceDate", "max"), country=("Country", "first"))
                  .sort_values("when", ascending=False).head(5))
        ui.recent_orders(orders)

with side:
    with st.container(key="card-quick"):
        st.html(ui.card_head("Quick Actions", "Jump straight to the job."))
        ui.link_rows([
            ("promo", "tag", "Create Promotion", "Boost your sales", "views/pricing.py"),
            ("stock", "box", "Check Stock", "Avoid stock-outs", "views/stock.py"),
            ("forecast", "forecast", "Sales Forecast", "Plan the next weeks", "views/forecast.py"),
            ("churn", "alert", "Win Back Customers", "See who may leave", "views/churn.py"),
        ], "qa")
    n_alert = int((plan.status != "OK").sum())
    with st.container(key="card-plan"):
        st.html(ui.card_head("This Week’s Action Plan", "3 high-impact actions to grow revenue.", "sparkle"))
        ui.plan_rows([
            ("stock", "Restock top-selling items", f"{n_alert} of your {len(plan)} best sellers need attention", "High", "views/stock.py"),
            ("promo", "Launch a targeted promotion", "Price-tested discounts for best sellers", "Medium", "views/pricing.py"),
            ("churn", "Review at-risk customers (churn)", "See who is about to stop buying", "Medium", "views/churn.py"),
        ])

# ── AI advisor ───────────────────────────────────────────────────────────
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


with st.container(key="card-ai"):
    st.html(ui.card_head("AI Advisor", "Press the button for a full plan, or ask your own question below.", "sparkle"))
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
