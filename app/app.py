import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from app.data_loader import load_data
from app.components.filters import render_filters
from app.views import dashboard, trends, map_view, comparisons

st.set_page_config(
    page_title="Crime Analytics Dashboard",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Header
st.markdown(
    """
    <div style='display:flex; align-items:center; gap:12px; margin-bottom:4px'>
        <span style='font-size:2rem'>🔍</span>
        <h1 style='margin:0; font-size:1.8rem'>Crime Analytics Dashboard</h1>
        <span style='margin-left:auto; font-size:0.85rem; color:#888'>NSW BOCSAR Data</span>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown("---")

# Load data
with st.spinner("Loading data..."):
    df = load_data()

# Sidebar nav + filters
st.sidebar.markdown("# Navigation")
page = st.sidebar.radio(
    "",
    ["📊 Overview", "📈 Trends", "🗺️ Hotspot Map", "⚖️ Comparisons"],
    label_visibility="collapsed",
)
st.sidebar.markdown("---")
filtered_df = render_filters(df)

# Render selected page
if page == "📊 Overview":
    dashboard.render(filtered_df)
elif page == "📈 Trends":
    trends.render(filtered_df)
elif page == "🗺️ Hotspot Map":
    map_view.render(filtered_df)
elif page == "⚖️ Comparisons":
    comparisons.render(filtered_df)
