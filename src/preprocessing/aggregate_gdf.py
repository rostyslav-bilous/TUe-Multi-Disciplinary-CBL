import geopandas as gpd
import pandas as pd

def aggregate_gdf(gdfs):
    if not gdfs:
        return None
    target_crs = gdfs[0].crs
    
    for i, gdf in enumerate(gdfs):
        if gdf.crs != target_crs:
            raise ValueError(f"CRS mismatch at {i}: {gdf.crs} instead of {target_crs}.")
    
    return gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True), crs=target_crs)
    