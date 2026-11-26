import hashlib
import hmac

import streamlit as st


def _h(p: str) -> str:
    return hashlib.sha256(p.encode()).hexdigest()


# username -> sha256(password). To add a user: USERS["name"] = _h("password")
USERS = {
    "imtiaz_001": "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918",  # admin
}

YELLOW = "#FDB913"

CSS = f"""
<style>
header[data-testid="stHeader"], [data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"], footer {{ display:none !important; }}

.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {{
    background: linear-gradient({YELLOW} 0, {YELLOW} 300px, #ffffff 300px) !important;
}}
.block-container {{ max-width: 420px !important; padding-top: 3rem !important; }}

.login-head h1 {{ color:#000 !important; font-size:2.2rem; font-weight:800; margin:0 0 .4rem 0; padding:0; }}
.login-head p  {{ color:#000 !important; font-size:.9rem; font-weight:500; margin:0 0 1.6rem 0; line-height:1.4; }}

[data-testid="stForm"] {{
    background:#fff !important; border:none !important; border-radius:32px !important;
    padding:28px 22px 24px 22px !important; box-shadow:0 10px 30px rgba(0,0,0,.12) !important;
}}
[data-testid="stForm"] label p {{ color:#555 !important; font-size:.8rem !important; font-weight:600 !important; }}
[data-testid="stForm"] [data-baseweb="input"],
[data-testid="stForm"] [data-baseweb="base-input"] {{
    background:#F4F4F4 !important; border:none !important; border-radius:999px !important;
}}
[data-testid="stForm"] input {{
    background:#F4F4F4 !important; color:#000 !important; border-radius:999px !important;
    padding:14px 20px !important;
}}
[data-testid="stForm"] [data-testid="stFormSubmitButton"] button {{
    width:100%; background:#000 !important; color:#fff !important; border:none !important;
    border-radius:999px !important; padding:14px 0 !important; font-weight:700 !important;
    margin-top:.6rem;
}}
[data-testid="stForm"] [data-testid="stFormSubmitButton"] button:hover {{ background:#222 !important; }}
.login-foot {{ text-align:center; color:#888; font-size:.75rem; margin-top:1.2rem; }}
</style>
"""


def require_login():
    if st.session_state.get("user"):
        with st.sidebar:
            st.caption(f"Logged in as **{st.session_state['user']}**")
            if st.button("Log out", use_container_width=True):
                st.session_state.clear()
                st.rerun()
        return

    st.markdown(CSS, unsafe_allow_html=True)
    st.markdown(
        '<div class="login-head"><h1>Sign In</h1>'
        '<p>Welcome to Bachat Bazaar. Log in to see your store insights.</p></div>',
        unsafe_allow_html=True,
    )
    with st.form("login"):
        u = st.text_input("Username", placeholder="Username")
        p = st.text_input("Password", type="password", placeholder="Password")
        ok = st.form_submit_button("Sign In")
    st.markdown('<div class="login-foot">🛍️ Bachat Bazaar</div>', unsafe_allow_html=True)

    if ok:
        key = u.strip().lower()
        stored = USERS.get(key)
        if stored and hmac.compare_digest(stored, _h(p)):
            st.session_state["user"] = key
            st.rerun()
        else:
            st.error("Wrong username or password.")
    st.stop()
