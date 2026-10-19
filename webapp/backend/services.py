"""Data access, geospatial querying, machine learning inference, and external services."""

from pathlib import Path
import json
import logging
import joblib
import pandas as pd
import numpy as np
import httpx
from typing import Dict, Any, List, Optional, Tuple

from src.utils import (
    CLEANED_GEO_DATA_PATH,
    PROCESSED_DATA_DIR,
    SAVED_MODEL_PATH,
    MODEL_METADATA_PATH,
    ALL_MODEL_FEATURES,
    TARGET_MAPPING,
)
from webapp.backend.schemas import (
    HealthResponse,
    CollisionsResponse,
    CollisionFeature,
    CollisionFeatureProperties,
    GeoJSONGeometry,
    HotspotsResponse,
    HotspotFeature,
    HotspotFeatureProperties,
    PredictionRequest,
    PredictionResponse,
    GeocodeResponse,
    GeocodeItem,
    DirectionsResponse,
)

logger = logging.getLogger("backend_services")
logging.basicConfig(level=logging.INFO)


class AppState:
    """Singleton holding in-memory loaded datasets, model pipeline, and cached structures."""
    def __init__(self):
        self.geo_df: Optional[pd.DataFrame] = None
        self.model_pipeline = None
        self.model_metadata: Dict[str, Any] = {}
        self.hotspots_df: Optional[pd.DataFrame] = None
        self.hotspots_json: Optional[Dict[str, Any]] = None
        self.is_loaded = False

    def load(self):
        if self.is_loaded:
            return

        logger.info("Initializing AppState: loading data and model artifacts...")
        # 1. Load Geo DataFrame
        if CLEANED_GEO_DATA_PATH.exists():
            self.geo_df = pd.read_parquet(CLEANED_GEO_DATA_PATH)
            logger.info(f"Loaded {len(self.geo_df):,} geographic collision records.")
        else:
            logger.error(f"Geo data missing at {CLEANED_GEO_DATA_PATH}")

        # 2. Load Model Pipeline
        if SAVED_MODEL_PATH.exists():
            self.model_pipeline = joblib.load(SAVED_MODEL_PATH)
            logger.info("Loaded trained scikit-learn pipeline.")
        else:
            logger.error(f"Model missing at {SAVED_MODEL_PATH}")

        if MODEL_METADATA_PATH.exists():
            with open(MODEL_METADATA_PATH, "r", encoding="utf-8") as f:
                self.model_metadata = json.load(f)

        # 3. Load Hotspots
        hotspots_csv = PROCESSED_DATA_DIR / "hotspots_clusters.csv"
        hotspots_json_path = PROCESSED_DATA_DIR / "hotspots_summary.json"
        if hotspots_csv.exists():
            self.hotspots_df = pd.read_csv(hotspots_csv)
            logger.info(f"Loaded {len(self.hotspots_df)} precomputed hotspot clusters.")

        if hotspots_json_path.exists():
            with open(hotspots_json_path, "r", encoding="utf-8") as f:
                self.hotspots_json = json.load(f)

        self.is_loaded = True


state = AppState()


def get_health() -> HealthResponse:
    """Returns backend system status and loaded asset statistics."""
    total_records = len(state.geo_df) if state.geo_df is not None else 0
    hotspots_count = len(state.hotspots_df) if state.hotspots_df is not None else 0
    model_name = state.model_metadata.get("model_name", "Balanced Random Forest")
    best_macro_f1 = float(state.model_metadata.get("best_macro_f1", 0.3691))

    return HealthResponse(
        status="ok",
        model_loaded=(state.model_pipeline is not None),
        data_loaded=(state.geo_df is not None and not state.geo_df.empty),
        model_name=model_name,
        model_version="1.0.0",
        total_collision_records=total_records,
        hotspot_clusters_count=hotspots_count,
        primary_metric="macro_f1",
        best_macro_f1=best_macro_f1,
    )


def get_hotspots_geojson() -> HotspotsResponse:
    """Returns precomputed DBSCAN hotspot clusters as GeoJSON."""
    if state.hotspots_df is None or state.hotspots_df.empty:
        return HotspotsResponse(
            type="FeatureCollection",
            features=[],
            total_clusters=0,
            crs="EPSG:27700",
        )

    features: List[HotspotFeature] = []
    for _, row in state.hotspots_df.iterrows():
        props = HotspotFeatureProperties(
            cluster_id=int(row["cluster_id"]),
            total_collisions=int(row["total_collisions"]),
            fatal_count=int(row["fatal_count"]),
            serious_count=int(row["serious_count"]),
            slight_count=int(row["slight_count"]),
            fatal_rate_pct=float(row["fatal_rate_pct"]),
            serious_rate_pct=float(row["serious_rate_pct"]),
            dominant_speed_limit=int(row["dominant_speed_limit"]),
            dominant_urban_rural=str(row["dominant_urban_rural"]),
            center_latitude=float(row["center_latitude"]),
            center_longitude=float(row["center_longitude"]),
        )
        geom = GeoJSONGeometry(
            type="Point",
            coordinates=[float(row["center_longitude"]), float(row["center_latitude"])],
        )
        features.append(HotspotFeature(geometry=geom, properties=props))

    crs = "EPSG:27700 (British National Grid, units: meters)"
    if state.hotspots_json and "crs" in state.hotspots_json:
        crs = state.hotspots_json["crs"]

    return HotspotsResponse(
        type="FeatureCollection",
        features=features,
        total_clusters=len(features),
        crs=crs,
    )


def query_collisions_viewport(
    min_lon: float,
    min_lat: float,
    max_lon: float,
    max_lat: float,
    severities: Optional[List[int]] = None,
    speed_limits: Optional[List[int]] = None,
    urban_rural: Optional[int] = None,
    limit: int = 500,
) -> CollisionsResponse:
    """Queries collision records within a geographic bounding box and filters.

    Enforces a strict result cap (max 2000) to protect browser memory and network performance.
    """
    if state.geo_df is None or state.geo_df.empty:
        return CollisionsResponse(
            type="FeatureCollection",
            features=[],
            total_in_viewport=0,
            returned_count=0,
            limit_applied=limit,
            is_capped=False,
        )

    hard_max_limit = 2000
    safe_limit = max(1, min(limit, hard_max_limit))

    # Fast spatial bounding box filter
    df = state.geo_df
    spatial_mask = (
        (df["longitude"] >= min_lon)
        & (df["longitude"] <= max_lon)
        & (df["latitude"] >= min_lat)
        & (df["latitude"] <= max_lat)
    )

    filtered = df[spatial_mask]

    # Severity filter
    if severities:
        filtered = filtered[filtered["collision_severity"].isin(severities)]

    # Speed limit filter
    if speed_limits:
        filtered = filtered[filtered["speed_limit"].isin(speed_limits)]

    # Urban/Rural filter
    if urban_rural in [1, 2]:
        filtered = filtered[filtered["urban_or_rural_area"] == urban_rural]

    total_in_viewport = len(filtered)
    is_capped = total_in_viewport > safe_limit

    # Sample if capped to preserve balanced geographic representation
    if is_capped:
        sampled_df = filtered.sample(n=safe_limit, random_state=42)
    else:
        sampled_df = filtered

    features: List[CollisionFeature] = []
    for _, row in sampled_df.iterrows():
        sev = int(row["collision_severity"])
        props = CollisionFeatureProperties(
            collision_index=str(row["collision_index"]),
            collision_severity=sev,
            severity_label=TARGET_MAPPING.get(sev, "Unknown"),
            speed_limit=int(row["speed_limit"]),
            number_of_vehicles=int(row["number_of_vehicles"]),
            first_road_class=int(row["first_road_class"]),
            road_type=int(row["road_type"]),
            weather_conditions=int(row["weather_conditions"]),
            road_surface_conditions=int(row["road_surface_conditions"]),
            light_conditions=int(row["light_conditions"]),
            urban_or_rural_area=int(row["urban_or_rural_area"]),
            collision_date=str(row.get("date", "")),
            collision_time=str(row.get("time", "")),
            collision_hour=int(row["collision_hour"]) if pd.notna(row.get("collision_hour")) else None,
        )
        geom = GeoJSONGeometry(
            type="Point",
            coordinates=[float(row["longitude"]), float(row["latitude"])],
        )
        features.append(CollisionFeature(geometry=geom, properties=props))

    return CollisionsResponse(
        type="FeatureCollection",
        features=features,
        total_in_viewport=total_in_viewport,
        returned_count=len(features),
        limit_applied=safe_limit,
        is_capped=is_capped,
    )


def predict_collision_severity(req: PredictionRequest) -> PredictionResponse:
    """Executes inference using the existing serialized scikit-learn pipeline."""
    if state.model_pipeline is None:
        raise RuntimeError("Model pipeline is not loaded on server.")

    # Determine is_night if not explicitly provided
    is_night_val = req.is_night
    if is_night_val is None:
        is_night_val = 1 if req.collision_hour in [21, 22, 23, 0, 1, 2, 3, 4, 5] else 0

    # Build input dictionary preserving ALL_MODEL_FEATURES order
    input_data = {
        "number_of_vehicles": [req.number_of_vehicles],
        "speed_limit": [req.speed_limit],
        "collision_hour": [req.collision_hour],
        "collision_month": [req.collision_month],
        "first_road_class": [req.first_road_class],
        "road_type": [req.road_type],
        "junction_detail_historic": [req.junction_detail_historic],
        "junction_control": [req.junction_control],
        "second_road_class": [req.second_road_class],
        "pedestrian_crossing_human_control_historic": [req.pedestrian_crossing_human_control_historic],
        "pedestrian_crossing_physical_facilities_historic": [req.pedestrian_crossing_physical_facilities_historic],
        "light_conditions": [req.light_conditions],
        "weather_conditions": [req.weather_conditions],
        "road_surface_conditions": [req.road_surface_conditions],
        "special_conditions_at_site": [req.special_conditions_at_site],
        "carriageway_hazards_historic": [req.carriageway_hazards_historic],
        "urban_or_rural_area": [req.urban_or_rural_area],
        "trunk_road_flag": [req.trunk_road_flag],
        "police_force": [req.police_force],
        "day_of_week": [req.day_of_week],
        "is_night": [is_night_val],
    }

    input_df = pd.DataFrame(input_data)
    # Ensure exact column ordering matching training contract
    input_df = input_df[ALL_MODEL_FEATURES]

    # Predict class
    pred = int(state.model_pipeline.predict(input_df)[0])
    pred_label = TARGET_MAPPING.get(pred, "Unknown")

    # Predict probabilities
    probas_dict = {"Fatal": 0.0, "Serious": 0.0, "Slight": 0.0}
    if hasattr(state.model_pipeline, "predict_proba"):
        raw_probas = state.model_pipeline.predict_proba(input_df)[0]
        classes = state.model_pipeline.classes_
        for idx, cls_code in enumerate(classes):
            name = TARGET_MAPPING.get(int(cls_code), str(cls_code))
            probas_dict[name] = round(float(raw_probas[idx]), 4)

    return PredictionResponse(
        predicted_severity=pred,
        predicted_label=pred_label,
        probabilities=probas_dict,
    )


# In-memory cache for search queries
_search_cache: Dict[str, List[GeocodeItem]] = {}

async def geocode_location(query: str, limit: int = 5) -> GeocodeResponse:
    """Location search using Photon by Komoot (permissive, free, OSM-based search).

    Caches queries in memory to avoid repeated requests.
    """
    q_clean = query.strip()
    if not q_clean:
        return GeocodeResponse(query=query, results=[])

    if q_clean.lower() in _search_cache:
        return GeocodeResponse(query=query, results=_search_cache[q_clean.lower()])

    url = f"https://photon.komoot.io/api/?q={q_clean}&limit={limit}"
    results: List[GeocodeItem] = []

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            headers = {"User-Agent": "RoadAccidentExplorer/1.0 (academic-safety-research)"}
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                for feat in data.get("features", []):
                    coords = feat.get("geometry", {}).get("coordinates", [])
                    props = feat.get("properties", {})
                    if len(coords) >= 2:
                        name = props.get("name", q_clean)
                        parts = [name]
                        if "city" in props and props["city"] != name:
                            parts.append(props["city"])
                        if "state" in props:
                            parts.append(props["state"])
                        if "country" in props:
                            parts.append(props["country"])

                        display_name = ", ".join(parts)
                        results.append(
                            GeocodeItem(
                                name=name,
                                display_name=display_name,
                                longitude=float(coords[0]),
                                latitude=float(coords[1]),
                                osm_type=props.get("osm_value"),
                                city=props.get("city"),
                                state=props.get("state"),
                                country=props.get("country"),
                                postcode=props.get("postcode"),
                            )
                        )
                _search_cache[q_clean.lower()] = results
    except Exception as e:
        logger.warning(f"Geocoding request failed: {e}")

    return GeocodeResponse(query=query, results=results)


async def get_directions(
    origin_lon: float,
    origin_lat: float,
    dest_lon: float,
    dest_lat: float,
) -> DirectionsResponse:
    """Driving directions using OSRM public demo routing service.

    Returns driving route GeoJSON, distance, and duration.
    """
    osrm_url = (
        f"https://router.project-osrm.org/route/v1/driving/"
        f"{origin_lon},{origin_lat};{dest_lon},{dest_lat}?"
        f"overview=full&geometries=geojson"
    )

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            headers = {"User-Agent": "RoadAccidentExplorer/1.0"}
            resp = await client.get(osrm_url, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == "Ok" and "routes" in data and len(data["routes"]) > 0:
                    route = data["routes"][0]
                    dist_meters = float(route.get("distance", 0.0))
                    duration_sec = float(route.get("duration", 0.0))
                    geometry = route.get("geometry")

                    dist_km = round(dist_meters / 1000.0, 2)
                    dist_miles = round(dist_km * 0.621371, 2)
                    duration_min = round(duration_sec / 60.0, 1)

                    return DirectionsResponse(
                        success=True,
                        distance_km=dist_km,
                        distance_miles=dist_miles,
                        duration_minutes=duration_min,
                        summary=f"{dist_miles} miles ({duration_min} mins)",
                        route_geojson={
                            "type": "Feature",
                            "geometry": geometry,
                            "properties": {
                                "distance_km": dist_km,
                                "duration_min": duration_min,
                            },
                        },
                    )
                else:
                    return DirectionsResponse(
                        success=False,
                        message=f"Routing service returned: {data.get('message', 'No route found')}",
                    )
            else:
                return DirectionsResponse(
                    success=False,
                    message=f"Routing service unavailable (HTTP {resp.status_code})",
                )
    except Exception as e:
        logger.warning(f"Directions request failed: {e}")
        return DirectionsResponse(
            success=False,
            message="Driving directions service temporarily unavailable. Please verify internet connectivity.",
        )
