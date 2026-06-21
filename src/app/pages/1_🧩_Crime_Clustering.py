import streamlit as st
import leafmap.foliumap as leafmap
import pandas as pd
from pathlib import Path

from src.config import DATA_DIR, RAW_DIR
from src.data.loaders import load_gpkg


st.set_page_config(layout="wide")

m = leafmap.Map(center=[52.5, -2.0  ], zoom=6.5)
m.add_basemap('CartoDB.Positron')
first_cont = st.container()
with first_cont:
    controls_col, map_col = st.columns([2,5], vertical_alignment="top", gap="xlarge")

# load geometries and tiers
gdf_msoas = load_gpkg(DATA_DIR / 'regions' / 'UK.gpkg').to_crs("EPSG:4326")
# df_tiers = pd.read_csv(DATA_DIR / 'tier_assignments_2026-04-01.csv').rename(columns={'msoa_code': 'MSOA21CD'}) 
# gdf_msoas = gdf_msoas.merge(df_tiers[['MSOA21CD', 'tier', 'final_weight']], how='left', on='MSOA21CD')
folder = DATA_DIR / 'monthly_tiers'
csv_paths = sorted(folder.glob('*.csv'))
folders = [f.parent for f in csv_paths]
file_names = [f.name for f in csv_paths]

first_cont = st.container()
with first_cont:
    controls_col, map_col = st.columns([2,5], vertical_alignment="top", gap="xlarge")
    with controls_col:
        st.subheader("Clusters/Tiers Prediction")
        with st.form("Map Controls"):
            selected_csv = st.selectbox("Select file", file_names, index=0)
            submitted = st.form_submit_button("Apply", type="primary")


    # load tiers file
    index = file_names.index(selected_csv)
    parent_folder = folders[index]
    month_csv_path = parent_folder / selected_csv
    df_tiers = pd.read_csv(month_csv_path).rename(columns={'msoa_code': 'MSOA21CD'})
    gdf_msoas = gdf_msoas.merge(df_tiers[['MSOA21CD', 'tier_adjusted', 'final_weight']], how='left', on='MSOA21CD')

    # load police force bounds
    gdf_pfa_bounds = load_gpkg(RAW_DIR / 'boundaries' / 'Police_Force_Areas_December_2023_EW_BSC.gpkg')

    with map_col:
        color_dict = {
        "Tier 1": "#DD0404",  # Tier 1
        "Tier 2": "#E9DA07",  # Tier 2
        "Tier 3": "#FFFFFF",  # Tier 3
        }

        def style_tiers(feature):
            tier = feature["properties"]["tier_adjusted"]

            return {
                "fillColor": color_dict.get(tier, "#cccccc"),
                "color": "black",   # border color
                "weight": 0.1,      # border thickness
                "fillOpacity": 0.8,
            }

        m.add_gdf(
            gdf_msoas,
            layer_name="MSOA tiers",
            style_function=style_tiers
        )

        def style_pfa(feature):
            return {
                "fillColor": 'white',
                "color": "purple",   # border color
                "weight": 0.7,      # border thickness
                "fillOpacity": 0.0,
            }
        
        m.add_gdf(
            gdf_pfa_bounds,
            layer_name="PFA bounds",
            style_function=style_pfa
        )
        
        m.to_streamlit()











