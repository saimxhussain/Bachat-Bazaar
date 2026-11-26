import hashlib
import hmac

import streamlit as st

def _h(p: str) -> str:
    return hashlib.sha256(p.encode()).hexdigest()

# username -> sha256(password). To add a user: USERS["name"] = _h("password")
USERS = {
    "imtiaz_001": "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918",  # admin
}


def require_login():
    if st.session_state.get("user"):
        with st.sidebar:
            st.caption(f"Logged in as **{st.session_state['user']}**")
            if st.button("Log out", use_container_width=True):
                st.session_state.clear()
                st.rerun()
        return

    _, c, _ = st.columns([1, 1.4, 1])
    with c:
        st.title("🛍️ Bachat Bazaar")
        st.caption("Sign in to continue")
        with st.form("login"):
            u = st.text_input("Email / Username")
            p = st.text_input("Password", type="password")
            ok = st.form_submit_button("Log in", use_container_width=True)
        if ok:
            key = u.strip().lower()
            stored = USERS.get(key)
            if stored and hmac.compare_digest(stored, _h(p)):
                st.session_state["user"] = key
                st.rerun()
            else:
                st.error("Wrong email or password.")
    st.stop()
