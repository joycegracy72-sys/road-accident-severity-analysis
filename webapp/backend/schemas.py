"""Pydantic data transfer schemas for FastAPI road accident explorer."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    model_loaded: bool
    data_loaded: bool
    model_name: str
    model_version: str = "1.0.0"
    total_collision_records: int
    hotspot_clusters_count: int
    primary_metric: str = "macro_f1"
    best_macro_f1: float


class GeoJSONGeometry(BaseModel):
    type: str = "Point"
    coordinates: List[float]  # [longitude, latitude]


class CollisionFeatureProperties(BaseModel):
    collision_index: str
    collision_severity: int
    severity_label: str
    speed_limit: int
    number_of_vehicles: int
    first_road_class: int
    road_type: int
    weather_conditions: int
    road_surface_conditions: int
    light_conditions: int
    urban_or_rural_area: int
    collision_date: Optional[str] = None
    collision_time: Optional[str] = None
    collision_hour: Optional[int] = None


class CollisionFeature(BaseModel):
    type: str = "Feature"
    geometry: GeoJSONGeometry
    properties: CollisionFeatureProperties


class CollisionsResponse(BaseModel):
    type: str = "FeatureCollection"
    features: List[CollisionFeature]
    total_in_viewport: int
    returned_count: int
    limit_applied: int
    is_capped: bool


class HotspotFeatureProperties(BaseModel):
    cluster_id: int
    total_collisions: int
    fatal_count: int
    serious_count: int
    slight_count: int
    fatal_rate_pct: float
    serious_rate_pct: float
    dominant_speed_limit: int
    dominant_urban_rural: str
    center_latitude: float
    center_longitude: float


class HotspotFeature(BaseModel):
    type: str = "Feature"
    geometry: GeoJSONGeometry
    properties: HotspotFeatureProperties


class HotspotsResponse(BaseModel):
    type: str = "FeatureCollection"
    features: List[HotspotFeature]
    total_clusters: int
    crs: str


class PredictionRequest(BaseModel):
    number_of_vehicles: int = Field(default=2, ge=1, le=20, description="Vehicles involved")
    speed_limit: int = Field(default=30, description="Speed limit in mph (20, 30, 40, 50, 60, 70)")
    collision_hour: int = Field(default=17, ge=0, le=23, description="Hour of collision (0-23)")
    collision_month: int = Field(default=10, ge=1, le=12, description="Month of collision (1-12)")
    first_road_class: int = Field(default=3, description="1=Motorway, 2=A(M), 3=A, 4=B, 5=C, 6=Unclassified")
    road_type: int = Field(default=6, description="1=Roundabout, 2=One-way, 3=Dual, 6=Single carriageway, 7=Slip")
    junction_detail_historic: int = Field(default=0, description="0=Not at junction, 1=Roundabout, 3=T-junction, 6=Crossroads")
    junction_control: int = Field(default=-1, description="-1=Not at junction, 2=Signal, 4=Give way/uncontrolled")
    second_road_class: int = Field(default=0, description="0=None, 1=Motorway, 3=A, 4=B, 6=Unclassified")
    pedestrian_crossing_human_control_historic: int = Field(default=0, description="0=None within 50m")
    pedestrian_crossing_physical_facilities_historic: int = Field(default=0, description="0=No physical facility within 50m")
    light_conditions: int = Field(default=1, description="1=Daylight, 4=Darkness lit, 6=Darkness no lights")
    weather_conditions: int = Field(default=1, description="1=Fine, 2=Rain, 3=Snow, 7=Fog")
    road_surface_conditions: int = Field(default=1, description="1=Dry, 2=Wet/damp, 3=Snow, 4=Frost/ice")
    special_conditions_at_site: int = Field(default=0, description="0=None, 4=Roadworks")
    carriageway_hazards_historic: int = Field(default=0, description="0=None")
    urban_or_rural_area: int = Field(default=1, description="1=Urban, 2=Rural")
    trunk_road_flag: int = Field(default=2, description="1=Trunk road, 2=Non-trunk")
    police_force: int = Field(default=1, description="Police force jurisdiction code")
    day_of_week: int = Field(default=6, ge=1, le=7, description="1=Sunday .. 7=Saturday")
    is_night: Optional[int] = Field(default=None, description="Optional night indicator; derived if omitted")


class PredictionResponse(BaseModel):
    predicted_severity: int
    predicted_label: str
    probabilities: Dict[str, float]
    disclaimer: str = (
        "Educational & Research Estimate: Predicts conditional severity given an incident has occurred. "
        "Does not predict occurrence probability. Not an operational emergency dispatch system."
    )


class GeocodeItem(BaseModel):
    name: str
    display_name: str
    latitude: float
    longitude: float
    osm_type: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postcode: Optional[str] = None


class GeocodeResponse(BaseModel):
    query: str
    results: List[GeocodeItem]


class DirectionsResponse(BaseModel):
    success: bool
    distance_km: Optional[float] = None
    distance_miles: Optional[float] = None
    duration_minutes: Optional[float] = None
    summary: Optional[str] = None
    route_geojson: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
