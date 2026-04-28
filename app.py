import streamlit as st
import pandas as pd
import plotly.express as px

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Real Estate CRM Dashboard",
    page_icon="🏢",
    layout="wide"
)

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data.csv")
    except:
        st.error("❌ data.csv not found")
        st.stop()

    df.columns = df.columns.str.strip()

    # Clean strings
    for col in df.select_dtypes(include="object"):
        df[col] = df[col].str.strip()

    # Format
    if "country" in df:
        df["country"] = df["country"].str.title()

    # Numeric fixes
    num_cols = ["sale_price", "floor_area_sqft", "engagement_score"]
    for col in num_cols:
        if col in df:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Clip values
    if "satisfaction_score" in df:
        df["satisfaction_score"] = df["satisfaction_score"].clip(1, 5)

    if "engagement_score" in df:
        df["engagement_score"] = df["engagement_score"].clip(0, 100)

    if "investment_score" in df:
        df["investment_score"] = df["investment_score"].clip(0, 1)

    if "sale_price" in df:
        df["sale_price"] = df["sale_price"].clip(lower=0)

    df = df.fillna(0)

    return df


df_raw = load_data()

# ─────────────────────────────────────────────
# SIDEBAR FILTERS
# ─────────────────────────────────────────────
st.sidebar.title("🔍 Filters")

def get_options(col):
    if col in df_raw.columns:
        return ["All"] + sorted(df_raw[col].unique())
    return ["All"]

country = st.sidebar.selectbox("Country", get_options("country"))
segment = st.sidebar.selectbox("Segment", get_options("segment"))

if "sale_price" in df_raw.columns:
    min_p = int(df_raw["sale_price"].min())
    max_p = int(df_raw["sale_price"].max())
    price_range = st.sidebar.slider("Price Range", min_p, max_p, (min_p, max_p))
else:
    price_range = (0, 0)

# ─────────────────────────────────────────────
# FILTER DATA
# ─────────────────────────────────────────────
df = df_raw.copy()

if country != "All" and "country" in df:
    df = df[df["country"] == country]

if segment != "All" and "segment" in df:
    df = df[df["segment"] == segment]

if "sale_price" in df:
    df = df[(df["sale_price"] >= price_range[0]) &
            (df["sale_price"] <= price_range[1])]

if df.empty:
    st.warning("⚠️ No data found for selected filters")
    st.stop()

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.title("🏢 Real Estate CRM Dashboard")
st.caption(f"Showing {len(df):,} records")

# ─────────────────────────────────────────────
# KPI SECTION
# ─────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

total_revenue = df["sale_price"].sum() if "sale_price" in df else 0
avg_price = df["sale_price"].mean() if "sale_price" in df else 0
avg_satisfaction = df["satisfaction_score"].mean() if "satisfaction_score" in df else 0
avg_engagement = df["engagement_score"].mean() if "engagement_score" in df else 0

col1.metric("Total Clients", len(df))
col2.metric("Total Revenue", f"${total_revenue:,.0f}")
col3.metric("Avg Price", f"${avg_price:,.0f}")
col4.metric("Satisfaction", f"{avg_satisfaction:.2f}")

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["Overview", "Segments", "Pricing"])

# ─────────────────────────────────────────────
# TAB 1 - OVERVIEW
# ─────────────────────────────────────────────
with tab1:
    col1, col2 = st.columns(2)

    if "client_type" in df:
        ct = df["client_type"].value_counts().reset_index()
        ct.columns = ["Type", "Count"]

        fig = px.pie(ct, values="Count", names="Type", title="Client Type")
        col1.plotly_chart(fig, use_container_width=True)

    if "referral_channel" in df:
        rc = df["referral_channel"].value_counts().reset_index()
        rc.columns = ["Channel", "Count"]

        fig = px.pie(rc, values="Count", names="Channel", title="Referral Channel")
        col2.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
# TAB 2 - SEGMENTS
# ─────────────────────────────────────────────
with tab2:
    if "segment" in df:
        seg = df.groupby("segment")["sale_price"].mean().reset_index()

        fig = px.bar(seg, x="segment", y="sale_price",
                     title="Avg Sale Price by Segment",
                     text_auto=True)

        st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
# TAB 3 - PRICING
# ─────────────────────────────────────────────
with tab3:
    if "sale_price" in df:
        fig = px.histogram(df, x="sale_price",
                           title="Sale Price Distribution")

        st.plotly_chart(fig, use_container_width=True)

    if "floor_area_sqft" in df:
        fig = px.scatter(df,
                         x="floor_area_sqft",
                         y="sale_price",
                         title="Area vs Price",
                         trendline="ols")

        st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
# DATA TABLE
# ─────────────────────────────────────────────
st.subheader("📊 Data Preview")
st.dataframe(df.head(100), use_container_width=True)

# ─────────────────────────────────────────────
# DOWNLOAD
# ─────────────────────────────────────────────
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("📥 Download Data", csv, "filtered_data.csv", "text/csv")

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.caption("Built with Streamlit & Plotly")

