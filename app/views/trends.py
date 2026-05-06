import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import pandas as pd
import plotly.express as px
from app.components.charts import yearly_trend_chart, COLOUR_SEQ


def render(df: pd.DataFrame):
    st.markdown("## Crime Trends Over Time")

    st.plotly_chart(yearly_trend_chart(df), use_container_width=True)

    st.markdown("### Monthly Pattern (average incidents per month)")
    monthly_avg = df.groupby("month")["incident_count"].mean().reset_index()
    month_names = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
                   7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
    monthly_avg["month_name"] = monthly_avg["month"].map(month_names)

    fig = px.bar(
        monthly_avg,
        x="month_name",
        y="incident_count",
        title="Average Incidents by Month",
        labels={"month_name": "Month", "incident_count": "Avg Incidents"},
        color_discrete_sequence=["#42A5F5"],
        category_orders={"month_name": list(month_names.values())},
    )
    fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Trend by Offence Group")
    group_year = df.groupby(["year", "offence_group"])["incident_count"].sum().reset_index()
    fig2 = px.line(
        group_year,
        x="year",
        y="incident_count",
        color="offence_group",
        title="Annual Trend by Offence Group",
        labels={"year": "Year", "incident_count": "Incidents", "offence_group": "Group"},
        color_discrete_sequence=COLOUR_SEQ,
        markers=True,
    )
    fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig2, use_container_width=True)
