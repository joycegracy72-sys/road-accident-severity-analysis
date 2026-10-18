"""Geographic hotspot analysis using British National Grid (EPSG:27700) projected clustering."""

from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from typing import Dict, Any, List

from src.utils import (
    CLEANED_GEO_DATA_PATH,
    PROCESSED_DATA_DIR,
    REPORTS_DIR,
    TARGET_COL,
    TARGET_MAPPING,
    setup_logger,
)

logger = setup_logger("hotspot_analysis")


def run_hotspot_analysis(
    eps_meters: float = 250.0,
    min_samples: int = 15,
) -> Dict[str, Any]:
    """Runs DBSCAN clustering on projected British National Grid (OSGR) coordinates in meters.
    
    Parameters:
      eps_meters: Maximum distance between two samples for them to be considered in the same neighborhood (meters).
      min_samples: The number of samples in a neighborhood for a point to be considered a core point.
    """
    logger.info(f"Loading geographic dataset from {CLEANED_GEO_DATA_PATH}...")
    df = pd.read_parquet(CLEANED_GEO_DATA_PATH)
    logger.info(f"Loaded {len(df):,} records with validated coordinates.")
    
    # Coordinates in true meters (EPSG:27700 British National Grid)
    coords_metric = df[["location_easting_osgr", "location_northing_osgr"]].values
    
    logger.info(f"Running DBSCAN clustering (eps={eps_meters}m, min_samples={min_samples})...")
    # Metric Euclidean distance directly on meters
    db = DBSCAN(eps=eps_meters, min_samples=min_samples, metric="euclidean", n_jobs=-1)
    df["cluster_id"] = db.fit_predict(coords_metric)
    
    num_clusters = int(df["cluster_id"].nunique() - (1 if -1 in df["cluster_id"] else 0))
    clustered_points = int((df["cluster_id"] != -1).sum())
    noise_points = int((df["cluster_id"] == -1).sum())
    
    logger.info(
        f"DBSCAN identified {num_clusters} acute clusters ({clustered_points:,} collisions in clusters, {noise_points:,} noise points)."
    )
    
    # Aggregate cluster statistics
    cluster_summaries: List[Dict[str, Any]] = []
    
    grouped = df[df["cluster_id"] != -1].groupby("cluster_id")
    for cluster_id, group in grouped:
        total_collisions = len(group)
        fatal_count = int((group[TARGET_COL] == 1).sum())
        serious_count = int((group[TARGET_COL] == 2).sum())
        slight_count = int((group[TARGET_COL] == 3).sum())
        
        center_easting = float(group["location_easting_osgr"].mean())
        center_northing = float(group["location_northing_osgr"].mean())
        center_lat = float(group["latitude"].mean())
        center_lon = float(group["longitude"].mean())
        
        # Dominant road type and speed limit
        mode_speed = int(group["speed_limit"].mode().iloc[0]) if not group["speed_limit"].empty else 30
        mode_urban = int(group["urban_or_rural_area"].mode().iloc[0]) if not group["urban_or_rural_area"].empty else 1
        
        cluster_summaries.append({
            "cluster_id": int(cluster_id),
            "total_collisions": total_collisions,
            "fatal_count": fatal_count,
            "serious_count": serious_count,
            "slight_count": slight_count,
            "fatal_rate_pct": round(fatal_count / total_collisions * 100, 2),
            "serious_rate_pct": round(serious_count / total_collisions * 100, 2),
            "center_latitude": round(center_lat, 6),
            "center_longitude": round(center_lon, 6),
            "center_easting": round(center_easting, 1),
            "center_northing": round(center_northing, 1),
            "dominant_speed_limit": mode_speed,
            "dominant_urban_rural": "Urban" if mode_urban == 1 else "Rural",
        })
        
    # Sort clusters by collision volume descending
    cluster_summaries.sort(key=lambda x: x["total_collisions"], reverse=True)
    
    # Save top clusters and overall analysis metadata
    output_meta = {
        "dataset_scope": "Great Britain personal-injury collisions (2022 snapshot)",
        "crs": "EPSG:27700 (British National Grid, units: meters)",
        "parameters": {
            "eps_meters": eps_meters,
            "min_samples": min_samples,
            "metric": "euclidean on OSGR Easting/Northing meters",
        },
        "total_analyzed_records": len(df),
        "total_clusters_found": num_clusters,
        "total_clustered_collisions": clustered_points,
        "clustered_percentage": round(clustered_points / len(df) * 100, 2),
        "top_20_clusters": cluster_summaries[:20],
    }
    
    out_json_path = PROCESSED_DATA_DIR / "hotspots_summary.json"
    with open(out_json_path, "w", encoding="utf-8") as f:
        json.dump(output_meta, f, indent=2)
    logger.info(f"Saved hotspots summary to {out_json_path}")
    
    # Also save top clusters CSV for simple dashboard loading
    top_clusters_df = pd.DataFrame(cluster_summaries)
    out_csv_path = PROCESSED_DATA_DIR / "hotspots_clusters.csv"
    top_clusters_df.to_csv(out_csv_path, index=False)
    logger.info(f"Saved cluster table to {out_csv_path}")
    
    return output_meta


if __name__ == "__main__":
    run_hotspot_analysis()
