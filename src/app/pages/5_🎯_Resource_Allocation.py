import streamlit as st
import leafmap.foliumap as leafmap
import pandas as pd
from pathlib import Path

from src.config import DATA_DIR, RAW_DIR
from src.data.loaders import load_gpkg


st.set_page_config(layout="wide")

m = leafmap.Map(center=[52.5, -2.0  ], zoom=6.5)
m.add_basemap('CartoDB.Positron')

gdf_departments = load_gpkg(RAW_DIR / 'boundaries' / 'Police_Force_Areas_December_2023_EW_BFE.gpkg')
m.add_gdf(gdf_departments, layer_name="Police Departments",)
m.to_streamlit()