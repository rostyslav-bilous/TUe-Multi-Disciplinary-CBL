# TUe-Multi-Disciplinary-CBL
## 🚀 Setup & Launch
### On Windows
In PowerShell run the following commands:
```
.\setup.ps1                             # initialize venv, install dependencies, and install src as a local package
.\.venv\Scripts\Activate.ps1            # activate virtual environment
python -m src.preprocessing.spatial     # preprocess data
```
Run `notebooks/tiering.ipynb` and then:
```
python -m streamlit run src/app/app.py  # launch the dashboard 
```
[Video setup & launch walkthrough on OneDrive](https://tuenl-my.sharepoint.com/:v:/g/personal/r_bilous_student_tue_nl/IQDo0rVgNeUsRr6NwqqDrwqmAeMqIScuycncIopi8QK8cGU?nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJPbmVEcml2ZUZvckJ1c2luZXNzIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXciLCJyZWZlcnJhbFZpZXciOiJNeUZpbGVzTGlua0NvcHkifX0&e=74LeRT)
###  On Linux/macOS/WSL2

If you are running on **Ubuntu/Debian**, ensure your system has Python's virtual environment development binaries installed:
```
sudo apt update && sudo apt install python3-venv python3-pip -y
```
Navigate to project's root folder in your terminal and run these three commands:
```
make setup                  # initialize venv, install dependencies, and install src as a local package
source .venv/bin/activate   # activate virtual environment
make preprocess             # preprocess data
```
Run `notebooks/tiering.ipynb` and then:
```
make app                    # launch the dashboard 
```
Open `http://localhost:8501`. 


## 🛠️ Development Manual
IMPORTANT: all source code files must be placed inside `src/`.

When working with scripts inside `src/`, activate your virtual environment:
```
source .venv/bin/activate
```
On Windows:
```
.\.venv\Scripts\Activate.ps1 
```
You should see `(.venv)` appear before the prompt line. When exiting the workspace deactivate venv:
```
deactivate
```

When running standalone scripts from your terminal, always stand at the project root folder and execute them using the module flag (-m) rather than direct file paths. This is because `src` is installed as a package for easier and safer path resolution.

## Project Structure
`notebooks/` contains Jupyter notebooks for prediction, clustering, and tiering; `data/` stores raw and processed data (raw crime data was stored remotely because of its size); `src/` includes code files. Some notebooks like regression-related notebooks relied on data stored remotely (SQL queries), the result of forecasts (regression) is stored at `data/processed/forecasts/intensityforecast12m.csv` and is later used by other notebooks. For police unit allocatio no notebook was written, code for this part can be found in `src/`, main file being `src/omptimization/allocate.py`.
