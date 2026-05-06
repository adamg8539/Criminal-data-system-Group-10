import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import pandas as pd
from app.components.charts import monthly_trend_chart, map_chart, offence_breakdown_chart, top_lga_chart


def render(df: pd.DataFrame):
    st.markdown("## Overview")

    # KPI metrics
    total_incidents = int(df["incident_count"].sum())
    total_lgas = df["lga"].nunique()
    peak_year = int(df.groupby("year")["incident_count"].sum().idxmax())
    top_offence = df.groupby("offence_category")["incident_count"].sum().idxmax()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Incidents", f"{total_incidents:,}")
    col2.metric("LGAs Covered", total_lgas)
    col3.metric("Peak Year", peak_year)
    col4.metric("Top Offence", top_offence)

    st.markdown("---")

    # Monthly trends + map side by side (matching inspo)
    left, right = st.columns(2)
    with left:
        st.plotly_chart(monthly_trend_chart(df), use_container_width=True)
    with right:
        st.plotly_chart(map_chart(df), use_container_width=True)

    st.markdown("---")

    # Bottom row
    left2, right2 = st.columns(2)
    with left2:
        st.plotly_chart(offence_breakdown_chart(df), use_container_width=True)
    with right2:
        st.plotly_chart(top_lga_chart(df), use_container_width=True)
