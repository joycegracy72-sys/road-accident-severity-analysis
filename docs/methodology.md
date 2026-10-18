# Methodological Framework: STATS19 Severity Analysis

## 1. Problem Formulation
Road traffic collisions represent complex socio-technical events governed by vehicle kinematics, infrastructure geometry, human factors, and environmental conditions. Our objective is to formulate a leak-safe, reproducible statistical and machine learning pipeline to classify collision severity into three statutory categories defined by STATS19:
1. **Fatal**: Death occurred within 30 days of the incident.
2. **Serious**: Casualties sustained severe trauma requiring hospital detention or specific severe injuries.
3. **Slight**: Minor injuries without prolonged hospitalisation.

---

## 2. Leakage-Safe Feature Selection Framework
A critical challenge in accident analysis is retrospective information leakage. Many attributes in administrative police databases are recorded *after* casualty outcomes are established. We implemented a strict chronological contract:

### A. Pre-Collision / Scene Context (Approved)
- Physical road geometry: `road_type`, `speed_limit`, `first_road_class`, `junction_detail_historic`, `junction_control`.
- Environmental conditions: `weather_conditions`, `road_surface_conditions`, `light_conditions`.
- Settlement & jurisdiction: `urban_or_rural_area`, `trunk_road_flag`, `police_force`.
- Cyclical temporal proxies: `collision_month`, `day_of_week`, `collision_hour`, `is_night`.
- Incident scope: `number_of_vehicles`.

### B. Post-Collision / Outcome Data (Strictly Forbidden)
- Casualty outcomes (`number_of_casualties`, `collision_injury_based`).
- Retrospective DfT statistical modeling adjustments (`collision_adjusted_severity_serious`, `collision_adjusted_severity_slight`, `enhanced_severity_collision`).
- Reporting attendance policies (`did_police_officer_attend_scene_of_accident`).

---

## 3. Projected Geospatial Clustering (EPSG:27700)
To avoid distortion from computing Euclidean distances on spherical angular coordinates (latitude/longitude degrees):
1. **Coordinate System**: We project coordinates to the **British National Grid (OSGR, EPSG:27700)**, where units are true metric distances (metres).
2. **DBSCAN Clustering**:
   - \(\epsilon = 250\text{ metres}\): Radius of local spatial neighborhood.
   - \(\text{MinSamples} = 15\text{ collisions}\): Density threshold for identifying persistent cluster cores.
3. **Exposure Interpretation**: High collision clusters indicate high spatial conflict density (e.g., major roundabouts or city centers) and must not be interpreted as per-vehicle risk without traffic flow denominators.
