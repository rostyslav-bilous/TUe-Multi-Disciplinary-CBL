import streamlit as st

# --- UI
pg = st.navigation(["pages/Home.py", "pages/Settings.py"], position="sidebar")
pg.run()
