.PHONY: setup preprocess app

setup:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt
	.venv/bin/pip install -e .
	@echo "Setup complete."

preprocess:
	.venv/bin/python3 -m src.preprocessing.spatial
	@echo "Preprocessing complete."

app:
	.venv/bin/python3 -m streamlit run src/app/app.py

