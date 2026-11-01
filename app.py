import streamlit as st

from core import theme, ui
from core.data import load_data

st.set_page_config(page_title="Bachat Bazaar", page_icon="🛍️", layout="wide")

theme.apply()
ui.topbar(load_data())

nav = st.navigation([
    st.Page("views/home.py", title="Home", icon=":material/home:", default=True),
    st.Page("views/forecast.py", title="Sales Forecast", icon=":material/trending_up:"),
    st.Page("views/segments.py", title="Customer Segments", icon=":material/groups:"),
    st.Page("views/recommend.py", title="Recommendations", icon=":material/layers:"),
    st.Page("views/churn.py", title="Churn Risk", icon=":material/warning:"),
    st.Page("views/clv.py", title="Customer Value", icon=":material/diamond:"),
    st.Page("views/stock.py", title="Stock Alerts", icon=":material/inventory_2:"),
    st.Page("views/pricing.py", title="Promotions", icon=":material/sell:"),
])
nav.run()
