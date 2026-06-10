import streamlit as st
import leafmap.foliumap as leafmap
import pandas as pd
from pathlib import Path
import numpy as np

from src.config import DATA_DIR, RAW_DIR
from src.data.loaders import load_gpkg


st.set_page_config(layout="wide")

# gdf_departments = load_gpkg(RAW_DIR / 'boundaries' / 'Police_Force_Areas_December_2023_EW_BFE.gpkg')
# m.add_gdf(gdf_departments, layer_name="Police Departments")

first_cont = st.container()
with first_cont:
    controls_col1, controls_col2 = st.columns([1,1], vertical_alignment="top", gap="xlarge")

    with controls_col1:
        folder_weights = DATA_DIR / 'monthly_tiers'
        csv_paths_weights = sorted(folder_weights.glob('*.csv'))
        folders_weights = [f.parent for f in csv_paths_weights]
        file_names_weights = [f.name for f in csv_paths_weights]
        with st.form("Weight Map Controls"):
            selected_weights_file = st.selectbox("Select weights file", file_names_weights, index=0)
            window_col1, window_col2 = st.columns([1,1], vertical_alignment="top", gap='large')
            with window_col1:
                st.slider("Primary responce window", 0, 15, 1)
            with window_col2:
                st.slider("Secondary responce window", 0, 30, 1)
            is_substitution = st.checkbox('Use substitution')
            number = st.number_input("Insert a number")
            submitted_weights = st.form_submit_button("Apply", type="primary")

    with controls_col2:
        st.subheader("Police Allocation")
        allocation_folder = DATA_DIR / 'allocation'
        allocation_paths = sorted(allocation_folder.glob('*.txt'))
        allocation_folders = [f.parent for f in allocation_paths]
        allocation_file_names = [f.name for f in allocation_paths]
        with st.form("Controls"):
            selected_allocation_file = st.selectbox("Select file", allocation_file_names, index=0)
            submitted_allocation = st.form_submit_button("Apply", type="primary")

    # load the selected monthly weights file
    weights_index = file_names_weights.index(selected_weights_file)
    parent_folder_weights = folders_weights[weights_index]
    month_csv_path = parent_folder_weights / selected_weights_file
    df_tiers = pd.read_csv(month_csv_path).rename(columns={'msoa_code': 'MSOA21CD'})

    # load the selected allocation file with chosen sites
    allocation_index = allocation_file_names.index(selected_allocation_file)
    allocation_parent_folder = allocation_folders[allocation_index]
    sites_path = allocation_parent_folder / selected_allocation_file
    with open(sites_path, 'r') as f:
        chosen_sites = [line.strip() for line in f]
        df_chosen_sites = pd.DataFrame({'MSOA21CD': chosen_sites})

    # load PWCs for selected sites
    gdf_cents = load_gpkg(DATA_DIR / 'regions' / 'UK.gpkg', 'population_centroids')
    gdf_chosen_cents = gdf_cents.merge(df_chosen_sites, on='MSOA21CD', how='right').to_crs('EPSG:4326')

    # load bounds and merge with tiers/weights
    gdf_bounds = load_gpkg(DATA_DIR / 'regions' / 'UK.gpkg', 'msoa_boundaries')
    gdf_weights = gdf_bounds.merge(df_tiers[['MSOA21CD', 'tier_adjusted', 'final_weight']], how='left', on='MSOA21CD')

    # establish min and max weight to continuous color map based on global min/max across UK
    vmin = df_tiers['final_weight'].min()
    vmax = df_tiers['final_weight'].max()

    # create smooth continuous colormap
    linear_colormap = leafmap.folium.branca.colormap.LinearColormap(
        colors=['#fff5f0', "#f32525", "#49000a"],
        vmin=vmin,
        vmax=vmax
    )

    def smooth_style(feature):
        metric = feature['properties']['final_weight']
        style = {
            "fillColor": linear_colormap(metric),
            "fillOpacity": 0.9,
            "color": "white",
            "weight": 1.0
        }
        return style
    
second_cont = st.container()
with second_cont:
    map_col1, map_col2 = st.columns([1, 1], vertical_alignment="top", gap="xlarge")
    with map_col1:
        m1 = leafmap.Map(center=[52.5, -2.0], zoom=6.5)
        m1.add_basemap('CartoDB.Positron')
        m1.add_gdf(gdf_weights, style_callback=smooth_style, layer_name="MSOA Weights")

        # legend bar
        linear_colormap.caption = "Weight"
        m1.add_layer(linear_colormap)
        m1.to_streamlit()
    
    def msoa_bounds_style(feature):
        style = {
            "fillColor": 'white',
            "fillOpacity": 0.0,
            "color": "black",
            'opacity': 0.5,
            "weight": 0.2
        }
        return style
    
    with map_col2:
        m2 = leafmap.Map(center=[52.5, -2.0  ], zoom=6.5)
        m2.add_basemap('CartoDB.Positron')
        m2.add_gdf(gdf_bounds, layer_name='MSOA bounds', style_callback=msoa_bounds_style)
        for idx, row in gdf_chosen_cents.iterrows():
            lat = row.geometry.y + np.random.uniform(-0.001, 0.001) # jitter to visually distinguish units at one site
            lon = row.geometry.x + np.random.uniform(-0.001, 0.001)
            leafmap.folium.Circle(
                location=[lat, lon],
                radius=500, # 500 meters
                color='blue',
                fill=True,
                fill_opacity=1.0,
                fill_color='black'
            ).add_to(m2)
        m2.to_streamlit()
    