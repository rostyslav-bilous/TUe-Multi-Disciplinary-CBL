import streamlit as st
import geopandas as gpd
import pandas as pd
from pathlib import Path
import leafmap.foliumap as leafmap

from src.config import DATA_DIR
from src.preprocessing.spatial import aggregate_gdf
from src.data.loaders import load_gpkg

st.set_page_config(layout="wide")
# st.title("Overview")

m = leafmap.Map(center=[52.5, -2.0  ], zoom=6.5)
m.add_basemap('CartoDB.Positron')

# def load_gpkg(file_path, layer_name):
#     gdf = gpd.read_file(file_path, layer=layer_name, engine="pyogrio")
#     return gdf.to_crs("EPSG:4326") # return in angle coordinates for leafmap rendering

first_cont = st.container()
with first_cont:
    controls_col, map_col = st.columns([2,5], vertical_alignment="top", gap="xlarge")

    with controls_col:
        st.subheader("Controls")

        with st.form("Map Controls"):
            regions = pd.read_csv(DATA_DIR / "regions" / "region_names.csv")
            selected_regions = st.multiselect("Regions", regions)

            st.segmented_control("Map type", ["None","Hotspots", "Tiers", "Some map"], width=   "stretch", default="None")
            prediction_span = st.slider("Months ahead", 0, 12, 1)
            number = st.number_input("Police units")

            submitted = st.form_submit_button("Apply", type="primary")

        
    selected_gdf_bounds = []
    selected_gdf_cents = []
    for region in selected_regions:
        gdf_bounds = load_gpkg(DATA_DIR / "regions"/ f"{region.replace(' ', '_')}.gpkg", "msoa_boundaries").to_crs("EPSG:4326")
        selected_gdf_bounds.append(gdf_bounds)

        gdf_cents = load_gpkg(DATA_DIR / "regions" / f"{region.replace(' ', '_')}.gpkg", "population_centroids").to_crs("EPSG:4326")
        selected_gdf_cents.append(gdf_cents)

        # poly_style = {'color': 'black', 'fillColor': 'blue', 'fillOpacity': 0.3, "weight": 1}
        # m.add_gdf(gdf=gdf_bounds, layer_name=f"Bounds {region}", style=poly_style)
        # m.add_gdf(gdf=gdf_cents, layer_name=f"Cetnts {region}")
    
    if selected_regions:
        gdf_combined_bounds = aggregate_gdf(selected_gdf_bounds)
        gdf_combined_cents = aggregate_gdf(selected_gdf_cents)
        m.add_data(gdf_combined_bounds, column="BNG_N", cmap='viridis', layer_name=f"Bounds", legend_title="Scale", k=8)

        # print(gdf_cents)

    with map_col:
        st.subheader("MSOA 2021 Map", text_alignment='right')
        m.to_streamlit()

