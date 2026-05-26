import geopandas as gpd

from src.config import DATA_DIR

def get_spatial_data(file_path, layer_name):
    gdf = gpd.read_file(DATA_DIR / file_path, layer=layer_name, engine="pyogrio")
    return gdf