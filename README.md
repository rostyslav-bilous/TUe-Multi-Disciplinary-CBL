# TUe-Multi-Disciplinary-CBL
## 🚀 Setup & Launch on Linux/macOS/WSL2:

If you are running on **Ubuntu/Debian**, ensure your system has Python's virtual environment development binaries installed:
```
sudo apt update && sudo apt install python3-venv python3-pip -y
```
Navigate to project's root folder in your terminal and run these three commands:
```
make setup        # initialize venv and install src as a local package
make preprocess   # preprocess data
make app          # launch web app
```
Open `http://localhost:8501`. 

_This does not include setup for the execution of cells within `.ipynb` files YET. This is because cells do not recognize virtual env by default. So make sure to have all packages needed for notebooks installed globally or use Anaconda or similar tools._
## 🛠️ Development Manual
!!IMPORTANT: all source code files must be placed inside `src/`.

When working with scripts inside `src/`, activate your virtual environment:
```
source .venv/bin/activate
```
You should see `(venv)` appear before the prompt line. When exiting the workspace deactivate venv:
```
deactivate
```

When running standalone scripts from your terminal, always stand at the project root folder and execute them using the module flag (-m) rather than direct file paths. This is because `src` is installed as a package for easier and safer path resolution (for example, looking up DATA_DIR from src.config inside the preprocessing pipeline):
```
python3 -m src.preprocessing.split_uk_geometries_by_region
```
