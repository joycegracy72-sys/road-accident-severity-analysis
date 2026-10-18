"""Automated tests for dashboard KPI and filtering calculations."""

import pytest
import pandas as pd
from src.utils import CLEANED_GEO_DATA_PATH


def test_dashboard_filtering_logic():
    df_geo = pd.read_parquet(CLEANED_GEO_DATA_PATH)
    
    # Filter by severity = 1 (Fatal)
    fatal_df = df_geo[df_geo["collision_severity"] == 1]
    assert len(fatal_df) == 1602
    
    # Filter by Urban vs Rural
    urban_df = df_geo[df_geo["urban_or_rural_area"] == 1]
    rural_df = df_geo[df_geo["urban_or_rural_area"] == 2]
    assert len(urban_df) == 71763
    assert len(rural_df) == 34219
    
    # Combined filter: Rural Fatal collisions
    rural_fatal = df_geo[(df_geo["urban_or_rural_area"] == 2) & (df_geo["collision_severity"] == 1)]
    assert len(rural_fatal) == 1022
    assert (len(rural_fatal) / len(rural_df) * 100) > 2.5, "Rural fatal rate must be ~2.99%"
