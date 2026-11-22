"""
PartPulse - Public NHTSA Quality Signal Radar
A presentation-ready automotive quality intelligence web application.
Explores recurring customer-reported vehicle concerns using public NHTSA complaint data.
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data_engine import (
    fetch_nhtsa_complaints,
    normalize_complaints,
    extract_component_frequencies,
)

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & METADATA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="PartPulse | Automotive Quality Signal Radar",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Popular makes catalog
FEATURED_MAKES = [
    "Jeep",
    "Ford",
    "Tesla",
    "Honda",
    "Toyota",
    "Chevrolet",
    "Ram",
    "Dodge",
    "Chrysler",
    "BMW",
    "Mercedes-Benz",
    "Hyundai",
    "Kia",
    "Subaru",
    "Nissan",
    "Volkswagen",
    "Rivian",
    "Volvo",
    "Audi",
    "Mazda",
]

# Quick presets for prominent industry demo cases
DEMO_PRESETS = [
    {
        "label": "🚙 2019 Jeep Wrangler",
        "make": "Jeep",
        "model": "Wrangler",
        "year": 2019,
        "tag": "Steering oscillation / 'Death Wobble'",
    },
    {
        "label": "🛻 2021 Ford F-150",
        "make": "Ford",
        "model": "F-150",
        "year": 2021,
        "tag": "Powertrain & 10-speed transmission shifts",
    },
    {
        "label": "🚗 2020 Honda Civic",
        "make": "Honda",
        "model": "Civic",
        "year": 2020,
        "tag": "Electric power steering sticky feel",
    },
    {
        "label": "⚡ 2022 Tesla Model 3",
        "make": "Tesla",
        "model": "Model 3",
        "year": 2022,
        "tag": "Forward collision & phantom braking reports",
    },
    {
        "label": "🚐 2020 Chrysler Pacifica",
        "make": "Chrysler",
        "model": "Pacifica",
        "year": 2020,
        "tag": "Electrical system & engine stall investigations",
    },
]

# -----------------------------------------------------------------------------
# 2. CUSTOM STYLING (Dark Ink, Slate, Teal Accent, Amber Alert)
# -----------------------------------------------------------------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #0F172A;
}

.stApp {
    background-color: #F8FAFC;
}

/* Header bar container */
.brand-hero {
    background: linear-gradient(135deg, #091726 0%, #102a43 65%, #0B3B48 100%);
    border-radius: 16px;
    padding: 28px 32px;
    color: #FFFFFF;
    margin-bottom: 24px;
    box-shadow: 0 10px 25px -5px rgba(9, 23, 38, 0.25);
    border: 1px solid rgba(255, 255, 255, 0.08);
}

.brand-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(20, 184, 166, 0.15);
    color: #2DD4BF;
    border: 1px solid rgba(45, 212, 191, 0.35);
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 4px 10px;
    border-radius: 20px;
    margin-bottom: 12px;
}

.brand-badge::before {
    content: "";
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #2DD4BF;
    box-shadow: 0 0 8px #2DD4BF;
}

.brand-title {
    font-size: 32px;
    font-weight: 800;
    letter-spacing: -0.03em;
    margin: 0 0 8px 0;
    color: #FFFFFF;
}

.brand-subtitle {
    font-size: 14.5px;
    color: #94A3B8;
    max-width: 820px;
    line-height: 1.55;
    margin: 0;
}

/* Metric KPI Cards */
.kpi-container {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 18px 20px;
    box-shadow: 0 2px 4px rgba(15, 23, 42, 0.03);
    height: 100%;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.kpi-container:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 16px rgba(15, 23, 42, 0.06);
}

.kpi-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #64748B;
    margin-bottom: 6px;
}

.kpi-value {
    font-size: 26px;
    font-weight: 800;
    letter-spacing: -0.03em;
    color: #0F172A;
    line-height: 1.2;
}

.kpi-note {
    font-size: 12px;
    color: #64748B;
    margin-top: 6px;
}

.kpi-amber {
    border-left: 4px solid #D97706;
}

.kpi-teal {
    border-left: 4px solid #0D9488;
}

.kpi-rose {
    border-left: 4px solid #E11D48;
}

/* Section Containers */
.card-box {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 22px 24px;
    box-shadow: 0 2px 4px rgba(15, 23, 42, 0.02);
    margin-bottom: 20px;
}

.section-heading {
    font-size: 18px;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: #0F172A;
    margin-bottom: 4px;
}

.section-subheading {
    font-size: 13px;
    color: #64748B;
    margin-bottom: 16px;
}

/* Custom quote narrative styling */
.narrative-quote {
    background: #F8FAFC;
    border-left: 3px solid #0D9488;
    padding: 12px 16px;
    border-radius: 0 8px 8px 0;
    font-size: 13.5px;
    line-height: 1.6;
    color: #334155;
    margin: 8px 0;
}

/* Pills & Badges */
.pill-tag {
    display: inline-block;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 600;
    border-radius: 6px;
    margin-right: 4px;
}
.pill-danger {
    background: #FEE2E2;
    color: #991B1B;
    border: 1px solid #FECACA;
}
.pill-warn {
    background: #FEF3C7;
    color: #92400E;
    border: 1px solid #FDE68A;
}
.pill-info {
    background: #E0F2FE;
    color: #075985;
    border: 1px solid #BAE6FD;
}
.pill-neutral {
    background: #F1F5F9;
    color: #475569;
    border: 1px solid #E2E8F0;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: #F1F5F9;
    border-right: 1px solid #E2E8F0;
}
</style>
""",
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# 3. CACHED API WRAPPER
# -----------------------------------------------------------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def get_cached_complaints(
    make: str, model: str, year: int
) -> Tuple[List[Dict], Optional[str]]:
    """Cached wrapper around data_engine.fetch_nhtsa_complaints."""
    return fetch_nhtsa_complaints(make, model, year)


# -----------------------------------------------------------------------------
# 4. SESSION STATE & NAVIGATION
# -----------------------------------------------------------------------------
if "active_make" not in st.session_state:
    st.session_state.active_make = "Jeep"
if "active_model" not in st.session_state:
    st.session_state.active_model = "Wrangler"
if "active_year" not in st.session_state:
    st.session_state.active_year = 2019


def select_preset(preset: Dict):
    st.session_state.active_make = preset["make"]
    st.session_state.active_model = preset["model"]
    st.session_state.active_year = preset["year"]


# -----------------------------------------------------------------------------
# 5. UI: HERO HEADER & PRODUCT CONTEXT
# -----------------------------------------------------------------------------
st.markdown(
    """
<div class="brand-hero">
    <div class="brand-badge">Public NHTSA Quality Signal Radar · Prototype</div>
    <h1 class="brand-title">PartPulse</h1>
    <p class="brand-subtitle">
        Empowering automotive quality reviewers, warranty teams, and reliability engineers to explore recurring 
        customer-reported vehicle concerns filed with the U.S. National Highway Traffic Safety Administration (NHTSA). 
        Surfaces patterns to guide human technical investigation.
    </p>
</div>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 6. SIDEBAR CONTROLS & QUICK PRESETS
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🔍 Vehicle Search")
    st.caption("Query the federal NHTSA complaints database by vehicle identification.")

    # Make selection
    current_make = st.session_state.active_make
    make_index = (
        FEATURED_MAKES.index(current_make) if current_make in FEATURED_MAKES else 0
    )
    selected_make = st.selectbox(
        "Make",
        options=FEATURED_MAKES + ["Other (Custom)"],
        index=make_index,
        help="Automobile manufacturer name as recognized by NHTSA.",
    )

    if selected_make == "Other (Custom)":
        custom_make = st.text_input(
            "Enter custom make",
            value=st.session_state.active_make
            if current_make not in FEATURED_MAKES
            else "",
            placeholder="e.g. Genesis",
        )
        active_make_input = custom_make.strip()
    else:
        active_make_input = selected_make

    # Model input
    active_model_input = st.text_input(
        "Model",
        value=st.session_state.active_model,
        placeholder="e.g. Wrangler, F-150, Civic",
        help="Vehicle model name. Note: some vehicles use hyphens (e.g. 'F-150').",
    )

    # Year input
    current_year = datetime.now().year
    active_year_input = st.number_input(
        "Model Year",
        min_value=1995,
        max_value=current_year + 1,
        value=int(st.session_state.active_year),
        step=1,
        help="Four-digit model year.",
    )

    # Search Trigger Button
    search_submitted = st.button(
        "⚡ Analyze Vehicle Reports",
        use_container_width=True,
        type="primary",
    )

    if search_submitted:
        st.session_state.active_make = active_make_input
        st.session_state.active_model = active_model_input.strip()
        st.session_state.active_year = int(active_year_input)
        st.rerun()

    st.markdown("---")
    st.markdown("### 💡 Quick Case Studies")
    st.caption("Click any high-profile vehicle case to instantly load real data:")

    for idx, preset in enumerate(DEMO_PRESETS):
        if st.button(
            preset["label"],
            key=f"preset_btn_{idx}",
            use_container_width=True,
            help=f"{preset['tag']} ({preset['year']} {preset['make']} {preset['model']})",
        ):
            select_preset(preset)
            st.rerun()

    st.markdown("---")
    st.caption(
        "**Engineering Note**: Complaints are owner-submitted narratives. "
        "They surface exploration signals, not confirmed engineering defects or fleet failure rates."
    )

# Active target query values
target_make = st.session_state.active_make
target_model = st.session_state.active_model
target_year = st.session_state.active_year

# -----------------------------------------------------------------------------
# 7. PROMINENT VEHICLE STATUS BAR
# -----------------------------------------------------------------------------
status_col1, status_col2 = st.columns([3, 1])
with status_col1:
    st.markdown(
        f"""
    <div style="display:flex; align-items:center; gap:12px; margin-bottom: 16px;">
        <span style="font-size:24px; font-weight:800; color:#0F172A; letter-spacing:-0.03em;">
            {target_year} {target_make} {target_model}
        </span>
        <span class="pill-tag pill-info" style="font-size:12px;">Official NHTSA Records</span>
    </div>
    """,
        unsafe_allow_html=True,
    )
with status_col2:
    st.caption(f"Last updated from API: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# Validation check
if not target_model:
    st.warning("⚠️ Please provide a vehicle model name in the left sidebar to query.")
    st.stop()

# -----------------------------------------------------------------------------
# 8. DATA ACQUISITION WITH LOADING & ERROR STATES
# -----------------------------------------------------------------------------
with st.spinner(
    f"Querying NHTSA complaints database for {target_year} {target_make} {target_model}..."
):
    raw_data, api_error = get_cached_complaints(
        target_make, target_model, target_year
    )

if api_error:
    st.error(f"❌ **API Connectivity Issue**: {api_error}")
    st.info(
        "💡 **Troubleshooting Tip**: The federal NHTSA API can occasionally experience temporary latency. "
        "Try re-submitting or testing another model like the 2019 Jeep Wrangler."
    )
    st.stop()

df_complaints = normalize_complaints(raw_data)
total_reports = len(df_complaints)

# Empty result handling
if total_reports == 0:
    st.markdown(
        f"""
    <div class="card-box" style="text-align:center; padding: 48px 24px;">
        <div style="font-size:48px; margin-bottom: 12px;">🔍</div>
        <div class="section-heading" style="font-size: 20px;">No Complaints Found</div>
        <p style="color:#64748B; max-width: 540px; margin: 8px auto 20px auto; font-size:14px;">
            NHTSA has zero complaint filings on record for <strong>{target_year} {target_make} {target_model}</strong>.
            This may occur if the vehicle is very newly released, sold in very low volume, or if the model name is spelled 
            differently in NHTSA's federal registry (e.g. 'F-150' vs 'F150', or 'RAV4' vs 'RAV 4').
        </p>
        <div style="display:flex; justify-content:center; gap:10px;">
            <span class="pill-tag pill-neutral">Verify spelling in sidebar</span>
            <span class="pill-tag pill-neutral">Try an adjacent model year</span>
            <span class="pill-tag pill-info">Try a preset case study</span>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.stop()

# -----------------------------------------------------------------------------
# 9. RESULTS OVERVIEW: EXECUTIVE KPI CARDS & EXPLAINABLE SIGNALS
# -----------------------------------------------------------------------------
comp_df = extract_component_frequencies(df_complaints)
top_comp_name = comp_df.iloc[0]["Component"] if not comp_df.empty else "N/A"
top_comp_share = comp_df.iloc[0]["Percentage"] if not comp_df.empty else 0.0

crash_count = int(df_complaints["crash"].sum())
fire_count = int(df_complaints["fire"].sum())
injury_count = int(df_complaints["injuries"].sum())
death_count = int(df_complaints["deaths"].sum())
safety_flagged_count = int(df_complaints["safety_flag"].sum())

# Explainable Safety Incident Signal Index
# Formula: (Count of complaints that flagged a crash, fire, or injury) / Total complaints * 100
safety_co_index = (
    round((safety_flagged_count / total_reports) * 100, 1) if total_reports > 0 else 0.0
)

kpi_cols = st.columns(5)

with kpi_cols[0]:
    st.markdown(
        f"""
    <div class="kpi-container kpi-teal">
        <div class="kpi-label">Total Reports</div>
        <div class="kpi-value">{total_reports:,}</div>
        <div class="kpi-note">Owner filings with NHTSA</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with kpi_cols[1]:
    st.markdown(
        f"""
    <div class="kpi-container kpi-teal">
        <div class="kpi-label">Top Concern</div>
        <div class="kpi-value" style="font-size:18px; padding-top:4px;" title="{top_comp_name}">
            {top_comp_name[:16] + ('…' if len(top_comp_name) > 16 else '')}
        </div>
        <div class="kpi-note">{top_comp_share}% of total reports</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with kpi_cols[2]:
    st.markdown(
        f"""
    <div class="kpi-container kpi-amber">
        <div class="kpi-label">Crash Flagged</div>
        <div class="kpi-value">{crash_count:,}</div>
        <div class="kpi-note">{round((crash_count/total_reports)*100, 1)}% of reports</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with kpi_cols[3]:
    st.markdown(
        f"""
    <div class="kpi-container kpi-rose">
        <div class="kpi-label">Fire Flagged</div>
        <div class="kpi-value">{fire_count:,}</div>
        <div class="kpi-note">{round((fire_count/total_reports)*100, 1)}% of reports</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with kpi_cols[4]:
    st.markdown(
        f"""
    <div class="kpi-container kpi-amber">
        <div class="kpi-label">Incident Signal Index</div>
        <div class="kpi-value">{safety_co_index}%</div>
        <div class="kpi-note">{safety_flagged_count} reports flag crash/fire/inj.</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

# Explanation callout for the Signal Index
st.caption(
    "📐 **Signal Metric Formula**: `Incident Signal Index = (Reports with Crash, Fire, or Injury / Total Reports) × 100`. "
    "This measures the proportion of filed complaints that involve acute safety events. "
    "It is strictly an exploratory prioritization metric, **not** a defect rate or vehicle failure probability."
)

st.markdown("<br>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 10. VISUAL ANALYTICS: TIMELINE & COMPONENT FREQUENCY
# -----------------------------------------------------------------------------
chart_col_left, chart_col_right = st.columns([1.15, 1])

with chart_col_left:
    st.markdown(
        """
    <div class="section-heading">📈 Complaint Filing Timeline</div>
    <div class="section-subheading">Monthly complaint volume filed with NHTSA over vehicle lifecycle</div>
    """,
        unsafe_allow_html=True,
    )

    valid_dates = df_complaints.dropna(subset=["parsed_date"]).copy()
    if not valid_dates.empty:
        valid_dates["YearMonth"] = (
            valid_dates["parsed_date"].dt.to_period("M").dt.to_timestamp()
        )
        timeline_df = (
            valid_dates.groupby("YearMonth", as_index=False)
            .size()
            .rename(columns={"size": "Reports"})
        )

        fig_timeline = px.area(
            timeline_df,
            x="YearMonth",
            y="Reports",
            labels={"YearMonth": "Filing Date", "Reports": "Complaints Filed"},
            color_discrete_sequence=["#0D9488"],
        )
        fig_timeline.update_traces(
            line=dict(width=2.5, color="#0D9488"),
            fillcolor="rgba(13, 148, 136, 0.15)",
            hovertemplate="<b>%{x|%b %Y}</b><br>Complaints Filed: %{y:,}<extra></extra>",
        )
        fig_timeline.update_layout(
            height=320,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Plus Jakarta Sans", color="#64748B", size=12),
            hovermode="x unified",
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                title=None,
                tickfont=dict(color="#64748B"),
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor="#E2E8F0",
                zeroline=False,
                title=None,
                rangemode="tozero",
                tickfont=dict(color="#64748B"),
            ),
        )
        st.plotly_chart(fig_timeline, use_container_width=True)
    else:
        st.info("Filing dates were unavailable in the retrieved records.")

with chart_col_right:
    st.markdown(
        """
    <div class="section-heading">⚙️ Top 10 Mentioned Components</div>
    <div class="section-subheading">Relative frequency in returned reports (atomic part categorization)</div>
    """,
        unsafe_allow_html=True,
    )

    if not comp_df.empty:
        top_10_comps = comp_df.head(10).sort_values("Count", ascending=True)

        # Highlight the #1 component with amber/accent
        bar_colors = [
            "#D97706" if i == len(top_10_comps) - 1 else "#0D9488"
            for i in range(len(top_10_comps))
        ]

        fig_comps = go.Figure(
            go.Bar(
                x=top_10_comps["Count"],
                y=top_10_comps["Component"],
                orientation="h",
                marker=dict(color=bar_colors),
                text=top_10_comps.apply(
                    lambda r: f"{r['Count']} ({r['Percentage']}%)", axis=1
                ),
                textposition="auto",
                hovertemplate="<b>%{y}</b><br>Reports: %{x:,}<extra></extra>",
            )
        )
        fig_comps.update_layout(
            height=320,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Plus Jakarta Sans", color="#64748B", size=11),
            xaxis=dict(showgrid=True, gridcolor="#E2E8F0", zeroline=False, title=None),
            yaxis=dict(showgrid=False, zeroline=False, title=None),
        )
        st.plotly_chart(fig_comps, use_container_width=True)
    else:
        st.info("No component labels available to chart.")

st.markdown("<br>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 11. DEEP REPORT EXPLORER WITH REAL-TIME FILTERING & EXCERPTS
# -----------------------------------------------------------------------------
st.markdown(
    """
<div class="section-heading">🔬 Owner Complaint Explorer</div>
<div class="section-subheading">
    Inspect raw customer-submitted narratives, affected assemblies, and federal ODI identifiers.
</div>
""",
    unsafe_allow_html=True,
)

with st.container():
    # Filtering control row
    filt_c1, filt_c2, filt_c3, filt_c4 = st.columns([1.5, 1.2, 1, 0.8])

    with filt_c1:
        keyword_query = st.text_input(
            "Search description keywords",
            placeholder="e.g. death wobble, stall, lockup, vibration...",
            help="Case-insensitive text search within the owner complaint summary.",
        )

    with filt_c2:
        all_comps_list = sorted(comp_df["Component"].unique().tolist())
        selected_component_filter = st.selectbox(
            "Filter by primary component",
            options=["All Components"] + all_comps_list,
            index=0,
        )

    with filt_c3:
        safety_option = st.selectbox(
            "Safety Incident Flag",
            options=[
                "All Reports",
                "Crash Only",
                "Fire Only",
                "Injury/Death Only",
                "Any Incident (Crash/Fire/Inj)",
            ],
            index=0,
        )

    with filt_c4:
        sort_order = st.selectbox(
            "Sort order",
            options=["Newest First", "Oldest First"],
            index=0,
        )

# Apply filters
df_filtered = df_complaints.copy()

# 1. Keyword search filter
if keyword_query:
    kw = keyword_query.strip().lower()
    df_filtered = df_filtered[
        df_filtered["summary"].str.lower().str.contains(kw, na=False)
        | df_filtered["components"].str.lower().str.contains(kw, na=False)
        | df_filtered["odi_number"].str.contains(kw, na=False)
    ]

# 2. Component filter
if selected_component_filter != "All Components":
    df_filtered = df_filtered[
        df_filtered["components"]
        .str.upper()
        .str.contains(selected_component_filter.upper(), na=False)
    ]

# 3. Safety flag filter
if safety_option == "Crash Only":
    df_filtered = df_filtered[df_filtered["crash"]]
elif safety_option == "Fire Only":
    df_filtered = df_filtered[df_filtered["fire"]]
elif safety_option == "Injury/Death Only":
    df_filtered = df_filtered[
        (df_filtered["injuries"] > 0) | (df_filtered["deaths"] > 0)
    ]
elif safety_option == "Any Incident (Crash/Fire/Inj)":
    df_filtered = df_filtered[df_filtered["safety_flag"]]

# 4. Sorting
if sort_order == "Newest First":
    df_filtered = df_filtered.sort_values(
        "parsed_date", ascending=False, na_position="last"
    )
else:
    df_filtered = df_filtered.sort_values(
        "parsed_date", ascending=True, na_position="last"
    )

# Result count summary & CSV export button row
exp_col_left, exp_col_right = st.columns([2, 1])

with exp_col_left:
    st.markdown(
        f"**Displaying {len(df_filtered):,} of {total_reports:,} reports** matching active filters."
    )

with exp_col_right:
    # Prepare clean CSV for download
    csv_export_df = df_filtered[
        [
            "odi_number",
            "report_date",
            "incident_date",
            "components",
            "crash",
            "fire",
            "injuries",
            "deaths",
            "vin",
            "summary",
        ]
    ].rename(
        columns={
            "odi_number": "ODI_ID",
            "report_date": "Report_Date",
            "incident_date": "Incident_Date",
            "components": "Components_Reported",
            "crash": "Crash_Flag",
            "fire": "Fire_Flag",
            "injuries": "Injuries",
            "deaths": "Deaths",
            "vin": "Masked_VIN",
            "summary": "Owner_Summary",
        }
    )
    csv_bytes = csv_export_df.to_csv(index=False).encode("utf-8")
    sanitized_filename = f"PartPulse_{target_year}_{target_make}_{target_model}_reports.csv".replace(
        " ", "_"
    )

    st.download_button(
        label="📥 Export Filtered Reports (CSV)",
        data=csv_bytes,
        file_name=sanitized_filename,
        mime="text/csv",
        use_container_width=True,
    )

# -----------------------------------------------------------------------------
# 12. TABBED EXPLORER: EVIDENCE CARDS & DATA TABLE
# -----------------------------------------------------------------------------
tab_cards, tab_table = st.tabs(
    ["📑 Detailed Complaint Evidence Cards", "📊 Structured Data Table"]
)

with tab_cards:
    if df_filtered.empty:
        st.info("No complaint reports match the currently selected filter criteria.")
    else:
        # Show top 50 matches for performance and readability
        records_to_show = df_filtered.head(50)
        if len(df_filtered) > 50:
            st.caption(
                f"Showing first 50 of {len(df_filtered):,} matching reports for fast review. Use the CSV download above to access the complete list."
            )

        for _, row in records_to_show.iterrows():
            odi = row["odi_number"]
            rep_date = row["report_date"] or "Date Unspecified"
            comp = row["components"]
            summ = row["summary"] or "No detailed owner summary provided."
            has_crash = row["crash"]
            has_fire = row["fire"]
            injuries = row["injuries"]

            # Badges header
            badges_html = ""
            if has_crash:
                badges_html += '<span class="pill-tag pill-danger">💥 CRASH</span>'
            if has_fire:
                badges_html += '<span class="pill-tag pill-danger">🔥 FIRE</span>'
            if injuries > 0:
                badges_html += (
                    f'<span class="pill-tag pill-warn">⚠️ {injuries} INJURIES</span>'
                )

            # Title for expander
            expander_title = (
                f"ODI #{odi} | Filed {rep_date} | {comp[:60]}"
                + ("…" if len(comp) > 60 else "")
            )

            with st.expander(expander_title):
                st.markdown(
                    f"""
                <div style="margin-bottom: 8px;">
                    {badges_html}
                    <span class="pill-tag pill-neutral">Component: <strong>{comp}</strong></span>
                    <span class="pill-tag pill-neutral">Incident Date: {row['incident_date'] or 'N/A'}</span>
                    <span class="pill-tag pill-neutral">Masked VIN: {row['vin'] or 'N/A'}</span>
                </div>
                <div class="narrative-quote">
                    "{summ}"
                </div>
                <div style="margin-top: 8px; font-size:12px; color:#64748B;">
                    Official Federal Record: 
                    <a href="https://www.nhtsa.gov/recalls?nhtsaId={odi}" target="_blank" style="color:#0D9488; text-decoration:none; font-weight:600;">
                        View NHTSA ODI Record #{odi} ↗
                    </a>
                </div>
                """,
                    unsafe_allow_html=True,
                )

with tab_table:
    if df_filtered.empty:
        st.info("No records to display.")
    else:
        table_view = df_filtered[
            [
                "odi_number",
                "report_date",
                "components",
                "crash",
                "fire",
                "injuries",
                "summary",
            ]
        ].rename(
            columns={
                "odi_number": "ODI ID",
                "report_date": "Filed Date",
                "components": "Components",
                "crash": "Crash?",
                "fire": "Fire?",
                "injuries": "Injuries",
                "summary": "Customer Narrative",
            }
        )
        st.dataframe(
            table_view,
            use_container_width=True,
            hide_index=True,
            height=380,
            column_config={
                "ODI ID": st.column_config.TextColumn("ODI ID", width="small"),
                "Filed Date": st.column_config.TextColumn(
                    "Filed Date", width="small"
                ),
                "Components": st.column_config.TextColumn(
                    "Components", width="medium"
                ),
                "Crash?": st.column_config.CheckboxColumn("Crash?", width="small"),
                "Fire?": st.column_config.CheckboxColumn("Fire?", width="small"),
                "Injuries": st.column_config.NumberColumn("Injuries", width="small"),
                "Customer Narrative": st.column_config.TextColumn(
                    "Customer Narrative", width="large"
                ),
            },
        )

st.markdown("<br>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 13. METHODOLOGY & QUALITY ENGINEERING LIMITATIONS
# -----------------------------------------------------------------------------
with st.expander("📖 Methodology, Automotive Quality Context & Limitations"):
    st.markdown(
        """
### Understanding NHTSA Complaint Data in Automotive Quality Engineering

#### 1. Nature of the Data
* **Owner-Submitted Signals**: Complaints logged in the NHTSA Office of Defects Investigation (ODI) database are filed directly by consumers, fleet operators, and dealers. 
* **Not Verified Defects**: These reports represent unverified consumer allegations and subjective descriptions. They are **not** confirmed engineering failures, recall orders, or judicial findings.

#### 2. The Missing Denominator (Volume vs. Rate)
* **Never treat raw complaint count as a failure rate**: A complaint volume of 300 on a high-volume pickup truck (with 800,000 units sold annually) represents an infinitesimally small fraction of vehicles on the road compared to 80 complaints on a low-production specialty EV (with 5,000 units sold).
* Without vehicle registration or fleet exposure denominators, count rankings only highlight areas of consumer friction, not mechanical failure probability.

#### 3. Component Categorization Nuances
* Component categories are mapped by NHTSA analysts and consumer drop-down selections. A single complaint frequently names multiple interacting subsystems (e.g. *STEERING* and *SUSPENSION*). PartPulse parses these into individual atomic components to prevent artificial label fragmentation.

#### 4. Role in the Quality Review Workflow
* In automotive quality engineering (e.g., Stellantis, Ford, GM quality operations), NHTSA data serves as an **Early Detection Radar**. It is combined with:
  1. Internal Warranty claims (cost per unit / R/1000).
  2. Dealer technical service bulletins (TSBs).
  3. Part return teardown analysis & metallurgy.
  4. Design Failure Mode and Effect Analysis (DFMEA) review.

---
*PartPulse is an independent student prototype utilizing the public U.S. NHTSA REST API. It is not affiliated with or endorsed by the U.S. Department of Transportation, NHTSA, or any vehicle manufacturer.*
"""
    )

# Footer
st.markdown(
    """
<div style="text-align: center; color: #94A3B8; font-size: 12.5px; padding: 24px 0 12px 0;">
    PartPulse Automotive Quality Signal Radar · Built with Streamlit, Plotly & NHTSA Open Data
</div>
""",
    unsafe_allow_html=True,
)
