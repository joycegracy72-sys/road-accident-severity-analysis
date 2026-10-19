import React, { useState, useEffect } from 'react';
import { Search, Navigation, X, MapPin, ArrowRight, Loader2 } from 'lucide-react';
import type { GeocodeItem, GeocodeResponse } from '../types';
import { searchLocations } from '../api';

interface SearchBarProps {
  onSelectLocation: (loc: GeocodeItem) => void;
  onRequestDirections: (origin: GeocodeItem, dest: GeocodeItem) => void;
  onClearDirections: () => void;
}

export const SearchBar: React.FC<SearchBarProps> = ({
  onSelectLocation,
  onRequestDirections,
  onClearDirections,
}) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<GeocodeItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [isDirectionsMode, setIsDirectionsMode] = useState(false);

  // Directions state
  const [originQuery, setOriginQuery] = useState('');
  const [destQuery, setDestQuery] = useState('');
  const [originResults, setOriginResults] = useState<GeocodeItem[]>([]);
  const [destResults, setDestResults] = useState<GeocodeItem[]>([]);
  const [selectedOrigin, setSelectedOrigin] = useState<GeocodeItem | null>(null);
  const [selectedDest, setSelectedDest] = useState<GeocodeItem | null>(null);

  // Debounced search for single location
  useEffect(() => {
    if (!query.trim() || isDirectionsMode) {
      setResults([]);
      return;
    }
    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        const res: GeocodeResponse = await searchLocations(query);
        setResults(res.results);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [query, isDirectionsMode]);

  // Search for origin
  useEffect(() => {
    if (!originQuery.trim() || selectedOrigin) {
      setOriginResults([]);
      return;
    }
    const timer = setTimeout(async () => {
      try {
        const res = await searchLocations(originQuery);
        setOriginResults(res.results);
      } catch (e) {}
    }, 300);
    return () => clearTimeout(timer);
  }, [originQuery, selectedOrigin]);

  // Search for destination
  useEffect(() => {
    if (!destQuery.trim() || selectedDest) {
      setDestResults([]);
      return;
    }
    const timer = setTimeout(async () => {
      try {
        const res = await searchLocations(destQuery);
        setDestResults(res.results);
      } catch (e) {}
    }, 300);
    return () => clearTimeout(timer);
  }, [destQuery, selectedDest]);

  const handleSelectSearch = (item: GeocodeItem) => {
    onSelectLocation(item);
    setQuery(item.name);
    setResults([]);
  };

  const handleRouteSubmit = () => {
    if (selectedOrigin && selectedDest) {
      onRequestDirections(selectedOrigin, selectedDest);
    }
  };

  const handleExitDirections = () => {
    setIsDirectionsMode(false);
    setSelectedOrigin(null);
    setSelectedDest(null);
    setOriginQuery('');
    setDestQuery('');
    onClearDirections();
  };

  return (
    <div className="search-container">
      {!isDirectionsMode ? (
        <div className="search-box">
          <Search size={18} className="search-icon" />
          <input
            type="text"
            className="search-input"
            placeholder="Search Great Britain locations, cities, postcodes..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          {loading && <Loader2 size={16} className="spinner" />}
          {query && !loading && (
            <button className="icon-btn" onClick={() => { setQuery(''); setResults([]); }}>
              <X size={16} />
            </button>
          )}
          <div className="divider" />
          <button
            className="icon-btn directions-toggle"
            title="Directions"
            onClick={() => setIsDirectionsMode(true)}
          >
            <Navigation size={18} color="#1a73e8" />
          </button>
        </div>
      ) : (
        <div className="directions-box">
          <div className="directions-header">
            <span className="font-semibold text-sm">Driving Directions</span>
            <button className="icon-btn" onClick={handleExitDirections}>
              <X size={16} />
            </button>
          </div>
          <div className="directions-inputs">
            <div className="direction-input-row">
              <span className="dot origin-dot" />
              <input
                type="text"
                placeholder="Choose starting point..."
                value={selectedOrigin ? selectedOrigin.name : originQuery}
                onChange={(e) => { setSelectedOrigin(null); setOriginQuery(e.target.value); }}
              />
              {selectedOrigin && (
                <button className="icon-btn" onClick={() => { setSelectedOrigin(null); setOriginQuery(''); }}>
                  <X size={14} />
                </button>
              )}
            </div>
            <div className="direction-input-row">
              <span className="dot dest-dot" />
              <input
                type="text"
                placeholder="Choose destination..."
                value={selectedDest ? selectedDest.name : destQuery}
                onChange={(e) => { setSelectedDest(null); setDestQuery(e.target.value); }}
              />
              {selectedDest && (
                <button className="icon-btn" onClick={() => { setSelectedDest(null); setDestQuery(''); }}>
                  <X size={14} />
                </button>
              )}
            </div>
          </div>

          <button
            className="route-btn"
            disabled={!selectedOrigin || !selectedDest}
            onClick={handleRouteSubmit}
          >
            Route Preview <ArrowRight size={14} />
          </button>
        </div>
      )}

      {!isDirectionsMode && results.length > 0 && (
        <div className="results-dropdown">
          {results.map((item, idx) => (
            <div key={idx} className="result-item" onClick={() => handleSelectSearch(item)}>
              <MapPin size={16} className="text-gray-500" />
              <div className="result-text">
                <div className="result-name">{item.name}</div>
                <div className="result-sub">{item.display_name}</div>
              </div>
            </div>
          ))}
        </div>
      )}

      {isDirectionsMode && originResults.length > 0 && !selectedOrigin && (
        <div className="results-dropdown">
          {originResults.map((item, idx) => (
            <div
              key={idx}
              className="result-item"
              onClick={() => { setSelectedOrigin(item); setOriginQuery(item.name); setOriginResults([]); }}
            >
              <MapPin size={16} className="text-gray-500" />
              <div className="result-text">
                <div className="result-name">{item.name}</div>
                <div className="result-sub">{item.display_name}</div>
              </div>
            </div>
          ))}
        </div>
      )}

      {isDirectionsMode && destResults.length > 0 && !selectedDest && (
        <div className="results-dropdown">
          {destResults.map((item, idx) => (
            <div
              key={idx}
              className="result-item"
              onClick={() => { setSelectedDest(item); setDestQuery(item.name); setDestResults([]); }}
            >
              <MapPin size={16} className="text-gray-500" />
              <div className="result-text">
                <div className="result-name">{item.name}</div>
                <div className="result-sub">{item.display_name}</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
