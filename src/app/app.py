import streamlit as st


pages = [
   "pages/1_🧩_Crime_Clustering.py",
   "pages/2_👮_Resource_Allocation.py",
]
pg = st.navigation(pages, position="top")
pg.run()
