# TUe-Multi-Disciplinary-CBL
## 🚀 Setup & Launch
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
make app                    # (optional) launch web app 
```
Open `http://localhost:8501`. 
### On Windows
In PowerShell run the following commands:
```
.\setup.ps1                             # initialize venv, install dependencies, and install src as a local package
.\.venv\Scripts\Activate.ps1            # activate virtual environment
python -m src.preprocessing.spatial     # preprocess data
python -m streamlit run src/app/app.py  # (optional) launch web app
```
If your PowerShell script execution is blocked, allow `setup.ps1` to be executed with the following command:
```
PowerShell.exe -ExecutionPolicy Bypass -File .\setup.ps1
```  

## 🛠️ Development Manual
!!IMPORTANT: all source code files must be placed inside `src/`.

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

When running standalone scripts from your terminal, always stand at the project root folder and execute them using the module flag (-m) rather than direct file paths. This is because `src` is installed as a package for easier and safer path resolution (for example, looking up DATA_DIR from src.config inside the preprocessing pipeline). Allocate `45` police units in `London` region, add `-s` to use substitution: 
```
python3 -m src.optimization.allocate -f regions/London -p 45
```
On Windows replace `python3` by `python`.