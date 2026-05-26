import streamlit as st


pages = [
   "pages/1_ℹ️_About_Project.py",
   "pages/2_📊_Data_Exploration.py",
   "pages/3_🔮_Crime_Prediction.py",
   "pages/4_🧩_Crime_Clustering.py",
   "pages/5_🎯_Resource_Allocation.py",
   "pages/6_📈_Model_Evaluation.py"
]
pg = st.navigation(pages, position="sidebar")
pg.run()
