"""Automated tests for dataset schema, missingness, and coordinate integrity."""

import pytest
import pandas as pd
from pathlib import Path

from src.utils import (
    RAW_DATA_PATH,
    CLEANED_MODEL_DATA_PATH,
    CLEANED_GEO_DATA_PATH,
    TARGET_COL,
    TARGET_MAPPING,
    WGS84_BOUNDS,
    OSGR_BOUNDS,
)
from src.clean_collisions import validate_raw_schema, validate_coordinates


def test_raw_dataset_exists_and_unmodified():
    assert RAW_DATA_PATH.exists(), f"Raw dataset missing at {RAW_DATA_PATH}"
    df_sample = pd.read_csv(RAW_DATA_PATH, nrows=10)
    assert len(df_sample.columns) == 44, f"Expected 44 columns, got {len(df_sample.columns)}"


def test_validate_raw_schema_rejects_missing_cols():
    bad_df = pd.DataFrame({"some_col": [1, 2]})
    with pytest.raises(ValueError, match="Missing essential raw columns"):
        validate_raw_schema(bad_df)


def test_target_distribution_and_mapping():
    assert TARGET_COL == "collision_severity"
    assert TARGET_MAPPING[1] == "Fatal"
    assert TARGET_MAPPING[2] == "Serious"
    assert TARGET_MAPPING[3] == "Slight"


def test_coordinate_filtering_and_bounds():
    df_geo = pd.read_parquet(CLEANED_GEO_DATA_PATH)
    assert len(df_geo) == 105982, f"Expected 105,982 records with valid coordinates, got {len(df_geo)}"
    
    lon_min, lon_max, lat_min, lat_max = WGS84_BOUNDS
    east_min, east_max, north_min, north_max = OSGR_BOUNDS
    
    assert df_geo["longitude"].isna().sum() == 0
    assert df_geo["latitude"].isna().sum() == 0
    assert (df_geo["longitude"] >= lon_min).all()
    assert (df_geo["longitude"] <= lon_max).all()
    assert (df_geo["latitude"] >= lat_min).all()
    assert (df_geo["latitude"] <= lat_max).all()
    assert (df_geo["location_easting_osgr"] >= east_min).all()
    assert (df_geo["location_easting_osgr"] <= east_max).all()
    assert (df_geo["location_northing_osgr"] >= north_min).all()
    assert (df_geo["location_northing_osgr"] <= north_max).all()
