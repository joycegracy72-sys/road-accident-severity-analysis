import React from 'react';
import { X, Flame } from 'lucide-react';
import type { HotspotProperties } from '../types';

interface HotspotDetailCardProps {
  hotspot: HotspotProperties;
  onClose: () => void;
}

export const HotspotDetailCard: React.FC<HotspotDetailCardProps> = ({ hotspot, onClose }) => {
  return (
    <div className="floating-card hotspot-card">
      <div className="card-header bg-red-50">
        <div className="flex items-center gap-2 text-red-700">
          <Flame size={18} />
          <span className="card-title font-bold">DBSCAN Hotspot Cluster #{hotspot.cluster_id}</span>
        </div>
        <button className="icon-btn" onClick={onClose}><X size={16} /></button>
      </div>

      <div className="card-body">
        <div className="hotspot-kpi">
          <div className="hotspot-stat-item">
            <div className="hotspot-stat-num">{hotspot.total_collisions}</div>
            <div className="hotspot-stat-lbl">Total Collisions (2022)</div>
          </div>
          <div className="hotspot-stat-item text-red-600">
            <div className="hotspot-stat-num">{hotspot.fatal_count}</div>
            <div className="hotspot-stat-lbl">Fatal ({hotspot.fatal_rate_pct}%)</div>
          </div>
          <div className="hotspot-stat-item text-amber-600">
            <div className="hotspot-stat-num">{hotspot.serious_count}</div>
            <div className="hotspot-stat-lbl">Serious ({hotspot.serious_rate_pct}%)</div>
          </div>
        </div>

        <div className="grid-details mt-3">
          <div className="detail-item">
            <span className="detail-label">Speed Limit</span>
            <span className="detail-val font-semibold">{hotspot.dominant_speed_limit} mph</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Area Type</span>
            <span className="detail-val font-semibold">{hotspot.dominant_urban_rural}</span>
          </div>
          <div className="detail-item col-span-2">
            <span className="detail-label">Coordinates</span>
            <span className="detail-val text-xs font-mono">
              {hotspot.center_latitude.toFixed(5)}, {hotspot.center_longitude.toFixed(5)}
            </span>
          </div>
        </div>

        <div className="card-footer-note mt-3">
          Clusters computed on British National Grid (EPSG:27700, radius 250m). High collision counts reflect concentrated exposure and multi-modal activity rather than inherent per-vehicle risk.
        </div>
      </div>
    </div>
  );
};
