import streamlit as st
import leafmap.foliumap as leafmap

st.title("🏠 Home")
m = leafmap.Map(center=[52.5, -2.0  ], zoom=6.5)
m.add_basemap('CartoDB.Positron')
m.to_streamlit()

