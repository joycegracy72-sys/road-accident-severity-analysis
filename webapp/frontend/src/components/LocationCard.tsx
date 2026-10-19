import React from 'react';
import { X, MapPin, Navigation } from 'lucide-react';
import type { GeocodeItem } from '../types';

interface LocationCardProps {
  location: GeocodeItem;
  onClose: () => void;
  onSetAsOrigin: (loc: GeocodeItem) => void;
  onSetAsDestination: (loc: GeocodeItem) => void;
}

export const LocationCard: React.FC<LocationCardProps> = ({
  location,
  onClose,
  onSetAsOrigin,
  onSetAsDestination,
}) => {
  return (
    <div className="floating-card location-card">
      <div className="card-header">
        <div className="flex items-center gap-2">
          <MapPin size={18} className="text-blue-600" />
          <span className="card-title truncate">{location.name}</span>
        </div>
        <button className="icon-btn" onClick={onClose}><X size={16} /></button>
      </div>

      <div className="card-body">
        <div className="text-xs text-gray-600 mb-3">{location.display_name}</div>
        <div className="text-xs font-mono text-gray-500 mb-3">
          {location.latitude.toFixed(5)}, {location.longitude.toFixed(5)}
        </div>

        <div className="location-actions">
          <button className="action-btn" onClick={() => onSetAsOrigin(location)}>
            <Navigation size={14} /> Start Route Here
          </button>
          <button className="action-btn primary" onClick={() => onSetAsDestination(location)}>
            <Navigation size={14} /> Directions Here
          </button>
        </div>
      </div>
    </div>
  );
};
