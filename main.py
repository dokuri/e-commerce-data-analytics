"""
E-Commerce Sales & Customer Analytics Dashboard  (single file)

Run:      streamlit run main.py
Install:  pip install -r requirements.txt
Data:     data/ecommerce_sales.csv   (or upload your own CSV from the sidebar)

How this file is organised
  1. SETTINGS            - page config, data path, currency symbol
  2. DATA & ANALYTICS    - load / filter the data, KPIs and every table behind a chart
  3. DASHBOARD (UI)      - sidebar filters, KPI cards and tabs with Plotly charts
"""
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# ============================================================================
# 1. SETTINGS
# ============================================================================
st.set_page_config(page_title="E-Commerce Sales & Customer Analytics", page_icon="🛒", layout="wide")

DATA_PATH = Path(__file__).parent / "data" / "ecommerce_sales.csv"
CURRENCY = "₹"

# ============================================================================
# 2. DATA & ANALYTICS  (plain pandas - no Streamlit calls in this section)
# ============================================================================
# Business rules
# --------------
# * "Net revenue" counts orders whose status is Delivered, Shipped or Processing.
#   Cancelled and Returned orders are excluded from revenue but are still counted
#   in the cancellation / return rates.

REVENUE_STATUSES = ["Delivered", "Shipped", "Processing"]

REQUIRED_COLUMNS = [
    "order_id", "order_date", "customer_id", "customer_name", "gender", "age",
    "city", "state", "product_category", "product_name", "quantity", "unit_price",
    "discount_pct", "shipping_fee", "total_amount", "payment_method", "device",
    "acquisition_channel", "order_status", "delivery_days", "rating", "customer_type",
]


# --------------------------------------------------------------------------- #
# Loading & filtering
# --------------------------------------------------------------------------- #
def load_data(source) -> pd.DataFrame:
    """Read the orders CSV (path or file-like object) and add derived columns."""
    df = pd.read_csv(source, parse_dates=["order_date"])
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"CSV is missing required columns: {missing}")

    df["order_month"] = df["order_date"].dt.to_period("M").dt.to_timestamp()
    df["weekday"] = df["order_date"].dt.day_name()
    df["is_revenue"] = df["order_status"].isin(REVENUE_STATUSES)
    df["net_revenue"] = np.where(df["is_revenue"], df["total_amount"], 0.0)
    df["age_group"] = pd.cut(
        df["age"], bins=[0, 24, 34, 44, 54, 200],
        labels=["18-24", "25-34", "35-44", "45-54", "55+"],
    ).astype(str)
    return df


def apply_filters(
    df: pd.DataFrame,
    start=None,
    end=None,
    categories=None,
    states=None,
    payments=None,
    statuses=None,
) -> pd.DataFrame:
    """Return the subset of orders matching every non-empty filter."""
    out = df
    if start is not None:
        out = out[out["order_date"] >= pd.Timestamp(start)]
    if end is not None:
        out = out[out["order_date"] <= pd.Timestamp(end)]
    if categories:
        out = out[out["product_category"].isin(categories)]
    if states:
        out = out[out["state"].isin(states)]
    if payments:
        out = out[out["payment_method"].isin(payments)]
    if statuses:
        out = out[out["order_status"].isin(statuses)]
    return out


# --------------------------------------------------------------------------- #
# KPIs
# --------------------------------------------------------------------------- #
def compute_kpis(df: pd.DataFrame) -> dict:
    rev = df[df["is_revenue"]]
    n_orders = len(df)
    orders_per_customer = df.groupby("customer_id").size()
    return {
        "net_revenue": float(rev["total_amount"].sum()),
        "orders": n_orders,
        "aov": float(rev["total_amount"].mean()) if len(rev) else 0.0,
        "customers": int(df["customer_id"].nunique()),
        "repeat_rate": float((orders_per_customer > 1).mean()) if len(orders_per_customer) else 0.0,
        "cancel_rate": float((df["order_status"] == "Cancelled").mean()) if n_orders else 0.0,
        "return_rate": float((df["order_status"] == "Returned").mean()) if n_orders else 0.0,
        "avg_rating": float(df["rating"].mean()) if df["rating"].notna().any() else float("nan"),
        "avg_delivery_days": float(df["delivery_days"].mean()) if df["delivery_days"].notna().any() else float("nan"),
    }


# --------------------------------------------------------------------------- #
# Aggregations used by the charts
# --------------------------------------------------------------------------- #
def monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    g = (
        df.groupby("order_month")
        .agg(orders=("order_id", "count"), net_revenue=("net_revenue", "sum"))
        .reset_index()
        .sort_values("order_month")
    )
    g["revenue_growth_pct"] = g["net_revenue"].pct_change() * 100
    return g


def monthly_category_revenue(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["order_month", "product_category"], as_index=False)["net_revenue"].sum()
        .sort_values("order_month")
    )


def weekday_summary(df: pd.DataFrame) -> pd.DataFrame:
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    g = (
        df.groupby("weekday")
        .agg(orders=("order_id", "count"), net_revenue=("net_revenue", "sum"))
        .reindex(order)
        .fillna(0)
        .reset_index()
    )
    return g


def category_summary(df: pd.DataFrame) -> pd.DataFrame:
    rev = df[df["is_revenue"]]
    g = (
        rev.groupby("product_category")
        .agg(net_revenue=("total_amount", "sum"), orders=("order_id", "count"),
             units=("quantity", "sum"), avg_discount_pct=("discount_pct", "mean"))
        .reset_index()
        .sort_values("net_revenue", ascending=False)
    )
    return g


def top_products(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    rev = df[df["is_revenue"]]
    return (
        rev.groupby(["product_category", "product_name"], as_index=False)
        .agg(net_revenue=("total_amount", "sum"), units=("quantity", "sum"), orders=("order_id", "count"))
        .sort_values("net_revenue", ascending=False)
        .head(n)
    )


def state_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("state")
        .agg(net_revenue=("net_revenue", "sum"), orders=("order_id", "count"),
             customers=("customer_id", "nunique"))
        .reset_index()
        .sort_values("net_revenue", ascending=False)
    )


def payment_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("payment_method")
        .agg(orders=("order_id", "count"), net_revenue=("net_revenue", "sum"))
        .reset_index()
        .sort_values("orders", ascending=False)
    )


def status_summary(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("order_status").size().reset_index(name="orders").sort_values("orders", ascending=False)


def channel_summary(df: pd.DataFrame) -> pd.DataFrame:
    g = (
        df.groupby("acquisition_channel")
        .agg(orders=("order_id", "count"), net_revenue=("net_revenue", "sum"),
             customers=("customer_id", "nunique"))
        .reset_index()
    )
    g["revenue_per_customer"] = g["net_revenue"] / g["customers"]
    return g.sort_values("net_revenue", ascending=False)


def rating_by_category(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.dropna(subset=["rating"])
        .groupby("product_category", as_index=False)["rating"].mean()
        .sort_values("rating", ascending=False)
    )


def customer_type_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("customer_type")
        .agg(orders=("order_id", "count"), net_revenue=("net_revenue", "sum"))
        .reset_index()
    )


def age_group_summary(df: pd.DataFrame) -> pd.DataFrame:
    order = ["18-24", "25-34", "35-44", "45-54", "55+"]
    g = df.groupby("age_group").agg(net_revenue=("net_revenue", "sum"), orders=("order_id", "count"))
    return g.reindex(order).fillna(0).reset_index()


def gender_summary(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("gender", as_index=False).agg(net_revenue=("net_revenue", "sum"))


# --------------------------------------------------------------------------- #
# RFM segmentation
# --------------------------------------------------------------------------- #
def _quartile_score(series: pd.Series, ascending: bool = True) -> pd.Series:
    """Score 1-4 by rank-based quartiles (rank avoids duplicate-edge errors)."""
    ranks = series.rank(method="first", ascending=ascending)
    return pd.qcut(ranks, 4, labels=[1, 2, 3, 4]).astype(int)


def rfm_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Recency / Frequency / Monetary table, one row per customer with revenue orders.

    Recency  = days since last order (lower is better)
    Frequency= number of orders
    Monetary = total spend
    Segment is derived from R+F+M (each scored 1-4).
    """
    rev = df[df["is_revenue"]]
    if rev.empty:
        return pd.DataFrame(columns=[
            "customer_id", "customer_name", "recency_days", "frequency", "monetary",
            "R", "F", "M", "rfm_score", "segment"])

    snapshot = rev["order_date"].max() + pd.Timedelta(days=1)
    t = (
        rev.groupby(["customer_id", "customer_name"])
        .agg(last_order=("order_date", "max"), frequency=("order_id", "count"),
             monetary=("total_amount", "sum"))
        .reset_index()
    )
    t["recency_days"] = (snapshot - t["last_order"]).dt.days

    if len(t) < 4:  # too few customers to form quartiles
        t[["R", "F", "M"]] = 2
        t["rfm_score"] = 6
        t["segment"] = "Promising"
        return t.drop(columns="last_order")

    # R: fewer days since last order -> higher score, so rank descending
    t["R"] = _quartile_score(t["recency_days"], ascending=False)
    t["F"] = _quartile_score(t["frequency"])
    t["M"] = _quartile_score(t["monetary"])
    t["rfm_score"] = t["R"] + t["F"] + t["M"]
    t["segment"] = pd.cut(
        t["rfm_score"], bins=[0, 5, 7, 9, 12],
        labels=["At Risk", "Promising", "Loyal", "Champions"],
    ).astype(str)
    return t.drop(columns="last_order").sort_values("monetary", ascending=False)


def rfm_segment_summary(rfm: pd.DataFrame) -> pd.DataFrame:
    if rfm.empty:
        return pd.DataFrame(columns=["segment", "customers", "total_spend", "avg_orders"])
    return (
        rfm.groupby("segment")
        .agg(customers=("customer_id", "count"), total_spend=("monetary", "sum"),
             avg_orders=("frequency", "mean"))
        .reset_index()
        .sort_values("total_spend", ascending=False)
    )


def top_customers(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    rev = df[df["is_revenue"]]
    return (
        rev.groupby(["customer_id", "customer_name", "city"], as_index=False)
        .agg(orders=("order_id", "count"), total_spend=("total_amount", "sum"))
        .sort_values("total_spend", ascending=False)
        .head(n)
    )


# ============================================================================
# 3. DASHBOARD (UI)
# ============================================================================
@st.cache_data(show_spinner=False)
def load_default(path: str):
    return load_data(path)


def show(fig, height: int = 380):
    """Apply a consistent look to every chart and render it."""
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=50, b=10), legend_title_text="")
    st.plotly_chart(fig)


def money(x: float) -> str:
    return f"{CURRENCY}{x:,.0f}"


# --------------------------------------------------------------------------- #
# Data source
# --------------------------------------------------------------------------- #
st.title("🛒 E-Commerce Sales & Customer Analytics")
st.caption("Interactive dashboard - use the sidebar to filter or upload your own orders CSV.")

uploaded = st.sidebar.file_uploader("Upload your own orders CSV (optional)", type="csv")
try:
    df = load_data(uploaded) if uploaded is not None else load_default(str(DATA_PATH))
except Exception as exc:  # noqa: BLE001 - show any load problem to the user
    st.error(f"Could not load data: {exc}")
    st.stop()

# --------------------------------------------------------------------------- #
# Sidebar filters
# --------------------------------------------------------------------------- #
st.sidebar.header("Filters")
d_min, d_max = df["order_date"].min().date(), df["order_date"].max().date()
date_range = st.sidebar.date_input("Order date", value=(d_min, d_max), min_value=d_min, max_value=d_max)
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start, end = date_range
else:  # user is mid-selection
    start, end = d_min, d_max

categories = st.sidebar.multiselect("Product category", sorted(df["product_category"].unique()))
states = st.sidebar.multiselect("State", sorted(df["state"].unique()))
payments = st.sidebar.multiselect("Payment method", sorted(df["payment_method"].unique()))
statuses = st.sidebar.multiselect("Order status", sorted(df["order_status"].unique()))
st.sidebar.caption("Leave a filter empty to include everything.")

fdf = apply_filters(df, start, end, categories, states, payments, statuses)
if fdf.empty:
    st.warning("No orders match the selected filters.")
    st.stop()

# --------------------------------------------------------------------------- #
# KPI cards
# --------------------------------------------------------------------------- #
k = compute_kpis(fdf)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Net revenue", money(k["net_revenue"]))
c2.metric("Orders", f"{k['orders']:,}")
c3.metric("Avg order value", money(k["aov"]))
c4.metric("Customers", f"{k['customers']:,}")

c5, c6, c7, c8 = st.columns(4)
c5.metric("Repeat-customer rate", f"{k['repeat_rate']:.1%}")
c6.metric("Cancellation rate", f"{k['cancel_rate']:.1%}")
c7.metric("Return rate", f"{k['return_rate']:.1%}")
c8.metric("Avg rating", "n/a" if k["avg_rating"] != k["avg_rating"] else f"{k['avg_rating']:.2f} / 5")

tab_sales, tab_products, tab_customers, tab_ops, tab_data = st.tabs(
    ["📈 Sales trends", "🛍️ Products", "👥 Customers", "🚚 Operations", "🗂️ Data"]
)

# --------------------------------------------------------------------------- #
# Tab 1 - Sales trends
# --------------------------------------------------------------------------- #
with tab_sales:
    monthly = monthly_trend(fdf)
    left, right = st.columns(2)
    with left:
        show(px.line(monthly, x="order_month", y="net_revenue", markers=True,
                     title="Monthly net revenue",
                     labels={"order_month": "Month", "net_revenue": f"Revenue ({CURRENCY})"}))
    with right:
        show(px.bar(monthly, x="order_month", y="orders", title="Monthly order count",
                    labels={"order_month": "Month", "orders": "Orders"}))

    show(px.area(monthly_category_revenue(fdf), x="order_month", y="net_revenue",
                 color="product_category", title="Revenue by category over time",
                 labels={"order_month": "Month", "net_revenue": f"Revenue ({CURRENCY})"}), height=420)

    show(px.bar(weekday_summary(fdf), x="weekday", y="net_revenue",
                title="Revenue by day of week",
                labels={"weekday": "", "net_revenue": f"Revenue ({CURRENCY})"}))

# --------------------------------------------------------------------------- #
# Tab 2 - Products
# --------------------------------------------------------------------------- #
with tab_products:
    cat = category_summary(fdf)
    left, right = st.columns(2)
    with left:
        show(px.bar(cat.sort_values("net_revenue"), x="net_revenue", y="product_category",
                    orientation="h", title="Revenue by category",
                    labels={"net_revenue": f"Revenue ({CURRENCY})", "product_category": ""}))
    with right:
        show(px.bar(cat, x="product_category", y="avg_discount_pct",
                    title="Average discount by category (%)",
                    labels={"product_category": "", "avg_discount_pct": "Avg discount %"}))

    prods = top_products(fdf, 10)
    show(px.treemap(top_products(fdf, 25), path=["product_category", "product_name"],
                    values="net_revenue", title="Product revenue treemap (top 25 products)"), height=460)
    st.subheader("Top 10 products")
    st.dataframe(prods, hide_index=True)

# --------------------------------------------------------------------------- #
# Tab 3 - Customers
# --------------------------------------------------------------------------- #
with tab_customers:
    rfm = rfm_table(fdf)
    seg = rfm_segment_summary(rfm)
    left, right = st.columns(2)
    with left:
        show(px.bar(seg, x="segment", y="customers", color="segment",
                    title="Customers per RFM segment", labels={"segment": "", "customers": "Customers"}))
    with right:
        show(px.scatter(rfm, x="frequency", y="monetary", color="segment",
                        hover_data=["customer_name", "recency_days"],
                        title="Frequency vs. spend (RFM)",
                        labels={"frequency": "Orders", "monetary": f"Total spend ({CURRENCY})"}))

    left, right = st.columns(2)
    with left:
        show(px.pie(customer_type_summary(fdf), names="customer_type", values="net_revenue",
                    hole=0.45, title="Revenue: new vs. returning customers"))
    with right:
        show(px.bar(age_group_summary(fdf), x="age_group", y="net_revenue",
                    title="Revenue by age group",
                    labels={"age_group": "Age group", "net_revenue": f"Revenue ({CURRENCY})"}))

    st.subheader("Top 10 customers")
    st.dataframe(top_customers(fdf, 10), hide_index=True)
    with st.expander("How is RFM scored?"):
        st.write(
            "Each customer gets a 1-4 score for **R**ecency (days since last order), "
            "**F**requency (order count) and **M**onetary value (total spend). "
            "R+F+M = 10-12 -> Champions, 8-9 -> Loyal, 6-7 -> Promising, 3-5 -> At Risk."
        )

# --------------------------------------------------------------------------- #
# Tab 4 - Operations
# --------------------------------------------------------------------------- #
with tab_ops:
    left, right = st.columns(2)
    with left:
        show(px.pie(status_summary(fdf), names="order_status", values="orders",
                    hole=0.45, title="Order status mix"))
    with right:
        show(px.pie(payment_summary(fdf), names="payment_method", values="orders",
                    title="Payment method mix"))

    left, right = st.columns(2)
    with left:
        show(px.bar(channel_summary(fdf), x="acquisition_channel", y="net_revenue",
                    title="Revenue by acquisition channel",
                    labels={"acquisition_channel": "", "net_revenue": f"Revenue ({CURRENCY})"}))
    with right:
        show(px.bar(state_summary(fdf).head(10), x="net_revenue", y="state", orientation="h",
                    title="Top states by revenue",
                    labels={"net_revenue": f"Revenue ({CURRENCY})", "state": ""}).update_yaxes(autorange="reversed"))

    left, right = st.columns(2)
    with left:
        delivered = fdf.dropna(subset=["delivery_days"])
        show(px.histogram(delivered, x="delivery_days", nbins=8, title="Delivery time (days)",
                          labels={"delivery_days": "Days to deliver"}))
    with right:
        show(px.bar(rating_by_category(fdf), x="product_category", y="rating",
                    title="Average rating by category", labels={"product_category": "", "rating": "Avg rating"}))

# --------------------------------------------------------------------------- #
# Tab 5 - Data
# --------------------------------------------------------------------------- #
with tab_data:
    st.write(f"{len(fdf):,} orders after filters")
    show_cols = [c for c in REQUIRED_COLUMNS if c in fdf.columns]
    st.dataframe(fdf[show_cols], hide_index=True)
    st.download_button("Download filtered data (CSV)", fdf[show_cols].to_csv(index=False).encode("utf-8"),
                       file_name="filtered_orders.csv", mime="text/csv")
