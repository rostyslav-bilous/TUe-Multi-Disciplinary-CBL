import streamlit as st
import leafmap.foliumap as leafmap
import pandas as pd
from pathlib import Path

from src.config import DATA_DIR, RAW_DIR
from src.data.loaders import load_gpkg


st.set_page_config(layout="wide")

m = leafmap.Map(center=[52.5, -2.0  ], zoom=6.5)
m.add_basemap('CartoDB.Positron')

# gdf_departments = load_gpkg(RAW_DIR / 'boundaries' / 'Police_Force_Areas_December_2023_EW_BFE.gpkg')
# m.add_gdf(gdf_departments, layer_name="Police Departments")

folder = DATA_DIR / 'allocation'
csv_paths = sorted(folder.glob('*.txt'))
folders = [f.parent for f in csv_paths]
file_names = [f.name for f in csv_paths]

first_cont = st.container()
with first_cont:
    controls_col, map_col = st.columns([2,5], vertical_alignment="top", gap="xlarge")
    with controls_col:
        st.subheader("Police Allocation")
        with st.form("Controls"):
            selected_csv = st.selectbox("Select file", file_names, index=0)
            submitted = st.form_submit_button("Apply", type="primary")

    # load correct file with chosen sites
    index = file_names.index(selected_csv)
    parent_folder = folders[index]
    sites_path = parent_folder / selected_csv   
    with open(sites_path, 'r') as f:
        sites = [line.strip() for line in f]


    gdf_cents = load_gpkg(DATA_DIR / 'regions' / 'UK.gpkg', 'population_centroids')
    gdf_chosen_cents = gdf_cents[gdf_cents['MSOA21CD'].isin(sites)].to_crs('EPSG:4326')
    
    gdf_chosen_cents['X_4326'] = gdf_chosen_cents.geometry.x
    gdf_chosen_cents['Y_4326'] = gdf_chosen_cents.geometry.y

    gdf_bounds = load_gpkg(DATA_DIR / 'regions' / 'UK.gpkg', 'msoa_boundaries')

    with map_col:
        m.add_gdf(gdf_bounds, 'MSOA bounds')
        m.add_gdf(gdf_chosen_cents, layer_name='Chosen sites')
        m.add_circle_markers_from_xy(gdf_chosen_cents, 
                                     x='X_4326', 
                                     y='Y_4326', 
                                     radius=15  , color="white", fill_color="green")
        m.to_streamlit()