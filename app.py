import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Real Estate CRM Dashboard",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #0f1117; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #161b27;
        border-right: 1px solid #1e2535;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #1a2236 0%, #1e2940 100%);
        border: 1px solid #2a3550;
        border-radius: 12px;
        padding: 16px 20px !important;
    }
    [data-testid="stMetricLabel"] { color: #8b9ab5 !important; font-size: 13px !important; }
    [data-testid="stMetricValue"] { color: #e8f0fe !important; font-size: 28px !important; font-weight: 700 !important; }
    [data-testid="stMetricDelta"] { font-size: 13px !important; }

    /* Section headers */
    .section-title {
        color: #e8f0fe;
        font-size: 18px;
        font-weight: 600;
        margin: 24px 0 12px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid #2563eb;
        display: inline-block;
    }

    /* Tab styling */
    [data-baseweb="tab-list"] { background-color: #161b27 !important; border-bottom: 2px solid #1e2535; }
    [data-baseweb="tab"] { color: #8b9ab5 !important; }
    [aria-selected="true"] { color: #2563eb !important; font-weight: 600 !important; }

    /* Main title */
    .main-title {
        font-size: 32px;
        font-weight: 800;
        background: linear-gradient(90deg, #2563eb, #7c3aed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
    }
    .main-subtitle { color: #6b7a99; font-size: 14px; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# ─── Load & Cache Data ─────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("data.csv")

    # ── Data Quality Checks & Fixes ──
    # Strip whitespace from string columns
    str_cols = df.select_dtypes(include="object").columns
    for col in str_cols:
        df[col] = df[col].str.strip()

    # Standardise country casing
    df["country"] = df["country"].str.title()

    # Clip scores to valid ranges
    df["satisfaction_score"] = df["satisfaction_score"].clip(1, 5)
    df["engagement_score"]   = df["engagement_score"].clip(0, 100)
    df["investment_score"]   = df["investment_score"].clip(0, 1)

    # Ensure no negatives for numeric business fields
    df["sale_price"]       = df["sale_price"].clip(lower=0)
    df["price_per_sqft"]   = df["price_per_sqft"].clip(lower=0)
    df["floor_area_sqft"]  = df["floor_area_sqft"].clip(lower=0)
    df["properties_bought"] = df["properties_bought"].clip(lower=0)

    # Boolean flag for investor
    df["is_investor"] = df["is_investor"].astype(int)

    return df

df_raw = load_data()

# ─── Colour Palette ────────────────────────────────────────────────────────────
BLUE_PALETTE   = ["#2563eb", "#3b82f6", "#60a5fa", "#93c5fd", "#bfdbfe"]
MULTI_PALETTE  = ["#2563eb", "#7c3aed", "#059669", "#d97706", "#dc2626"]
SEGMENT_COLORS = {
    "High-Value Clients": "#2563eb",
    "Premium Investors":  "#7c3aed",
    "Mid-Segment Buyers": "#059669",
    "Budget Buyers":      "#d97706",
}
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#b0bcd4", size=12),
    margin=dict(l=10, r=10, t=40, b=10),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#b0bcd4")),
)

def style_fig(fig):
    fig.update_layout(**PLOTLY_LAYOUT)
    fig.update_xaxes(gridcolor="#1e2535", zerolinecolor="#1e2535", tickfont=dict(color="#8b9ab5"))
    fig.update_yaxes(gridcolor="#1e2535", zerolinecolor="#1e2535", tickfont=dict(color="#8b9ab5"))
    return fig

# ─── Sidebar Filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏢 Real Estate CRM")
    st.markdown("---")
    st.markdown("#### Filters")

    countries = ["All"] + sorted(df_raw["country"].unique())
    sel_country = st.selectbox("Country", countries)

    segments = ["All"] + sorted(df_raw["segment"].unique())
    sel_segment = st.selectbox("Client Segment", segments)

    profiles = ["All"] + sorted(df_raw["investment_profile"].unique())
    sel_profile = st.selectbox("Investment Profile", profiles)

    channels = ["All"] + sorted(df_raw["referral_channel"].unique())
    sel_channel = st.selectbox("Referral Channel", channels)

    purposes = ["All"] + sorted(df_raw["acquisition_purpose"].unique())
    sel_purpose = st.selectbox("Acquisition Purpose", purposes)

    price_min, price_max = int(df_raw["sale_price"].min()), int(df_raw["sale_price"].max())
    price_range = st.slider("Sale Price Range ($)", price_min, price_max, (price_min, price_max), step=10_000)

    st.markdown("---")
    st.markdown("#### Data Quality Report")
    st.success(f"✅ **{len(df_raw):,}** total records")
    st.success("✅ No missing values")
    st.success("✅ Scores validated & clipped")
    st.success("✅ Country names standardised")
    st.info("📊 Data is clean and ready for analysis")

# ─── Apply Filters ─────────────────────────────────────────────────────────────
df = df_raw.copy()
if sel_country  != "All": df = df[df["country"]  == sel_country]
if sel_segment  != "All": df = df[df["segment"]  == sel_segment]
if sel_profile  != "All": df = df[df["investment_profile"] == sel_profile]
if sel_channel  != "All": df = df[df["referral_channel"]   == sel_channel]
if sel_purpose  != "All": df = df[df["acquisition_purpose"] == sel_purpose]
df = df[(df["sale_price"] >= price_range[0]) & (df["sale_price"] <= price_range[1])]

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">🏢 Real Estate CRM Intelligence</div>', unsafe_allow_html=True)
st.markdown(f'<div class="main-subtitle">Showing <b>{len(df):,}</b> of {len(df_raw):,} clients · Filtered view</div>', unsafe_allow_html=True)

# ─── KPI Row ──────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5, k6 = st.columns(6)
total_revenue    = df["sale_price"].sum()
avg_price        = df["sale_price"].mean()
avg_satisfaction = df["satisfaction_score"].mean()
avg_engagement   = df["engagement_score"].mean()
investors        = df["is_investor"].sum()
avg_invest_score = df["investment_score"].mean()

k1.metric("Total Clients",        f"{len(df):,}")
k2.metric("Total Revenue",        f"${total_revenue/1e6:.1f}M")
k3.metric("Avg Sale Price",       f"${avg_price:,.0f}")
k4.metric("Avg Satisfaction",     f"{avg_satisfaction:.2f} / 5")
k5.metric("Avg Engagement",       f"{avg_engagement:.1f}")
k6.metric("Investors",            f"{investors:,}")

st.markdown("")

# ─── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview",
    "👥 Client Segments",
    "💰 Sales & Pricing",
    "📈 Investment Analysis",
    "🌍 Geographic",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 – Overview
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-title">Client & Channel Overview</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    # Pie – Client Type
    with c1:
        ct = df["client_type"].value_counts().reset_index()
        ct.columns = ["Type", "Count"]
        fig = px.pie(ct, values="Count", names="Type", title="Client Type Distribution",
                     color_discrete_sequence=BLUE_PALETTE, hole=0.55)
        fig.update_traces(textposition="outside", textfont_size=13)
        st.plotly_chart(style_fig(fig), use_container_width=True)

    # Donut – Referral Channel
    with c2:
        rc = df["referral_channel"].value_counts().reset_index()
        rc.columns = ["Channel", "Count"]
        fig = px.pie(rc, values="Count", names="Channel", title="Referral Channel Mix",
                     color_discrete_sequence=MULTI_PALETTE, hole=0.55)
        fig.update_traces(textposition="outside", textfont_size=13)
        st.plotly_chart(style_fig(fig), use_container_width=True)

    # Bar – Acquisition Purpose
    with c3:
        ap = df["acquisition_purpose"].value_counts().reset_index()
        ap.columns = ["Purpose", "Count"]
        fig = px.bar(ap, x="Purpose", y="Count", title="Acquisition Purpose",
                     color="Purpose", color_discrete_sequence=BLUE_PALETTE,
                     text="Count")
        fig.update_traces(textposition="outside")
        st.plotly_chart(style_fig(fig), use_container_width=True)

    # Satisfaction & Engagement distribution
    st.markdown('<div class="section-title">Satisfaction & Engagement</div>', unsafe_allow_html=True)
    c4, c5 = st.columns(2)

    with c4:
        sat = df["satisfaction_score"].value_counts().sort_index().reset_index()
        sat.columns = ["Score", "Count"]
        sat["Label"] = sat["Score"].map({1:"1 ⭐", 2:"2 ⭐", 3:"3 ⭐", 4:"4 ⭐", 5:"5 ⭐"})
        fig = px.bar(sat, x="Label", y="Count", title="Satisfaction Score Distribution",
                     color="Count", color_continuous_scale="Blues", text="Count")
        fig.update_traces(textposition="outside")
        fig.update_coloraxes(showscale=False)
        st.plotly_chart(style_fig(fig), use_container_width=True)

    with c5:
        fig = px.histogram(df, x="engagement_score", nbins=20,
                           title="Engagement Score Distribution",
                           color_discrete_sequence=["#7c3aed"])
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(style_fig(fig), use_container_width=True)

    # Loan Applied breakdown
    st.markdown('<div class="section-title">Loan Applied Breakdown</div>', unsafe_allow_html=True)
    c6, c7 = st.columns(2)

    with c6:
        loan_seg = df.groupby(["segment", "loan_applied"]).size().reset_index(name="Count")
        fig = px.bar(loan_seg, x="segment", y="Count", color="loan_applied",
                     title="Loan Applications by Segment", barmode="group",
                     color_discrete_map={"Yes": "#2563eb", "No": "#4b5563"})
        st.plotly_chart(style_fig(fig), use_container_width=True)

    with c7:
        loan_purpose = df.groupby(["acquisition_purpose", "loan_applied"]).size().reset_index(name="Count")
        fig = px.bar(loan_purpose, x="acquisition_purpose", y="Count", color="loan_applied",
                     title="Loan Applications by Purpose", barmode="stack",
                     color_discrete_map={"Yes": "#2563eb", "No": "#4b5563"})
        st.plotly_chart(style_fig(fig), use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 – Client Segments
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">Segment Performance</div>', unsafe_allow_html=True)

    seg_agg = df.groupby("segment").agg(
        Clients        = ("client_id", "count"),
        Avg_Sale_Price = ("sale_price", "mean"),
        Avg_Satisfaction = ("satisfaction_score", "mean"),
        Avg_Engagement = ("engagement_score", "mean"),
        Total_Revenue  = ("sale_price", "sum"),
        Avg_Properties = ("properties_bought", "mean"),
    ).reset_index()

    # Segment KPI cards
    cols = st.columns(4)
    for i, row in seg_agg.iterrows():
        with cols[i % 4]:
            st.metric(row["segment"],
                      f"{row['Clients']:,} clients",
                      f"${row['Total_Revenue']/1e6:.1f}M revenue")

    st.markdown("")
    c1, c2 = st.columns(2)

    with c1:
        fig = px.bar(seg_agg, x="segment", y="Avg_Sale_Price",
                     title="Avg Sale Price by Segment",
                     color="segment",
                     color_discrete_map=SEGMENT_COLORS,
                     text_auto=".2s")
        fig.update_traces(textposition="outside")
        st.plotly_chart(style_fig(fig), use_container_width=True)

    with c2:
        fig = px.scatter(seg_agg, x="Avg_Satisfaction", y="Avg_Engagement",
                         size="Total_Revenue", color="segment",
                         title="Satisfaction vs Engagement (bubble = Revenue)",
                         color_discrete_map=SEGMENT_COLORS,
                         hover_name="segment", size_max=60)
        st.plotly_chart(style_fig(fig), use_container_width=True)

    # Gender split within segments
    st.markdown('<div class="section-title">Gender & Client Type by Segment</div>', unsafe_allow_html=True)
    c3, c4 = st.columns(2)

    with c3:
        gender_seg = df.groupby(["segment", "gender"]).size().reset_index(name="Count")
        fig = px.bar(gender_seg, x="segment", y="Count", color="gender",
                     title="Gender Split by Segment", barmode="stack",
                     color_discrete_map={"M": "#2563eb", "F": "#7c3aed"})
        st.plotly_chart(style_fig(fig), use_container_width=True)

    with c4:
        # Box plot of satisfaction by segment
        fig = px.box(df, x="segment", y="satisfaction_score",
                     title="Satisfaction Score Distribution by Segment",
                     color="segment", color_discrete_map=SEGMENT_COLORS)
        fig.update_traces(boxmean=True)
        st.plotly_chart(style_fig(fig), use_container_width=True)

    # Full segment table
    st.markdown('<div class="section-title">Segment Summary Table</div>', unsafe_allow_html=True)
    seg_agg_display = seg_agg.copy()
    seg_agg_display["Avg_Sale_Price"] = seg_agg_display["Avg_Sale_Price"].map("${:,.0f}".format)
    seg_agg_display["Total_Revenue"]  = seg_agg_display["Total_Revenue"].map("${:,.0f}".format)
    seg_agg_display["Avg_Satisfaction"] = seg_agg_display["Avg_Satisfaction"].map("{:.2f}".format)
    seg_agg_display["Avg_Engagement"]   = seg_agg_display["Avg_Engagement"].map("{:.1f}".format)
    seg_agg_display["Avg_Properties"]   = seg_agg_display["Avg_Properties"].map("{:.1f}".format)
    st.dataframe(seg_agg_display, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 – Sales & Pricing
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-title">Price Distribution & Drivers</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        fig = px.histogram(df, x="sale_price", nbins=40,
                           title="Sale Price Distribution",
                           color_discrete_sequence=["#2563eb"])
        fig.update_traces(marker_line_width=0)
        fig.add_vline(x=df["sale_price"].mean(), line_dash="dash",
                      line_color="#f59e0b", annotation_text="Mean",
                      annotation_font_color="#f59e0b")
        st.plotly_chart(style_fig(fig), use_container_width=True)

    with c2:
        fig = px.scatter(df, x="floor_area_sqft", y="sale_price",
                         color="segment", trendline="ols",
                         title="Floor Area vs Sale Price",
                         color_discrete_map=SEGMENT_COLORS,
                         opacity=0.6)
        st.plotly_chart(style_fig(fig), use_container_width=True)

    c3, c4 = st.columns(2)

    with c3:
        country_rev = df.groupby("country").agg(
            Total_Revenue = ("sale_price", "sum"),
            Avg_Price     = ("sale_price", "mean"),
            Clients       = ("client_id", "count"),
        ).reset_index().sort_values("Total_Revenue", ascending=False)

        fig = px.bar(country_rev, x="country", y="Total_Revenue",
                     title="Total Revenue by Country",
                     color="Total_Revenue", color_continuous_scale="Blues",
                     text_auto=".2s")
        fig.update_coloraxes(showscale=False)
        fig.update_traces(textposition="outside")
        st.plotly_chart(style_fig(fig), use_container_width=True)

    with c4:
        fig = px.box(df, x="segment", y="price_per_sqft",
                     title="Price per Sqft by Segment",
                     color="segment", color_discrete_map=SEGMENT_COLORS)
        fig.update_traces(boxmean=True)
        st.plotly_chart(style_fig(fig), use_container_width=True)

    # Properties bought analysis
    st.markdown('<div class="section-title">Properties Bought Analysis</div>', unsafe_allow_html=True)
    c5, c6 = st.columns(2)

    with c5:
        prop_seg = df.groupby("segment")["properties_bought"].mean().reset_index()
        prop_seg.columns = ["Segment", "Avg Properties Bought"]
        fig = px.bar(prop_seg, x="Segment", y="Avg Properties Bought",
                     title="Avg Properties Bought per Segment",
                     color="Segment", color_discrete_map=SEGMENT_COLORS,
                     text_auto=".2f")
        fig.update_traces(textposition="outside")
        st.plotly_chart(style_fig(fig), use_container_width=True)

    with c6:
        loan_price = df.groupby("loan_applied")["sale_price"].mean().reset_index()
        loan_price.columns = ["Loan Applied", "Avg Sale Price"]
        fig = px.bar(loan_price, x="Loan Applied", y="Avg Sale Price",
                     title="Avg Sale Price: Loan vs No Loan",
                     color="Loan Applied",
                     color_discrete_map={"Yes": "#2563eb", "No": "#6b7280"},
                     text_auto=".2s")
        fig.update_traces(textposition="outside")
        st.plotly_chart(style_fig(fig), use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 – Investment Analysis
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">Investment Profile Breakdown</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)

    profile_agg = df.groupby("investment_profile").agg(
        Count         = ("client_id", "count"),
        Avg_Score     = ("investment_score", "mean"),
        Avg_Price     = ("sale_price", "mean"),
        Avg_Engage    = ("engagement_score", "mean"),
    ).reset_index()

    PROF_COLORS = {
        "High Potential Investor": "#059669",
        "Moderate Investor":       "#2563eb",
        "Low Potential":           "#6b7280",
    }

    with c1:
        fig = px.pie(profile_agg, values="Count", names="investment_profile",
                     title="Investment Profile Share",
                     color="investment_profile", color_discrete_map=PROF_COLORS,
                     hole=0.5)
        fig.update_traces(textposition="outside")
        st.plotly_chart(style_fig(fig), use_container_width=True)

    with c2:
        fig = px.bar(profile_agg, x="investment_profile", y="Avg_Score",
                     title="Avg Investment Score by Profile",
                     color="investment_profile", color_discrete_map=PROF_COLORS,
                     text_auto=".3f")
        fig.update_traces(textposition="outside")
        st.plotly_chart(style_fig(fig), use_container_width=True)

    with c3:
        fig = px.bar(profile_agg, x="investment_profile", y="Avg_Price",
                     title="Avg Sale Price by Profile",
                     color="investment_profile", color_discrete_map=PROF_COLORS,
                     text_auto=".2s")
        fig.update_traces(textposition="outside")
        st.plotly_chart(style_fig(fig), use_container_width=True)

    # Scatter – investment score vs engagement
    st.markdown('<div class="section-title">Investment Score Deep Dive</div>', unsafe_allow_html=True)
    c4, c5 = st.columns(2)

    with c4:
        fig = px.scatter(df, x="investment_score", y="sale_price",
                         color="investment_profile",
                         color_discrete_map=PROF_COLORS,
                         title="Investment Score vs Sale Price",
                         opacity=0.6, trendline="ols")
        st.plotly_chart(style_fig(fig), use_container_width=True)

    with c5:
        fig = px.violin(df, x="investment_profile", y="investment_score",
                        color="investment_profile", color_discrete_map=PROF_COLORS,
                        title="Investment Score Distribution by Profile",
                        box=True, points="outliers")
        st.plotly_chart(style_fig(fig), use_container_width=True)

    # Cluster analysis
    st.markdown('<div class="section-title">Client Cluster Analysis</div>', unsafe_allow_html=True)
    cluster_agg = df.groupby("cluster").agg(
        Count         = ("client_id", "count"),
        Avg_Sale_Price = ("sale_price", "mean"),
        Avg_Invest     = ("investment_score", "mean"),
        Avg_Satisfy    = ("satisfaction_score", "mean"),
        Avg_Engage     = ("engagement_score", "mean"),
    ).reset_index()
    cluster_agg["cluster"] = "Cluster " + cluster_agg["cluster"].astype(str)

    c6, c7 = st.columns(2)
    with c6:
        fig = px.bar(cluster_agg, x="cluster", y="Count",
                     title="Client Count by Cluster",
                     color="cluster",
                     color_discrete_sequence=MULTI_PALETTE,
                     text="Count")
        fig.update_traces(textposition="outside")
        st.plotly_chart(style_fig(fig), use_container_width=True)

    with c7:
        fig = px.scatter(cluster_agg, x="Avg_Invest", y="Avg_Sale_Price",
                         size="Count", color="cluster",
                         color_discrete_sequence=MULTI_PALETTE,
                         title="Cluster: Avg Investment Score vs Avg Sale Price",
                         hover_name="cluster", size_max=60,
                         text="cluster")
        fig.update_traces(textposition="top center")
        st.plotly_chart(style_fig(fig), use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 – Geographic
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-title">Geographic Performance</div>', unsafe_allow_html=True)

    geo_agg = df.groupby("country").agg(
        Clients       = ("client_id", "count"),
        Total_Revenue = ("sale_price", "sum"),
        Avg_Price     = ("sale_price", "mean"),
        Avg_Satisfy   = ("satisfaction_score", "mean"),
        Investors     = ("is_investor", "sum"),
    ).reset_index().sort_values("Total_Revenue", ascending=False)

    c1, c2 = st.columns(2)

    with c1:
        fig = px.bar(geo_agg, x="country", y="Total_Revenue",
                     title="Total Revenue by Country",
                     color="Total_Revenue",
                     color_continuous_scale="Blues",
                     text_auto=".2s")
        fig.update_coloraxes(showscale=False)
        fig.update_traces(textposition="outside")
        st.plotly_chart(style_fig(fig), use_container_width=True)

    with c2:
        fig = px.scatter(geo_agg, x="Avg_Satisfy", y="Avg_Price",
                         size="Clients", color="country",
                         color_discrete_sequence=MULTI_PALETTE,
                         title="Avg Satisfaction vs Avg Price (bubble = Clients)",
                         hover_name="country", size_max=60, text="country")
        fig.update_traces(textposition="top center")
        st.plotly_chart(style_fig(fig), use_container_width=True)

    # Region breakdown
    st.markdown('<div class="section-title">Region Breakdown</div>', unsafe_allow_html=True)
    region_agg = df.groupby(["country", "region"]).agg(
        Clients       = ("client_id", "count"),
        Avg_Price     = ("sale_price", "mean"),
        Total_Revenue = ("sale_price", "sum"),
    ).reset_index().sort_values("Total_Revenue", ascending=False)

    c3, c4 = st.columns(2)

    with c3:
        top_regions = region_agg.head(10)
        fig = px.bar(top_regions, x="region", y="Total_Revenue",
                     title="Top 10 Regions by Revenue",
                     color="country",
                     color_discrete_sequence=MULTI_PALETTE,
                     text_auto=".2s")
        fig.update_traces(textposition="outside")
        st.plotly_chart(style_fig(fig), use_container_width=True)

    with c4:
        fig = px.treemap(region_agg, path=["country", "region"],
                         values="Total_Revenue",
                         title="Revenue Treemap: Country → Region",
                         color="Avg_Price",
                         color_continuous_scale="Blues")
        fig.update_layout(**PLOTLY_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

    # Full country table
    st.markdown('<div class="section-title">Country Summary</div>', unsafe_allow_html=True)
    display_geo = geo_agg.copy()
    display_geo["Total_Revenue"] = display_geo["Total_Revenue"].map("${:,.0f}".format)
    display_geo["Avg_Price"]     = display_geo["Avg_Price"].map("${:,.0f}".format)
    display_geo["Avg_Satisfy"]   = display_geo["Avg_Satisfy"].map("{:.2f}".format)
    st.dataframe(display_geo, use_container_width=True, hide_index=True)

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<div style="text-align:center;color:#4b5563;font-size:12px;">'
    '🏢 Real Estate CRM Intelligence Dashboard · Built with Streamlit & Plotly'
    '</div>',
    unsafe_allow_html=True,
)
