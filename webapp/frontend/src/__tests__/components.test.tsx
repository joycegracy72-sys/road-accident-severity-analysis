import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { CollisionDetailCard } from '../components/CollisionDetailCard';
import { HotspotDetailCard } from '../components/HotspotDetailCard';
import { DirectionsCard } from '../components/DirectionsCard';

describe('UI Component Cards', () => {
  it('CollisionDetailCard renders collision details correctly', () => {
    const mockCollision = {
      collision_index: '2022010001234',
      collision_severity: 1, // Fatal
      severity_label: 'Fatal',
      speed_limit: 60,
      number_of_vehicles: 2,
      first_road_class: 3,
      road_type: 6,
      weather_conditions: 1,
      road_surface_conditions: 1,
      light_conditions: 1,
      urban_or_rural_area: 2, // Rural
      collision_date: '12/05/2022',
      collision_time: '18:30',
    };

    render(<CollisionDetailCard collision={mockCollision} onClose={vi.fn()} />);

    expect(screen.getByText('Fatal Collision')).toBeDefined();
    expect(screen.getByText('2022010001234')).toBeDefined();
    expect(screen.getByText('60 mph')).toBeDefined();
    expect(screen.getByText('2 vehicle(s)')).toBeDefined();
    expect(screen.getByText('Rural')).toBeDefined();
  });

  it('HotspotDetailCard renders hotspot stats correctly', () => {
    const mockHotspot = {
      cluster_id: 21,
      total_collisions: 862,
      fatal_count: 3,
      serious_count: 163,
      slight_count: 696,
      fatal_rate_pct: 0.35,
      serious_rate_pct: 18.91,
      dominant_speed_limit: 20,
      dominant_urban_rural: 'Urban',
      center_latitude: 51.513,
      center_longitude: -0.147,
    };

    render(<HotspotDetailCard hotspot={mockHotspot} onClose={vi.fn()} />);

    expect(screen.getByText('DBSCAN Hotspot Cluster #21')).toBeDefined();
    expect(screen.getByText('862')).toBeDefined();
    expect(screen.getByText('Fatal (0.35%)')).toBeDefined();
    expect(screen.getByText('20 mph')).toBeDefined();
    expect(screen.getByText('Urban')).toBeDefined();
  });

  it('DirectionsCard displays route distance and duration', () => {
    const mockDirections = {
      success: true,
      distance_km: 45.2,
      distance_miles: 28.1,
      duration_minutes: 36.5,
      summary: '28.1 miles (36.5 mins)',
      route_geojson: {},
    };

    render(<DirectionsCard directions={mockDirections} onClose={vi.fn()} />);

    expect(screen.getByText('28.1 mi')).toBeDefined();
    expect(screen.getByText('36.5 min')).toBeDefined();
  });
});
