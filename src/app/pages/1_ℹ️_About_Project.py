import streamlit as st
import geopandas as gpd
import pandas as pd
from pathlib import Path
import leafmap.foliumap as leafmap
from src.config import DATA_DIR


st.set_page_config(layout="wide")
# st.title("Overview")

m = leafmap.Map(center=[52.5, -2.0  ], zoom=6.5)
m.add_basemap('CartoDB.Positron')

def get_spatial_data(file_path, layer_name):
    gdf = gpd.read_file(file_path, layer=layer_name, engine="pyogrio")
    return gdf.to_crs("EPSG:4326") # return in angle coordinates for leafmap rendering

# gdf_bounds_London = get_spatial_data(DATA_DIR / "London.gpkg", "msoa_boundaries")
# gdf_bounds_Wales = get_spatial_data(DATA_DIR / "Wales.gpkg", "msoa_boundaries")
# gdf_cents = get_spatial_data(DATA_DIR / "London.gpkg", "population_centroids")
# m.add_gdf(gdf=gdf_bounds_London, layer_name="MSOA Polygons London")
# m.add_gdf(gdf=gdf_bounds_Wales, layer_name="MSOA Polygons Wales")
# m.add_gdf(gdf=gdf_cents, layer_name="MSOA PWCs")

first_cont = st.container()
with first_cont:
    controls_col, map_col = st.columns([2,5], vertical_alignment="top", gap="xlarge")

    with controls_col:
        st.subheader("Controls")
        regions = pd.read_csv(DATA_DIR / "region_names.csv")
        selected_regions = st.multiselect("Regions", regions)

        st.segmented_control("Map type", ["None","Hotspots", "Tiers", "Some map"], width="stretch", default="None")
        prediction_span = st.slider("Months ahead", 0, 12, 1)
        number = st.number_input("Police units")
        

    for region in selected_regions:
        gdf_bounds = get_spatial_data(DATA_DIR / f"{region.replace(' ', '_')}.gpkg", "msoa_boundaries")
        poly_style = {'color': 'black', 'fillColor': 'blue', 'fillOpacity': 0.3, "weight": 1}
        m.add_gdf(gdf=gdf_bounds, layer_name=f"Bounds {region}", style=poly_style)

    with map_col:
        st.subheader("MSOA 2021 Map", text_alignment='right')
        m.to_streamlit()

