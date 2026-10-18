# Implementation Plan: Road Accident Severity Analysis and Prediction

## Project Overview
An end-to-end, production-grade machine learning and geospatial analytics system for analyzing and predicting road accident severity in Great Britain using the UK Department for Transport (DfT) 2022 STATS19 personal injury collision dataset (106,004 records, 44 attributes).

---

## 1. Architecture & Repository Structure

```
DSE PRO/
├── .venv/                              # Python 3.10.11 virtual environment
├── data/
│   ├── raw/
│   │   └── dft-road-casualty-statistics-collision-2022.csv   # IMMUTABLE original dataset (106,004 rows)
│   └── processed/
│       ├── collisions_cleaned_model.parquet                  # Feature-engineered model-ready dataset
│       └── collisions_cleaned_geo.parquet                    # Validated coordinate dataset for GIS (105,982 rows)
├── docs/
│   ├── feature_register.md             # Complete 44-column audit, definitions, and leak-safety decisions
│   ├── implementation_plan.md          # Technical roadmap and architecture
│   ├── data_dictionary.md              # Cleaned feature schema, value mappings, and sentinel handling
│   ├── eda_findings.md                 # Statistical analysis, class imbalance, and environmental distributions
│   ├── methodology.md                  # Methodological framework and validation standards
│   ├── model_card.md                   # Model governance, intended use, limitations, and performance
│   ├── limitations.md                  # Exposure data absence, single-year snapshot, reporting caveats
│   └── reproducibility.md              # Environment setup, execution scripts, and random seed governance
├── models/
│   ├── trained_pipeline.joblib         # Serialized best model pipeline with preprocessing
│   ├── model_metadata.json             # Feature lists, hyperparameters, metrics, and threshold data
│   └── baseline_metrics.json           # DummyClassifier and candidate evaluation benchmarks
├── reports/
│   ├── figures/                        # High-resolution EDA and evaluation charts
│   │   ├── target_distribution.png
│   │   ├── monthly_trend.png
│   │   ├── speed_limit_severity.png
│   │   ├── weather_road_surface.png
│   │   ├── confusion_matrices.png
│   │   └── pr_roc_curves.png
│   └── evaluation_summary.json         # Macro-F1, per-class metrics, confusion matrices
├── src/
│   ├── __init__.py
│   ├── utils.py                        # Common path helpers, logging, metrics calculation, and CRS helpers
│   ├── audit_collisions.py             # Read-only raw data audit (existing)
│   ├── clean_collisions.py             # Validation, sentinel recoding, coordinate checks, data split creation
│   ├── feature_engineering.py          # Temporal feature extraction, one-hot/ordinal preprocessing pipelines
│   ├── train_model.py                  # Training pipeline for Dummy baseline, Logistic Regression, Random Forest, HistGradientBoosting
│   ├── evaluate_model.py               # Evaluation across Macro-F1, balanced accuracy, confusion matrix, and reporting
│   └── hotspot_analysis.py             # EPSG:27700 projected clustering (DBSCAN & density aggregation), GeoJSON export
├── app/
│   ├── __init__.py
│   └── dashboard.py                    # Streamlit + Folium interactive road-safety explorer
├── tests/
│   ├── __init__.py
│   ├── test_data_validation.py         # Tests for raw schema, missing values, coordinate bounds
│   ├── test_cleaning_and_features.py   # Tests for sentinel handling, temporal feature engineering, split reproducibility
│   ├── test_leakage_safety.py          # Strict assertions prohibiting target/casualty/adjustment leakage
│   ├── test_model_pipeline.py          # Tests for pipeline inference, output format, class probabilities
│   ├── test_hotspot_analysis.py        # Tests for EPSG:27700 projection, DBSCAN clustering, output shapes
│   └── test_dashboard_logic.py         # Tests for filtering functions and KPI calculations
├── requirements.txt                    # Locked, clean dependency manifest
└── README.md                           # Executive summary, installation, usage, and portfolio highlights
```

---

## 2. Key Technical Decisions & Methodological Rigor

### A. Prediction-Time Contract & Leakage Prevention
- **Objective**: Predict collision severity (`Fatal`, `Serious`, `Slight`) given initial scene / environmental context.
- **Strict Leakage Prevention**:
  - Exclude direct target derivations: `collision_severity`, `enhanced_severity_collision`, `collision_adjusted_severity_serious`, `collision_adjusted_severity_slight`.
  - Exclude post-event consequence and clinical outcomes: `number_of_casualties`, `collision_injury_based`.
  - Exclude reporting bias: `did_police_officer_attend_scene_of_accident`.
  - Exclude high-cardinality nominal identifiers: `collision_index`, `collision_ref_no`, `first_road_number`, `second_road_number`, `lsoa_of_accident_location`, `local_authority_ons_district`.
  - Approved predictors (17 base + 4 engineered temporal features = 21 features):
    `number_of_vehicles`, `speed_limit`, `first_road_class`, `road_type`, `junction_detail_historic`, `junction_control`, `second_road_class`, `pedestrian_crossing_human_control_historic`, `pedestrian_crossing_physical_facilities_historic`, `light_conditions`, `weather_conditions`, `road_surface_conditions`, `special_conditions_at_site`, `carriageway_hazards_historic`, `urban_or_rural_area`, `trunk_road_flag`, `police_force`, `collision_month`, `day_of_week`, `collision_hour`, `is_night`.

### B. Preprocessing & Leakage-Safe Fitting
- Data split: 80% train / 20% test stratified on `collision_severity` with fixed `random_state=42`.
- Preprocessing transformations (imputation, scaling, one-hot encoding) are embedded inside `sklearn.pipeline.Pipeline` or `ColumnTransformer`, fit **exclusively** on training data, preventing any test set snooping.
- Handling sentinels: -1 and 9/99 codes for unknown values are formally recoded as explicit category `'Unknown'` or missing indicator before imputation.

### C. Addressing Class Imbalance & Evaluation Protocol
- **Target Distribution**:
  - Fatal (Class 1): 1,602 (~1.51%)
  - Serious (Class 2): 23,333 (~22.01%)
  - Slight (Class 3): 81,069 (~76.48%)
- Baseline: Majority-class `DummyClassifier(strategy='most_frequent')` yields ~76.5% accuracy but 0.0 macro recall/F1 for minority classes.
- Candidate Models:
  1. `DummyClassifier` (majority baseline)
  2. `LogisticRegression` (with balanced class weights and L2 regularization)
  3. `RandomForestClassifier` (with `class_weight='balanced_subsample'`, n_estimators=100)
  4. `HistGradientBoostingClassifier` (with `class_weight='balanced'`, fast tree boosting)
- Primary metric: **Macro-averaged F1-Score** and per-class recall (especially for Fatal and Serious classes).
- Transparent reporting: Accuracy is reported as secondary context; models will be compared fairly against the ~76.5% baseline.

### D. Geographic Hotspot Analysis with EPSG:27700 Projection
- Coordinate data quality: Exactly 22 records lack coordinates and are filtered only for geographic tasks (leaving 105,982 records).
- Distance metric validity: Raw WGS84 lat/long degrees are **never** used for Euclidean distance.
- We utilize the native British National Grid (OSGR) coordinates (`location_easting_osgr`, `location_northing_osgr`), which represent true metric coordinates (EPSG:27700, units in meters).
- Clustering: Spatial density analysis and DBSCAN clustering (e.g. eps=250m, min_samples=15) to identify persistent geographic collision clusters, distinguishing high collision frequency from high-risk per exposure.

### E. Interactive Streamlit Dashboard
- Google Maps-inspired clean interface for Great Britain road safety exploration.
- Caching (`@st.cache_data`, `@st.cache_resource`) for fast filtering across 100k+ records.
- Severity-filtered Choropleth / Cluster maps using Folium / MarkerCluster.
- Summary KPI cards showing true filtered counts.
- Interactive severity scenario predictor using the trained model pipeline with educational disclaimer.

---

## 3. Verification & Testing Plan
- Automated test suite covering:
  - Dataset schema and required columns validation
  - Missingness and coordinate bounds checks (GB bounding box)
  - Leakage prevention (ensuring none of the forbidden columns enter the model feature matrix)
  - Train/test split stratification and reproducibility
  - Model pipeline training, inference shape, and prediction bounds
  - Geographic coordinate projection and DBSCAN clustering outputs
  - Dashboard KPI and filtering calculations
- Execution of all scripts end-to-end to generate processed data, figures, models, and test outputs.
