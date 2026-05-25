import geopandas as gpd
import pandas as pd
from src.config import RAW_DIR
from src.config import DATA_DIR

def split_uk_geometries_by_region():
    boundaries = gpd.read_file(RAW_DIR / "msoa_2021_Boundaries_BSC.gpkg", engine="pyogrio")
    centroids = pd.read_csv(RAW_DIR / "msoa_2021_PWCs.csv")
    lookup = pd.read_csv(RAW_DIR / "msoa_region_lookup_2022.csv")

    regions = lookup['RGN22NM'].unique()
    
    for region in regions:
        # filter MSOAs to match the region
        region_msoa_codes = lookup[lookup['RGN22NM'] == region]['MSOA21CD'].unique()

        # filter boundaries to match filtered MSOAs
        gdf_region_bounds = boundaries[boundaries['MSOA21CD'].isin(region_msoa_codes)].copy()
        gdf_region_bounds = gdf_region_bounds.to_crs("EPSG:27700") # British National Grid - force coordinates in meters
        gdf_region_bounds = gdf_region_bounds.reset_index(drop=True)

        # filter centroids to match filtered MSOAs
        region_cents = centroids[centroids['MSOA21CD'].isin(region_msoa_codes)].copy()
        gdf_region_cents = gpd.GeoDataFrame(
            region_cents,
            geometry=gpd.points_from_xy(region_cents['X'], region_cents['Y']),
            crs="EPSG:4326" # angle coordinates are used by default
        )
        gdf_region_cents = gdf_region_cents.to_crs("EPSG:27700") # translate angle coordinates to meters
        gdf_region_cents = gdf_region_cents.reset_index(drop=True)

        # save GeoPackage file
        region_name = region.replace(' ', '_')
        save_path = DATA_DIR / f"{region_name}.gpkg"
        print(save_path)
        gdf_region_bounds.to_file(save_path, driver="GPKG", layer="msoa_boundaries")
        gdf_region_cents.to_file(save_path, driver="GPKG", layer="population_centroids")

    pd.Series(regions).to_csv(DATA_DIR / "region_names.csv", index=False)
    
if __name__ == "__main__":
    split_uk_geometries_by_region()