"""Visual identity: deep-navy canvas, colourful glass icon tiles, Poppins type.

Call `theme.apply()` once from app.py. Pages use `theme.header(...)`;
the home page also uses `theme.hero(...)` and `theme.tile(...)`.
"""
from html import escape

import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

# ── palette ────────────────────────────────────────────────────────────────
NAVY, INDIGO = "#17134A", "#241F6B"
PALETTE = ["#FFA62B", "#3B9CFF", "#2BD576", "#A678FF", "#FF5D73", "#22D3EE", "#FFD166"]

# (light, deep) gradient pair per tint, used by the glass icons
TINTS = {
    "orange": ("#FFC24D", "#FF8A00"),
    "blue":   ("#6DB8FF", "#2F6BFF"),
    "green":  ("#5EEB9B", "#12B76A"),
    "purple": ("#C4A3FF", "#7C4DFF"),
    "coral":  ("#FF9AA8", "#F0405E"),
    "cyan":   ("#7DEBFA", "#0EA5C6"),
    "gold":   ("#FFE08A", "#F5B301"),
}

# Lucide-style 24px line icons (inner SVG markup only)
ICONS = {
    "home": '<circle cx="8" cy="21" r="1"/><circle cx="19" cy="21" r="1"/><path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12"/>',
    "forecast": '<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>',
    "segments": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "recommend": '<path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4Z"/><path d="M3 6h18"/><path d="M16 10a4 4 0 0 1-8 0"/>',
    "churn": '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
    "clv": '<path d="M6 3h12l4 6-10 13L2 9Z"/><path d="M11 3 8 9l4 13 4-13-3-6"/><path d="M2 9h20"/>',
    "stock": '<path d="m7.5 4.27 9 5.15"/><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/>',
    "pricing": '<path d="M12.586 2.586A2 2 0 0 0 11.172 2H4a2 2 0 0 0-2 2v7.172a2 2 0 0 0 .586 1.414l8.704 8.704a2.426 2.426 0 0 0 3.42 0l6.58-6.58a2.426 2.426 0 0 0 0-3.42z"/><circle cx="7.5" cy="7.5" r="1"/>',
}

# page key -> (icon, tint)
PAGES = {
    "home": ("home", "orange"), "forecast": ("forecast", "orange"), "segments": ("segments", "purple"),
    "recommend": ("recommend", "coral"), "churn": ("churn", "coral"), "clv": ("clv", "cyan"),
    "stock": ("stock", "green"), "pricing": ("pricing", "blue"),
}

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');

:root{--bz-text:#F4F2FF;--bz-muted:#B9B4E8;--bz-line:rgba(255,255,255,.16);--bz-glass:rgba(255,255,255,.08);
  --bz-orange:#FFA62B;--bz-ink:#17134A}

/* canvas: navy with soft colour orbs for the glass to refract */
.stApp{
  background:
    radial-gradient(52rem 38rem at 92% -8%, rgba(255,166,43,.30), transparent 62%),
    radial-gradient(46rem 40rem at -10% 18%, rgba(59,156,255,.32), transparent 62%),
    radial-gradient(44rem 34rem at 78% 108%, rgba(166,120,255,.34), transparent 62%),
    radial-gradient(34rem 26rem at 12% 100%, rgba(43,213,118,.16), transparent 62%),
    linear-gradient(160deg,#1B1750,#17134A) !important;
  background-attachment:fixed !important;
}
.stApp, .stApp :is(p,li,label,h1,h2,h3,h4,h5,h6,button,input,textarea,a,td,th,
  [data-testid="stMetricValue"],[data-testid="stMetricLabel"]){
  font-family:'Poppins','Segoe UI',system-ui,sans-serif !important;
}
[data-testid="stHeader"]{background:transparent !important}
div[data-testid="stElementContainer"]:has(> style), div[data-testid="stElementContainer"]:has(> div > style){display:none}
.block-container{max-width:1120px;padding-top:2.2rem}
@media (max-width:640px){.block-container{padding:1.4rem .9rem 6rem}}

h1,h2,h3{letter-spacing:-.01em;font-weight:700 !important}
h2,h3{margin-top:.6rem}
[data-testid="stCaptionContainer"]{color:var(--bz-muted)}

/* sidebar */
[data-testid="stSidebar"]{background:rgba(255,255,255,.05) !important;
  -webkit-backdrop-filter:blur(22px) saturate(160%);backdrop-filter:blur(22px) saturate(160%);
  border-right:1px solid var(--bz-line)}
[data-testid="stSidebarNavLink"]{border-radius:16px !important;margin:2px 0;font-weight:500}
[data-testid="stSidebarNavLink"][aria-current="page"]{
  background:linear-gradient(135deg,rgba(255,166,43,.30),rgba(255,255,255,.10)) !important;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.35)}

/* glass surfaces */
[data-testid="stMetric"],[data-testid="stExpander"],[data-testid="stPlotlyChart"],
[data-testid="stChatMessage"],[data-testid="stAlert"],[data-testid="stFileUploader"] section{
  background:linear-gradient(155deg,rgba(255,255,255,.13),rgba(255,255,255,.05)) !important;
  border:1px solid var(--bz-line) !important;border-radius:24px !important;
  -webkit-backdrop-filter:blur(16px) saturate(150%);backdrop-filter:blur(16px) saturate(150%);
  box-shadow:inset 0 1px 0 rgba(255,255,255,.28),0 18px 40px -22px rgba(0,0,0,.55)}
[data-testid="stMetric"]{padding:1rem 1.2rem}
[data-testid="stMetricValue"]{font-weight:700 !important}
[data-testid="stMetricLabel"]{color:var(--bz-muted)}
[data-testid="stPlotlyChart"]{padding:.5rem .6rem;overflow:hidden}
[data-testid="stExpander"] details{border:none !important;background:transparent !important}
[data-testid="stDataFrame"]{border-radius:20px;overflow:hidden;border:1px solid var(--bz-line)}

/* inputs */
[data-baseweb="input"],[data-baseweb="select"] > div,[data-testid="stChatInput"] > div{
  border-radius:16px !important;background:rgba(255,255,255,.08) !important;border-color:var(--bz-line) !important}

/* buttons: orange pill for the main action, glass for the rest */
.stButton > button,.stDownloadButton > button{
  border-radius:999px;padding:.55rem 1.4rem;font-weight:600;border:1px solid var(--bz-line);
  background:rgba(255,255,255,.10);color:var(--bz-text);transition:transform .15s ease}
.stButton > button:hover,.stDownloadButton > button:hover{transform:translateY(-1px);border-color:rgba(255,255,255,.4)}
.stButton > button[kind="primary"]{
  background:linear-gradient(135deg,#FFC24D,#FF8A00);color:var(--bz-ink);border:none;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.6),0 12px 26px -10px rgba(255,138,0,.7)}
.stButton > button:focus-visible,.stDownloadButton > button:focus-visible,[data-testid="stPageLink"] a:focus-visible{
  outline:3px solid #fff;outline-offset:2px}

/* ── glass / liquid icon ─────────────────────────────────────────────── */
.bz-gi{position:relative;width:var(--s,60px);height:var(--s,60px);flex:none}
.bz-gi .orb{position:absolute;inset:8% 20% 20% 8%;border-radius:50%;
  background:radial-gradient(circle at 30% 30%,var(--c1),var(--c2));transform:translate(28%,26%);opacity:.95}
.bz-gi .glass{position:absolute;inset:0;border-radius:34%;display:grid;place-items:center;overflow:hidden;
  background:linear-gradient(145deg,rgba(255,255,255,.46),rgba(255,255,255,.08) 52%,rgba(255,255,255,.22));
  -webkit-backdrop-filter:blur(9px) saturate(190%);backdrop-filter:blur(9px) saturate(190%);
  border:1px solid rgba(255,255,255,.5);
  box-shadow:inset 0 1.5px 1px rgba(255,255,255,.75),inset 0 -10px 18px rgba(255,255,255,.10),
             inset 0 0 0 1px rgba(255,255,255,.06),0 14px 26px -10px var(--c2)}
.bz-gi .glass::after{content:"";position:absolute;left:10%;top:6%;width:58%;height:34%;border-radius:50%;
  background:linear-gradient(180deg,rgba(255,255,255,.7),rgba(255,255,255,0));filter:blur(1px)}
.bz-gi svg{position:relative;z-index:1;width:46%;height:46%;stroke:#fff;fill:none;stroke-width:1.9;
  stroke-linecap:round;stroke-linejoin:round;filter:drop-shadow(0 2px 3px rgba(0,0,0,.28))}

/* page header */
.bz-head{display:flex;align-items:center;gap:1.1rem;margin:.2rem 0 1.4rem}
.bz-head h1{margin:0;padding:0;font-size:clamp(1.55rem,4.6vw,2.2rem);line-height:1.15}
.bz-head p{margin:.25rem 0 0;color:var(--bz-muted);font-size:.98rem;max-width:60ch}

/* home hero */
.bz-hero{position:relative;overflow:hidden;border-radius:32px;padding:1.8rem 1.8rem 1.7rem;margin:.2rem 0 1.4rem;
  display:flex;justify-content:space-between;align-items:center;gap:1rem;
  background:linear-gradient(135deg,#3B6CFF 0%,#7C4DFF 100%);
  border:1px solid rgba(255,255,255,.35);
  box-shadow:inset 0 1.5px 1px rgba(255,255,255,.55),0 28px 50px -26px rgba(76,60,255,.9)}
.bz-hero h1{margin:.5rem 0 .3rem;font-size:clamp(1.8rem,5.4vw,2.7rem);line-height:1.1;color:#fff}
.bz-hero p{margin:0;color:rgba(255,255,255,.88);max-width:42ch}
.bz-hero .pill{display:inline-block;padding:.2rem .8rem;border-radius:999px;font-size:.8rem;font-weight:600;
  background:rgba(255,255,255,.2);border:1px solid rgba(255,255,255,.4)}
.bz-hero .cluster{display:flex;gap:.7rem;align-items:flex-end}
.bz-hero .cluster .bz-gi:nth-child(2){margin-bottom:1.4rem}
@media (max-width:640px){.bz-hero .cluster{display:none}}

/* tool tiles on the home page */
[class*="st-key-tile-"]{position:relative;border-radius:28px;padding:1.1rem 1.1rem .8rem;
  background:linear-gradient(155deg,rgba(255,255,255,.14),rgba(255,255,255,.05));
  border:1px solid var(--bz-line);
  -webkit-backdrop-filter:blur(16px) saturate(150%);backdrop-filter:blur(16px) saturate(150%);
  box-shadow:inset 0 1px 0 rgba(255,255,255,.3),0 20px 40px -24px rgba(0,0,0,.6);
  transition:transform .18s ease,border-color .18s ease}
[class*="st-key-tile-"]:hover{transform:translateY(-3px);border-color:rgba(255,255,255,.4)}
.bz-tile h4{margin:.9rem 0 .15rem;font-size:1.05rem;font-weight:600}
.bz-tile .stage{display:inline-block;font-size:.72rem;font-weight:600;padding:.1rem .6rem;border-radius:999px;
  background:rgba(255,255,255,.14);border:1px solid var(--bz-line);color:#fff}
.bz-tile p{margin:.45rem 0 .2rem;color:var(--bz-muted);font-size:.85rem;line-height:1.4}
[data-testid="stPageLink"] a{border-radius:999px;font-weight:600;color:#FFC24D;padding:.25rem .2rem}

@media (prefers-reduced-motion:reduce){*{transition:none !important}}
"""


def _plotly_template():
    t = go.layout.Template()
    axis = dict(gridcolor="rgba(255,255,255,.09)", zerolinecolor="rgba(255,255,255,.16)",
                linecolor="rgba(255,255,255,.22)")
    t.layout = go.Layout(
        font=dict(family="Poppins, Segoe UI, sans-serif", color="#EDEBFF"),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", colorway=PALETTE,
        xaxis=axis, yaxis=axis, legend=dict(bgcolor="rgba(0,0,0,0)"),
        title=dict(font=dict(size=16)), margin=dict(l=12, r=12, t=52, b=12),
        hoverlabel=dict(bgcolor="#2A2475", font=dict(color="#FFFFFF")))
    return t


def _patch_plotly():
    """Charts must use our template, not Streamlit's, so turn its theme override off by default."""
    from streamlit.delta_generator import DeltaGenerator
    if getattr(DeltaGenerator.plotly_chart, "_bazaar", False):
        return
    orig = DeltaGenerator.plotly_chart

    def wrapped(self, *a, **k):
        k.setdefault("theme", None)
        return orig(self, *a, **k)

    wrapped._bazaar = True
    DeltaGenerator.plotly_chart = wrapped
    st.plotly_chart = lambda *a, **k: wrapped(st._main, *a, **k)


def apply():
    """Inject CSS + chart template. Call once in app.py, after set_page_config."""
    pio.templates["bazaar"] = _plotly_template()
    pio.templates.default = "bazaar"
    try:
        _patch_plotly()
    except Exception:  # charts still work, just with Streamlit's default look
        pass
    st.html(f"<style>{CSS}</style>")


def glass_icon(icon: str, tint: str = "orange", size: int = 60) -> str:
    c1, c2 = TINTS[tint]
    return (f'<div class="bz-gi" style="--s:{size}px;--c1:{c1};--c2:{c2}"><div class="orb"></div>'
            f'<div class="glass"><svg viewBox="0 0 24 24" aria-hidden="true">{ICONS[icon]}</svg></div></div>')


def header(page: str, title: str, caption: str):
    icon, tint = PAGES[page]
    st.html(f'<div class="bz-head">{glass_icon(icon, tint, 64)}'
            f'<div><h1>{escape(title)}</h1><p>{escape(caption)}</p></div></div>')


def hero(pill: str, title: str, text: str):
    cluster = "".join(glass_icon(i, t, s) for i, t, s in
                      [("forecast", "orange", 66), ("segments", "purple", 56), ("stock", "green", 62)])
    st.html(f'<div class="bz-hero"><div><span class="pill">{escape(pill)}</span><h1>{escape(title)}</h1>'
            f'<p>{escape(text)}</p></div><div class="cluster">{cluster}</div></div>')


def tile(page: str, title: str, stage: str, text: str, path: str):
    """A glass card with icon, stage pill, one-line description and a link to the page."""
    icon, tint = PAGES[page]
    with st.container(key=f"tile-{page}"):
        st.html(f'<div class="bz-tile">{glass_icon(icon, tint, 56)}<h4>{escape(title)}</h4>'
                f'<span class="stage">{escape(stage)}</span><p>{escape(text)}</p></div>')
        st.page_link(path, label="Open")
