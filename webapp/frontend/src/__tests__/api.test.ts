import { describe, it, expect, vi, beforeEach } from 'vitest';
import { API_BASE, fetchCollisions, postPrediction, searchLocations } from '../api';

describe('Frontend API Client', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('fetchCollisions formats query string with bounds and limit', async () => {
    const mockResponse = { type: 'FeatureCollection', features: [], total_in_viewport: 0, returned_count: 0, limit_applied: 500, is_capped: false };
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    } as any);

    const res = await fetchCollisions({
      min_lon: -1.5,
      min_lat: 52.0,
      max_lon: -0.5,
      max_lat: 53.0,
      severities: [1, 2],
      speed_limits: [30, 40],
      limit: 250,
    });

    expect(fetchSpy).toHaveBeenCalledTimes(1);
    const calledUrl = fetchSpy.mock.calls[0][0] as string;
    expect(calledUrl).toContain('min_lon=-1.5');
    expect(calledUrl).toContain('max_lat=53');
    expect(calledUrl).toContain('severity=1');
    expect(calledUrl).toContain('severity=2');
    expect(calledUrl).toContain('speed_limit=30');
    expect(calledUrl).toContain('limit=250');
    expect(res).toEqual(mockResponse);
  });

  it('postPrediction sends POST with correct body and headers', async () => {
    const mockPred = {
      predicted_severity: 2,
      predicted_label: 'Serious',
      probabilities: { Fatal: 0.1, Serious: 0.5, Slight: 0.4 },
      disclaimer: 'test',
    };
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => mockPred,
    } as any);

    const payload = {
      number_of_vehicles: 2,
      speed_limit: 40,
      collision_hour: 14,
      collision_month: 6,
      first_road_class: 3,
      road_type: 6,
      junction_detail_historic: 0,
      junction_control: -1,
      second_road_class: 0,
      pedestrian_crossing_human_control_historic: 0,
      pedestrian_crossing_physical_facilities_historic: 0,
      light_conditions: 1,
      weather_conditions: 1,
      road_surface_conditions: 1,
      special_conditions_at_site: 0,
      carriageway_hazards_historic: 0,
      urban_or_rural_area: 2,
      trunk_road_flag: 2,
      police_force: 1,
      day_of_week: 5,
    };

    const res = await postPrediction(payload);
    expect(fetchSpy).toHaveBeenCalledWith(`${API_BASE}/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    expect(res.predicted_label).toBe('Serious');
  });

  it('searchLocations returns empty array for empty query', async () => {
    const res = await searchLocations('   ');
    expect(res.results).toEqual([]);
  });
});
