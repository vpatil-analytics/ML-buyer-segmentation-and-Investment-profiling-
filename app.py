import streamlit as st
import pandas as pd
import plotly.express as px

# ─── PAGE CONFIG ─────────────────────────────
st.set_page_config(
    page_title="Real Estate CRM Dashboard",
    page_icon="🏢",
    layout="wide"
)

# ─── PREMIUM DARK UI ─────────────────────────
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #0f172a 0%, #020617 100%);
}
[data-testid="stSidebar"] {
    background: #020617;
    border-right: 1px solid #1e293b;
}
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #1e293b, #0f172a);
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 15px;
}
[data-testid="stMetricValue"] {
    color: #e0f2fe;
    font-weight: 700;
}
[data-testid="stMetricLabel"] {
    color: #94a3b8;
}
h1, h2, h3 {
    color: #e2e8f0;
}
.stDownloadButton button {
    background: linear-gradient(90deg, #2563eb, #7c3aed);
    color: white;
    border-radius: 8px;
    border: none;
}
</style>
""", unsafe_allow_html=True)

# ─── COLOR PALETTE ───────────────────────────
COLORS = ["#2563eb", "#7c3aed", "#059669", "#f59e0b", "#ef4444"]

def style_fig(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#cbd5e1"),
        margin=dict(l=10, r=10, t=40, b=10)
    )
    fig.update_xaxes(gridcolor="#1e293b")
    fig.update_yaxes(gridcolor="#1e293b")
    return fig

# ─── LOAD DATA ───────────────────────────────
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data.csv")
    except:
        st.error("❌ data.csv not found")
        st.stop()

    df.columns = df.columns.str.strip()

    num_cols = ["sale_price", "floor_area_sqft", "engagement_score"]
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.fillna(0)
    return df

df_raw = load_data()

# ─── SIDEBAR ─────────────────────────────────
st.sidebar.title("🔍 Filters")

def safe(col):
    if col in df_raw.columns:
        return ["All"] + sorted(df_raw[col].unique())
    return ["All"]

country = st.sidebar.selectbox("Country", safe("country"))
segment = st.sidebar.selectbox("Segment", safe("segment"))

if "sale_price" in df_raw.columns:
    min_p = int(df_raw["sale_price"].min())
    max_p = int(df_raw["sale_price"].max())
    price = st.sidebar.slider("Price Range", min_p, max_p, (min_p, max_p))
else:
    price = (0, 0)

# ─── FILTER DATA ─────────────────────────────
df = df_raw.copy()

if country != "All" and "country" in df:
    df = df[df["country"] == country]

if segment != "All" and "segment" in df:
    df = df[df["segment"] == segment]

if "sale_price" in df:
    df = df[(df["sale_price"] >= price[0]) & (df["sale_price"] <= price[1])]

if df.empty:
    st.warning("⚠️ No data found")
    st.stop()

# ─── HEADER ──────────────────────────────────
st.markdown("""
<h1 style='
    background: linear-gradient(90deg,#2563eb,#7c3aed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size:36px;
    font-weight:800;
'>
🏢 Real Estate CRM Intelligence Dashboard
</h1>
""", unsafe_allow_html=True)

st.caption(f"Showing {len(df):,} records")

# ─── KPIs ───────────────────────────────────
c1, c2, c3, c4 = st.columns(4)

total_rev = df["sale_price"].sum()
avg_price = df["sale_price"].mean()

c1.metric("Clients", len(df))
c2.metric("Revenue", f"${total_rev:,.0f}")
c3.metric("Avg Price", f"${avg_price:,.0f}")

if "is_investor" in df:
    c4.metric("Investors", int(df["is_investor"].sum()))
else:
    c4.metric("Investors", "N/A")

st.markdown("---")

# ─── TABS ───────────────────────────────────
tab1, tab2, tab3 = st.tabs(["Overview", "Segments", "Pricing"])

# ─── OVERVIEW ───────────────────────────────
with tab1:
    col1, col2 = st.columns(2)

    if "client_type" in df:
        ct = df["client_type"].value_counts().reset_index()
        ct.columns = ["Type", "Count"]
        fig = px.pie(ct, values="Count", names="Type",
                     color_discrete_sequence=COLORS, hole=0.5)
        col1.plotly_chart(style_fig(fig), use_container_width=True, key="pie1")

    if "referral_channel" in df:
        rc = df["referral_channel"].value_counts().reset_index()
        rc.columns = ["Channel", "Count"]
        fig = px.pie(rc, values="Count", names="Channel",
                     color_discrete_sequence=COLORS, hole=0.5)
        col2.plotly_chart(style_fig(fig), use_container_width=True, key="pie2")

    if "engagement_score" in df:
        fig = px.histogram(df, x="engagement_score",
                           color_discrete_sequence=["#3b82f6"])
        st.plotly_chart(style_fig(fig), use_container_width=True, key="hist1")

# ─── SEGMENTS ───────────────────────────────
with tab2:
    if "segment" in df:
        seg = df.groupby("segment")["sale_price"].mean().reset_index()

        fig = px.bar(seg, x="segment", y="sale_price",
                     color="segment",
                     color_discrete_sequence=COLORS,
                     text_auto=".2s")

        st.plotly_chart(style_fig(fig), use_container_width=True, key="bar1")

# ─── PRICING ────────────────────────────────
with tab3:
    col1, col2 = st.columns(2)

    fig = px.histogram(df, x="sale_price",
                       color_discrete_sequence=["#2563eb"])
    col1.plotly_chart(style_fig(fig), use_container_width=True, key="hist2")

    if "floor_area_sqft" in df:
        fig = px.scatter(df, x="floor_area_sqft", y="sale_price",
                         color="segment",
                         color_discrete_sequence=COLORS,
                         opacity=0.7)
        col2.plotly_chart(style_fig(fig), use_container_width=True, key="scatter1")

# ─── TABLE ──────────────────────────────────
st.subheader("📊 Data Preview")
st.dataframe(df.head(100), use_container_width=True)

# ─── DOWNLOAD ───────────────────────────────
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("📥 Download Data", csv, "data.csv", "text/csv")

# ─── FOOTER ─────────────────────────────────
st.markdown("---")
st.caption("Built with Streamlit | Professional Dashboard")
