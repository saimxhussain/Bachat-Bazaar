"""RetailIQ look: clean light dashboard, Inter type, blue accent, soft glass icon tiles.

Call `theme.apply()` once from app.py. Page components live in core/ui.py.
"""
from html import escape

import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

BRAND = "RetailIQ"
BLUE, GREEN, ORANGE, PURPLE, CORAL = "#3B63F5", "#16A34A", "#F97316", "#8B5CF6", "#F0405E"
PALETTE = [BLUE, GREEN, ORANGE, PURPLE, CORAL, "#0EA5C6", "#F5B301"]

# (light, deep) gradient pair for the big glass page icons
TINTS = {
    "orange": ("#FFC24D", "#FF8A00"), "blue": ("#7FB2FF", "#2F6BFF"), "green": ("#5EEB9B", "#12B76A"),
    "purple": ("#C4A3FF", "#7C4DFF"), "coral": ("#FF9AA8", "#F0405E"), "cyan": ("#7DEBFA", "#0EA5C6"),
}

# Lucide-style 24px line icons (inner SVG markup only)
ICONS = {
    "cart": '<circle cx="8" cy="21" r="1"/><circle cx="19" cy="21" r="1"/><path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12"/>',
    "forecast": '<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>',
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "bag": '<path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4Z"/><path d="M3 6h18"/><path d="M16 10a4 4 0 0 1-8 0"/>',
    "alert": '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
    "gem": '<path d="M6 3h12l4 6-10 13L2 9Z"/><path d="M11 3 8 9l4 13 4-13-3-6"/><path d="M2 9h20"/>',
    "box": '<path d="m7.5 4.27 9 5.15"/><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/>',
    "tag": '<path d="M12.586 2.586A2 2 0 0 0 11.172 2H4a2 2 0 0 0-2 2v7.172a2 2 0 0 0 .586 1.414l8.704 8.704a2.426 2.426 0 0 0 3.42 0l6.58-6.58a2.426 2.426 0 0 0 0-3.42z"/><circle cx="7.5" cy="7.5" r="1"/>',
    "wallet": '<path d="M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2"/><path d="M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4"/>',
    "chevron": '<path d="m9 18 6-6-6-6"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/>',
    "sparkle": '<path d="M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9z"/><path d="M19 15l.7 1.8L21.5 17.5l-1.8.7L19 20l-.7-1.8-1.8-.7 1.8-.7z"/>',
    "file": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 13h4"/><path d="M10 17h4"/>',
}

# page key -> (icon, tint) for the page headers
PAGES = {
    "home": ("cart", "orange"), "forecast": ("forecast", "blue"), "segments": ("users", "purple"),
    "recommend": ("bag", "coral"), "churn": ("alert", "coral"), "clv": ("gem", "cyan"),
    "stock": ("box", "green"), "pricing": ("tag", "orange"),
}

LOGO = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 36 36'%3E"
        "%3Crect width='36' height='36' rx='10' fill='%23111827'/%3E"
        "%3Ccircle cx='18' cy='18' r='6.5' fill='none' stroke='white' stroke-width='3'/%3E"
        "%3Cpath d='M18 18l5.5-5.5' stroke='%2360A5FA' stroke-width='3' stroke-linecap='round'/%3E%3C/svg%3E")

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root{--text:#111827;--muted:#6B7280;--line:#E8EBF3;--card:#fff;--blue:#3B63F5;--blue-soft:#EAF0FF;
  --green:#16A34A;--green-soft:#E3F7EA;--red:#DC2626;--red-soft:#FDE8E8;--orange:#F97316;--amber-soft:#FFF3D6;--amber:#B7791F;
  --shadow:0 1px 2px rgba(16,24,40,.04),0 8px 24px -14px rgba(16,24,40,.14)}

.stApp{background:#FAFBFD !important}
.stApp, .stApp :is(p,li,label,h1,h2,h3,h4,h5,h6,button,input,textarea,a,td,th,
  [data-testid="stMetricValue"],[data-testid="stMetricLabel"]){
  font-family:'Inter','Segoe UI',system-ui,sans-serif !important}
[data-testid="stHeader"]{background:transparent !important}
div[data-testid="stElementContainer"]:has(> style), div[data-testid="stElementContainer"]:has(> div > style){display:none}
.block-container{max-width:1280px;padding:1.2rem 2rem 4rem}
@media (max-width:760px){.block-container{padding:1rem .9rem 5rem}}
h1,h2,h3{letter-spacing:-.015em;font-weight:700 !important}
[data-testid="stCaptionContainer"]{color:var(--muted)}

/* ── sidebar ───────────────────────────────────────────── */
[data-testid="stSidebar"]{background:#F6F7FB !important;border-right:1px solid var(--line)}
[data-testid="stSidebarHeader"]{padding:1.5rem 1.1rem 1rem}
[data-testid="stSidebarHeader"]::before{content:"RetailIQ";flex:1;font-weight:700;font-size:1.3rem;letter-spacing:-.02em;
  line-height:38px;padding-left:50px;background:url("LOGO_URI") no-repeat left center/38px 38px}
[data-testid="stSidebarNavLink"]{border-radius:12px !important;margin:3px 0;padding:.55rem .8rem;font-weight:500;color:#374151}
[data-testid="stSidebarNavLink"]:hover{background:#ECEFF8 !important}
[data-testid="stSidebarNavLink"][aria-current="page"]{background:var(--blue-soft) !important;color:var(--blue) !important;font-weight:600;
  border:1px solid #D5E0FF}

/* ── cards ─────────────────────────────────────────────── */
[class*="st-key-card-"],[data-testid="stMetric"],[data-testid="stExpander"],[data-testid="stPlotlyChart"],
[data-testid="stChatMessage"],[data-testid="stAlert"]{
  background:var(--card) !important;border:1px solid var(--line) !important;border-radius:16px !important;box-shadow:var(--shadow)}
[class*="st-key-card-"]{padding:1.15rem 1.25rem 1.1rem}
[data-testid="stMetric"]{padding:1rem 1.2rem}
[data-testid="stMetricValue"]{font-weight:700 !important}
[data-testid="stMetricLabel"]{color:var(--muted)}
[data-testid="stPlotlyChart"]{padding:.4rem .6rem;overflow:hidden}
[class*="st-key-card-"] [data-testid="stPlotlyChart"]{border:none !important;box-shadow:none;padding:0}
[data-testid="stExpander"] details{border:none !important;background:transparent !important}
[data-testid="stDataFrame"]{border-radius:14px;overflow:hidden;border:1px solid var(--line)}

/* inputs */
[data-baseweb="input"],[data-baseweb="select"] > div,[data-testid="stChatInput"] > div{
  border-radius:12px !important;background:#fff !important;border-color:var(--line) !important}

/* buttons */
.stButton > button,.stDownloadButton > button{border-radius:12px;padding:.5rem 1.2rem;font-weight:600;
  background:#fff;color:var(--text);border:1px solid var(--line);box-shadow:var(--shadow)}
.stButton > button:hover,.stDownloadButton > button:hover{border-color:#C7D2FE;color:var(--blue)}
.stButton > button[kind="primary"]{background:var(--blue);color:#fff;border:none;box-shadow:0 10px 20px -10px rgba(59,99,245,.8)}
.stButton > button[kind="primary"]:hover{color:#fff;background:#2F55E6}
.stButton > button:focus-visible,.stDownloadButton > button:focus-visible{outline:3px solid #93A9FF;outline-offset:2px}

/* segmented control (Revenue | Orders | Customers) */
[data-testid="stButtonGroup"]{background:#F1F3F9;border-radius:12px;padding:3px;gap:2px;width:fit-content}
[data-testid="stBaseButton-segmented_control"],[data-testid="stBaseButton-segmented_controlActive"]{
  border:none !important;background:transparent !important;border-radius:9px !important;font-weight:500;box-shadow:none;color:var(--muted)}
[data-testid="stBaseButton-segmented_controlActive"]{background:#fff !important;color:var(--text) !important;
  box-shadow:0 1px 3px rgba(16,24,40,.14) !important;font-weight:600}

/* ── glass icons ───────────────────────────────────────── */
.bz-gi{position:relative;width:var(--s,60px);height:var(--s,60px);flex:none}
.bz-gi .orb{position:absolute;inset:8% 20% 20% 8%;border-radius:50%;
  background:radial-gradient(circle at 30% 30%,var(--c1),var(--c2));transform:translate(28%,26%)}
.bz-gi .glass{position:absolute;inset:0;border-radius:34%;display:grid;place-items:center;overflow:hidden;
  background:linear-gradient(145deg,rgba(255,255,255,.5),rgba(255,255,255,.1) 55%,rgba(255,255,255,.28));
  -webkit-backdrop-filter:blur(9px) saturate(190%);backdrop-filter:blur(9px) saturate(190%);
  border:1px solid rgba(255,255,255,.7);
  box-shadow:inset 0 1.5px 1px rgba(255,255,255,.85),inset 0 -10px 18px rgba(255,255,255,.1),0 12px 22px -10px var(--c2)}
.bz-gi .glass::after{content:"";position:absolute;left:10%;top:6%;width:58%;height:34%;border-radius:50%;
  background:linear-gradient(180deg,rgba(255,255,255,.75),rgba(255,255,255,0));filter:blur(1px)}
.bz-gi svg{position:relative;z-index:1;width:46%;height:46%;stroke:#fff;fill:none;stroke-width:1.9;
  stroke-linecap:round;stroke-linejoin:round;filter:drop-shadow(0 2px 3px rgba(0,0,0,.25))}
.ic{width:1em;height:1em;stroke:currentColor;fill:none;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round;flex:none}

/* small tinted glass tile used on KPI cards */
.bz-ki{width:40px;height:40px;border-radius:13px;display:grid;place-items:center;flex:none;font-size:20px;
  background:linear-gradient(145deg,rgba(255,255,255,.9),var(--soft));border:1px solid rgba(255,255,255,.95);color:var(--ink);
  box-shadow:inset 0 1px 1px #fff,0 6px 14px -7px var(--ink)}
.t-green{--soft:#CDF3DC;--ink:#16A34A;--c:#16A34A}.t-blue{--soft:#D6E6FF;--ink:#2F6BFF;--c:#2F6BFF}
.t-purple{--soft:#E6DBFF;--ink:#7C4DFF;--c:#8B5CF6}.t-orange{--soft:#FFE0C7;--ink:#F97316;--c:#F97316}

/* page header (other pages) */
.bz-head{display:flex;align-items:center;gap:1rem;margin:.2rem 0 1.3rem}
.bz-head h1{margin:0;padding:0;font-size:clamp(1.5rem,4.4vw,2rem);line-height:1.15}
.bz-head p{margin:.25rem 0 0;color:var(--muted);font-size:.95rem;max-width:62ch}

/* ── top bar ───────────────────────────────────────────── */
.st-key-bz_search input{height:46px;padding-left:44px !important;border-radius:12px;
  background:#fff url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%236B7280' stroke-width='2' stroke-linecap='round'%3E%3Ccircle cx='11' cy='11' r='7'/%3E%3Cpath d='m21 21-4.3-4.3'/%3E%3C/svg%3E") no-repeat 14px center/18px}
.bz-user{display:flex;align-items:center;justify-content:flex-end;gap:.6rem;font-weight:600}
.bz-user .av{width:38px;height:38px;border-radius:50%;display:grid;place-items:center;color:#fff;font-weight:600;
  background:linear-gradient(135deg,#7C8CFF,#6D4DFF)}
.bz-sr{margin:.4rem 0 1rem}
.bz-sr h5{margin:.2rem 0 .5rem;font-size:.8rem;color:var(--muted);font-weight:600}
.bz-sr .r{display:flex;align-items:center;gap:.8rem;padding:.45rem 0;border-top:1px solid var(--line);font-size:.9rem}
.bz-sr .r:first-of-type{border-top:none}.bz-sr .r b{font-weight:600}.bz-sr .r .sp{margin-left:auto;color:var(--muted)}

/* ── home ──────────────────────────────────────────────── */
.bz-hello small{display:block;color:var(--muted);font-size:1rem;margin-bottom:.1rem}
.bz-hello h1{margin:0;font-size:clamp(1.7rem,4.6vw,2.4rem);line-height:1.15}
.bz-hello p{margin:.35rem 0 0;color:var(--muted)}
.st-key-period [data-baseweb="select"] > div{height:46px;font-weight:500}

.bz-kpi{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:1rem 1.1rem .9rem;box-shadow:var(--shadow);height:100%}
.bz-kpi .top{display:flex;align-items:center;gap:.65rem;color:#374151;font-size:.9rem;font-weight:500}
.bz-kpi .val{font-size:1.75rem;font-weight:700;letter-spacing:-.02em;margin:.7rem 0 .45rem;line-height:1.1}
.bz-kpi .delta{display:flex;align-items:center;gap:.45rem;font-size:.78rem;color:var(--muted);flex-wrap:wrap}
.chip{display:inline-block;padding:.12rem .5rem;border-radius:7px;font-weight:600;font-size:.78rem}
.chip.up{background:var(--green-soft);color:var(--green)}.chip.down{background:var(--red-soft);color:var(--red)}
.chip.flat{background:#F1F3F9;color:var(--muted)}
.spark{position:relative;height:46px;margin-top:.6rem;color:var(--c)}
.spark svg{position:absolute;inset:0;width:100%;height:100%;overflow:visible}
.spark .a path{fill:var(--c);stroke:none}
.spark .a{opacity:.26;-webkit-mask-image:linear-gradient(#000,transparent);mask-image:linear-gradient(#000,transparent)}
.spark .l path{fill:none;stroke:var(--c);stroke-width:2;vector-effect:non-scaling-stroke;stroke-linecap:round;stroke-linejoin:round}

.bz-ch h3{margin:0;font-size:1.08rem;font-weight:600 !important;letter-spacing:-.01em}
.bz-ch p{margin:.2rem 0 .7rem;color:var(--muted);font-size:.84rem}
.bz-ch .row{display:flex;align-items:center;gap:.6rem}
.bz-ch .row .ic{font-size:20px;color:var(--blue)}

/* top products table */
.bz-tw{overflow-x:auto}
.bz-t{min-width:540px;font-size:.84rem}
.bz-t .tr{display:grid;grid-template-columns:22px minmax(150px,2.6fr) .9fr 1.15fr 1.15fr 1.25fr;gap:.6rem;align-items:center;
  padding:.55rem 0;border-top:1px solid var(--line)}
.bz-t .th{border-top:none;color:var(--muted);font-size:.74rem;font-weight:600;padding-top:0}
.bz-p{display:flex;align-items:center;gap:.7rem;min-width:0}
.bz-p .im{position:relative;width:40px;height:40px;border-radius:10px;background:#F1F3F9;flex:none;overflow:hidden;
  display:grid;place-items:center;color:#9CA3AF;font-size:18px}
.bz-p .im img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;background:#fff}
.bz-p b{display:block;font-weight:600;font-size:.84rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.bz-p span.s{display:block;color:var(--muted);font-size:.72rem}
.bz-p > div:last-child{min-width:0}
.dot{display:inline-block;width:7px;height:7px;border-radius:50%;margin-right:.35rem;background:var(--c)}
.st-ok{--c:#16A34A}.st-low{--c:#F59E0B}.st-out{--c:#DC2626}.st-na{--c:#9CA3AF}
.bz-t .tr .tc{display:flex;align-items:center;gap:.4rem}
.bz-t .spark{height:24px;margin:0;width:56px;flex:none}
.up-t{color:var(--green);font-weight:600}.down-t{color:var(--red);font-weight:600}
.bz-note{margin:.6rem 0 0;color:#9CA3AF;font-size:.72rem}

/* recent orders */
.bz-o{font-size:.84rem}
.bz-o .tr{display:grid;grid-template-columns:minmax(70px,1fr) .9fr 1.5fr 1fr;gap:.5rem;align-items:center;padding:.62rem 0;border-top:1px solid var(--line)}
.bz-o .tr:first-child{border-top:none}
.bz-o .id{font-weight:600}
.pill{display:inline-block;padding:.12rem .6rem;border-radius:999px;font-size:.72rem;font-weight:600;background:var(--blue-soft);color:#2F55E6;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:100%}
.pill.high{background:var(--red-soft);color:var(--red)}.pill.med{background:var(--amber-soft);color:var(--amber)}
.bz-o .when{color:var(--muted);font-size:.76rem;text-align:right}

/* quick actions + action plan: whole row is a link */
[class*="st-key-qa-"],[class*="st-key-ap-"]{position:relative;border:1px solid var(--line);border-radius:14px;background:#fff;
  box-shadow:var(--shadow);margin-bottom:.1rem;transition:border-color .15s ease}
[class*="st-key-qa-"]:hover,[class*="st-key-ap-"]:hover{border-color:#B8C7FF}
[class*="st-key-qa-"]:focus-within,[class*="st-key-ap-"]:focus-within{outline:3px solid #93A9FF}
[class*="st-key-qa-"] [data-testid="stElementContainer"],[class*="st-key-ap-"] [data-testid="stElementContainer"]{position:static}
[class*="st-key-qa-"] [data-testid="stPageLink"],[class*="st-key-ap-"] [data-testid="stPageLink"]{position:absolute;inset:0;margin:0;width:100%}
[class*="st-key-qa-"] [data-testid="stPageLink"] a,[class*="st-key-ap-"] [data-testid="stPageLink"] a{
  position:absolute;inset:0;opacity:0;padding:0;min-height:0;width:100%}
.bz-qa{display:flex;align-items:center;gap:.9rem;padding:.8rem 1rem}
.bz-qa .ic{font-size:24px;color:#374151}
.bz-qa b{display:block;font-weight:600;font-size:.88rem}
.bz-qa span.s{display:block;color:var(--muted);font-size:.76rem}
.bz-qa .go{margin-left:auto;color:#9CA3AF;font-size:16px}
.bz-ap{display:flex;align-items:center;gap:.8rem;padding:.7rem .9rem}
.bz-ap .n{width:24px;height:24px;border-radius:7px;display:grid;place-items:center;flex:none;font-size:.75rem;font-weight:700;
  background:var(--blue-soft);color:var(--blue)}
.bz-ap b{display:block;font-weight:600;font-size:.84rem}
.bz-ap span.s{display:block;color:var(--muted);font-size:.74rem}
.bz-ap .go{margin-left:.2rem;color:#9CA3AF;font-size:16px}

@media (prefers-reduced-motion:reduce){*{transition:none !important}}
""".replace("LOGO_URI", LOGO)


def _plotly_template():
    t = go.layout.Template()
    axis = dict(gridcolor="#EEF0F6", zerolinecolor="#E5E7EB", linecolor="#E5E7EB", tickfont=dict(color="#6B7280", size=11))
    t.layout = go.Layout(
        font=dict(family="Inter, Segoe UI, sans-serif", color="#374151"),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", colorway=PALETTE,
        xaxis=axis, yaxis=axis, legend=dict(bgcolor="rgba(0,0,0,0)"),
        title=dict(font=dict(size=15)), margin=dict(l=12, r=12, t=48, b=12),
        hoverlabel=dict(bgcolor="#FFFFFF", bordercolor="#E5E7EB", font=dict(color="#111827")))
    return t


def _patch_plotly():
    """Charts use our template, so switch off Streamlit's chart theme override by default."""
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


def icon(name: str) -> str:
    return f'<svg class="ic" viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg>'


def glass_icon(name: str, tint: str = "orange", size: int = 60) -> str:
    c1, c2 = TINTS[tint]
    return (f'<div class="bz-gi" style="--s:{size}px;--c1:{c1};--c2:{c2}"><div class="orb"></div>'
            f'<div class="glass"><svg viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg></div></div>')


def header(page: str, title: str, caption: str):
    ic, tint = PAGES[page]
    st.html(f'<div class="bz-head">{glass_icon(ic, tint, 56)}'
            f'<div><h1>{escape(title)}</h1><p>{escape(caption)}</p></div></div>')
