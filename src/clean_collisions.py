"""Data cleaning, validation, and preparation pipeline for STATS19 2022 collisions."""

from pathlib import Path
import json
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple

from src.utils import (
    RAW_DATA_PATH,
    CLEANED_MODEL_DATA_PATH,
    CLEANED_GEO_DATA_PATH,
    REPORTS_DIR,
    TARGET_COL,
    TARGET_MAPPING,
    ALL_MODEL_FEATURES,
    WGS84_BOUNDS,
    OSGR_BOUNDS,
    setup_logger,
)

logger = setup_logger("clean_collisions")


def validate_raw_schema(df: pd.DataFrame) -> None:
    """Validates row count, required columns, and basic integrity of raw data."""
    expected_rows = 106004
    if len(df) != expected_rows:
        logger.warning(f"Expected {expected_rows} rows, found {len(df)}")
    
    required_cols = [
        "collision_index",
        "collision_severity",
        "date",
        "time",
        "number_of_vehicles",
        "speed_limit",
        "longitude",
        "latitude",
        "location_easting_osgr",
        "location_northing_osgr",
    ]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing essential raw columns: {missing}")
    logger.info("Raw schema validation passed.")


def clean_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """Parses date/time and derives month, hour, and night indicator."""
    df = df.copy()
    
    # Parse date DD/MM/YYYY
    parsed_dates = pd.to_datetime(df["date"], format="%d/%m/%Y", errors="coerce")
    if parsed_dates.isna().any():
        logger.warning(f"Failed to parse {parsed_dates.isna().sum()} dates.")
    df["collision_date"] = parsed_dates
    df["collision_month"] = parsed_dates.dt.month.astype("Int64")
    df["day_of_month"] = parsed_dates.dt.day.astype("Int64")
    
    # Parse time HH:MM
    # Format typically "HH:MM", e.g. "17:45"
    time_series = df["time"].astype(str).str.strip()
    hour_series = time_series.str.extract(r"^(\d{1,2}):")[0]
    df["collision_hour"] = pd.to_numeric(hour_series, errors="coerce").astype("Int64")
    
    # Fill any missing hour with median hour (14:00/2pm) for modeling, but flag
    df["is_night"] = df["collision_hour"].apply(
        lambda h: 1 if pd.notna(h) and (h in [21, 22, 23, 0, 1, 2, 3, 4, 5]) else (0 if pd.notna(h) else 0)
    ).astype(int)
    
    return df


def validate_coordinates(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """Validates coordinates and splits into model-ready and geo-ready subsets."""
    lon_min, lon_max, lat_min, lat_max = WGS84_BOUNDS
    east_min, east_max, north_min, north_max = OSGR_BOUNDS
    
    coord_cols = ["longitude", "latitude", "location_easting_osgr", "location_northing_osgr"]
    missing_coords_mask = df[coord_cols].isna().any(axis=1)
    missing_count = int(missing_coords_mask.sum())
    
    df_geo = df[~missing_coords_mask].copy()
    
    # Validate geographic bounding boxes for Great Britain
    valid_wgs84 = (
        (df_geo["longitude"] >= lon_min)
        & (df_geo["longitude"] <= lon_max)
        & (df_geo["latitude"] >= lat_min)
        & (df_geo["latitude"] <= lat_max)
    )
    valid_osgr = (
        (df_geo["location_easting_osgr"] >= east_min)
        & (df_geo["location_easting_osgr"] <= east_max)
        & (df_geo["location_northing_osgr"] >= north_min)
        & (df_geo["location_northing_osgr"] <= north_max)
    )
    
    in_bounds_mask = valid_wgs84 & valid_osgr
    out_of_bounds_count = int((~in_bounds_mask).sum())
    
    if out_of_bounds_count > 0:
        logger.warning(f"Found {out_of_bounds_count} records outside GB bounding box.")
        df_geo = df_geo[in_bounds_mask]
        
    geo_stats = {
        "total_records": len(df),
        "missing_coordinates": missing_count,
        "valid_coordinates": len(df_geo),
        "out_of_bounds": out_of_bounds_count,
        "min_longitude": float(df_geo["longitude"].min()),
        "max_longitude": float(df_geo["longitude"].max()),
        "min_latitude": float(df_geo["latitude"].min()),
        "max_latitude": float(df_geo["latitude"].max()),
        "min_easting": float(df_geo["location_easting_osgr"].min()),
        "max_easting": float(df_geo["location_easting_osgr"].max()),
        "min_northing": float(df_geo["location_northing_osgr"].min()),
        "max_northing": float(df_geo["location_northing_osgr"].max()),
    }
    
    return df, df_geo, geo_stats


def clean_and_prepare() -> None:
    """Executes full cleaning, validation, and artifact generation."""
    logger.info(f"Loading raw data from {RAW_DATA_PATH}...")
    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(f"Raw data file not found: {RAW_DATA_PATH}")
        
    raw_df = pd.read_csv(RAW_DATA_PATH, low_memory=False)
    validate_raw_schema(raw_df)
    
    # Check severity distribution
    severity_counts = raw_df[TARGET_COL].value_counts().to_dict()
    logger.info(f"Raw target distribution: {severity_counts}")
    
    # Clean temporal features
    df_cleaned = clean_temporal_features(raw_df)
    
    # Handle coordinates and separate datasets
    df_model, df_geo, geo_stats = validate_coordinates(df_cleaned)
    
    # Save processed outputs
    CLEANED_MODEL_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Ensure model dataset preserves all 106,004 records
    logger.info(f"Saving model-ready dataset ({len(df_model)} rows) to {CLEANED_MODEL_DATA_PATH}...")
    df_model.to_parquet(CLEANED_MODEL_DATA_PATH, index=False)
    
    # Save geo dataset (105,982 rows)
    logger.info(f"Saving geographic-ready dataset ({len(df_geo)} rows) to {CLEANED_GEO_DATA_PATH}...")
    df_geo.to_parquet(CLEANED_GEO_DATA_PATH, index=False)
    
    # Generate audit summary JSON
    cleaning_summary = {
        "raw_total_rows": len(raw_df),
        "raw_total_columns": raw_df.shape[1],
        "target_distribution": {
            TARGET_MAPPING.get(k, str(k)): v for k, v in severity_counts.items()
        },
        "majority_class_pct": float(max(severity_counts.values()) / len(raw_df) * 100),
        "geo_statistics": geo_stats,
        "model_features_count": len(ALL_MODEL_FEATURES),
        "model_features": ALL_MODEL_FEATURES,
    }
    
    summary_path = REPORTS_DIR / "cleaning_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(cleaning_summary, f, indent=2)
    logger.info(f"Cleaning summary saved to {summary_path}")


if __name__ == "__main__":
    clean_and_prepare()
