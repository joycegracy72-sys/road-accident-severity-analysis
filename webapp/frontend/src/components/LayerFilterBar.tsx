import React from 'react';
import { Layers, Flame, AlertCircle, Cpu } from 'lucide-react';
import type { FilterState } from '../types';

interface LayerFilterBarProps {
  filters: FilterState;
  onChangeFilters: (filters: FilterState) => void;
  onOpenPrediction: () => void;
  totalInView: number;
  returnedCount: number;
  isCapped: boolean;
  mapStyle: string;
  onChangeStyle: (style: string) => void;
}

export const LayerFilterBar: React.FC<LayerFilterBarProps> = ({
  filters,
  onChangeFilters,
  onOpenPrediction,
  totalInView,
  returnedCount,
  isCapped,
  mapStyle,
  onChangeStyle,
}) => {
  return (
    <div className="floating-filter-bar">
      <div className="filter-group">
        <button
          className={`filter-chip ${filters.showHotspots ? 'active-hotspot' : ''}`}
          onClick={() => onChangeFilters({ ...filters, showHotspots: !filters.showHotspots })}
          title="Toggle 293 DBSCAN Hotspot Clusters"
        >
          <Flame size={14} /> Hotspots (293)
        </button>

        <button
          className={`filter-chip ${filters.showCollisions ? 'active-primary' : ''}`}
          onClick={() => onChangeFilters({ ...filters, showCollisions: !filters.showCollisions })}
          title="Toggle Historical Collision Points"
        >
          <AlertCircle size={14} /> Collisions ({returnedCount.toLocaleString()})
        </button>
      </div>

      <div className="bar-separator" />

      <div className="filter-group">
        <button
          className={`severity-chip fatal ${filters.showFatal ? 'active' : ''}`}
          onClick={() => onChangeFilters({ ...filters, showFatal: !filters.showFatal })}
        >
          <span className="chip-dot red" /> Fatal
        </button>
        <button
          className={`severity-chip serious ${filters.showSerious ? 'active' : ''}`}
          onClick={() => onChangeFilters({ ...filters, showSerious: !filters.showSerious })}
        >
          <span className="chip-dot orange" /> Serious
        </button>
        <button
          className={`severity-chip slight ${filters.showSlight ? 'active' : ''}`}
          onClick={() => onChangeFilters({ ...filters, showSlight: !filters.showSlight })}
        >
          <span className="chip-dot blue" /> Slight
        </button>
      </div>

      <div className="bar-separator" />

      <div className="filter-group speed-group">
        <label className="text-xs text-gray-500 font-medium">Speed:</label>
        <select
          className="filter-select"
          value={filters.speedLimit}
          onChange={(e) =>
            onChangeFilters({
              ...filters,
              speedLimit: e.target.value === 'all' ? 'all' : parseInt(e.target.value),
            })
          }
        >
          <option value="all">All Speeds</option>
          <option value="20">20 mph</option>
          <option value="30">30 mph</option>
          <option value="40">40 mph</option>
          <option value="50">50 mph</option>
          <option value="60">60 mph</option>
          <option value="70">70 mph</option>
        </select>
      </div>

      <div className="filter-group style-group">
        <Layers size={14} className="text-gray-500" />
        <select
          className="filter-select"
          value={mapStyle}
          onChange={(e) => onChangeStyle(e.target.value)}
        >
          <option value="osm-standard">OpenStreetMap (Standard)</option>
          <option value="osm-hot">Humanitarian (Light)</option>
          <option value="osm-topo">OpenTopoMap (Terrain)</option>
          <option value="carto-positron">CARTO Positron</option>
        </select>
      </div>

      <div className="bar-separator" />

      <button className="predict-btn-chip" onClick={onOpenPrediction}>
        <Cpu size={15} /> Predict Severity
      </button>

      {isCapped && (
        <span className="capped-badge" title="Displaying capped sample in current viewport">
          Showing 500 of {totalInView.toLocaleString()} in view
        </span>
      )}
    </div>
  );
};
