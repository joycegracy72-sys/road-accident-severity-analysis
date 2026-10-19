"""FastAPI application entrypoint for Road Accident Severity Explorer."""

import sys
from pathlib import Path

# Ensure repository root is in sys.path for robust resolution in all deployment environments
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from contextlib import asynccontextmanager
from typing import List, Optional
from fastapi import FastAPI, Query, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from webapp.backend.services import (
    state,
    get_health,
    get_hotspots_geojson,
    query_collisions_viewport,
    predict_collision_severity,
    geocode_location,
    get_directions,
)
from webapp.backend.schemas import (
    HealthResponse,
    HotspotsResponse,
    CollisionsResponse,
    PredictionRequest,
    PredictionResponse,
    GeocodeResponse,
    DirectionsResponse,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load datasets and model
    state.load()
    yield
    # Shutdown


app = FastAPI(
    title="Road Accident Severity & Hotspot Explorer API",
    description="Backend API for interactive geospatial exploration and ML severity prediction (GB 2022).",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for frontend local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse, tags=["System"])
def health_endpoint():
    """Returns backend system status, model loaded status, and dataset record counts."""
    return get_health()


@app.get("/api/hotspots", response_model=HotspotsResponse, tags=["Geospatial"])
def hotspots_endpoint():
    """Returns precomputed DBSCAN acute hotspot clusters as GeoJSON."""
    return get_hotspots_geojson()


@app.get("/api/collisions", response_model=CollisionsResponse, tags=["Geospatial"])
def collisions_endpoint(
    min_lon: float = Query(..., description="Western bounding box boundary"),
    min_lat: float = Query(..., description="Southern bounding box boundary"),
    max_lon: float = Query(..., description="Eastern bounding box boundary"),
    max_lat: float = Query(..., description="Northern bounding box boundary"),
    severity: Optional[List[int]] = Query(None, description="Filter by collision severity (1, 2, 3)"),
    speed_limit: Optional[List[int]] = Query(None, description="Filter by posted speed limit (mph)"),
    urban_rural: Optional[int] = Query(None, description="1=Urban, 2=Rural"),
    limit: int = Query(500, ge=1, le=2000, description="Max collision points returned in viewport"),
):
    """Returns collision points within the requested map viewport, subject to a hard result limit."""
    if min_lon > max_lon or min_lat > max_lat:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid bounding box: min coordinates must be <= max coordinates.",
        )
    return query_collisions_viewport(
        min_lon=min_lon,
        min_lat=min_lat,
        max_lon=max_lon,
        max_lat=max_lat,
        severities=severity,
        speed_limits=speed_limit,
        urban_rural=urban_rural,
        limit=limit,
    )


@app.post("/api/predict", response_model=PredictionResponse, tags=["Machine Learning"])
def predict_endpoint(req: PredictionRequest):
    """Predicts collision severity using the existing Balanced Random Forest pipeline."""
    try:
        return predict_collision_severity(req)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference error: {str(e)}",
        )


@app.get("/api/geocode", response_model=GeocodeResponse, tags=["Geospatial"])
async def geocode_endpoint(
    q: str = Query(..., min_length=1, description="Location search query string"),
    limit: int = Query(5, ge=1, le=10, description="Max results"),
):
    """Search for locations using free OpenStreetMap-powered geocoding."""
    return await geocode_location(q, limit=limit)


@app.get("/api/directions", response_model=DirectionsResponse, tags=["Geospatial"])
async def directions_endpoint(
    origin_lon: float = Query(..., description="Origin longitude"),
    origin_lat: float = Query(..., description="Origin latitude"),
    dest_lon: float = Query(..., description="Destination longitude"),
    dest_lat: float = Query(..., description="Destination latitude"),
):
    """Calculates driving directions between origin and destination using OSRM."""
    return await get_directions(
        origin_lon=origin_lon,
        origin_lat=origin_lat,
        dest_lon=dest_lon,
        dest_lat=dest_lat,
    )
