# TUe-Multi-Disciplinary-CBL
## To access Streamlit app
Navigate to `/src/viz/`

Install dependencies either globally:
```
pip install streamlit leafmap
streamlit run app.py
```
OR in a virtual environment (RECOMMENDED):
```
python3 -m venv .venv
source .venv/bin/activate
pip install streamlit leafmap
streamlit run app.py
```
Open `http://localhost:8501`. 
Later, before running the app and working on the website source code again, type `source .venv/bin/activate` 

Remember to exit the virtual environment by typing `deactivate` when closing the app or finishing working on the website.

**_On Windows the virtual environment folder has slightly different structure._**

To install the exact versions of all dependencies: `pip install -r requirements.txt`, although it installs more than we need for the app (like `geopandas`).
