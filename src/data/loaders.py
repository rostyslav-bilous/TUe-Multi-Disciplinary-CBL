import geopandas as gpd

def load_gpkg(file_path, layer_name=None):
    gdf = gpd.read_file(file_path, layer=layer_name, engine="pyogrio")
    return gdf
