import geopandas as gpd
import pandas as pd

# data loaders
def load_gpkg(file_path, layer_name=None):
    gdf = gpd.read_file(file_path, layer=layer_name, engine="pyogrio")
    return gdf

def load_excel(file_path, sheet_name, engine, header):
    df = pd.read_excel(file_path, sheet_name=sheet_name, engine=engine, header=header)
    return df
