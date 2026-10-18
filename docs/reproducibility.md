# Reproducibility Guide & Workflow Commands

## 1. Environment & Prerequisites
- **Operating System**: Windows (tested on Windows 10/11)
- **Python Version**: 3.10.11
- **Virtual Environment**: `.venv`
- **Global Seed**: `RANDOM_STATE = 42` (configured across splits, models, and sampling)

## 2. Environment Activation & Dependencies
```powershell
# Activate virtual environment
.venv\Scripts\Activate.ps1

# Install / verify locked dependencies
pip install -r requirements.txt
```

## 3. Step-by-Step Pipeline Execution
```powershell
# Step 1: Clean raw data and generate processed Parquet datasets
python -m src.clean_collisions

# Step 2: Run Exploratory Data Analysis and generate charts
python -m src.eda_analysis

# Step 3: Train baseline and candidate ML models
python -m src.train_model

# Step 4: Evaluate models and plot confusion matrices
python -m src.evaluate_model

# Step 5: Run British National Grid (EPSG:27700) hotspot analysis
python -m src.hotspot_analysis

# Step 6: Execute automated pytest test suite
pytest -v

# Step 7: Launch the interactive Streamlit dashboard
streamlit run app/dashboard.py
```
