import geopandas as gpd
import pandas as pd

def split_uk_by_region():
    boundaries = gpd.read_file("data/msoa_2021_Boundaries_BSC.gpkg", engine="pyogrio")
    centroids = pd.read_csv("data/msoa_2021_PWCs.csv")
    lookup = pd.read_csv("data/msoa_region_lookup_2022.csv")

    regions = lookup['RGN22NM'].unique()
    
    for region in regions:
        # filter MSOAs to match the region
        region_msoa_codes = lookup[lookup['RGN22NM'] == region]['MSOA21CD'].unique()

        # filter boundaries to match filtered MSOAs
        gdf_region_bounds = boundaries[boundaries['MSOA21CD'].isin(region_msoa_codes)].copy()
        gdf_region_bounds = gdf_region_bounds.reset_index(drop=True)

        # filter centroids to match filtered MSOAs
        region_cents = centroids[centroids['MSOA21CD'].isin(region_msoa_codes)].copy()
        gdf_region_cents = gpd.GeoDataFrame(
            region_cents,
            geometry=gpd.points_from_xy(region_cents['X'], region_cents['Y']),
            crs="EPSG:4326"
        )
        gdf_region_cents = gdf_region_cents.to_crs("EPSG:27700")
        gdf_region_cents = gdf_region_cents.reset_index(drop=True)


        # save GeoPackage file
        region_name = region.replace(' ', '_')
        gdf_region_bounds.to_file(f'data/boundaries_{region_name}.gpkg', driver="GPKG", layer="msoa_boundaries")
        gdf_region_bounds.to_file(f'data/centroids_{region_name}.gpkg', driver="GPKG", layer="msoa_centroids")

if __name__ == "__main__":
    split_uk_by_region()