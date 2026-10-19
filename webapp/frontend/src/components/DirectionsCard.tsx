import React from 'react';
import { X, Navigation } from 'lucide-react';
import type { DirectionsResponse } from '../types';

interface DirectionsCardProps {
  directions: DirectionsResponse;
  onClose: () => void;
}

export const DirectionsCard: React.FC<DirectionsCardProps> = ({ directions, onClose }) => {
  if (!directions.success) {
    return (
      <div className="floating-card directions-summary-card">
        <div className="card-header">
          <span className="card-title text-red-600">Route Unavailable</span>
          <button className="icon-btn" onClick={onClose}><X size={16} /></button>
        </div>
        <div className="card-body text-xs text-gray-600">
          {directions.message || 'Unable to calculate driving route.'}
        </div>
      </div>
    );
  }

  return (
    <div className="floating-card directions-summary-card">
      <div className="card-header">
        <div className="flex items-center gap-2 text-blue-600">
          <Navigation size={18} />
          <span className="card-title font-bold">Driving Route</span>
        </div>
        <button className="icon-btn" onClick={onClose}><X size={16} /></button>
      </div>
      <div className="card-body">
        <div className="route-stats">
          <div className="route-stat">
            <span className="route-val">{directions.distance_miles} mi</span>
            <span className="route-lbl">Distance ({directions.distance_km} km)</span>
          </div>
          <div className="route-stat">
            <span className="route-val text-emerald-600">{directions.duration_minutes} min</span>
            <span className="route-lbl">Estimated Travel Time</span>
          </div>
        </div>
        <div className="card-footer-note mt-2">
          Driving directions via OpenStreetMap (OSRM). Road safety collision layers remain active along the route.
        </div>
      </div>
    </div>
  );
};
