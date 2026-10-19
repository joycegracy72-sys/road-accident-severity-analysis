export interface CollisionProperties {
  collision_index: string;
  collision_severity: number;
  severity_label: string;
  speed_limit: number;
  number_of_vehicles: number;
  first_road_class: number;
  road_type: number;
  weather_conditions: number;
  road_surface_conditions: number;
  light_conditions: number;
  urban_or_rural_area: number;
  collision_date?: string;
  collision_time?: string;
  collision_hour?: number;
}

export interface CollisionFeature {
  type: 'Feature';
  geometry: {
    type: 'Point';
    coordinates: [number, number]; // [lon, lat]
  };
  properties: CollisionProperties;
}

export interface CollisionsResponse {
  type: 'FeatureCollection';
  features: CollisionFeature[];
  total_in_viewport: number;
  returned_count: number;
  limit_applied: number;
  is_capped: boolean;
}

export interface HotspotProperties {
  cluster_id: number;
  total_collisions: number;
  fatal_count: number;
  serious_count: number;
  slight_count: number;
  fatal_rate_pct: number;
  serious_rate_pct: number;
  dominant_speed_limit: number;
  dominant_urban_rural: string;
  center_latitude: number;
  center_longitude: number;
}

export interface HotspotFeature {
  type: 'Feature';
  geometry: {
    type: 'Point';
    coordinates: [number, number];
  };
  properties: HotspotProperties;
}

export interface HotspotsResponse {
  type: 'FeatureCollection';
  features: HotspotFeature[];
  total_clusters: number;
  crs: string;
}

export interface PredictionRequest {
  number_of_vehicles: number;
  speed_limit: number;
  collision_hour: number;
  collision_month: number;
  first_road_class: number;
  road_type: number;
  junction_detail_historic: number;
  junction_control: number;
  second_road_class: number;
  pedestrian_crossing_human_control_historic: number;
  pedestrian_crossing_physical_facilities_historic: number;
  light_conditions: number;
  weather_conditions: number;
  road_surface_conditions: number;
  special_conditions_at_site: number;
  carriageway_hazards_historic: number;
  urban_or_rural_area: number;
  trunk_road_flag: number;
  police_force: number;
  day_of_week: number;
  is_night?: number;
}

export interface PredictionResponse {
  predicted_severity: number;
  predicted_label: string;
  probabilities: {
    Fatal: number;
    Serious: number;
    Slight: number;
  };
  disclaimer: string;
}

export interface GeocodeItem {
  name: string;
  display_name: string;
  latitude: number;
  longitude: number;
  city?: string;
  state?: string;
  country?: string;
  postcode?: string;
}

export interface GeocodeResponse {
  query: string;
  results: GeocodeItem[];
}

export interface DirectionsResponse {
  success: boolean;
  distance_km?: number;
  distance_miles?: number;
  duration_minutes?: number;
  summary?: string;
  route_geojson?: any;
  message?: string;
}

export interface FilterState {
  showFatal: boolean;
  showSerious: boolean;
  showSlight: boolean;
  speedLimit: number | 'all';
  urbanRural: number | 'all';
  showHotspots: boolean;
  showCollisions: boolean;
}
