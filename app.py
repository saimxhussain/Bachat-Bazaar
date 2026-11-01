import streamlit as st

st.set_page_config(page_title="Store Sales Agent", page_icon="🛒", layout="wide")

nav = st.navigation([
    st.Page("views/home.py", title="Home", icon="🏠", default=True),
    st.Page("views/forecast.py", title="Sales Forecast", icon="📈"),
    st.Page("views/segments.py", title="Customer Segments", icon="👥"),
    st.Page("views/recommend.py", title="Recommendations", icon="🛍️"),
    st.Page("views/churn.py", title="Churn Risk", icon="⚠️"),
    st.Page("views/clv.py", title="Customer Value", icon="💎"),
    st.Page("views/stock.py", title="Stock Alerts", icon="📦"),
    st.Page("views/pricing.py", title="Promotions", icon="🏷️"),
])
nav.run()
