# Road Accident Severity Analysis and Prediction Using Machine Learning

[![Python 3.10.11](https://img.shields.io/badge/python-3.10.11-blue.svg)](https://www.python.org/)
[![License: OGL v3.0](https://img.shields.io/badge/License-OGL_v3.0-green.svg)](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)
[![Tests: Pytest](https://img.shields.io/badge/tests-15%20passed-brightgreen.svg)](https://pytest.org/)

An end-to-end, production-grade machine learning and geospatial analytics system for analyzing and predicting road accident severity across Great Britain using the official UK Department for Transport (DfT) 2022 STATS19 personal-injury collision dataset (106,004 records, 44 attributes).

---

## 📌 Executive Summary
- **Data Scope**: 106,004 personal-injury collisions reported by police across Great Britain in 2022.
- **Target Variable**: `collision_severity` (Fatal: 1,602 [1.51%], Serious: 23,333 [22.01%], Slight: 81,069 [76.48%]).
- **The Majority Baseline Paradox**: Always predicting `Slight` yields **76.48% accuracy** while missing 100% of fatalities and serious injuries.
- **Selected Champion Model**: **Balanced Random Forest Pipeline** achieving **Macro-F1 of 0.3691** (vs 0.2889 baseline) and **0.5013 Balanced Accuracy**, successfully detecting severe collisions under acute imbalance.
- **Geospatial Hotspots**: DBSCAN clustering on native **British National Grid (EPSG:27700)** coordinates identified **294 acute hotspot clusters** across Great Britain.
- **Interactive Application**: Streamlit & Folium web explorer featuring KPI metric cards, multi-dimensional filters, cluster popups, and real-time what-if scenario prediction.

---

## 🏗️ Repository Architecture
```
DSE PRO/
├── .venv/                              # Python 3.10.11 virtual environment
├── data/
│   ├── raw/
│   │   └── dft-road-casualty-statistics-collision-2022.csv   # IMMUTABLE original dataset (106,004 rows)
│   └── processed/
│       ├── collisions_cleaned_model.parquet                  # Feature-engineered model-ready dataset
│       ├── collisions_cleaned_geo.parquet                    # Validated coordinate dataset for GIS (105,982 rows)
│       └── hotspots_clusters.csv                             # Top DBSCAN spatial hotspot clusters
├── docs/
│   ├── feature_register.md             # Complete 44-column audit and leak-safety decisions
│   ├── implementation_plan.md          # Technical roadmap and architecture
│   ├── data_dictionary.md              # Cleaned feature schema, mappings, and sentinels
│   ├── eda_findings.md                 # Statistical analysis, class imbalance, and distributions
│   ├── methodology.md                  # Methodological framework and validation standards
│   ├── model_card.md                   # Model governance, intended use, limitations, and performance
│   ├── limitations.md                  # Exposure data absence, single-year snapshot, reporting caveats
│   └── reproducibility.md              # Environment setup, execution scripts, and random seed governance
├── models/
│   ├── trained_pipeline.joblib         # Serialized best model pipeline with preprocessing
│   └── model_metadata.json             # Feature lists, hyperparameters, metrics, and thresholds
├── reports/
│   ├── figures/                        # High-resolution EDA and evaluation charts
│   ├── cleaning_summary.json           # Raw vs processed audit trail
│   ├── eda_summary.json                # Empirical EDA statistics
│   └── evaluation_summary.json         # Benchmark evaluation metrics across all models
├── src/
│   ├── utils.py                        # Common path helpers, logging, and CRS constants
│   ├── audit_collisions.py             # Read-only raw data audit
│   ├── clean_collisions.py             # Validation, sentinel recoding, and data split creation
│   ├── feature_engineering.py          # Preprocessing pipelines and strict leakage assertions
│   ├── train_model.py                  # Training pipeline for baseline and candidate models
│   ├── evaluate_model.py               # Evaluation across Macro-F1, confusion matrix, and reporting
│   └── hotspot_analysis.py             # EPSG:27700 projected clustering (DBSCAN)
├── app/
│   └── dashboard.py                    # Streamlit + Folium interactive road-safety explorer
├── tests/
│   ├── test_data_validation.py         # Schema, missing values, and coordinate bounds tests
│   ├── test_cleaning_and_features.py   # Sentinel handling and split reproducibility tests
│   ├── test_leakage_safety.py          # Strict assertions prohibiting target/casualty leakage
│   ├── test_model_pipeline.py          # Tests for pipeline inference and class probabilities
│   ├── test_hotspot_analysis.py        # EPSG:27700 projection and DBSCAN clustering tests
│   └── test_dashboard_logic.py         # Dashboard filtering and KPI calculation tests
├── requirements.txt                    # Locked dependency manifest
└── README.md
```

---

## 🛡️ Leakage-Safe Prediction-Time Contract
The model predicts collision severity *immediately post-incident* using information plausibly available to the initial police report.
- **Strictly Excluded**: Target (`collision_severity`), retrospective clinical adjustments (`enhanced_severity_collision`, `collision_adjusted_severity_serious`, `collision_adjusted_severity_slight`), casualty totals (`number_of_casualties`, `collision_injury_based`), reporting attendance bias (`did_police_officer_attend_scene_of_accident`), and nominal identifiers (`collision_index`, `first_road_number`).
- **Approved Predictors (21 features)**: `number_of_vehicles`, `speed_limit`, `collision_hour`, `collision_month`, `first_road_class`, `road_type`, `junction_detail_historic`, `junction_control`, `second_road_class`, `pedestrian_crossing_human_control_historic`, `pedestrian_crossing_physical_facilities_historic`, `light_conditions`, `weather_conditions`, `road_surface_conditions`, `special_conditions_at_site`, `carriageway_hazards_historic`, `urban_or_rural_area`, `trunk_road_flag`, `police_force`, `day_of_week`, `is_night`.

---

## 📊 Model Evaluation Benchmark

Evaluated on held-out 20% test set (21,201 samples) stratified on severity:

| Model Candidate | Macro-F1 | Accuracy | Balanced Accuracy | Fatal Recall (Class 1) | Serious Recall (Class 2) | Slight Recall (Class 3) |
|---|---|---|---|---|---|---|
| **Majority-Class Dummy Baseline** | **0.2889** | **0.7648** | **0.3333** | 0.00 | 0.00 | **1.00** |
| **Weighted Logistic Regression** | **0.3493** | 0.5017 | **0.5229** | 0.58 | 0.44 | 0.52 |
| **Balanced Random Forest (Selected)** | **0.3691** | **0.5595** | **0.5013** | 0.38 | 0.42 | 0.60 |
| **Histogram Gradient Boosting** | **0.3621** | 0.5281 | 0.5112 | 0.48 | 0.43 | 0.56 |

---

## 🚀 Quickstart & Reproduction

### 1. Environment Setup
```powershell
# Open project directory in PowerShell
cd "C:\Users\JOYCE GRACY\OneDrive\Documents\DSE PRO"

# Activate the existing virtual environment
.venv\Scripts\Activate.ps1
```

### 2. Run Pipeline End-to-End
```powershell
python -m src.clean_collisions
python -m src.eda_analysis
python -m src.train_model
python -m src.evaluate_model
python -m src.hotspot_analysis
```

### 3. Run Automated Tests
```powershell
pytest -v
```

### 4. Launch the Interactive Dashboard
```powershell
streamlit run app/dashboard.py
```

---

## 📜 Dataset Attribution & Licensing
Contains public sector information licensed under the Open Government Licence v3.0.
Source: UK Department for Transport (DfT) Road Safety Open Data:
https://www.gov.uk/government/statistical-data-sets/road-safety-open-data
