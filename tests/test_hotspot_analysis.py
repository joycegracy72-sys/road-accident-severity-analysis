"""Automated tests for EPSG:27700 British National Grid projected hotspot analysis."""

import pytest
import json
import pandas as pd
from src.utils import PROCESSED_DATA_DIR
from src.hotspot_analysis import run_hotspot_analysis


def test_hotspot_analysis_output_exists_and_valid():
    json_path = PROCESSED_DATA_DIR / "hotspots_summary.json"
    csv_path = PROCESSED_DATA_DIR / "hotspots_clusters.csv"
    
    assert json_path.exists(), "Hotspots summary JSON must exist"
    assert csv_path.exists(), "Hotspots CSV must exist"
    
    with open(json_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
        
    assert meta["crs"] == "EPSG:27700 (British National Grid, units: meters)"
    assert meta["total_clusters_found"] > 0
    assert len(meta["top_20_clusters"]) > 0
    
    df_clusters = pd.read_csv(csv_path)
    assert not df_clusters.empty
    assert "total_collisions" in df_clusters.columns
    assert "fatal_count" in df_clusters.columns
    assert "serious_count" in df_clusters.columns
    assert "center_latitude" in df_clusters.columns
    assert "center_longitude" in df_clusters.columns
