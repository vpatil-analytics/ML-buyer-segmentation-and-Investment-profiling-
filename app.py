import streamlit as st
import pandas as pd
import plotly.express as px

# ─────────────────────────────
# CONFIG
# ─────────────────────────────
st.set_page_config(
    page_title="Real Estate CRM Dashboard",
    page_icon="🏢",
    layout="wide"
)

st.title("🏢 Real Estate CRM Dashboard")

# ─────────────────────────────
# LOAD DATA
# ─────────────────────────────
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data.csv")
    except Exception as e:
        st.error(f"❌ Error loading data.csv: {e}")
        st.stop()

    df.columns = df.columns.str.strip().str.lower()

    for col in df.select_dtypes(include="object"):
        df[col] = df[col].astype(str).str.strip()

    if "country" in df.columns:
        df["country"] = df["country"].str.title()

    df = df.fillna(0)

    return df


df = load_data()

# ─────────────────────────────
# SIDEBAR FILTERS
# ─────────────────────────────
st.sidebar.header("Filters")

country = st.sidebar.selectbox(
    "Country",
    ["All"] + sorted(df["country"].unique()) if "country" in df else ["All"]
)

segment = st.sidebar.selectbox(
    "Segment",
    ["All"] + sorted(df["segment"].unique()) if "segment" in df else ["All"]
)

# Apply filters
filtered = df.copy()

if country != "All" and "country" in df:
    filtered = filtered[filtered["country"] == country]

if segment != "All" and "segment" in df:
    filtered = filtered[filtered["segment"] == segment]

# ─────────────────────────────
# KPIs
# ─────────────────────────────
col1, col2, col3 = st.columns(3)

col1.metric("Clients", len(filtered))

if "sale_price" in filtered:
    col2.metric("Revenue", f"${filtered['sale_price'].sum():,.0f}")
    col3.metric("Avg Price", f"${filtered['sale_price'].mean():,.0f}")

# ─────────────────────────────
# CHARTS
# ─────────────────────────────
st.subheader("Overview")

if "client_type" in filtered:
    fig = px.pie(filtered, names="client_type", title="Client Types")
    st.plotly_chart(fig, use_container_width=True)

if "segment" in filtered and "sale_price" in filtered:
    fig = px.bar(
        filtered.groupby("segment")["sale_price"].mean().reset_index(),
        x="segment",
        y="sale_price",
        title="Avg Price by Segment"
    )
    st.plotly_chart(fig, use_container_width=True)

if "sale_price" in filtered:
    fig = px.histogram(filtered, x="sale_price", title="Price Distribution")
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────
# DATA TABLE
# ─────────────────────────────
st.subheader("Data Preview")
st.dataframe(filtered.head(100))

# ─────────────────────────────
# DOWNLOAD
# ─────────────────────────────
csv = filtered.to_csv(index=False).encode("utf-8")
st.download_button("Download Data", csv, "data.csv", "text/csv")

# ─────────────────────────────
# FOOTER
# ─────────────────────────────
st.markdown("---")
st.caption("Built with Streamlit")

