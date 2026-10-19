import React, { useState, useEffect } from 'react';
import { MapLibreMap } from './components/MapLibreMap';
import { SearchBar } from './components/SearchBar';
import { LayerFilterBar } from './components/LayerFilterBar';
import { CollisionDetailCard } from './components/CollisionDetailCard';
import { HotspotDetailCard } from './components/HotspotDetailCard';
import { LocationCard } from './components/LocationCard';
import { DirectionsCard } from './components/DirectionsCard';
import { PredictionModal } from './components/PredictionModal';
import type {
  CollisionsResponse,
  HotspotsResponse,
  CollisionProperties,
  HotspotProperties,
  GeocodeItem,
  DirectionsResponse,
  FilterState,
} from './types';
import { fetchHotspots, fetchCollisions, fetchDirections } from './api';

export const App: React.FC = () => {
  const [mapStyle, setMapStyle] = useState('osm-standard');
  const [currentBounds, setCurrentBounds] = useState<{ min_lon: number; min_lat: number; max_lon: number; max_lat: number } | null>(null);

  const [hotspotsData, setHotspotsData] = useState<HotspotsResponse | null>(null);
  const [collisionsData, setCollisionsData] = useState<CollisionsResponse | null>(null);
  const [directionsData, setDirectionsData] = useState<DirectionsResponse | null>(null);

  const [selectedLocation, setSelectedLocation] = useState<GeocodeItem | null>(null);
  const [selectedCollision, setSelectedCollision] = useState<CollisionProperties | null>(null);
  const [selectedHotspot, setSelectedHotspot] = useState<HotspotProperties | null>(null);

  const [isPredictionOpen, setIsPredictionOpen] = useState(false);

  const [filters, setFilters] = useState<FilterState>({
    showFatal: true,
    showSerious: true,
    showSlight: true,
    speedLimit: 'all',
    urbanRural: 'all',
    showHotspots: true,
    showCollisions: true,
  });

  useEffect(() => {
    fetchHotspots()
      .then(setHotspotsData)
      .catch((err) => console.error('Failed to load hotspots', err));
  }, []);

  useEffect(() => {
    if (!currentBounds || !filters.showCollisions) return;

    const timer = setTimeout(() => {
      const activeSeverities: number[] = [];
      if (filters.showFatal) activeSeverities.push(1);
      if (filters.showSerious) activeSeverities.push(2);
      if (filters.showSlight) activeSeverities.push(3);

      const activeSpeedLimits = filters.speedLimit !== 'all' ? [filters.speedLimit] : undefined;
      const activeUrbanRural = filters.urbanRural !== 'all' ? filters.urbanRural : undefined;

      fetchCollisions({
        min_lon: currentBounds.min_lon,
        min_lat: currentBounds.min_lat,
        max_lon: currentBounds.max_lon,
        max_lat: currentBounds.max_lat,
        severities: activeSeverities,
        speed_limits: activeSpeedLimits,
        urban_rural: activeUrbanRural,
        limit: 500,
      })
        .then(setCollisionsData)
        .catch((err) => console.error('Failed to fetch collisions', err));
    }, 250);

    return () => clearTimeout(timer);
  }, [currentBounds, filters]);

  const handleRequestDirections = async (origin: GeocodeItem, dest: GeocodeItem) => {
    try {
      const res = await fetchDirections(origin.longitude, origin.latitude, dest.longitude, dest.latitude);
      setDirectionsData(res);
      setSelectedLocation(null);
    } catch (e) {
      console.error(e);
      setDirectionsData({ success: false, message: 'Directions service failed.' });
    }
  };

  const handleClearDirections = () => {
    setDirectionsData(null);
  };

  return (
    <div className="app-container">
      <MapLibreMap
        mapStyleUrl={mapStyle}
        collisionsData={collisionsData}
        hotspotsData={hotspotsData}
        directionsData={directionsData}
        selectedLocation={selectedLocation}
        showCollisions={filters.showCollisions}
        showHotspots={filters.showHotspots}
        onViewportChange={setCurrentBounds}
        onSelectCollision={(col) => {
          setSelectedCollision(col);
          setSelectedHotspot(null);
          setSelectedLocation(null);
        }}
        onSelectHotspot={(hs) => {
          setSelectedHotspot(hs);
          setSelectedCollision(null);
          setSelectedLocation(null);
        }}
        onFallbackToOSM={() => setMapStyle('osm-standard')}
      />

      <SearchBar
        onSelectLocation={(loc) => {
          setSelectedLocation(loc);
          setSelectedCollision(null);
          setSelectedHotspot(null);
        }}
        onRequestDirections={handleRequestDirections}
        onClearDirections={handleClearDirections}
      />

      <LayerFilterBar
        filters={filters}
        onChangeFilters={setFilters}
        onOpenPrediction={() => setIsPredictionOpen(true)}
        totalInView={collisionsData?.total_in_viewport || 0}
        returnedCount={collisionsData?.returned_count || 0}
        isCapped={collisionsData?.is_capped || false}
        mapStyle={mapStyle}
        onChangeStyle={setMapStyle}
      />

      {selectedCollision && (
        <CollisionDetailCard
          collision={selectedCollision}
          onClose={() => setSelectedCollision(null)}
        />
      )}

      {selectedHotspot && (
        <HotspotDetailCard
          hotspot={selectedHotspot}
          onClose={() => setSelectedHotspot(null)}
        />
      )}

      {selectedLocation && (
        <LocationCard
          location={selectedLocation}
          onClose={() => setSelectedLocation(null)}
          onSetAsOrigin={(loc) => {
            // Can be expanded to populate origin
            setSelectedLocation(loc);
          }}
          onSetAsDestination={(loc) => {
            // Can be expanded to populate destination
            setSelectedLocation(loc);
          }}
        />
      )}

      {directionsData && (
        <DirectionsCard
          directions={directionsData}
          onClose={() => setDirectionsData(null)}
        />
      )}

      <PredictionModal
        isOpen={isPredictionOpen}
        onClose={() => setIsPredictionOpen(false)}
      />
    </div>
  );
};

export default App;
