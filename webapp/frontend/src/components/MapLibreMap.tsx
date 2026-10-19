import React, { useEffect, useRef, useState, useCallback } from 'react';
import * as maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import mapWorkerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url';
import type {
  CollisionsResponse,
  HotspotsResponse,
  CollisionProperties,
  HotspotProperties,
  GeocodeItem,
  DirectionsResponse,
} from '../types';

// Configure MapLibre Web Worker for Vite bundling
if (typeof maplibregl.setWorkerUrl === 'function') {
  maplibregl.setWorkerUrl(mapWorkerUrl);
}

// Robust basemap specifications with guaranteed tile availability & attribution
export const BASEMAP_STYLES: Record<string, { name: string; style: maplibregl.StyleSpecification }> = {
  'osm-standard': {
    name: 'OpenStreetMap (Standard)',
    style: {
      version: 8,
      sources: {
        'osm-tiles': {
          type: 'raster',
          tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
          tileSize: 256,
          attribution:
            '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors',
          maxzoom: 19,
        },
      },
      layers: [
        {
          id: 'osm-tiles-layer',
          type: 'raster',
          source: 'osm-tiles',
          minzoom: 0,
          maxzoom: 19,
        },
      ],
    },
  },
  'osm-hot': {
    name: 'Humanitarian (Light)',
    style: {
      version: 8,
      sources: {
        'osm-hot-tiles': {
          type: 'raster',
          tiles: [
            'https://a.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png',
            'https://b.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png',
          ],
          tileSize: 256,
          attribution:
            '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors, Tiles &copy; <a href="https://www.hotosm.org/" target="_blank" rel="noopener">HOT</a>',
          maxzoom: 19,
        },
      },
      layers: [
        {
          id: 'osm-hot-layer',
          type: 'raster',
          source: 'osm-hot-tiles',
          minzoom: 0,
          maxzoom: 19,
        },
      ],
    },
  },
  'osm-topo': {
    name: 'OpenTopoMap (Terrain)',
    style: {
      version: 8,
      sources: {
        'opentopo-tiles': {
          type: 'raster',
          tiles: [
            'https://a.tile.opentopomap.org/{z}/{x}/{y}.png',
            'https://b.tile.opentopomap.org/{z}/{x}/{y}.png',
            'https://c.tile.opentopomap.org/{z}/{x}/{y}.png',
          ],
          tileSize: 256,
          attribution:
            '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors, &copy; <a href="https://opentopomap.org" target="_blank" rel="noopener">OpenTopoMap</a>',
          maxzoom: 17,
        },
      },
      layers: [
        {
          id: 'opentopo-layer',
          type: 'raster',
          source: 'opentopo-tiles',
          minzoom: 0,
          maxzoom: 17,
        },
      ],
    },
  },
  'carto-positron': {
    name: 'CARTO Positron',
    style: {
      version: 8,
      sources: {
        'carto-positron': {
          type: 'raster',
          tiles: [
            'https://a.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png',
            'https://b.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png',
            'https://c.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png',
            'https://d.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png',
          ],
          tileSize: 256,
          attribution:
            '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors, &copy; <a href="https://carto.com/attributions" target="_blank" rel="noopener">CARTO</a>',
          maxzoom: 19,
        },
      },
      layers: [
        {
          id: 'carto-positron-layer',
          type: 'raster',
          source: 'carto-positron',
          minzoom: 0,
          maxzoom: 19,
        },
      ],
    },
  },
};

export const OSM_RASTER_STYLE = BASEMAP_STYLES['osm-standard'].style;

export function resolveMapStyle(urlOrKey: string): string | maplibregl.StyleSpecification {
  if (BASEMAP_STYLES[urlOrKey]) {
    return BASEMAP_STYLES[urlOrKey].style;
  }
  if (urlOrKey.includes('positron')) {
    return BASEMAP_STYLES['carto-positron'].style;
  }
  if (urlOrKey.includes('hot')) {
    return BASEMAP_STYLES['osm-hot'].style;
  }
  if (urlOrKey.includes('topo')) {
    return BASEMAP_STYLES['osm-topo'].style;
  }
  // Default fallback is OpenStreetMap Standard
  return BASEMAP_STYLES['osm-standard'].style;
}

interface MapLibreMapProps {
  mapStyleUrl: string;
  collisionsData: CollisionsResponse | null;
  hotspotsData: HotspotsResponse | null;
  directionsData: DirectionsResponse | null;
  selectedLocation: GeocodeItem | null;
  showCollisions: boolean;
  showHotspots: boolean;
  onViewportChange: (bounds: { min_lon: number; min_lat: number; max_lon: number; max_lat: number }) => void;
  onSelectCollision: (collision: CollisionProperties | null) => void;
  onSelectHotspot: (hotspot: HotspotProperties | null) => void;
  onFallbackToOSM?: () => void;
}

export const MapLibreMap: React.FC<MapLibreMapProps> = ({
  mapStyleUrl,
  collisionsData,
  hotspotsData,
  directionsData,
  selectedLocation,
  showCollisions,
  showHotspots,
  onViewportChange,
  onSelectCollision,
  onSelectHotspot,
  onFallbackToOSM,
}) => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const locationMarkerRef = useRef<maplibregl.Marker | null>(null);
  const currentStyleRef = useRef<string>(mapStyleUrl);

  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [mapError, setMapError] = useState<string | null>(null);

  // Helper to attach custom GeoJSON sources and rendering layers
  const setupLayers = useCallback((map: maplibregl.Map) => {
    // 1. Hotspots Source & Layers
    if (!map.getSource('hotspots-src')) {
      map.addSource('hotspots-src', {
        type: 'geojson',
        data: { type: 'FeatureCollection', features: [] },
      });
    }

    if (!map.getLayer('hotspots-layer')) {
      map.addLayer({
        id: 'hotspots-layer',
        type: 'circle',
        source: 'hotspots-src',
        paint: {
          'circle-radius': [
            'interpolate',
            ['linear'],
            ['get', 'total_collisions'],
            15, 8,
            100, 16,
            500, 26,
            900, 36,
          ],
          'circle-color': '#dc2626',
          'circle-opacity': 0.55,
          'circle-stroke-width': 2,
          'circle-stroke-color': '#ffffff',
        },
      });
    }

    if (!map.getLayer('hotspots-labels')) {
      map.addLayer({
        id: 'hotspots-labels',
        type: 'symbol',
        source: 'hotspots-src',
        layout: {
          'text-field': ['get', 'total_collisions'],
          'text-size': 11,
          'text-allow-overlap': true,
        },
        paint: {
          'text-color': '#ffffff',
          'text-halo-color': '#991b1b',
          'text-halo-width': 1.5,
        },
      });
    }

    // 2. Collisions Source & Layer
    if (!map.getSource('collisions-src')) {
      map.addSource('collisions-src', {
        type: 'geojson',
        data: { type: 'FeatureCollection', features: [] },
      });
    }

    if (!map.getLayer('collisions-layer')) {
      map.addLayer({
        id: 'collisions-layer',
        type: 'circle',
        source: 'collisions-src',
        paint: {
          'circle-radius': [
            'interpolate',
            ['linear'],
            ['zoom'],
            6, 3,
            12, 6,
            16, 9,
          ],
          'circle-color': [
            'match',
            ['get', 'collision_severity'],
            1, '#ef4444',
            2, '#f59e0b',
            3, '#3b82f6',
            '#94a3b8',
          ],
          'circle-stroke-width': 1.2,
          'circle-stroke-color': '#ffffff',
          'circle-opacity': 0.85,
        },
      });
    }

    // 3. Directions Route Source & Layers
    if (!map.getSource('directions-src')) {
      map.addSource('directions-src', {
        type: 'geojson',
        data: { type: 'FeatureCollection', features: [] },
      });
    }

    if (!map.getLayer('directions-route-casing')) {
      map.addLayer({
        id: 'directions-route-casing',
        type: 'line',
        source: 'directions-src',
        layout: { 'line-join': 'round', 'line-cap': 'round' },
        paint: {
          'line-color': '#1d4ed8',
          'line-width': 8,
          'line-opacity': 0.4,
        },
      });
    }

    if (!map.getLayer('directions-route')) {
      map.addLayer({
        id: 'directions-route',
        type: 'line',
        source: 'directions-src',
        layout: { 'line-join': 'round', 'line-cap': 'round' },
        paint: {
          'line-color': '#2563eb',
          'line-width': 5,
        },
      });
    }
  }, []);

  // Sync data to map sources
  const syncDataToSources = useCallback((map: maplibregl.Map) => {
    const colSrc = map.getSource('collisions-src') as maplibregl.GeoJSONSource | undefined;
    if (colSrc && collisionsData) {
      colSrc.setData(collisionsData as any);
    }

    const hsSrc = map.getSource('hotspots-src') as maplibregl.GeoJSONSource | undefined;
    if (hsSrc && hotspotsData) {
      hsSrc.setData(hotspotsData as any);
    }

    const dirSrc = map.getSource('directions-src') as maplibregl.GeoJSONSource | undefined;
    if (dirSrc) {
      if (directionsData && directionsData.success && directionsData.route_geojson) {
        dirSrc.setData(directionsData.route_geojson);
      } else {
        dirSrc.setData({ type: 'FeatureCollection', features: [] });
      }
    }
  }, [collisionsData, hotspotsData, directionsData]);

  // Sync layer visibility
  const syncVisibility = useCallback((map: maplibregl.Map) => {
    if (map.getLayer('collisions-layer')) {
      map.setLayoutProperty('collisions-layer', 'visibility', showCollisions ? 'visible' : 'none');
    }
    if (map.getLayer('hotspots-layer')) {
      map.setLayoutProperty('hotspots-layer', 'visibility', showHotspots ? 'visible' : 'none');
    }
    if (map.getLayer('hotspots-labels')) {
      map.setLayoutProperty('hotspots-labels', 'visibility', showHotspots ? 'visible' : 'none');
    }
  }, [showCollisions, showHotspots]);

  // Initialize Map
  useEffect(() => {
    if (!mapContainer.current || mapRef.current) return;

    setIsLoading(true);
    setMapError(null);

    const initialResolvedStyle = resolveMapStyle(mapStyleUrl);

    const map = new maplibregl.Map({
      container: mapContainer.current,
      style: initialResolvedStyle,
      center: [-2.5, 54.5], // Center of Great Britain
      zoom: 6,
      attributionControl: { compact: true },
    });

    mapRef.current = map;
    (window as any).__map = map;

    map.addControl(new maplibregl.NavigationControl({ showCompass: true }), 'bottom-right');

    // Trigger viewport changes to parent
    const triggerViewport = () => {
      try {
        const bounds = map.getBounds();
        onViewportChange({
          min_lon: bounds.getWest(),
          min_lat: bounds.getSouth(),
          max_lon: bounds.getEast(),
          max_lat: bounds.getNorth(),
        });
      } catch (e) {
        // Map bounds might not be available before first layout
      }
    };

    map.on('moveend', triggerViewport);

    // Initial load handler
    map.on('load', () => {
      setIsLoading(false);
      setMapError(null);
      setupLayers(map);
      syncDataToSources(map);
      syncVisibility(map);
      triggerViewport();
    });

    // Style load handler (triggers on initial style AND subsequent setStyle changes)
    map.on('style.load', () => {
      setIsLoading(false);
      setupLayers(map);
      syncDataToSources(map);
      syncVisibility(map);
    });

    // Error handler
    map.on('error', (e) => {
      console.warn('MapLibre event error:', e.error);
      const msg = e.error?.message || '';
      if (msg.includes('Worker') || msg.includes('Failed to fetch') || msg.includes('404') || msg.includes('403')) {
        setMapError('Failed to load map tiles. Click below to use standard OpenStreetMap basemap.');
      }
    });

    map.on('idle', () => {
      setIsLoading(false);
    });

    // Click Listeners
    map.on('click', 'collisions-layer', (e: any) => {
      if (e.features && e.features[0]) {
        const props = e.features[0].properties as any;
        onSelectCollision(props);
      }
    });

    map.on('click', 'hotspots-layer', (e: any) => {
      if (e.features && e.features[0]) {
        const props = e.features[0].properties as any;
        onSelectHotspot(props);
      }
    });

    map.on('mouseenter', 'collisions-layer', () => (map.getCanvas().style.cursor = 'pointer'));
    map.on('mouseleave', 'collisions-layer', () => (map.getCanvas().style.cursor = ''));
    map.on('mouseenter', 'hotspots-layer', () => (map.getCanvas().style.cursor = 'pointer'));
    map.on('mouseleave', 'hotspots-layer', () => (map.getCanvas().style.cursor = ''));

    // ResizeObserver ensures map adjusts to non-zero container width/height immediately
    const resizeObserver = new ResizeObserver(() => {
      if (mapRef.current) {
        mapRef.current.resize();
      }
    });

    if (mapContainer.current) {
      resizeObserver.observe(mapContainer.current);
    }

    return () => {
      resizeObserver.disconnect();
      map.remove();
      mapRef.current = null;
    };
  }, []);

  // Update Map Style ONLY when mapStyleUrl actually changes
  useEffect(() => {
    if (!mapRef.current) return;
    if (currentStyleRef.current === mapStyleUrl) return;

    currentStyleRef.current = mapStyleUrl;
    setIsLoading(true);
    setMapError(null);

    const resolved = resolveMapStyle(mapStyleUrl);
    mapRef.current.setStyle(resolved);
  }, [mapStyleUrl]);

  // Update Collisions Source Data
  useEffect(() => {
    if (!mapRef.current) return;
    const src = mapRef.current.getSource('collisions-src') as maplibregl.GeoJSONSource | undefined;
    if (src && collisionsData) {
      src.setData(collisionsData as any);
    }
  }, [collisionsData]);

  // Update Hotspots Source Data
  useEffect(() => {
    if (!mapRef.current) return;
    const src = mapRef.current.getSource('hotspots-src') as maplibregl.GeoJSONSource | undefined;
    if (src && hotspotsData) {
      src.setData(hotspotsData as any);
    }
  }, [hotspotsData]);

  // Update Directions Route Source & Fit Bounds
  useEffect(() => {
    if (!mapRef.current) return;
    const src = mapRef.current.getSource('directions-src') as maplibregl.GeoJSONSource | undefined;
    if (!src) return;

    if (directionsData && directionsData.success && directionsData.route_geojson) {
      src.setData(directionsData.route_geojson);
      const coords = directionsData.route_geojson.geometry.coordinates;
      if (coords && coords.length > 0) {
        const bounds = coords.reduce(
          (b: maplibregl.LngLatBounds, c: [number, number]) => b.extend(c),
          new maplibregl.LngLatBounds(coords[0], coords[0])
        );
        mapRef.current.fitBounds(bounds, { padding: 80 });
      }
    } else {
      src.setData({ type: 'FeatureCollection', features: [] });
    }
  }, [directionsData]);

  // Toggle Layer Visibilities
  useEffect(() => {
    if (!mapRef.current) return;
    syncVisibility(mapRef.current);
  }, [showCollisions, showHotspots, syncVisibility]);

  // Update Location Marker & FlyTo
  useEffect(() => {
    if (!mapRef.current) return;
    const map = mapRef.current;

    if (selectedLocation) {
      if (!locationMarkerRef.current) {
        locationMarkerRef.current = new maplibregl.Marker({ color: '#ea4335' });
      }
      locationMarkerRef.current
        .setLngLat([selectedLocation.longitude, selectedLocation.latitude])
        .addTo(map);

      map.flyTo({
        center: [selectedLocation.longitude, selectedLocation.latitude],
        zoom: 13,
        essential: true,
      });
    } else {
      if (locationMarkerRef.current) {
        locationMarkerRef.current.remove();
        locationMarkerRef.current = null;
      }
    }
  }, [selectedLocation]);

  return (
    <div className="map-canvas-wrapper" style={{ position: 'absolute', inset: 0, width: '100%', height: '100%' }}>
      <div ref={mapContainer} className="maplibre-map-element" style={{ width: '100%', height: '100%' }} />

      {isLoading && (
        <div className="map-loading-indicator">
          <div className="map-loading-spinner" />
          <span>Loading map tiles...</span>
        </div>
      )}

      {mapError && (
        <div className="map-error-banner">
          <span>{mapError}</span>
          {onFallbackToOSM && (
            <button
              type="button"
              className="map-error-btn"
              onClick={() => {
                setMapError(null);
                onFallbackToOSM();
              }}
            >
              Use OpenStreetMap
            </button>
          )}
        </div>
      )}
    </div>
  );
};
