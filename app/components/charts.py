import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

COLOUR_SEQ = px.colors.qualitative.Safe

# NSW LGA centroids (lat/lon) for map scatter
LGA_COORDS = {
    "Albury": (-36.08, 146.91), "Armidale Regional": (-30.51, 151.67),
    "Ballina": (-28.87, 153.56), "Balranald": (-34.64, 143.56),
    "Bathurst Regional": (-33.42, 149.58), "Bayside": (-33.95, 151.13),
    "Bega Valley": (-36.67, 149.84), "Bellingen": (-30.45, 152.90),
    "Berrigan": (-35.66, 145.82), "Blacktown": (-33.77, 150.91),
    "Bland": (-33.36, 147.24), "Blayney": (-33.53, 149.25),
    "Blue Mountains": (-33.71, 150.31), "Bogan": (-31.11, 147.67),
    "Bourke": (-30.09, 145.94), "Brewarrina": (-29.96, 146.86),
    "Broken Hill": (-31.95, 141.47), "Burwood": (-33.87, 151.10),
    "Byron": (-28.65, 153.61), "Cabonne": (-33.13, 148.67),
    "Camden": (-34.06, 150.70), "Campbelltown": (-34.07, 150.81),
    "Canada Bay": (-33.86, 151.13), "Canterbury-Bankstown": (-33.91, 151.03),
    "Carrathool": (-34.16, 145.43), "Central Coast": (-33.43, 151.34),
    "Central Darling": (-31.93, 143.37), "Cessnock": (-32.83, 151.36),
    "Clarence Valley": (-29.68, 152.93), "Cobar": (-31.50, 145.84),
    "Coffs Harbour": (-30.30, 153.11), "Coolamon": (-34.82, 147.20),
    "Coonamble": (-30.95, 148.38), "Cootamundra-Gundagai": (-34.65, 148.03),
    "Cowra": (-33.83, 148.68), "Cumberland": (-33.84, 150.98),
    "Dubbo Regional": (-32.24, 148.60), "Dungog": (-32.40, 151.75),
    "Edward River": (-35.61, 144.75), "Eurobodalla": (-35.75, 150.07),
    "Fairfield": (-33.87, 150.94), "Federation": (-35.93, 146.85),
    "Forbes": (-33.38, 148.01), "Georges River": (-33.97, 151.08),
    "Gilgandra": (-31.71, 148.66), "Glen Innes Severn": (-29.73, 151.74),
    "Goulburn Mulwaree": (-34.75, 149.72), "Greater Hume Shire": (-35.83, 147.07),
    "Griffith": (-34.29, 146.04), "Gunnedah": (-30.98, 150.26),
    "Gwydir": (-29.56, 150.27), "Hawkesbury": (-33.56, 150.75),
    "Hay": (-34.51, 144.85), "Hilltops": (-34.31, 148.46),
    "Hornsby": (-33.70, 151.10), "Hunters Hill": (-33.83, 151.15),
    "Inner West": (-33.89, 151.14), "Inverell": (-29.78, 151.11),
    "Junee": (-34.87, 147.58), "Kempsey": (-31.08, 152.84),
    "Kiama": (-34.67, 150.85), "Ku-ring-gai": (-33.73, 151.15),
    "Kyogle": (-28.62, 153.00), "Lachlan": (-33.54, 146.72),
    "Lake Macquarie": (-33.08, 151.62), "Lane Cove": (-33.82, 151.17),
    "Leeton": (-34.55, 146.40), "Lismore": (-28.81, 153.28),
    "Lithgow": (-33.48, 150.15), "Liverpool": (-33.92, 150.92),
    "Liverpool Plains": (-31.35, 150.50), "Lockhart": (-35.22, 146.72),
    "Lord Howe Island": (-31.55, 159.08), "Maitland": (-32.73, 151.56),
    "Mid-Coast": (-32.10, 152.20), "Mid-Western Regional": (-32.59, 149.84),
    "Moree Plains": (-29.47, 149.84), "Mosman": (-33.83, 151.24),
    "Murray River": (-35.32, 143.90), "Murrumbidgee": (-34.67, 145.68),
    "Muswellbrook": (-32.27, 150.89), "Nambucca Valley": (-30.64, 152.99),
    "Narrabri": (-30.33, 149.78), "Narrandera": (-34.75, 146.55),
    "Narromine": (-32.23, 148.24), "Newcastle": (-32.93, 151.78),
    "North Sydney": (-33.84, 151.21), "Northern Beaches": (-33.74, 151.28),
    "Oberon": (-33.70, 149.86), "Orange": (-33.28, 149.10),
    "Parkes": (-33.13, 148.18), "Parramatta": (-33.81, 151.00),
    "Penrith": (-33.75, 150.69), "Port Macquarie-Hastings": (-31.43, 152.91),
    "Port Stephens": (-32.72, 152.10), "Queanbeyan-Palerang Regional": (-35.35, 149.23),
    "Randwick": (-33.91, 151.24), "Richmond Valley": (-28.99, 153.06),
    "Ryde": (-33.82, 151.10), "Shellharbour": (-34.58, 150.87),
    "Shoalhaven": (-34.90, 150.60), "Singleton": (-32.57, 151.17),
    "Snowy Monaro Regional": (-36.23, 149.13), "Snowy Valleys": (-35.71, 148.23),
    "Strathfield": (-33.87, 151.09), "Sutherland Shire": (-34.03, 151.07),
    "Sydney": (-33.87, 151.21), "Tamworth Regional": (-31.09, 150.93),
    "Temora": (-34.45, 147.53), "Tenterfield": (-29.05, 152.02),
    "The Hills Shire": (-33.68, 150.97), "Tweed": (-28.18, 153.55),
    "Unincorporated Far West": (-31.00, 141.50), "Upper Hunter Shire": (-32.03, 150.88),
    "Upper Lachlan Shire": (-34.34, 149.37), "Uralla": (-30.64, 151.50),
    "Wagga Wagga": (-35.12, 147.37), "Walcha": (-30.99, 151.60),
    "Walgett": (-30.02, 148.12), "Warren": (-31.70, 147.83),
    "Warrumbungle Shire": (-31.47, 148.98), "Waverley": (-33.89, 151.25),
    "Weddin": (-33.85, 147.83), "Wentworth": (-34.12, 141.92),
    "Willoughby": (-33.80, 151.20), "Wingecarribee": (-34.52, 150.39),
    "Wollondilly": (-34.19, 150.47), "Wollongong": (-34.43, 150.89),
    "Woollahra": (-33.89, 151.26), "Yass Valley": (-34.84, 148.91),
}


def monthly_trend_chart(df: pd.DataFrame) -> go.Figure:
    monthly = (
        df.groupby(["year", "month"])["incident_count"]
        .sum()
        .reset_index()
        .sort_values(["year", "month"])
    )
    monthly["period"] = monthly["year"].astype(str) + "-" + monthly["month"].astype(str).str.zfill(2)

    fig = px.bar(
        monthly,
        x="period",
        y="incident_count",
        title="Monthly Crime Trends",
        labels={"period": "Month", "incident_count": "Incidents"},
        color_discrete_sequence=["#E05C5C"],
    )
    fig.update_layout(
        xaxis_tickangle=-45,
        xaxis=dict(nticks=24),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(t=40, b=60),
    )
    return fig


def yearly_trend_chart(df: pd.DataFrame) -> go.Figure:
    yearly = df.groupby("year")["incident_count"].sum().reset_index()
    fig = px.line(
        yearly,
        x="year",
        y="incident_count",
        title="Annual Crime Trend",
        labels={"year": "Year", "incident_count": "Total Incidents"},
        markers=True,
        color_discrete_sequence=["#2196F3"],
    )
    fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", margin=dict(t=40))
    return fig


def offence_breakdown_chart(df: pd.DataFrame) -> go.Figure:
    breakdown = df.groupby("offence_group")["incident_count"].sum().reset_index()
    breakdown = breakdown.sort_values("incident_count", ascending=False)
    fig = px.bar(
        breakdown,
        x="offence_group",
        y="incident_count",
        title="Incidents by Offence Group",
        labels={"offence_group": "Offence Group", "incident_count": "Incidents"},
        color="offence_group",
        color_discrete_sequence=COLOUR_SEQ,
    )
    fig.update_layout(showlegend=False, plot_bgcolor="white", paper_bgcolor="white", margin=dict(t=40))
    return fig


def top_lga_chart(df: pd.DataFrame, n: int = 15) -> go.Figure:
    top = (
        df.groupby("lga")["incident_count"]
        .sum()
        .nlargest(n)
        .reset_index()
        .sort_values("incident_count")
    )
    fig = px.bar(
        top,
        x="incident_count",
        y="lga",
        orientation="h",
        title=f"Top {n} LGAs by Total Incidents",
        labels={"lga": "LGA", "incident_count": "Incidents"},
        color_discrete_sequence=["#5C6BC0"],
    )
    fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", margin=dict(t=40, l=160))
    return fig


def map_chart(df: pd.DataFrame) -> go.Figure:
    lga_totals = df.groupby("lga")["incident_count"].sum().reset_index()
    lga_totals["lat"] = lga_totals["lga"].map(lambda x: LGA_COORDS.get(x, (None, None))[0])
    lga_totals["lon"] = lga_totals["lga"].map(lambda x: LGA_COORDS.get(x, (None, None))[1])
    lga_totals = lga_totals.dropna(subset=["lat", "lon"])

    fig = px.scatter_mapbox(
        lga_totals,
        lat="lat",
        lon="lon",
        size="incident_count",
        color="incident_count",
        hover_name="lga",
        hover_data={"incident_count": True, "lat": False, "lon": False},
        color_continuous_scale="Reds",
        size_max=40,
        zoom=5,
        center={"lat": -32.5, "lon": 147.5},
        title="Crime Hotspots by LGA",
        labels={"incident_count": "Incidents"},
    )
    fig.update_layout(
        mapbox_style="carto-positron",
        margin=dict(t=40, r=0, l=0, b=0),
        coloraxis_colorbar=dict(title="Incidents"),
    )
    return fig


def category_pie_chart(df: pd.DataFrame) -> go.Figure:
    cat = df.groupby("offence_category")["incident_count"].sum().reset_index()
    cat = cat.sort_values("incident_count", ascending=False).head(8)
    fig = px.pie(
        cat,
        names="offence_category",
        values="incident_count",
        title="Incidents by Category",
        color_discrete_sequence=COLOUR_SEQ,
        hole=0.4,
    )
    fig.update_layout(margin=dict(t=40))
    return fig


def region_comparison_chart(df: pd.DataFrame) -> go.Figure:
    region = df.groupby(["year", "region"])["incident_count"].sum().reset_index()
    fig = px.line(
        region,
        x="year",
        y="incident_count",
        color="region",
        title="Crime Trends by Region",
        labels={"year": "Year", "incident_count": "Incidents", "region": "Region"},
        color_discrete_sequence=COLOUR_SEQ,
    )
    fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", margin=dict(t=40))
    return fig
