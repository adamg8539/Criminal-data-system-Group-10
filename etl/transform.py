import pandas as pd
from calendar import monthrange

ID_COLUMNS = ["LGA", "Offence category", "Subcategory"]

# Maps BOCSAR offence categories → broad offence group
OFFENCE_GROUP_MAP = {
    "Homicide": "Violent",
    "Assault": "Violent",
    "Sexual offences": "Violent",
    "Robbery": "Violent",
    "Abduction and kidnapping": "Violent",
    "Theft": "Property",
    "Break and enter dwelling": "Property",
    "Break and enter non-dwelling": "Property",
    "Receive or handle stolen goods": "Property",
    "Motor vehicle theft": "Property",
    "Steal from motor vehicle": "Property",
    "Steal from retail store": "Property",
    "Steal from dwelling": "Property",
    "Steal from person": "Property",
    "Drug offences": "Drug",
    "Prohibited and regulated weapons offences": "Other",
    "Disorderly conduct": "Public Order",
    "Against justice procedures": "Justice",
    "Transport regulatory offences": "Other",
    "Other offences": "Other",
    "Fraud": "Property",
}

# Maps NSW LGA → regional grouping
LGA_REGION_MAP = {
    # Greater Sydney
    "Bayside": "Greater Sydney",
    "Blacktown": "Greater Sydney",
    "Blue Mountains": "Greater Sydney",
    "Burwood": "Greater Sydney",
    "Camden": "Greater Sydney",
    "Campbelltown": "Greater Sydney",
    "Canada Bay": "Greater Sydney",
    "Canterbury-Bankstown": "Greater Sydney",
    "Cumberland": "Greater Sydney",
    "Fairfield": "Greater Sydney",
    "Georges River": "Greater Sydney",
    "Hawkesbury": "Greater Sydney",
    "Hornsby": "Greater Sydney",
    "Hunters Hill": "Greater Sydney",
    "Inner West": "Greater Sydney",
    "Ku-ring-gai": "Greater Sydney",
    "Lane Cove": "Greater Sydney",
    "Liverpool": "Greater Sydney",
    "Mosman": "Greater Sydney",
    "North Sydney": "Greater Sydney",
    "Northern Beaches": "Greater Sydney",
    "Parramatta": "Greater Sydney",
    "Penrith": "Greater Sydney",
    "Randwick": "Greater Sydney",
    "Ryde": "Greater Sydney",
    "Strathfield": "Greater Sydney",
    "Sutherland Shire": "Greater Sydney",
    "Sydney": "Greater Sydney",
    "The Hills Shire": "Greater Sydney",
    "Waverley": "Greater Sydney",
    "Willoughby": "Greater Sydney",
    "Wollondilly": "Greater Sydney",
    "Woollahra": "Greater Sydney",
    # Hunter
    "Cessnock": "Hunter",
    "Dungog": "Hunter",
    "Lake Macquarie": "Hunter",
    "Maitland": "Hunter",
    "Muswellbrook": "Hunter",
    "Newcastle": "Hunter",
    "Port Stephens": "Hunter",
    "Singleton": "Hunter",
    "Upper Hunter Shire": "Hunter",
    # Illawarra
    "Kiama": "Illawarra",
    "Shellharbour": "Illawarra",
    "Shoalhaven": "Illawarra",
    "Wollongong": "Illawarra",
    # Central Coast
    "Central Coast": "Central Coast",
    # Mid North Coast
    "Bellingen": "Mid North Coast",
    "Coffs Harbour": "Mid North Coast",
    "Kempsey": "Mid North Coast",
    "Mid-Coast": "Mid North Coast",
    "Nambucca Valley": "Mid North Coast",
    "Port Macquarie-Hastings": "Mid North Coast",
    # New England and North West
    "Armidale Regional": "New England and North West",
    "Glen Innes Severn": "New England and North West",
    "Gunnedah": "New England and North West",
    "Gwydir": "New England and North West",
    "Inverell": "New England and North West",
    "Liverpool Plains": "New England and North West",
    "Moree Plains": "New England and North West",
    "Narrabri": "New England and North West",
    "Tamworth Regional": "New England and North West",
    "Tenterfield": "New England and North West",
    "Uralla": "New England and North West",
    "Walcha": "New England and North West",
    # Northern Rivers
    "Ballina": "Northern Rivers",
    "Byron": "Northern Rivers",
    "Clarence Valley": "Northern Rivers",
    "Kyogle": "Northern Rivers",
    "Lismore": "Northern Rivers",
    "Richmond Valley": "Northern Rivers",
    "Tweed": "Northern Rivers",
    # Orana
    "Bogan": "Orana",
    "Bourke": "Orana",
    "Brewarrina": "Orana",
    "Cobar": "Orana",
    "Coonamble": "Orana",
    "Dubbo Regional": "Orana",
    "Gilgandra": "Orana",
    "Narromine": "Orana",
    "Walgett": "Orana",
    "Warren": "Orana",
    "Warrumbungle Shire": "Orana",
    # Central West
    "Bathurst Regional": "Central West",
    "Blayney": "Central West",
    "Cabonne": "Central West",
    "Cowra": "Central West",
    "Forbes": "Central West",
    "Lachlan": "Central West",
    "Lithgow": "Central West",
    "Mid-Western Regional": "Central West",
    "Oberon": "Central West",
    "Orange": "Central West",
    "Parkes": "Central West",
    "Upper Lachlan Shire": "Central West",
    "Weddin": "Central West",
    # Riverina
    "Berrigan": "Riverina",
    "Bland": "Riverina",
    "Coolamon": "Riverina",
    "Cootamundra-Gundagai": "Riverina",
    "Edward River": "Riverina",
    "Federation": "Riverina",
    "Griffith": "Riverina",
    "Junee": "Riverina",
    "Leeton": "Riverina",
    "Lockhart": "Riverina",
    "Murrumbidgee": "Riverina",
    "Narrandera": "Riverina",
    "Temora": "Riverina",
    "Wagga Wagga": "Riverina",
    # Murray
    "Albury": "Murray",
    "Balranald": "Murray",
    "Carrathool": "Murray",
    "Greater Hume Shire": "Murray",
    "Hay": "Murray",
    "Murray River": "Murray",
    "Snowy Valleys": "Murray",
    "Wentworth": "Murray",
    # South East and Tablelands
    "Bega Valley": "South East and Tablelands",
    "Eurobodalla": "South East and Tablelands",
    "Goulburn Mulwaree": "South East and Tablelands",
    "Hilltops": "South East and Tablelands",
    "Queanbeyan-Palerang Regional": "South East and Tablelands",
    "Snowy Monaro Regional": "South East and Tablelands",
    "Wingecarribee": "South East and Tablelands",
    "Yass Valley": "South East and Tablelands",
    # Far West
    "Broken Hill": "Far West",
    "Central Darling": "Far West",
    "Unincorporated Far West": "Far West",
    # Special
    "In Custody": "Other",
    "Lord Howe Island": "Other",
}


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """Transform the dataset from wide format to long format."""
    df = df.dropna(subset=ID_COLUMNS)

    date_columns = [col for col in df.columns if col not in ID_COLUMNS]

    df_long = df.melt(
        id_vars=ID_COLUMNS,
        value_vars=date_columns,
        var_name="date",
        value_name="incident_count",
    )

    df_long["date"] = pd.to_datetime(df_long["date"], errors="coerce")
    df_long = df_long.dropna(subset=["date", "incident_count"])

    df_long = df_long.rename(
        columns={
            "LGA": "lga",
            "Offence category": "offence_category",
            "Subcategory": "offence_subcategory",
        }
    )

    df_long["incident_count"] = df_long["incident_count"].astype(int)

    # Derive offence_group from offence_category
    df_long["offence_group"] = (
        df_long["offence_category"].map(OFFENCE_GROUP_MAP).fillna("Other")
    )

    # Derive region from LGA
    df_long["region"] = df_long["lga"].map(LGA_REGION_MAP).fillna("Other")

    # Derive period start/end dates from the monthly date
    df_long["period_start_date"] = df_long["date"].values.astype("datetime64[M]")
    df_long["period_end_date"] = df_long["date"].apply(
        lambda d: d.replace(day=monthrange(d.year, d.month)[1])
    )

    return df_long


if __name__ == "__main__":
    from etl.extract import extract_data
    from pathlib import Path

    raw_df = extract_data()
    transformed_df = transform_data(raw_df)

    output_file = Path("data/processed/crime_long_format.csv")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    transformed_df.to_csv(output_file, index=False)

    print(f"Saved transformed data to {output_file}")
    print(transformed_df.head())
    print(transformed_df.shape)
