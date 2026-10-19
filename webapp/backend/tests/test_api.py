"""Automated unit and integration tests for FastAPI backend."""

import pytest
from fastapi.testclient import TestClient
import numpy as np
import pandas as pd

from webapp.backend.main import app
from webapp.backend.services import state
from src.utils import SAVED_MODEL_PATH, ALL_MODEL_FEATURES


@pytest.fixture(scope="module", autouse=True)
def initialize_state():
    """Ensure state is loaded prior to running API tests."""
    state.load()


def test_api_health_endpoint():
    with TestClient(app) as client:
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["model_loaded"] is True
        assert data["data_loaded"] is True
        assert data["total_collision_records"] == 105982
        assert data["hotspot_clusters_count"] == 293


def test_api_hotspots_endpoint():
    with TestClient(app) as client:
        resp = client.get("/api/hotspots")
        assert resp.status_code == 200
        data = resp.json()
        assert data["type"] == "FeatureCollection"
        assert data["total_clusters"] == 293
        assert len(data["features"]) == 293

        first_feat = data["features"][0]
        assert first_feat["type"] == "Feature"
        assert "coordinates" in first_feat["geometry"]
        assert "total_collisions" in first_feat["properties"]
        assert "fatal_count" in first_feat["properties"]


def test_api_collisions_viewport_query():
    with TestClient(app) as client:
        # Central London bounding box
        params = {
            "min_lon": -0.2,
            "min_lat": 51.45,
            "max_lon": 0.0,
            "max_lat": 51.55,
            "limit": 50,
        }
        resp = client.get("/api/collisions", params=params)
        assert resp.status_code == 200
        data = resp.json()
        assert data["type"] == "FeatureCollection"
        assert data["total_in_viewport"] > 0
        assert data["returned_count"] <= 50
        assert len(data["features"]) == data["returned_count"]


def test_api_collisions_invalid_bbox_rejected():
    with TestClient(app) as client:
        # Invalid: min > max
        params = {
            "min_lon": 1.0,
            "min_lat": 55.0,
            "max_lon": -1.0,
            "max_lat": 50.0,
        }
        resp = client.get("/api/collisions", params=params)
        assert resp.status_code == 400


def test_api_collisions_severity_filter():
    with TestClient(app) as client:
        params = {
            "min_lon": -8.0,
            "min_lat": 49.0,
            "max_lon": 2.0,
            "max_lat": 61.0,
            "severity": [1],  # Fatal only
            "limit": 100,
        }
        resp = client.get("/api/collisions", params=params)
        assert resp.status_code == 200
        data = resp.json()
        for feat in data["features"]:
            assert feat["properties"]["collision_severity"] == 1


def test_api_predict_consistency_with_pipeline():
    """Asserts that /api/predict produces identical output to raw model pipeline."""
    with TestClient(app) as client:
        payload = {
            "number_of_vehicles": 2,
            "speed_limit": 30,
            "collision_hour": 17,
            "collision_month": 10,
            "first_road_class": 3,
            "road_type": 6,
            "junction_detail_historic": 0,
            "junction_control": -1,
            "second_road_class": 0,
            "pedestrian_crossing_human_control_historic": 0,
            "pedestrian_crossing_physical_facilities_historic": 0,
            "light_conditions": 1,
            "weather_conditions": 1,
            "road_surface_conditions": 1,
            "special_conditions_at_site": 0,
            "carriageway_hazards_historic": 0,
            "urban_or_rural_area": 1,
            "trunk_road_flag": 2,
            "police_force": 1,
            "day_of_week": 6,
            "is_night": 0,
        }
        resp = client.post("/api/predict", json=payload)
        assert resp.status_code == 200
        api_data = resp.json()

        # Run direct prediction on pipeline
        direct_df = pd.DataFrame([payload])[ALL_MODEL_FEATURES]
        direct_pred = int(state.model_pipeline.predict(direct_df)[0])
        direct_proba = state.model_pipeline.predict_proba(direct_df)[0]

        assert api_data["predicted_severity"] == direct_pred
        # Check proba sum ~ 1.0
        assert sum(api_data["probabilities"].values()) == pytest.approx(1.0, rel=1e-2)


def test_api_predict_validation_errors():
    with TestClient(app) as client:
        # Invalid hour: 99
        bad_payload = {"collision_hour": 99}
        resp = client.post("/api/predict", json=bad_payload)
        assert resp.status_code == 422
