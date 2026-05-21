import streamlit as st
import leafmap.foliumap as leafmap

st.title("🏠 Home")
st.subheader("LSOA/MSOA 2021 Map")

lsoa_polygons = 'src/viz/pages/Lower_layer_Super_Output_Areas_December_2021_Boundaries_EW_BSC_V4_6894679968818356315.geojson'
msoa_polygons = 'src/viz/pages/Middle_layer_Super_Output_Areas_December_2021_Boundaries_EW_BSC_V3_1633701655676791957.geojson'
msoa_pwc = 'src/viz/pages/MSOA_PopCentroids_EW_2021_V2.geojson'

m = leafmap.Map(center=[52.5, -2.0  ], zoom=6.5)
m.add_basemap('CartoDB.Positron')
# m.add_geojson(lsoa_polygons, layer_name='UK LSOAs')
m.add_geojson(msoa_polygons, layer_name='MSOAs')
m.add_geojson(msoa_pwc, layer_name='MSOA PWCs', show=False)



m.to_streamlit()

