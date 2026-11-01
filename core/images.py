"""Find a product photo on the web from the product's name.

Order: DuckDuckGo image search (no key) -> Wikimedia Commons -> nothing (the UI shows a placeholder icon).
Hits are cached in data/product_images.json so each product is only looked up once.
"""
import json
import re
import threading
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import streamlit as st

CACHE_FILE = Path(__file__).resolve().parent.parent / "data" / "product_images.json"
_LOCK = threading.Lock()
_MEM: dict = {}


def _load():
    if not _MEM and CACHE_FILE.exists():
        try:
            _MEM.update(json.loads(CACHE_FILE.read_text(encoding="utf-8")))
        except Exception:
            pass


def _save():
    try:
        CACHE_FILE.write_text(json.dumps(_MEM, indent=0), encoding="utf-8")
    except Exception:  # read-only filesystem: keep it in memory only
        pass


def _clean(name: str) -> str:
    n = re.sub(r"\b(set of \d+|\d+\s?pcs?|\d+ ?x ?\d+)\b", "", name, flags=re.I)
    return re.sub(r"\s+", " ", n).strip()


def _ddg(q: str) -> str:
    try:
        from ddgs import DDGS
        for r in DDGS().images(q, max_results=4) or []:
            u = r.get("thumbnail") or r.get("image") or ""
            if u.startswith("https://"):
                return u
    except Exception:
        pass
    return ""


def _wiki(q: str) -> str:
    try:
        params = urllib.parse.urlencode({
            "action": "query", "format": "json", "generator": "search", "gsrnamespace": 6,
            "gsrsearch": q, "gsrlimit": 3, "prop": "imageinfo", "iiprop": "url", "iiurlwidth": 120})
        req = urllib.request.Request("https://commons.wikimedia.org/w/api.php?" + params,
                                     headers={"User-Agent": "BachatBazaar-dashboard/1.0"})
        with urllib.request.urlopen(req, timeout=5) as r:
            pages = (json.load(r).get("query") or {}).get("pages") or {}
        for p in pages.values():
            u = ((p.get("imageinfo") or [{}])[0]).get("thumburl") or ""
            if u.lower().split("?")[0].endswith((".jpg", ".jpeg", ".png", ".webp")):
                return u
    except Exception:
        pass
    return ""


def _lookup(name: str) -> str:
    with _LOCK:
        _load()
        if name in _MEM:
            return _MEM[name]
    q = _clean(name)
    url = _ddg(f"{q} product") or _wiki(q)
    if url:
        with _LOCK:
            _MEM[name] = url
            _save()
    return url


@st.cache_data(ttl=3600, show_spinner=False)
def lookup_many(names: tuple) -> dict:
    """{product name: image url or ''}. Pass a tuple so Streamlit can cache it."""
    with ThreadPoolExecutor(max_workers=5) as ex:
        return dict(zip(names, ex.map(_lookup, names)))
