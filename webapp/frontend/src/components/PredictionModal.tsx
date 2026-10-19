import React, { useState } from 'react';
import { X, Cpu, Loader2, Info } from 'lucide-react';
import type { PredictionRequest, PredictionResponse } from '../types';
import { postPrediction } from '../api';

interface PredictionModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const PredictionModal: React.FC<PredictionModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  const [formData, setFormData] = useState<PredictionRequest>({
    number_of_vehicles: 2,
    speed_limit: 30,
    collision_hour: 17,
    collision_month: 10,
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
    urban_or_rural_area: 1,
    trunk_road_flag: 2,
    police_force: 1,
    day_of_week: 6,
  });

  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await postPrediction(formData);
      setResult(res);
    } catch (err: any) {
      setError(err.message || 'Prediction failed');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field: keyof PredictionRequest, value: number) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <div className="modal-overlay">
      <div className="modal-container">
        <div className="modal-header">
          <div className="flex items-center gap-2">
            <Cpu size={20} className="text-blue-600" />
            <h2 className="text-base font-bold text-gray-800">ML Accident Severity Predictor</h2>
          </div>
          <button className="icon-btn" onClick={onClose}><X size={18} /></button>
        </div>

        <div className="modal-body">
          <p className="text-xs text-gray-500 mb-4">
            Predicts collision severity using the trained <b>Balanced Random Forest</b> pipeline. Select hypothetical collision circumstances below:
          </p>

          <form onSubmit={handleSubmit} className="prediction-form">
            <div className="form-grid">
              <div className="form-group">
                <label>Number of Vehicles Involved</label>
                <input
                  type="number"
                  min={1}
                  max={10}
                  value={formData.number_of_vehicles}
                  onChange={(e) => handleChange('number_of_vehicles', parseInt(e.target.value) || 1)}
                />
              </div>

              <div className="form-group">
                <label>Posted Speed Limit</label>
                <select
                  value={formData.speed_limit}
                  onChange={(e) => handleChange('speed_limit', parseInt(e.target.value))}
                >
                  <option value={20}>20 mph</option>
                  <option value={30}>30 mph</option>
                  <option value={40}>40 mph</option>
                  <option value={50}>50 mph</option>
                  <option value={60}>60 mph</option>
                  <option value={70}>70 mph</option>
                </select>
              </div>

              <div className="form-group">
                <label>Settlement Classification</label>
                <select
                  value={formData.urban_or_rural_area}
                  onChange={(e) => handleChange('urban_or_rural_area', parseInt(e.target.value))}
                >
                  <option value={1}>Urban Area</option>
                  <option value={2}>Rural Area</option>
                </select>
              </div>

              <div className="form-group">
                <label>Road Layout</label>
                <select
                  value={formData.road_type}
                  onChange={(e) => handleChange('road_type', parseInt(e.target.value))}
                >
                  <option value={6}>Single Carriageway</option>
                  <option value={3}>Dual Carriageway</option>
                  <option value={1}>Roundabout</option>
                  <option value={2}>One-way Street</option>
                  <option value={7}>Slip Road</option>
                </select>
              </div>

              <div className="form-group">
                <label>Road Hierarchy Class</label>
                <select
                  value={formData.first_road_class}
                  onChange={(e) => handleChange('first_road_class', parseInt(e.target.value))}
                >
                  <option value={3}>A-Road</option>
                  <option value={1}>Motorway</option>
                  <option value={2}>A(M)</option>
                  <option value={4}>B-Road</option>
                  <option value={5}>C-Road</option>
                  <option value={6}>Unclassified</option>
                </select>
              </div>

              <div className="form-group">
                <label>Weather Condition</label>
                <select
                  value={formData.weather_conditions}
                  onChange={(e) => handleChange('weather_conditions', parseInt(e.target.value))}
                >
                  <option value={1}>Fine (no high winds)</option>
                  <option value={2}>Raining (no high winds)</option>
                  <option value={3}>Snowing</option>
                  <option value={4}>Fine + high winds</option>
                  <option value={5}>Raining + high winds</option>
                  <option value={7}>Fog or mist</option>
                </select>
              </div>

              <div className="form-group">
                <label>Road Surface</label>
                <select
                  value={formData.road_surface_conditions}
                  onChange={(e) => handleChange('road_surface_conditions', parseInt(e.target.value))}
                >
                  <option value={1}>Dry</option>
                  <option value={2}>Wet or damp</option>
                  <option value={3}>Snow</option>
                  <option value={4}>Frost or ice</option>
                  <option value={5}>Flood (&gt;3cm deep)</option>
                </select>
              </div>

              <div className="form-group">
                <label>Lighting</label>
                <select
                  value={formData.light_conditions}
                  onChange={(e) => handleChange('light_conditions', parseInt(e.target.value))}
                >
                  <option value={1}>Daylight</option>
                  <option value={4}>Darkness (lights lit)</option>
                  <option value={5}>Darkness (lights unlit)</option>
                  <option value={6}>Darkness (no lighting)</option>
                </select>
              </div>

              <div className="form-group">
                <label>Hour of Day (0-23)</label>
                <input
                  type="number"
                  min={0}
                  max={23}
                  value={formData.collision_hour}
                  onChange={(e) => handleChange('collision_hour', parseInt(e.target.value) || 0)}
                />
              </div>

              <div className="form-group">
                <label>Day of Week</label>
                <select
                  value={formData.day_of_week}
                  onChange={(e) => handleChange('day_of_week', parseInt(e.target.value))}
                >
                  <option value={1}>Sunday</option>
                  <option value={2}>Monday</option>
                  <option value={3}>Tuesday</option>
                  <option value={4}>Wednesday</option>
                  <option value={5}>Thursday</option>
                  <option value={6}>Friday</option>
                  <option value={7}>Saturday</option>
                </select>
              </div>
            </div>

            <button type="submit" className="submit-prediction-btn" disabled={loading}>
              {loading ? <Loader2 size={16} className="spinner" /> : <Cpu size={16} />}
              {loading ? 'Running Model Inference...' : 'Predict Collision Severity'}
            </button>
          </form>

          {error && <div className="error-box">{error}</div>}

          {result && (
            <div className="prediction-result-card">
              <div className="result-headline">
                <span className="text-xs uppercase font-bold text-gray-500">Predicted Severity</span>
                <div className={`predicted-badge sev-${result.predicted_severity}`}>
                  {result.predicted_label}
                </div>
              </div>

              <div className="probability-bars">
                <div className="prob-item">
                  <div className="prob-header">
                    <span className="font-semibold text-red-700">Fatal Probability</span>
                    <span>{(result.probabilities.Fatal * 100).toFixed(1)}%</span>
                  </div>
                  <div className="progress-track">
                    <div className="progress-fill red" style={{ width: `${result.probabilities.Fatal * 100}%` }} />
                  </div>
                </div>

                <div className="prob-item">
                  <div className="prob-header">
                    <span className="font-semibold text-amber-700">Serious Probability</span>
                    <span>{(result.probabilities.Serious * 100).toFixed(1)}%</span>
                  </div>
                  <div className="progress-track">
                    <div className="progress-fill orange" style={{ width: `${result.probabilities.Serious * 100}%` }} />
                  </div>
                </div>

                <div className="prob-item">
                  <div className="prob-header">
                    <span className="font-semibold text-blue-700">Slight Probability</span>
                    <span>{(result.probabilities.Slight * 100).toFixed(1)}%</span>
                  </div>
                  <div className="progress-track">
                    <div className="progress-fill blue" style={{ width: `${result.probabilities.Slight * 100}%` }} />
                  </div>
                </div>
              </div>

              <div className="disclaimer-text">
                <Info size={14} className="inline mr-1" /> {result.disclaimer}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
