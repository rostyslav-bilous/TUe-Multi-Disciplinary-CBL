import streamlit as st
import leafmap.foliumap as leafmap

from src.config import DATA_DIR
from src.data.loaders import load_gpkg


st.set_page_config(layout="wide")

m = leafmap.Map(center=[52.5, -2.0  ], zoom=6.5)
m.add_basemap('CartoDB.Positron')

# gdf_uk_speeds = load_gpkg(DATA_DIR / "allocation"/ "UK_speeds.gpkg", "msoa_speeds").to_crs("EPSG:4326")
# print(gdf_uk_speeds)
# m.add_data(gdf_uk_speeds, column="avg_speed_kph", cmap='magma_r', layer_name="MSOA svg speeds", legend_title="Scale", k=15)
# m.save(DATA_DIR / "msoa_speeds_map.html")

m.to_streamlit()