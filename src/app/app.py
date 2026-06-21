import streamlit as st


pages = [
   "pages/4_🧩_Crime_Clustering.py",
   "pages/5_👮_Resource_Allocation.py",
]
pg = st.navigation(pages, position="top")
pg.run()
