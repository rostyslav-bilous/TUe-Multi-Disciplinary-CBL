import streamlit as st
import geopandas as gpd
from pathlib import Path
import leafmap.foliumap as leafmap
from src.config import DATA_DIR


st.set_page_config(layout="wide")
st.title("🏠 Home")

# st.subheader("LSOA/MSOA 2021 Map")  

# lsoa_polygons = str(CURRENT_DIR / "Lower_layer_Super_Output_Areas_December_2021_Boundaries_EW_BSC_V4_6894679968818356315.geojson")
# msoa_polygons = str(CURRENT_DIR / "Middle_layer_Super_Output_Areas_December_2021_Boundaries_EW_BSC_V3_1633701655676791957.geojson")
# msoa_pwc = str(CURRENT_DIR / "MSOA_PopCentroids_EW_2021_V2.geojson")

m = leafmap.Map(center=[52.5, -2.0  ], zoom=6.5)
m.add_basemap('CartoDB.Positron')
# m.add_geojson(lsoa_polygons, layer_name='LSOAs', show=False)
# m.add_geojson(msoa_polygons, layer_name='MSOAs')
# m.add_geojson(msoa_pwc, layer_name='MSOA PWCs', show=False)

st.subheader("MSOA 2021 Map")

def get_spatial_data(file_path, layer_name):
    gdf = gpd.read_file(file_path, layer=layer_name, engine="pyogrio")
    return gdf.to_crs("EPSG:4326") # return in angle coordinates for leafmap rendering

gdf_bounds = get_spatial_data(DATA_DIR / "London.gpkg", "msoa_boundaries")
gdf_cents = get_spatial_data(DATA_DIR / "London.gpkg", "population_centroids")
m.add_gdf(gdf=gdf_bounds, layer_name="MSOA Polygons")

m.to_streamlit()

