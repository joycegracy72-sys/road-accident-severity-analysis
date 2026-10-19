import React from 'react';
import { X, AlertTriangle } from 'lucide-react';
import type { CollisionProperties } from '../types';

interface CollisionDetailCardProps {
  collision: CollisionProperties;
  onClose: () => void;
}

export const CollisionDetailCard: React.FC<CollisionDetailCardProps> = ({ collision, onClose }) => {
  const getSeverityBadge = (sev: number) => {
    if (sev === 1) return <span className="badge badge-fatal">Fatal Collision</span>;
    if (sev === 2) return <span className="badge badge-serious">Serious Injury</span>;
    return <span className="badge badge-slight">Slight Injury</span>;
  };

  const roadTypes: Record<number, string> = {
    1: 'Roundabout',
    2: 'One-way street',
    3: 'Dual carriageway',
    6: 'Single carriageway',
    7: 'Slip road',
  };

  const roadClasses: Record<number, string> = {
    1: 'Motorway',
    2: 'A(M)',
    3: 'A-Road',
    4: 'B-Road',
    5: 'C-Road',
    6: 'Unclassified',
  };

  return (
    <div className="floating-card detail-card">
      <div className="card-header">
        <div className="flex items-center gap-2">
          <AlertTriangle size={18} className="text-red-600" />
          <span className="card-title">Collision Record</span>
        </div>
        <button className="icon-btn" onClick={onClose}><X size={16} /></button>
      </div>

      <div className="card-body">
        <div className="mb-3">{getSeverityBadge(collision.collision_severity)}</div>

        <div className="grid-details">
          <div className="detail-item">
            <span className="detail-label">Index</span>
            <span className="detail-val font-mono">{collision.collision_index}</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Speed Limit</span>
            <span className="detail-val font-bold">{collision.speed_limit} mph</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Vehicles</span>
            <span className="detail-val">{collision.number_of_vehicles} vehicle(s)</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Settlement</span>
            <span className="detail-val">{collision.urban_or_rural_area === 1 ? 'Urban' : 'Rural'}</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Road Layout</span>
            <span className="detail-val">{roadTypes[collision.road_type] || 'Standard'}</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Road Class</span>
            <span className="detail-val">{roadClasses[collision.first_road_class] || 'General'}</span>
          </div>
          {collision.collision_date && (
            <div className="detail-item">
              <span className="detail-label">Date</span>
              <span className="detail-val">{collision.collision_date}</span>
            </div>
          )}
          {collision.collision_time && (
            <div className="detail-item">
              <span className="detail-label">Time</span>
              <span className="detail-val">{collision.collision_time}</span>
            </div>
          )}
        </div>

        <div className="card-footer-note">
          Official UK DfT STATS19 Reported Collision (2022 Archive).
        </div>
      </div>
    </div>
  );
};
