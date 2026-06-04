# Create the virtual environment
python -m venv .venv 

# Install dependencies using the Windows path
.\.venv\Scripts\pip.exe install -r requirements.txt
.\.venv\Scripts\pip.exe install -e .

# Register the Jupyter kernel
.\.venv\Scripts\python.exe -m ipykernel install --user --name=my-project-venv --display-name "Python (.venv)"

echo "Setup complete."