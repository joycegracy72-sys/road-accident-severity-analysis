"""Automated tests for trained model pipeline inference, metadata, and performance."""

import pytest
import joblib
import pandas as pd
import numpy as np

from src.utils import SAVED_MODEL_PATH, MODEL_METADATA_PATH, ALL_MODEL_FEATURES


def test_trained_pipeline_exists_and_loads():
    assert SAVED_MODEL_PATH.exists(), f"Model artifact not found at {SAVED_MODEL_PATH}"
    pipeline = joblib.load(SAVED_MODEL_PATH)
    assert hasattr(pipeline, "predict"), "Pipeline must implement predict method"


def test_pipeline_inference_on_single_sample():
    pipeline = joblib.load(SAVED_MODEL_PATH)
    sample_dict = {
        "number_of_vehicles": [2],
        "speed_limit": [30],
        "collision_hour": [17],
        "collision_month": [10],
        "first_road_class": [3],
        "road_type": [6],
        "junction_detail_historic": [0],
        "junction_control": [-1],
        "second_road_class": [0],
        "pedestrian_crossing_human_control_historic": [0],
        "pedestrian_crossing_physical_facilities_historic": [0],
        "light_conditions": [1],
        "weather_conditions": [1],
        "road_surface_conditions": [1],
        "special_conditions_at_site": [0],
        "carriageway_hazards_historic": [0],
        "urban_or_rural_area": [1],
        "trunk_road_flag": [2],
        "police_force": [1],
        "day_of_week": [6],
        "is_night": [0],
    }
    sample_df = pd.DataFrame(sample_dict)
    
    pred = pipeline.predict(sample_df)
    assert len(pred) == 1
    assert pred[0] in [1, 2, 3]
    
    if hasattr(pipeline, "predict_proba"):
        proba = pipeline.predict_proba(sample_df)
        assert proba.shape == (1, 3)
        assert np.isclose(proba.sum(), 1.0)
