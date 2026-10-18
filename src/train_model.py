"""Model training, validation split, and model serialization."""

from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from sklearn.model_selection import train_test_split
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, f1_score, accuracy_score, balanced_accuracy_score, confusion_matrix

from src.utils import (
    CLEANED_MODEL_DATA_PATH,
    MODELS_DIR,
    SAVED_MODEL_PATH,
    MODEL_METADATA_PATH,
    REPORTS_DIR,
    TARGET_COL,
    TARGET_MAPPING,
    ALL_MODEL_FEATURES,
    RANDOM_STATE,
    setup_logger,
)
from src.feature_engineering import get_preprocessor, validate_feature_safety

logger = setup_logger("train_model")


def load_and_split_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Loads cleaned model dataset, validates feature safety, and performs stratified 80/20 split."""
    logger.info(f"Loading model dataset from {CLEANED_MODEL_DATA_PATH}...")
    df = pd.read_parquet(CLEANED_MODEL_DATA_PATH)
    
    validate_feature_safety(ALL_MODEL_FEATURES)
    
    X = df[ALL_MODEL_FEATURES].copy()
    y = df[TARGET_COL].copy()
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.20,
        random_state=RANDOM_STATE,
        stratify=y,
    )
    
    logger.info(
        f"Stratified split complete. Training: {len(X_train):,} samples, Test: {len(X_test):,} samples."
    )
    return X_train, X_test, y_train, y_test


def train_and_compare_models() -> Dict[str, Any]:
    """Trains 4 candidate models, benchmarks against majority baseline, and serializes best model."""
    X_train, X_test, y_train, y_test = load_and_split_data()
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    candidates = {
        "Majority-Class Dummy Baseline": DummyClassifier(strategy="most_frequent"),
        "Weighted Logistic Regression": Pipeline(
            steps=[
                ("preprocessor", get_preprocessor()),
                ("classifier", LogisticRegression(class_weight="balanced", max_iter=1000, random_state=RANDOM_STATE)),
            ]
        ),
        "Balanced Random Forest": Pipeline(
            steps=[
                ("preprocessor", get_preprocessor()),
                ("classifier", RandomForestClassifier(
                    n_estimators=100,
                    max_depth=12,
                    class_weight="balanced_subsample",
                    random_state=RANDOM_STATE,
                    n_jobs=-1,
                )),
            ]
        ),
        "Histogram Gradient Boosting": Pipeline(
            steps=[
                ("preprocessor", get_preprocessor()),
                ("classifier", HistGradientBoostingClassifier(
                    class_weight="balanced",
                    max_iter=100,
                    random_state=RANDOM_STATE,
                )),
            ]
        ),
    }
    
    results = {}
    best_model_name = None
    best_macro_f1 = -1.0
    best_pipeline = None
    
    for name, model in candidates.items():
        logger.info(f"Training {name}...")
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        macro_f1 = float(f1_score(y_test, y_pred, average="macro"))
        acc = float(accuracy_score(y_test, y_pred))
        bal_acc = float(balanced_accuracy_score(y_test, y_pred))
        cm = confusion_matrix(y_test, y_pred, labels=[1, 2, 3]).tolist()
        
        report_dict = classification_report(
            y_test, y_pred,
            labels=[1, 2, 3],
            target_names=["Fatal", "Serious", "Slight"],
            output_dict=True,
            zero_division=0,
        )
        
        results[name] = {
            "macro_f1": round(macro_f1, 4),
            "accuracy": round(acc, 4),
            "balanced_accuracy": round(bal_acc, 4),
            "confusion_matrix": cm,
            "classification_report": report_dict,
        }
        
        logger.info(
            f"{name} -> Macro-F1: {macro_f1:.4f} | Accuracy: {acc:.4f} | Balanced Acc: {bal_acc:.4f}"
        )
        
        if macro_f1 > best_macro_f1:
            best_macro_f1 = macro_f1
            best_model_name = name
            best_pipeline = model
            
    logger.info(f"Selected best model: {best_model_name} with Macro-F1: {best_macro_f1:.4f}")
    
    # Serialize best pipeline
    logger.info(f"Saving best pipeline to {SAVED_MODEL_PATH}...")
    joblib.dump(best_pipeline, SAVED_MODEL_PATH)
    
    # Save metadata
    metadata = {
        "model_name": best_model_name,
        "selected_metric": "macro_f1",
        "best_macro_f1": best_macro_f1,
        "features": ALL_MODEL_FEATURES,
        "training_samples": len(X_train),
        "test_samples": len(X_test),
        "random_state": RANDOM_STATE,
        "classes": [1, 2, 3],
        "class_labels": ["Fatal", "Serious", "Slight"],
        "comparison": {
            k: {
                "macro_f1": v["macro_f1"],
                "accuracy": v["accuracy"],
                "balanced_accuracy": v["balanced_accuracy"],
            }
            for k, v in results.items()
        },
    }
    
    with open(MODEL_METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
        
    summary_path = REPORTS_DIR / "evaluation_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
        
    logger.info(f"Model artifacts and evaluation summary saved successfully.")
    return results


if __name__ == "__main__":
    train_and_compare_models()
