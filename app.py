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
# DEBUG (optional)
# ─────────────────────────────────────────────
st.write("✅ App started")

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data.csv")
    except Exception as e:
        st.error(f"❌ Error loading data.csv: {e}")
        st.stop()

    # Clean column names
    df.columns = df.columns.str.strip().str.lower()

    # Clean string columns
    for col in df.select_dtypes(include="object"):
        df[col] = df[col].astype(str).str.strip()

    # Standardize country
    if "country" in df.columns:
        df["country"] = df["country"].str.title()

    # Convert numeric columns safely
    num_cols = ["sale_price", "engagement_score", "floor_area_sqft"]
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Fill missing values
    df = df.fillna(0)

    return df


df_raw = load_data()

# ─────────────────────────────────────────────
# SIDEBAR FILTERS
# ─────────────────────────────────────────────
st.sidebar.header("🔍 Filters")

def get_options(col):
    if col in df_raw.columns:
        return ["All"] + sorted(df_raw[col].unique())
    return ["All"]

country = st.sidebar.selectbox("Country", get_options("country"))
segment = st.sidebar.selectbox("Segment", get_options("segment"))

# Price filter
if "sale_price" in df_raw.columns:
    min_p = int(df_raw["sale_price"].min())
    max_p = int(df_raw["sale_price"].max())
    price_range = st.sidebar.slider("Price Range", min_p, max_p, (min_p, max_p))
else:
    price_range = (0, 0)

# ─────────────────────────────────────────────
# APPLY FILTERS
# ─────────────────────────────────────────────
df = df_raw.copy()

if country != "All" and "country" in df.columns:
    df = df[df["country"] == country]

if segment != "All" and "segment" in df.columns:
    df = df[df["segment"] == segment]

if "sale_price" in df.columns:
    df = df[
        (df["sale_price"] >= price_range[0]) &
        (df["sale_price"] <= price_range[1])
    ]

if df.empty:
    st.warning("⚠️ No data available for selected filters")
    st.stop()

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.title("🏢 Real Estate CRM Dashboard")
st.caption(f"Showing {len(df):,} records")

# ─────────────────────────────────────────────
# KPIs
# ─────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

total_revenue = df["sale_price"].sum() if "sale_price" in df else 0
avg_price = df["sale_price"].mean() if "sale_price" in df else 0
avg_satisfaction = df["satisfaction_score"].mean() if "satisfaction_score" in df else 0
avg_engagement = df["engagement_score"].mean() if "engagement_score" in df else 0

col1.metric("Total Clients", len(df))
col2.metric("Total Revenue", f"${total_revenue:,.0f}")
col3.metric("Avg Price", f"${avg_price:,.0f}")
col4.metric("Avg Engagement", f"{avg_engagement:.1f}")

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["Overview", "Segments", "Pricing"])

# ─────────────────────────────────────────────
# TAB 1: OVERVIEW
# ─────────────────────────────────────────────
with tab1:
    col1, col2 = st.columns(2)

    if "client_type" in df.columns:
        ct = df["client_type"].value_counts().reset_index()
        ct.columns = ["Type", "Count"]

        fig = px.pie(ct, values="Count", names="Type", title="Client Type Distribution")
        col1.plotly_chart(fig, use_container_width=True)

    if "referral_channel" in df.columns:
        rc = df["referral_channel"].value_counts().reset_index()
        rc.columns = ["Channel", "Count"]

        fig = px.pie(rc, values="Count", names="Channel", title="Referral Channels")
        col2.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
# TAB 2: SEGMENTS
# ─────────────────────────────────────────────
with tab2:
    if "segment" in df.columns and "sale_price" in df.columns:
        seg = df.groupby("segment")["sale_price"].mean().reset_index()

        fig = px.bar(
            seg,
            x="segment",
            y="sale_price",
            title="Average Sale Price by Segment",
            text_auto=True
        )

        st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
# TAB 3: PRICING
# ─────────────────────────────────────────────
with tab3:
    if "sale_price" in df.columns:
        fig = px.histogram(df, x="sale_price", title="Sale Price Distribution")
        st.plotly_chart(fig, use_container_width=True)

    if "floor_area_sqft" in df.columns:
        fig = px.scatter(
            df,
            x="floor_area_sqft",
            y="sale_price",
            title="Area vs Price",
            trendline="ols"
        )
        st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
# DATA TABLE
# ─────────────────────────────────────────────
st.subheader("📊 Data Preview")
st.dataframe(df.head(100), use_container_width=True)

# ─────────────────────────────────────────────
# DOWNLOAD BUTTON
# ─────────────────────────────────────────────
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("📥 Download Data", csv, "filtered_data.csv", "text/csv")

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.caption("Built with Streamlit & Plotly")

