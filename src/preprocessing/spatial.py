import geopandas as gpd
import pandas as pd
from src.config import RAW_DIR
from src.config import DATA_DIR
from src.data.loaders import load_gpkg, load_excel

def aggregate_gdf(gdfs):
    if not gdfs:
        return None
    target_crs = gdfs[0].crs
    
    for i, gdf in enumerate(gdfs):
        if gdf.crs != target_crs:
            raise ValueError(f"CRS mismatch at {i}: {gdf.crs} instead of {target_crs}.")
    
    return gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True), crs=target_crs)


def split_uk_spatial_by_region():
    boundaries = load_gpkg(RAW_DIR / "boundaries" / "msoa_2021_Boundaries_BSC.gpkg")
    centroids = pd.read_csv(RAW_DIR / "centroids" / "msoa_2021_PWCs.csv")
    lookup = pd.read_csv(RAW_DIR / "lookup" / "msoa_region_lookup_2022.csv")

    regions = lookup['RGN22NM'].unique()
    
    for region in regions:
        # filter MSOAs to match the region
        region_msoa_codes = lookup[lookup['RGN22NM'] == region]['MSOA21CD'].unique()

        # filter boundaries to match filtered MSOAs
        gdf_region_bounds = boundaries[boundaries['MSOA21CD'].isin(region_msoa_codes)].copy()
        gdf_region_bounds = gdf_region_bounds.to_crs("EPSG:4326") # convert to angle coordinates
        gdf_region_bounds = gdf_region_bounds.reset_index(drop=True)

        # filter centroids to match filtered MSOAs
        region_cents = centroids[centroids['MSOA21CD'].isin(region_msoa_codes)].copy()
        gdf_region_cents = gpd.GeoDataFrame(
            region_cents,
            geometry=gpd.points_from_xy(region_cents['X'], region_cents['Y']),
            crs="EPSG:27700" # meter coordinates are used by default
        )
        gdf_region_cents.to_crs("EPSG:4326")
        gdf_region_cents = gdf_region_cents.reset_index(drop=True)

        # save GeoPackage file
        region_name = region.replace(' ', '_')
        save_path = DATA_DIR / "regions" / f"{region_name}.gpkg"
        print(save_path)
        gdf_region_bounds.to_file(save_path, driver="GPKG", layer="msoa_boundaries")
        gdf_region_cents.to_file(save_path, driver="GPKG", layer="population_centroids")

    pd.Series(regions).to_csv(DATA_DIR / "regions" /"region_names.csv", index=False)


def consolidate_uk_spatial():
    gdf_bounds = load_gpkg(RAW_DIR / "boundaries" / "msoa_2021_Boundaries_BSC.gpkg")
    cents = pd.read_csv(RAW_DIR / "centroids" / "msoa_2021_PWCs.csv")
    gdf_cents = gpd.GeoDataFrame(
            cents,
            geometry=gpd.points_from_xy(cents['X'], cents['Y']),
            crs="EPSG:27700" # meter coordinates are used by default
        )
    gdf_cents.to_crs("EPSG:4326")
    save_path = DATA_DIR / "regions" / "UK.gpkg"
    gdf_bounds.to_file(save_path, driver="GPKG", layer="msoa_boundaries")
    gdf_cents.to_file(save_path, driver="GPKG", layer="population_centroids")
    print(save_path)

def speeds_and_delays():
    # read tables
    df_speeds = load_excel(RAW_DIR / "road" / "avg_speed_cgn0503.ods", "CGN0503d", "odf", 3)
    df_speeds_latest = df_speeds[["Country/Region/Local Authority", "ONS area code", "2025 [Note 10]"]].copy()

    df_speeds_latest["2025 [Note 10]"] = pd.to_numeric(df_speeds_latest["2025 [Note 10]"], errors='coerce') # convert to float
    df_speeds_latest["2025 [Note 10]"] = df_speeds_latest["2025 [Note 10]"].fillna(24.0) # fill missing values
    df_speeds_latest['avg_speed_kph'] = df_speeds_latest["2025 [Note 10]"] * 1.6 

    # resolve codes mismatch
    ons_code_remapping = {
        "E10000023": "E06000065", # Map old North Yorkshire County to new Unitary Authority
        "E10000027": "E06000066", # Map old Somerset County to new Unitary Authority
        "E08000019": "E08000039", # Map Sheffield 
        "E08000016": "E08000038", # Map Barnsley 
    }
    df_speeds_latest['ONS area code'] = df_speeds_latest['ONS area code'].replace(ons_code_remapping)

    # map metrics to msoas
    lookup = pd.read_csv(RAW_DIR / "lookup" / "msoa_counties_and_unitary_authority_lookup_(april_2025).csv")
    df_speeds_latest = df_speeds_latest.rename(columns={"ONS area code": "CTYUA25CD"})
    df_speeds_mapped = pd.merge(
        lookup[["MSOA21CD", "CTYUA25CD"]],
        df_speeds_latest[["CTYUA25CD", "avg_speed_kph"]],
        on="CTYUA25CD",
        how="left"
    )
    print(f'NaN speed values: {df_speeds_mapped['avg_speed_kph'].isna().sum()}')
    gdf_uk_bounds = load_gpkg(DATA_DIR / "regions" / f"UK.gpkg", "msoa_boundaries")
    gdf_uk_speeds = gdf_uk_bounds.merge(
        df_speeds_mapped[['MSOA21CD', 'avg_speed_kph']],
        on='MSOA21CD',
        how='left'
    )
    print(gdf_uk_speeds.head())
    gdf_uk_speeds.to_file(DATA_DIR / "allocation" / f"UK_speeds.gpkg", driver="GPKG", layer="msoa_speeds")

    # 1. See what code your lookup table has given to the City of Nottingham
    print(lookup[lookup['CTYUA25NM'].str.contains("Barnsley", na=False)][['CTYUA25CD', 'CTYUA25NM']].drop_duplicates())
    # 2. See what code the DfT spreadsheet uses for the City vs the County
    print(df_speeds_latest[df_speeds_latest['Country/Region/Local Authority'].str.contains("Barnsley", na=False)])




if __name__ == "__main__":
    # split_uk_spatial_by_region()
    # consolidate_uk_spatial()
    speeds_and_delays()