import streamlit as st
import leafmap.foliumap as leafmap
import pandas as pd
from pathlib import Path
import numpy as np

from src.config import DATA_DIR, RAW_DIR
from src.data.loaders import load_gpkg
from src.optimization.allocate import allocate


st.set_page_config(layout="wide")

# gdf_departments = load_gpkg(RAW_DIR / 'boundaries' / 'Police_Force_Areas_December_2023_EW_BFE.gpkg')
# m.add_gdf(gdf_departments, layer_name="Police Departments")

# first_cont = st.container()
# with first_cont:
#     controls_col1, controls_col2 = st.columns([1,1], vertical_alignment="top", gap="xlarge")

#     with controls_col1:
#         folder_weights = DATA_DIR / 'monthly_tiers'
#         csv_paths_weights = sorted(folder_weights.glob('*.csv'))
#         folders_weights = [f.parent for f in csv_paths_weights]
#         file_names_weights = [f.name for f in csv_paths_weights]
#         with st.form("Weight Map Controls"):
#             selected_weights_file = st.selectbox("Select weights file", file_names_weights, index=0)
#             window_col1, window_col2 = st.columns([1,1], vertical_alignment="top", gap='large')
#             with window_col1:
#                 st.slider("Primary responce window", 0, 15, 1)
#             with window_col2:
#                 st.slider("Secondary responce window", 0, 30, 1)
#             is_substitution = st.checkbox('Use substitution')
#             number = st.number_input("Insert a number")
#             submitted_weights = st.form_submit_button("Apply", type="primary")

#     with controls_col2:
#         st.subheader("Police Allocation")
#         allocation_folder = DATA_DIR / 'allocation'
#         allocation_paths = sorted(allocation_folder.glob('*.txt'))
#         allocation_folders = [f.parent for f in allocation_paths]
#         allocation_file_names = [f.name for f in allocation_paths]
#         with st.form("Controls"):
#             selected_allocation_file = st.selectbox("Select file", allocation_file_names, index=0)
#             submitted_allocation = st.form_submit_button("Apply", type="primary")

#     # load the selected monthly weights file
#     weights_index = file_names_weights.index(selected_weights_file)
#     parent_folder_weights = folders_weights[weights_index]
#     month_csv_path = parent_folder_weights / selected_weights_file
#     df_tiers = pd.read_csv(month_csv_path).rename(columns={'msoa_code': 'MSOA21CD'})

#     # load the selected allocation file with chosen sites
#     allocation_index = allocation_file_names.index(selected_allocation_file)
#     allocation_parent_folder = allocation_folders[allocation_index]
#     sites_path = allocation_parent_folder / selected_allocation_file
#     with open(sites_path, 'r') as f:
#         chosen_sites = [line.strip() for line in f]
#         df_chosen_sites = pd.DataFrame({'MSOA21CD': chosen_sites})

#     # load PWCs for selected sites
#     gdf_cents = load_gpkg(DATA_DIR / 'regions' / 'UK.gpkg', 'population_centroids')
#     gdf_chosen_cents = gdf_cents.merge(df_chosen_sites, on='MSOA21CD', how='right').to_crs('EPSG:4326')

#     # load bounds and merge with tiers/weights
#     gdf_bounds = load_gpkg(DATA_DIR / 'regions' / 'UK.gpkg', 'msoa_boundaries')
#     gdf_weights = gdf_bounds.merge(df_tiers[['MSOA21CD', 'tier_adjusted', 'final_weight']], how='left', on='MSOA21CD')

#     # establish min and max weight to continuous color map based on global min/max across UK
#     vmin = df_tiers['final_weight'].min()
#     vmax = df_tiers['final_weight'].max()

#     # create smooth continuous colormap
#     linear_colormap = leafmap.folium.branca.colormap.LinearColormap(
#         colors=['#fff5f0', "#f32525", "#49000a"],
#         vmin=vmin,
#         vmax=vmax
#     )

#     def smooth_style(feature):
#         metric = feature['properties']['final_weight']
#         style = {
#             "fillColor": linear_colormap(metric),
#             "fillOpacity": 0.9,
#             "color": "white",
#             "weight": 1.0
#         }
#         return style
    
# second_cont = st.container()
# with second_cont:
#     map_col1, map_col2 = st.columns([1, 1], vertical_alignment="top", gap="xlarge")
#     with map_col1:
#         m1 = leafmap.Map(center=[52.5, -2.0], zoom=6.5)
#         m1.add_basemap('CartoDB.Positron')
#         m1.add_gdf(gdf_weights, style_callback=smooth_style, layer_name="MSOA Weights")

#         # legend bar
#         linear_colormap.caption = "Weight"
#         m1.add_layer(linear_colormap)
#         m1.to_streamlit()
    
#     def msoa_bounds_style(feature):
#         style = {
#             "fillColor": 'white',
#             "fillOpacity": 0.0,
#             "color": "black",
#             'opacity': 0.5,
#             "weight": 0.2
#         }
#         return style
    
#     with map_col2:
#         m2 = leafmap.Map(center=[52.5, -2.0  ], zoom=6.5)
#         m2.add_basemap('CartoDB.Positron')
#         m2.add_gdf(gdf_bounds, layer_name='MSOA bounds', style_callback=msoa_bounds_style)
#         for idx, row in gdf_chosen_cents.iterrows():
#             lat = row.geometry.y + np.random.uniform(-0.001, 0.001) # jitter to visually distinguish units at one site
#             lon = row.geometry.x + np.random.uniform(-0.001, 0.001)
#             leafmap.folium.Circle(
#                 location=[lat, lon],
#                 radius=500, # 500 meters
#                 color='blue',
#                 fill=True,
#                 fill_opacity=1.0,
#                 fill_color='black'
#             ).add_to(m2)
#         m2.to_streamlit()


# global access to columns
CONT1_COL1 = None
CONT1_COL2 = None
def color_weights(gdf_bounds, df_weights, m):
    # establish min and max weight to continuous color map based on global min/max across UK
    vmin = df_weights['final_weight'].min()
    vmax = df_weights['final_weight'].max()

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
    gdf_weights = gdf_bounds.merge()
    m.add_gdf(gdf_weights, style_callback=smooth_style, layer_name="MSOA Weights")

    
def validate_allocation_inputs(num_units, window_pr, window_ba, selected_weights_file, selected_pfa, prob_pr, prob_ba):
    errors = []

    if window_pr >= window_ba:
        errors.append("Primary response window must be smaller than backup window.")

    if selected_weights_file is None or selected_weights_file == "":
        errors.append("Tier assignment file is not selected.")

    if selected_pfa is None or selected_pfa == "":
        errors.append("Police force area is not selected.")
    
    if prob_pr <= 0.0 or prob_pr >= 1.0 or prob_ba <= 0.0 or prob_ba >= 1.0 or prob_ba < prob_pr:
        errors.append("Probabilities of unavailability must be in the range (0,1) and prob. backup must be greater than or equal to prob. primary.") 

    return errors


def format_metric_value(value):
    return f"{float(value):,.0f}"


def render_allocation_map(selected_weights_file, selected_pfa, gdf_chosen_sites):
    gdf_bounds = load_gpkg(DATA_DIR / 'regions' / 'UK.gpkg')
    df_msoa_pfa = pd.read_csv(RAW_DIR / 'lookup' / 'msoa_pfa_lookup.csv')
    df_selected_msoas = df_msoa_pfa[df_msoa_pfa["PFA22NM"] == selected_pfa]
    df_weights = pd.read_csv(DATA_DIR / 'monthly_tiers' / selected_weights_file).rename(columns={'msoa_code': 'MSOA21CD'})

    if df_selected_msoas.empty:
        st.warning("No MSOAs were found for the selected police force area.")
        return

    gdf_selected_msoas = gdf_bounds.merge(df_selected_msoas, how='right', on='MSOA21CD')
    print(gdf_selected_msoas)
    gdf_selected_msoas = gdf_selected_msoas.merge(df_weights, how='left', on='MSOA21CD')
    with CONT1_COL2:
        m1 = leafmap.Map(center=[52.5, -2.0], zoom=6.5)
        m1.add_basemap('CartoDB.Positron')

        # establish min and max weight to continuous color map based on global min/max across UK
        vmin = df_weights['final_weight'].min()
        vmax = df_weights['final_weight'].max()

        # create smooth continuous colormap
        linear_colormap = leafmap.folium.branca.colormap.LinearColormap(
            colors=["#4abd33","#ebfc05","#DB1A1A"],
            vmin=vmin,
            vmax=vmax
        )

        def weights_style(feature):
            metric = feature['properties']['final_weight']
            style = {
                "fillColor": linear_colormap(metric),
                "fillOpacity": 0.9,
                "color": "white",
                "weight": 1.0
            }
            return style
        m1.add_gdf(gdf_selected_msoas, style_callback=weights_style, layer_name="MSOA Weights")
        # legend bar
        linear_colormap.caption = "Weight"
        m1.add_layer(linear_colormap)

        
        for idx, row in gdf_chosen_sites.iterrows():
            lat = row.geometry.y + np.random.uniform(-0.001, 0.001) # jitter to visually distinguish units at one site
            lon = row.geometry.x + np.random.uniform(-0.001, 0.001)
            leafmap.folium.Circle(
                location=[lat, lon],
                radius=500, # 500 meters
                color='blue',
                fill=True,
                fill_opacity=1.0,
                fill_color='black'
            ).add_to(m1)

        m1.to_streamlit()



def msoa_bounds_style(feature):
    style = {
        "fillColor": 'pink',
        "fillOpacity": 0.3,
        "color": "green",
        'opacity': 1.0,
        "weight": 1.0
    }
    return style


controls_container = st.container()
with controls_container:
    st.subheader("Allocate police resources")
    CONT1_COL1, CONT1_COL2 = st.columns([1.3,2], gap="medium")

    with CONT1_COL1:
        with st.form('Hello'):
            form_col1, form_col2 = st.columns([1,1], gap="small")
            with form_col2:
                # load weights/tiers files
                folder_weights = DATA_DIR / 'monthly_tiers'
                csv_paths_weights = sorted(folder_weights.glob('*.csv'))
                folders_weights = [f.parent for f in csv_paths_weights]
                file_names_weights = [f.name for f in csv_paths_weights]

                # tiers file selectbox
                selected_weights_file = st.selectbox("Tiers/weights file", file_names_weights, index=0, placeholder="Select tier assignments file...")

                # load police force areas
                df_msoa_pfa = pd.read_csv(RAW_DIR / 'lookup' / 'msoa_pfa_lookup.csv')
                pfa_names = df_msoa_pfa['PFA22NM'].unique()
                
                # police force area selectbox
                selected_pfa = st.selectbox("Police force area", pfa_names, index=1, placeholder="Select police force area...")
                prob_col1, prob_col2 = st.columns([1,1], gap="small")
                prob_pr = float(prob_col1.text_input("Prob. of unavailability of primary units", value=0.1))
                prob_ba = float(prob_col2.text_input("Prob. of unavailability of backup units", value=0.4))
                submitted_inputs = st.form_submit_button("Submit", type="primary")
                
            with form_col1:
                num_units = int(st.text_input("Number of police units", value=10))
                window_pr = st.slider("Primary response window (min)", 0, 15, 8)
                window_ba = st.slider("Backup response window (min)", 0, 30, 16)
                use_substitution = st.checkbox("Use substitution")


        if submitted_inputs:
            validation_errors = validate_allocation_inputs(
                num_units,
                window_pr,
                window_ba,
                selected_weights_file,
                selected_pfa,
                prob_pr,
                prob_ba
            )

            if validation_errors:
                for error in validation_errors:
                    st.error(error)
            else:
                gdf_cents = load_gpkg(DATA_DIR / 'regions'  / f"UK.gpkg", "population_centroids")
                df_msoa_pfa = pd.read_csv(RAW_DIR / 'lookup' / 'msoa_pfa_lookup.csv')
                gdf_cents = gdf_cents.merge(df_msoa_pfa, how='left', on='MSOA21CD')
                gdf_selected_cents = gdf_cents[gdf_cents["PFA22NM"] == selected_pfa]
                df_weights = pd.read_csv(DATA_DIR / 'monthly_tiers' / selected_weights_file).rename(columns={'msoa_code': 'MSOA21CD'})

                # allocate
                site_codes, twec, max_twec = allocate(num_units, gdf_selected_cents, use_substitution, df_weights, prob_pr, prob_ba, window_pr, window_ba, None)

                df_sites = pd.DataFrame({'MSOA21CD': site_codes})
                gdf_chosen_sites = gdf_cents.merge(df_sites, on='MSOA21CD', how='right').to_crs('EPSG:4326') #sites chosen by the algorithm
                
                render_allocation_map(
                    selected_weights_file,
                    selected_pfa,
                    gdf_chosen_sites
                )
                metric_col1, metric_col2, metric_col3 = st.columns([1,1,1], gap="small")
                metric_col1.metric(label='TWEC', value=format_metric_value(twec))
                metric_col2.metric(label='Max Theoretical TWEC', value=format_metric_value(max_twec))
                metric_col3.metric(label="Weight Covered", value=f"{(twec / max_twec):.2%}")







