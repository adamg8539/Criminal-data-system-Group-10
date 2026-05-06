import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import pandas as pd
from app.components.charts import map_chart, top_lga_chart


def render(df: pd.DataFrame):
    st.markdown("## Crime Hotspot Map")
    st.caption("Bubble size and colour represent total incidents per LGA.")

    st.plotly_chart(map_chart(df), use_container_width=True)

    st.markdown("---")
    st.markdown("### LGA Rankings")

    n = st.slider("Show top N LGAs", min_value=5, max_value=30, value=15)
    st.plotly_chart(top_lga_chart(df, n=n), use_container_width=True)

    # Table
    st.markdown("### Data Table")
    lga_table = (
        df.groupby(["lga", "region"])["incident_count"]
        .sum()
        .reset_index()
        .sort_values("incident_count", ascending=False)
        .rename(columns={"lga": "LGA", "region": "Region", "incident_count": "Total Incidents"})
    )
    lga_table["Total Incidents"] = lga_table["Total Incidents"].apply(lambda x: f"{x:,}")
    st.dataframe(lga_table, use_container_width=True, hide_index=True)
