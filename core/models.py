import numpy as np
import pandas as pd
import streamlit as st
from scipy import sparse
from sklearn.cluster import KMeans
from sklearn.ensemble import GradientBoostingRegressor, RandomForestClassifier
from sklearn.metrics import (accuracy_score, mean_absolute_error, precision_score,
                             r2_score, recall_score, roc_auc_score, silhouette_score)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# NOTE: parameters starting with "_" are skipped by st.cache_data hashing (the data never changes).


def customers_only(df):
    c = df.dropna(subset=["CustomerID"]).copy()
    c["CustomerID"] = c.CustomerID.astype(int)
    return c


@st.cache_data
def product_names(_df):
    return _df.groupby("StockCode").Description.agg(lambda s: s.mode().iat[0])


# ───────────── 1. SALES FORECAST ─────────────
def _feat(s):
    d = pd.DataFrame({"y": s})
    i = d.index
    d["dow"], d["dom"], d["month"] = i.dayofweek, i.day, i.month
    d["woy"] = i.isocalendar().week.astype(int).values
    for lag in (1, 7, 14):
        d[f"lag{lag}"] = d.y.shift(lag)
    d["r7"] = d.y.shift(1).rolling(7).mean()
    d["r28"] = d.y.shift(1).rolling(28).mean()
    return d


def _fit(s):
    d = _feat(s).dropna()
    m = GradientBoostingRegressor(n_estimators=300, max_depth=3, learning_rate=0.05,
                                  subsample=0.8, random_state=42)
    return m.fit(d.drop(columns="y"), d.y)


def _roll(m, s, h):
    s = s.copy()
    for _ in range(h):
        nd = s.index[-1] + pd.Timedelta(days=1)
        s.loc[nd] = np.nan
        x = _feat(s).iloc[[-1]].drop(columns="y")
        s.loc[nd] = max(float(m.predict(x)[0]), 0.0)
    return s.iloc[-h:]


@st.cache_data(show_spinner="Training forecast model...")
def sales_forecast(_df, horizon=14):
    s = _df.groupby("Date").Revenue.sum().asfreq("D", fill_value=0.0)
    hold = 28
    pred = _roll(_fit(s.iloc[:-hold]), s.iloc[:-hold], hold)
    actual = s.iloc[-hold:]
    naive = s.shift(7).iloc[-hold:]
    return dict(
        history=s,
        backtest=pd.DataFrame({"actual": actual, "predicted": pred}),
        forecast=_roll(_fit(s), s, horizon),
        mae=mean_absolute_error(actual, pred),
        mae_naive=mean_absolute_error(actual, naive),
        wape=(actual - pred).abs().sum() / actual.sum(),
    )


# ───────────── 2. CUSTOMER SEGMENTATION (RFM + KMeans) ─────────────
SEG_NAMES = {3: ["Lost", "Loyal", "Champions"],
             4: ["Lost", "At risk", "Loyal", "Champions"],
             5: ["Lost", "At risk", "Promising", "Loyal", "Champions"]}


@st.cache_data(show_spinner="Clustering customers...")
def rfm_segments(_df, k=4):
    c = customers_only(_df)
    snap = c.InvoiceDate.max().normalize() + pd.Timedelta(days=1)
    g = c.groupby("CustomerID")
    r = pd.DataFrame({"Recency": (snap - g.InvoiceDate.max()).dt.days,
                      "Frequency": g.InvoiceNo.nunique(),
                      "Monetary": g.Revenue.sum()})
    X = StandardScaler().fit_transform(np.log1p(r))
    inertia = {kk: KMeans(kk, n_init=10, random_state=42).fit(X).inertia_ for kk in range(2, 9)}
    km = KMeans(k, n_init=10, random_state=42).fit(X)
    r["cluster"] = km.labels_
    cm = r.groupby("cluster")[["Recency", "Frequency", "Monetary"]].mean()
    score = (-cm.Recency).rank() + cm.Frequency.rank() + cm.Monetary.rank()
    mapping = dict(zip(score.sort_values().index, SEG_NAMES[k]))
    r["Segment"] = r.cluster.map(mapping)
    summary = (r.groupby("Segment").agg(Customers=("Monetary", "size"), Recency=("Recency", "mean"),
                                        Frequency=("Frequency", "mean"), AvgSpend=("Monetary", "mean"),
                                        Revenue=("Monetary", "sum")).round(1))
    summary["RevenueShare"] = (summary.Revenue / summary.Revenue.sum() * 100).round(1)
    summary = summary.reindex([n for n in SEG_NAMES[k][::-1]])
    return dict(rfm=r, summary=summary, inertia=inertia,
                silhouette=silhouette_score(X, km.labels_, sample_size=2000, random_state=42))


# ───────────── 3. PRODUCT RECOMMENDATIONS (basket analysis) ─────────────
@st.cache_data(show_spinner="Mining product associations...")
def basket_model(_df, top_n=400):
    d = _df[["InvoiceNo", "StockCode"]].drop_duplicates()
    top = d.StockCode.value_counts().head(top_n).index
    d = d[d.StockCode.isin(top)]
    inv, prod = d.InvoiceNo.astype("category"), d.StockCode.astype("category")
    X = sparse.csr_matrix((np.ones(len(d)), (inv.cat.codes, prod.cat.codes)))
    co = (X.T @ X).toarray()
    cnt = np.diag(co).copy()
    np.fill_diagonal(co, 0)
    return dict(codes=list(prod.cat.categories), co=co, cnt=cnt, n=X.shape[0])


def recommend(model, names, code, k=8, min_pair=15):
    i = model["codes"].index(code)
    co, cnt, n = model["co"][i], model["cnt"], model["n"]
    conf = co / cnt[i]
    out = pd.DataFrame({"StockCode": model["codes"],
                        "Product": [names[c] for c in model["codes"]],
                        "Bought together": co.astype(int),
                        "Confidence": conf,
                        "Lift": conf / (cnt / n)})
    return out[out["Bought together"] >= min_pair].sort_values("Lift", ascending=False).head(k)


def top_pairs(model, names, k=15, min_pair=30):
    co = np.triu(model["co"])
    i, j = np.nonzero(co >= min_pair)
    cnt, n, codes = model["cnt"], model["n"], model["codes"]
    return (pd.DataFrame({"Product A": [names[codes[a]] for a in i],
                          "Product B": [names[codes[b]] for b in j],
                          "Together": co[i, j].astype(int),
                          "Lift": co[i, j] * n / (cnt[i] * cnt[j])})
            .sort_values("Lift", ascending=False).head(k))


# ───────────── 4 + 5. CHURN & CUSTOMER LIFETIME VALUE ─────────────
def _cust_feats(c, asof):
    h = c[c.InvoiceDate < asof]
    g = h.groupby("CustomerID")
    f = pd.DataFrame({"recency": (asof - g.InvoiceDate.max()).dt.days,
                      "tenure": (asof - g.InvoiceDate.min()).dt.days,
                      "frequency": g.InvoiceNo.nunique(),
                      "monetary": g.Revenue.sum(),
                      "n_products": g.StockCode.nunique()})
    f["aov"] = f.monetary / f.frequency
    f["avg_gap"] = f.tenure / f.frequency
    recent = h[h.InvoiceDate >= asof - pd.Timedelta(days=90)].groupby("CustomerID").InvoiceNo.nunique()
    f["orders_90d"] = recent.reindex(f.index).fillna(0)
    return f


@st.cache_data(show_spinner="Training churn & lifetime-value models...")
def customer_models(_df, horizon=90):
    c = customers_only(_df)
    end = c.InvoiceDate.max().normalize() + pd.Timedelta(days=1)
    cut = end - pd.Timedelta(days=horizon)

    X = _cust_feats(c, cut)                                   # what we knew at the cutoff
    future = c[c.InvoiceDate >= cut].groupby("CustomerID").Revenue.sum()
    value = future.reindex(X.index).fillna(0.0)               # what they spent afterwards
    churn = (value == 0).astype(int)                          # no purchase = churned

    Xtr, Xte, ytr, yte, vtr, vte = train_test_split(X, churn, value, test_size=0.25,
                                                    random_state=42, stratify=churn)
    clf = RandomForestClassifier(n_estimators=300, min_samples_leaf=5, class_weight="balanced",
                                 random_state=42, n_jobs=-1).fit(Xtr, ytr)
    p = clf.predict_proba(Xte)[:, 1]
    churn_metrics = dict(accuracy=accuracy_score(yte, p > .5), precision=precision_score(yte, p > .5),
                         recall=recall_score(yte, p > .5), auc=roc_auc_score(yte, p),
                         base_rate=churn.mean())

    reg = GradientBoostingRegressor(n_estimators=250, max_depth=3, learning_rate=0.05,
                                    subsample=0.8, random_state=42).fit(Xtr, np.log1p(vtr))
    pv = np.expm1(reg.predict(Xte)).clip(0)
    clv_metrics = dict(mae=mean_absolute_error(vte, pv), r2_log=r2_score(np.log1p(vte), reg.predict(Xte)))

    now = _cust_feats(c, end)                                 # score everyone today
    s = now.copy()
    s["churn_prob"] = clf.predict_proba(now)[:, 1]
    s["pred_value"] = np.expm1(reg.predict(now)).clip(0)
    s["clv_12m"] = s.pred_value * 365 / horizon
    s["value_at_risk"] = s.churn_prob * s.monetary * horizon / s.tenure.clip(lower=horizon)
    return dict(scores=s, churn=churn_metrics, clv=clv_metrics,
                importances=pd.Series(clf.feature_importances_, index=X.columns).sort_values())


# ───────────── 6. STOCK & REORDER ALERTS ─────────────
@st.cache_data(show_spinner="Forecasting product demand...")
def product_demand(_df, top_n=60):
    top = _df.groupby("StockCode").Quantity.sum().nlargest(top_n).index
    d = _df[_df.StockCode.isin(top)]
    wk = d.set_index("Date").groupby("StockCode").Quantity.resample("W").sum().unstack(0).fillna(0)
    wk = wk.iloc[:-1]                                         # last week is partial
    rows = {}
    for code in wk.columns:
        y = wk[code].iloc[-12:].values
        slope, icpt = np.polyfit(np.arange(len(y)), y, 1)     # 12-week linear trend
        nxt = np.clip(slope * len(y) + icpt, 0.5 * y.mean(), 2 * y.mean())
        rows[code] = dict(weekly_mean=y.mean(), weekly_std=y.std(), next_week=nxt)
    return pd.DataFrame(rows).T


def demo_stock(dem):
    rng = np.random.default_rng(7)
    return (dem.weekly_mean * rng.uniform(0.2, 3.0, len(dem))).round().astype(int)


def reorder_plan(dem, on_hand, lead_days=7, z=1.65, cover_days=14):
    p = dem.copy()
    p["on_hand"] = on_hand.reindex(p.index)
    p = p.dropna(subset=["on_hand"])
    daily = p.next_week / 7
    lead_demand = daily * lead_days
    safety = z * (p.weekly_std / np.sqrt(7)) * np.sqrt(lead_days)
    p["days_cover"] = (p.on_hand / daily).round(1)
    p["reorder_point"] = (lead_demand + safety).round()
    p["order_qty"] = np.ceil((daily * (lead_days + cover_days) + safety - p.on_hand).clip(lower=0))
    p["status"] = np.where(p.on_hand < lead_demand, "Stock-out risk",
                           np.where(p.on_hand < p.reorder_point, "Reorder now", "OK"))
    return p


# ───────────── 7. PRICE ELASTICITY & DISCOUNTS ─────────────
DISCOUNTS = np.array([0.20, 0.15, 0.10, 0.05, 0.0])   # last column = no discount
PRIOR_ELASTICITY = -1.5


@st.cache_data(show_spinner="Estimating price elasticity...")
def price_elasticity(_df, top_n=150):
    r = _df[_df.Quantity <= 12]                               # retail-sized lines only (removes wholesale price tiers)
    top = r.groupby("StockCode").Revenue.sum().nlargest(top_n).index
    d = r[r.StockCode.isin(top)]
    w = d.groupby(["StockCode", pd.Grouper(key="Date", freq="W")]).agg(units=("Quantity", "sum"),
                                                                       revenue=("Revenue", "sum")).reset_index()
    w["price"] = w.revenue / w.units
    w["lp"], w["lq"] = np.log(w.price), np.log(w.units)
    # pooled estimate: within-product regression of log units on log price
    lp_d = w.lp - w.groupby("StockCode").lp.transform("mean")
    lq_d = w.lq - w.groupby("StockCode").lq.transform("mean")
    pooled = float((lp_d * lq_d).sum() / (lp_d ** 2).sum())
    pooled = pooled if pooled < -0.3 else PRIOR_ELASTICITY
    rows = []
    for code, x in w.groupby("StockCode"):
        e, src = pooled, "pooled"
        if len(x) >= 10 and x.lp.std() > 0.03:
            own = np.polyfit(x.lp, x.lq, 1)[0]
            if own < 0:
                e, src = 0.5 * own + 0.5 * pooled, "own data (shrunk)"   # shrink noisy estimate toward pooled
        recent = x.tail(8)
        rows.append(dict(StockCode=code, price=recent.revenue.sum() / recent.units.sum(),
                         weekly_units=recent.units.mean(), elasticity=float(np.clip(e, -4, -0.3)), source=src))
    return pd.DataFrame(rows).set_index("StockCode"), pooled


def simulate(price, units, e, cost_ratio, disc=DISCOUNTS):
    """Weekly units / revenue / profit for each discount level (constant-elasticity demand)."""
    u = units * (1 - disc) ** e
    p = price * (1 - disc)
    return u, u * p, u * (p - price * cost_ratio)


def promo_plan(el, cost_ratio=0.55, tolerance=0.10):
    """Per product: biggest-revenue discount that keeps profit within `tolerance` of today."""
    u, rev, prof = simulate(el.price.values[:, None], el.weekly_units.values[:, None],
                            el.elasticity.values[:, None], cost_ratio)
    ok = prof >= prof[:, [-1]] * (1 - tolerance)
    best = np.where(ok, rev, -np.inf).argmax(1)
    i = np.arange(len(el))
    out = el.copy()
    out["discount"] = DISCOUNTS[best]
    out["unit_lift"] = u[i, best] / u[:, -1] - 1
    out["revenue_gain"] = rev[i, best] - rev[:, -1]
    out["profit_change"] = prof[i, best] - prof[:, -1]
    return out
