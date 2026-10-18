"""Automated tests for cleaning transformations and feature extraction."""

import pytest
import pandas as pd
import numpy as np

from src.utils import CLEANED_MODEL_DATA_PATH, RANDOM_STATE
from src.clean_collisions import clean_temporal_features
from src.train_model import load_and_split_data


def test_temporal_feature_extraction():
    dummy = pd.DataFrame({
        "date": ["15/01/2022", "30/08/2022"],
        "time": ["08:30", "23:45"],
    })
    cleaned = clean_temporal_features(dummy)
    assert cleaned["collision_month"].tolist() == [1, 8]
    assert cleaned["day_of_month"].tolist() == [15, 30]
    assert cleaned["collision_hour"].tolist() == [8, 23]
    assert cleaned["is_night"].tolist() == [0, 1]


def test_cleaned_model_dataset_preserves_all_rows():
    df_model = pd.read_parquet(CLEANED_MODEL_DATA_PATH)
    assert len(df_model) == 106004, f"Expected 106,004 rows in model dataset, got {len(df_model)}"
    assert "collision_month" in df_model.columns
    assert "collision_hour" in df_model.columns
    assert "is_night" in df_model.columns


def test_reproducible_stratified_split():
    X_train1, X_test1, y_train1, y_test1 = load_and_split_data()
    X_train2, X_test2, y_train2, y_test2 = load_and_split_data()
    
    assert len(X_train1) == 84803
    assert len(X_test1) == 21201
    assert (X_train1.index == X_train2.index).all(), "Splits must be deterministic"
    assert (X_test1.index == X_test2.index).all(), "Splits must be deterministic"
    
    # Check stratification: fatal share ~1.51%
    train_fatal_rate = (y_train1 == 1).mean()
    test_fatal_rate = (y_test1 == 1).mean()
    assert abs(train_fatal_rate - test_fatal_rate) < 0.001
