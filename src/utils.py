"""Common utilities, configurations, path constants, and validation helpers."""

from pathlib import Path
import logging
from typing import Dict, List, Tuple

# Base Project Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_PATH = DATA_DIR / "raw" / "dft-road-casualty-statistics-collision-2022.csv"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
CLEANED_MODEL_DATA_PATH = PROCESSED_DATA_DIR / "collisions_cleaned_model.parquet"
CLEANED_GEO_DATA_PATH = PROCESSED_DATA_DIR / "collisions_cleaned_geo.parquet"

MODELS_DIR = PROJECT_ROOT / "models"
SAVED_MODEL_PATH = MODELS_DIR / "trained_pipeline.joblib"
MODEL_METADATA_PATH = MODELS_DIR / "model_metadata.json"

REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
EVALUATION_SUMMARY_PATH = REPORTS_DIR / "evaluation_summary.json"

# Fixed Reproducibility Seed
RANDOM_STATE = 42

# Target Definition
TARGET_COL = "collision_severity"
TARGET_MAPPING: Dict[int, str] = {
    1: "Fatal",
    2: "Serious",
    3: "Slight",
}

# Forbidden Leakage and Identity Columns
FORBIDDEN_LEAKAGE_COLUMNS: List[str] = [
    "collision_severity",  # Target
    "number_of_casualties",  # Post-event consequence
    "enhanced_severity_collision",  # Retrospective adjustment
    "collision_injury_based",  # Reporting methodology
    "collision_adjusted_severity_serious",  # Statistical adjustment
    "collision_adjusted_severity_slight",  # Statistical adjustment
    "collision_index",  # Identifier
    "collision_ref_no",  # Identifier
    "collision_year",  # Constant 2022
    "local_authority_district",  # Constant -1
    "did_police_officer_attend_scene_of_accident",  # Reporting attendance bias
    "first_road_number",  # Nominal memorisation
    "second_road_number",  # Nominal memorisation
    "lsoa_of_accident_location",  # Extreme cardinality nominal
    "local_authority_ons_district",  # High cardinality nominal
    "local_authority_highway",  # Redundant administrative
    "local_authority_highway_current",  # Synthetic post-hoc mapping
    "junction_detail",  # Lossy redundant version
    "pedestrian_crossing",  # Lossy redundant version
    "carriageway_hazards",  # Inconsistent redundant version
]

# Approved Model Predictors
NUMERIC_FEATURES: List[str] = [
    "number_of_vehicles",
    "speed_limit",
    "collision_hour",
    "collision_month",
]

CATEGORICAL_FEATURES: List[str] = [
    "first_road_class",
    "road_type",
    "junction_detail_historic",
    "junction_control",
    "second_road_class",
    "pedestrian_crossing_human_control_historic",
    "pedestrian_crossing_physical_facilities_historic",
    "light_conditions",
    "weather_conditions",
    "road_surface_conditions",
    "special_conditions_at_site",
    "carriageway_hazards_historic",
    "urban_or_rural_area",
    "trunk_road_flag",
    "police_force",
    "day_of_week",
    "is_night",
]

ALL_MODEL_FEATURES: List[str] = NUMERIC_FEATURES + CATEGORICAL_FEATURES

# Great Britain Coordinate Valid Bounding Boxes
# WGS84 (lon, lat)
WGS84_BOUNDS: Tuple[float, float, float, float] = (-8.5, 2.0, 49.8, 61.0)
# British National Grid OSGR EPSG:27700 (easting, northing in meters)
OSGR_BOUNDS: Tuple[float, float, float, float] = (0.0, 700000.0, 0.0, 1300000.0)


def setup_logger(name: str = "road_safety") -> logging.Logger:
    """Configures and returns a consistent console logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
