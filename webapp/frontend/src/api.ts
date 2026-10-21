import type {
  CollisionsResponse,
  HotspotsResponse,
  PredictionRequest,
  PredictionResponse,
  GeocodeResponse,
  DirectionsResponse,
} from './types';

function getApiBase(): string {
  const envUrl = import.meta.env.VITE_API_BASE_URL;
  if (envUrl && typeof envUrl === 'string') {
    const trimmed = envUrl.trim().replace(/\/+$/, '');
    return trimmed.endsWith('/api') ? trimmed : `${trimmed}/api`;
  }
  return import.meta.env.PROD ? 'https://road-accident-api.onrender.com/api' : '/api';
}

export const API_BASE = getApiBase();

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error('Failed to fetch health');
  return res.json();
}

export async function fetchHotspots(): Promise<HotspotsResponse> {
  const res = await fetch(`${API_BASE}/hotspots`);
  if (!res.ok) throw new Error('Failed to fetch hotspots');
  return res.json();
}

export async function fetchCollisions(params: {
  min_lon: number;
  min_lat: number;
  max_lon: number;
  max_lat: number;
  severities?: number[];
  speed_limits?: number[];
  urban_rural?: number;
  limit?: number;
}): Promise<CollisionsResponse> {
  const query = new URLSearchParams();
  query.set('min_lon', params.min_lon.toString());
  query.set('min_lat', params.min_lat.toString());
  query.set('max_lon', params.max_lon.toString());
  query.set('max_lat', params.max_lat.toString());
  if (params.limit) query.set('limit', params.limit.toString());
  if (params.urban_rural) query.set('urban_rural', params.urban_rural.toString());

  if (params.severities && params.severities.length > 0) {
    params.severities.forEach((s) => query.append('severity', s.toString()));
  }
  if (params.speed_limits && params.speed_limits.length > 0) {
    params.speed_limits.forEach((sl) => query.append('speed_limit', sl.toString()));
  }

  const res = await fetch(`${API_BASE}/collisions?${query.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch collisions');
  return res.json();
}

export async function postPrediction(data: PredictionRequest): Promise<PredictionResponse> {
  const res = await fetch(`${API_BASE}/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Prediction failed');
  }
  return res.json();
}

export async function searchLocations(q: string): Promise<GeocodeResponse> {
  if (!q.trim()) return { query: q, results: [] };
  const res = await fetch(`${API_BASE}/geocode?q=${encodeURIComponent(q)}&limit=5`);
  if (!res.ok) throw new Error('Search failed');
  return res.json();
}

export async function fetchDirections(
  originLon: number,
  originLat: number,
  destLon: number,
  destLat: number
): Promise<DirectionsResponse> {
  const res = await fetch(
    `${API_BASE}/directions?origin_lon=${originLon}&origin_lat=${originLat}&dest_lon=${destLon}&dest_lat=${destLat}`
  );
  if (!res.ok) throw new Error('Failed to fetch directions');
  return res.json();
}
