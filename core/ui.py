"""RetailIQ page components: top bar + search, KPI cards, tables, quick actions, action plan."""
import os
from datetime import datetime
from html import escape

import pandas as pd
import streamlit as st

from core import images
from core import models as M
from core.theme import icon


# ───────────── helpers ─────────────
def owner() -> str:
    try:
        v = st.secrets.get("OWNER_NAME", "")
    except Exception:
        v = ""
    return v or os.getenv("OWNER_NAME") or "Hussain"


def greeting() -> str:
    try:
        from zoneinfo import ZoneInfo
        h = datetime.now(ZoneInfo(os.getenv("OWNER_TZ", "Asia/Karachi"))).hour
    except Exception:
        h = datetime.now().hour
    return "Good morning" if h < 12 else "Good afternoon" if h < 18 else "Good evening"


def money(v: float) -> str:
    if abs(v) >= 1e6:
        return f"£{v / 1e6:,.2f}M"
    return f"£{v:,.0f}"


def pct_change(cur: float, prev: float):
    return None if not prev else cur / prev - 1


def spark(vals, w=130, h=46, pad=3) -> str:
    """Smooth sparkline: faded area + line, coloured by the parent's --c."""
    v = [float(x) for x in vals] or [0.0]
    if len(v) < 2:
        v = v * 2
    lo, hi = min(v), max(v)
    rng = (hi - lo) or 1.0
    pts = [(pad + i * (w - 2 * pad) / (len(v) - 1), h - pad - (x - lo) / rng * (h - 2 * pad)) for i, x in enumerate(v)]
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(len(pts) - 1):
        p0 = pts[i - 1] if i else pts[i]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < len(pts) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    area = d + f" L{pts[-1][0]:.1f},{h} L{pts[0][0]:.1f},{h} Z"
    return (f'<div class="spark"><svg class="a" viewBox="0 0 {w} {h}" preserveAspectRatio="none"><path d="{area}"/></svg>'
            f'<svg class="l" viewBox="0 0 {w} {h}" preserveAspectRatio="none"><path d="{d}"/></svg></div>')


def _chip(p) -> str:
    if p is None:
        return '<span class="chip flat">–</span>'
    cls, arrow = ("up", "↑") if p >= 0 else ("down", "↓")
    return f'<span class="chip {cls}">{arrow} {abs(p) * 100:.1f}%</span>'


def _img(url: str) -> str:
    inner = icon("box")
    if url:
        inner += f'<img src="{escape(url, quote=True)}" alt="" loading="lazy" referrerpolicy="no-referrer">'
    return f'<div class="im">{inner}</div>'


# ───────────── top bar + search ─────────────
def topbar(df: pd.DataFrame):
    c = st.columns([5, 1.6], vertical_alignment="center")
    q = c[0].text_input("Search", placeholder="Search products, customers, orders…", key="bz_search",
                        label_visibility="collapsed")
    name = owner()
    c[1].html(f'<div class="bz-user"><div class="av">{escape(name[:1].upper())}</div>{escape(name)}</div>')
    if q and q.strip():
        _search_results(df, q.strip())


def _search_results(df: pd.DataFrame, q: str):
    names = M.product_names(df)
    rev = df.groupby("StockCode").Revenue.sum()
    hits = names[names.str.lower().str.contains(q.lower(), regex=False)]
    top = rev.reindex(hits.index).dropna().nlargest(4)
    html = ""
    if len(top):
        pics = images.lookup_many(tuple(names[c] for c in top.index))
        rows = "".join(f'<div class="r">{_img(pics.get(names[c], ""))}<b>{escape(names[c])}</b>'
                       f'<span class="sp">{money(v)} revenue</span></div>' for c, v in top.items())
        html += f"<h5>Products</h5>{rows}"
    digits = q.lstrip("#").strip()
    if digits.isdigit():
        inv = (df[df.InvoiceNo.str.startswith(digits)].groupby("InvoiceNo")
               .agg(total=("Revenue", "sum"), when=("InvoiceDate", "max"), country=("Country", "first")).head(3))
        if len(inv):
            rows = "".join(f'<div class="r"><b>#{escape(i)}</b><span class="pill">{escape(r.country)}</span>'
                           f'<span class="sp">{money(r.total)} · {r.when:%d %b %Y}</span></div>' for i, r in inv.iterrows())
            html += f"<h5>Orders</h5>{rows}"
        cust = df[df.CustomerID == int(digits)] if len(digits) <= 9 else df.iloc[0:0]
        if len(cust):
            html += (f'<h5>Customer</h5><div class="r"><b>Customer {digits}</b><span class="pill">{escape(cust.Country.iat[0])}</span>'
                     f'<span class="sp">{cust.InvoiceNo.nunique()} orders · {money(cust.Revenue.sum())} spent</span></div>')
    if not html:
        html = f'<div class="r">No matches for “{escape(q)}”. Try a product name, an order number or a customer ID.</div>'
    with st.container(key="card-search"):
        st.html(f'<div class="bz-sr">{html}</div>')


# ───────────── home components ─────────────
def hello(period_text: str):
    st.html(f'<div class="bz-hello"><small>{greeting()},</small><h1>Welcome back, {escape(owner())} 👋</h1>'
            f'<p>Here’s what’s happening with your store {escape(period_text)}.</p></div>')


def kpi(label: str, value: str, pct, vs: str, ic: str, tint: str, series):
    st.html(f'<div class="bz-kpi t-{tint}"><div class="top"><span class="bz-ki">{icon(ic)}</span>{escape(label)}</div>'
            f'<div class="val">{escape(value)}</div><div class="delta">{_chip(pct)}<span>{escape(vs)}</span></div>'
            f'{spark(series)}</div>')


def card_head(title: str, sub: str, ic: str = ""):
    lead = f'<div class="row">{icon(ic)}<h3>{escape(title)}</h3></div>' if ic else f"<h3>{escape(title)}</h3>"
    return f'<div class="bz-ch">{lead}<p>{escape(sub)}</p></div>'


def top_products(rows: list, note: str):
    """rows: dict(rank, name, code, units, revenue, stock, trend_pct, series, img)."""
    stock_cls = {"In stock": "st-ok", "Low stock": "st-low", "Stock-out risk": "st-out"}
    out = ('<div class="bz-tw"><div class="bz-t"><div class="tr th"><span>#</span><span>Product</span><span>Sales</span>'
           '<span>Revenue</span><span>Stock</span><span>Trend</span></div>')
    for r in rows:
        tp = r["trend_pct"]
        trend = ("new" if tp is None else
                 f'<span class="{"up-t" if tp >= 0 else "down-t"}">{"↑" if tp >= 0 else "↓"} {abs(tp) * 100:.0f}%</span>')
        st_txt = r["stock"] or "–"
        out += (f'<div class="tr"><span>{r["rank"]}</span>'
                f'<div class="bz-p">{_img(r["img"])}<div><b title="{escape(r["name"], quote=True)}">{escape(r["name"])}</b>'
                f'<span class="s">Code {escape(str(r["code"]))}</span></div></div>'
                f'<span>{r["units"]:,.0f}</span><span>{money(r["revenue"])}</span>'
                f'<span class="{stock_cls.get(r["stock"], "st-na")}"><i class="dot"></i>{escape(st_txt)}</span>'
                f'<div class="tc t-green" style="--c:{"#16A34A" if (tp or 0) >= 0 else "#DC2626"}">{spark(r["series"], 56, 24, 2)}{trend}</div></div>')
    out += f'</div></div><p class="bz-note">{escape(note)}</p>'
    st.html(out)


def recent_orders(orders: pd.DataFrame):
    out = '<div class="bz-o">'
    for inv, r in orders.iterrows():
        out += (f'<div class="tr"><span class="id">#{escape(str(inv))}</span><span>{money(r.total)}</span>'
                f'<span><span class="pill">{escape(str(r.country))}</span></span>'
                f'<span class="when">{r.when:%d %b, %H:%M}</span></div>')
    st.html(out + "</div>")


def link_rows(items: list, prefix: str):
    """Quick-action rows. items: (key, icon, title, subtitle, page path)."""
    for key, ic, title, sub, path in items:
        with st.container(key=f"{prefix}-{key}"):
            st.html(f'<div class="bz-qa">{icon(ic)}<div><b>{escape(title)}</b><span class="s">{escape(sub)}</span></div>'
                    f'<span class="go">{icon("chevron")}</span></div>')
            st.page_link(path, label=title)


def plan_rows(items: list):
    """Action-plan rows. items: (key, title, subtitle, priority 'High'|'Medium', page path)."""
    for n, (key, title, sub, prio, path) in enumerate(items, 1):
        with st.container(key=f"ap-{key}"):
            st.html(f'<div class="bz-ap"><span class="n">{n}</span><div><b>{escape(title)}</b><span class="s">{escape(sub)}</span></div>'
                    f'<span class="pill {"high" if prio == "High" else "med"}" style="margin-left:auto">{prio}</span>'
                    f'<span class="go">{icon("chevron")}</span></div>')
            st.page_link(path, label=title)
