import streamlit as st
import pandas as pd


def render_filters(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.markdown("## 🔍 Filters")

    years = sorted(df["year"].unique())
    year_range = st.sidebar.select_slider(
        "Year range",
        options=years,
        value=(years[-10], years[-1]),
    )

    regions = ["All regions"] + sorted(df["region"].unique())
    selected_region = st.sidebar.selectbox("Region", regions)

    if selected_region != "All regions":
        lga_options = sorted(df[df["region"] == selected_region]["lga"].unique())
    else:
        lga_options = sorted(df["lga"].unique())
    selected_lga = st.sidebar.selectbox("LGA", ["All LGAs"] + lga_options)

    groups = ["All groups"] + sorted(df["offence_group"].unique())
    selected_group = st.sidebar.selectbox("Offence group", groups)

    if selected_group != "All groups":
        cat_options = sorted(df[df["offence_group"] == selected_group]["offence_category"].unique())
    else:
        cat_options = sorted(df["offence_category"].unique())
    selected_cat = st.sidebar.selectbox("Offence category", ["All categories"] + cat_options)

    filtered = df[df["year"].between(year_range[0], year_range[1])]
    if selected_region != "All regions":
        filtered = filtered[filtered["region"] == selected_region]
    if selected_lga != "All LGAs":
        filtered = filtered[filtered["lga"] == selected_lga]
    if selected_group != "All groups":
        filtered = filtered[filtered["offence_group"] == selected_group]
    if selected_cat != "All categories":
        filtered = filtered[filtered["offence_category"] == selected_cat]

    st.sidebar.markdown("---")
    st.sidebar.metric("Matching records", f"{len(filtered):,}")
    return filtered
