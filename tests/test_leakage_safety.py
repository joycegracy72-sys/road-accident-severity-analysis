"""Automated tests guaranteeing zero target, consequence, or retrospective leakage."""

import pytest
from src.utils import (
    FORBIDDEN_LEAKAGE_COLUMNS,
    ALL_MODEL_FEATURES,
    NUMERIC_FEATURES,
    CATEGORICAL_FEATURES,
)
from src.feature_engineering import validate_feature_safety


def test_forbidden_columns_never_in_model_features():
    overlap = set(ALL_MODEL_FEATURES).intersection(set(FORBIDDEN_LEAKAGE_COLUMNS))
    assert len(overlap) == 0, f"LEAKAGE VIOLATION: Model feature list contains forbidden columns: {overlap}"


def test_target_excluded_from_predictors():
    assert "collision_severity" not in ALL_MODEL_FEATURES
    assert "collision_severity" in FORBIDDEN_LEAKAGE_COLUMNS


def test_casualty_and_clinical_adjustments_excluded():
    forbidden_subset = [
        "number_of_casualties",
        "enhanced_severity_collision",
        "collision_injury_based",
        "collision_adjusted_severity_serious",
        "collision_adjusted_severity_slight",
        "did_police_officer_attend_scene_of_accident",
    ]
    for col in forbidden_subset:
        assert col not in ALL_MODEL_FEATURES, f"Forbidden column {col} found in model features"
        assert col in FORBIDDEN_LEAKAGE_COLUMNS


def test_feature_safety_validator_raises_on_leakage():
    compromised_features = ["speed_limit", "number_of_casualties"]
    with pytest.raises(ValueError, match="CRITICAL LEAKAGE DETECTED"):
        validate_feature_safety(compromised_features)
