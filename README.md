# TUe-Multi-Disciplinary-CBL
## 🚀 Setup & Launch on Linux/macOS/WSL2:
Navigate to project's root folder. In your terminal run these three commands:
```
make setup
make preprocess
make app
```
Open `http://localhost:8501`. 

_This does not include setup for the execution of cells within `.ipynb` files YET. This is because cells do not recognize virtual env by default. So make sure to have all packages needed for notebooks installed globally or use Anaconda or similar tools._
## 🛠️ Development Manual
!!IMPORTANT: all source code files must be placed inside `src/`.

When working with scripts inside `src/`, activate your virtual env:
```
source .venv/bin/activate
```
You should see `(venv)` appear before the prompt line. When exiting the workspace deactivate venv:
```
deactivate
```

When running standalone scripts from your terminal, always stand at the project root folder and execute them using the module flag (-m) rather than direct file paths. This is because `src` is a packgage - it guarantees easier and safer path resolution (for example, looking up DATA_DIR from src.config inside the preprocessing pipeline:
```
python3 -m src.preprocessing.split_uk_geometries_by_region
```
