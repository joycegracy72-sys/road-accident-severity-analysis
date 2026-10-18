"""Feature engineering and leakage-safe preprocessing pipelines."""

from typing import List, Tuple
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

from src.utils import (
    NUMERIC_FEATURES,
    CATEGORICAL_FEATURES,
    FORBIDDEN_LEAKAGE_COLUMNS,
    setup_logger,
)

logger = setup_logger("feature_engineering")


def validate_feature_safety(feature_names: List[str]) -> None:
    """Strictly validates that no forbidden leakage columns are present in features."""
    detected_leakage = [col for col in feature_names if col in FORBIDDEN_LEAKAGE_COLUMNS]
    if detected_leakage:
        raise ValueError(
            f"CRITICAL LEAKAGE DETECTED! Forbidden columns present in feature matrix: {detected_leakage}"
        )
    logger.info("Feature safety validation passed. Zero forbidden leakage columns detected.")


def get_preprocessor() -> ColumnTransformer:
    """Constructs a scikit-learn ColumnTransformer for preprocessing.
    
    Numeric pipeline:
      - SimpleImputer with median
      - StandardScaler
      
    Categorical pipeline:
      - SimpleImputer with constant (-1 / sentinel)
      - OneHotEncoder with handle_unknown='ignore'
    """
    validate_feature_safety(NUMERIC_FEATURES + CATEGORICAL_FEATURES)
    
    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    
    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value=-1)),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, NUMERIC_FEATURES),
            ("cat", categorical_transformer, CATEGORICAL_FEATURES),
        ],
        remainder="drop",
    )
    
    return preprocessor
