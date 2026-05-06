import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import pandas as pd
import plotly.express as px
from app.components.charts import region_comparison_chart, COLOUR_SEQ


def render(df: pd.DataFrame):
    st.markdown("## Comparisons")

    tab1, tab2 = st.tabs(["Region vs Region", "LGA vs LGA"])

    with tab1:
        st.plotly_chart(region_comparison_chart(df), use_container_width=True)

        st.markdown("### Region Summary")
        region_table = (
            df.groupby("region")["incident_count"]
            .agg(["sum", "mean"])
            .reset_index()
            .rename(columns={"region": "Region", "sum": "Total Incidents", "mean": "Avg per Record"})
            .sort_values("Total Incidents", ascending=False)
        )
        region_table["Total Incidents"] = region_table["Total Incidents"].apply(lambda x: f"{int(x):,}")
        region_table["Avg per Record"] = region_table["Avg per Record"].apply(lambda x: f"{x:.1f}")
        st.dataframe(region_table, use_container_width=True, hide_index=True)

    with tab2:
        all_lgas = sorted(df["lga"].unique())
        selected = st.multiselect(
            "Select LGAs to compare (max 6)",
            options=all_lgas,
            default=all_lgas[:3],
            max_selections=6,
        )

        if selected:
            lga_year = (
                df[df["lga"].isin(selected)]
                .groupby(["year", "lga"])["incident_count"]
                .sum()
                .reset_index()
            )
            fig = px.line(
                lga_year,
                x="year",
                y="incident_count",
                color="lga",
                title="Annual Incidents — Selected LGAs",
                labels={"year": "Year", "incident_count": "Incidents", "lga": "LGA"},
                color_discrete_sequence=COLOUR_SEQ,
                markers=True,
            )
            fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Select at least one LGA above.")
