import streamlit as st
import leafmap.foliumap as leafmap
import pandas as pd

from src.config import DATA_DIR
from src.data.loaders import load_gpkg


st.set_page_config(layout="wide")

m = leafmap.Map(center=[52.5, -2.0  ], zoom=6.5)
m.add_basemap('CartoDB.Positron')

gdf_msoas = load_gpkg(DATA_DIR / 'regions' / 'UK.gpkg').to_crs("EPSG:4326")
df_tiers = pd.read_csv(DATA_DIR / 'tier_assignments_2026-04-01.csv').rename(columns={'msoa_code': 'MSOA21CD'}) 
gdf_msoas = gdf_msoas.merge(df_tiers[['MSOA21CD', 'tier', 'final_weight']], how='left', on='MSOA21CD')


color_dict = {
    "Tier 1": "#DD0404",  # Tier 1
    "Tier 2": "#E9DA07",  # Tier 2
    "Tier 3": "#FFFFFF",  # Tier 3
}

def style_function(feature):
    tier = feature["properties"]["tier"]

    return {
        "fillColor": color_dict.get(tier, "#cccccc"),
        "color": "black",   # border color
        "weight": 0.1,      # border thickness
        "fillOpacity": 0.8,
    }

m.add_gdf(
    gdf_msoas,
    layer_name="MSOA tiers",
    style_function=style_function
)

m.save(DATA_DIR / "msoa_tier_map.html")

m.to_streamlit()

