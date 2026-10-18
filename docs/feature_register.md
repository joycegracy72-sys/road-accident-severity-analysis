# STATS19 Collision Feature Register (44 Fields)

## Project Title
**Road Accident Severity Analysis and Prediction Using Machine Learning**

## Dataset Scope
UK Department for Transport (DfT) STATS19 Personal-Injury Road Collisions (Great Britain, 2022).
Total Records: 106,004 rows | Total Attributes: 44 columns | Year: 2022.

---

## Prediction-Time Contract

### Contract Definition
**Objective**: Predict the recorded collision severity (`Fatal`, `Serious`, or `Slight`) of a road traffic collision *immediately after it has occurred and has been reported to the attending police / emergency dispatch*.

### Strict Leakage Constraints:
1. **No Target Leakage**: The model must never ingest the target variable (`collision_severity`), its direct clinical enhancements (`enhanced_severity_collision`), or retrospective statistical adjustments (`collision_adjusted_severity_serious`, `collision_adjusted_severity_slight`).
2. **No Post-Collision Outcome Leakage**: Features detailing medical outcomes, injury severity codes (`collision_injury_based`), or casualty totals (`number_of_casualties`) are strictly excluded as they reflect medical consequences rather than circumstances preceding/causing injury severity.
3. **No Reporting-Bias Leakage**: Features dependent on officer post-investigation attendance decisions (`did_police_officer_attend_scene_of_accident`) are excluded to avoid conditioning on severity-dependent dispatch policies.
4. **No Identity Memorisation**: Unique identifiers (`collision_index`, `collision_ref_no`) and extreme-cardinality nominal geographic/road numbers (`first_road_number`, `second_road_number`, `lsoa_of_accident_location`, `local_authority_ons_district`, `local_authority_highway`) are excluded to force models to learn generalisable physical and environmental patterns rather than memorising specific junctions or postcodes.
5. **No Data Snooping / Split Contamination**: Preprocessing encoders, scalers, and imputers must be fit strictly on training splits.

---

## Comprehensive 44-Column Feature Register

| # | Column Name | Verified Definition | Data Type | Missingness & Sentinels | Decision | Decision Rationale & Leakage Assessment |
|---|---|---|---|---|---|---|
| 1 | `collision_index` | Unique identifier for each collision record, combining collision year and police reference number. | String (`object`) | 0 missing (0%) | **EXCLUDE** | **Identity Memorisation Risk**: High-cardinality primary key. Contains no physical predictive signal and allows models to memorise incident IDs. |
| 2 | `collision_year` | Calendar year in which the collision occurred. | Integer (`int64`) | 0 missing (0%); 100% = 2022 | **EXCLUDE** | **Zero Variance**: Dataset is restricted strictly to 2022; single constant value across all 106,004 records. |
| 3 | `collision_ref_no` | In-year reference number assigned by the reporting police force. | String (`object`) | 0 missing (0%) | **EXCLUDE** | **Identity Memorisation Risk**: Police administrative internal reference. |
| 4 | `location_easting_osgr` | British National Grid (OSGR) Easting coordinate in metres (EPSG:27700). | Float (`float64`) | 22 missing (0.02%); 105,982 valid | **EXCLUDE from ML; PRESERVE for GIS** | **Spatial Overfitting Risk in ML**: Direct coordinates in tabular trees encourage memorising local accident points. **Essential for Geospatial Hotspot Analysis** (DBSCAN & metric distance in meters). |
| 5 | `location_northing_osgr` | British National Grid (OSGR) Northing coordinate in metres (EPSG:27700). | Float (`float64`) | 22 missing (0.02%); 105,982 valid | **EXCLUDE from ML; PRESERVE for GIS** | **Spatial Overfitting Risk in ML**: Same as easting. Metric coordinate preserved for British National Grid spatial clustering. |
| 6 | `longitude` | Geodetic longitude in WGS84 decimal degrees. | Float (`float64`) | 22 missing (0.02%); 105,982 valid | **EXCLUDE from ML; PRESERVE for GIS/UI** | **Spatial Overfitting Risk in ML**: Preserved for Folium web mapping and interactive GIS exploration. |
| 7 | `latitude` | Geodetic latitude in WGS84 decimal degrees. | Float (`float64`) | 22 missing (0.02%); 105,982 valid | **EXCLUDE from ML; PRESERVE for GIS/UI** | **Spatial Overfitting Risk in ML**: Preserved for Folium web mapping and interactive GIS exploration. |
| 8 | `police_force` | Numeric code indicating the police force area in Great Britain responsible for the jurisdiction. | Categorical / Int (`int64`) | 0 missing (0%); 51 active forces | **INCLUDE** | **Regional Context**: Captures regional jurisdiction and broad geographic territory without high-cardinality overfitting. Available at initial recording. No leakage. |
| 9 | `collision_severity` | Recorded severity of collision: 1 = Fatal, 2 = Serious, 3 = Slight. Determined by the most severely injured casualty. | Categorical / Int (`int64`) | 0 missing (0%); Imbalance: 1: 1,602, 2: 23,333, 3: 81,069 | **TARGET** | **Dependent Variable**: The ground truth target to be predicted. Must never be used as a predictor. |
| 10 | `number_of_vehicles` | Total count of vehicles involved in the collision. | Integer (`int64`) | 0 missing (0%); Range: 1 - 16 | **INCLUDE** | **Plausibly Available at Initial Scene**: Attending officers or callers immediately ascertain whether a collision is single-vehicle (run-off-road) or multi-vehicle pileup. Strong physical proxy for collision kinetic dynamics. |
| 11 | `number_of_casualties` | Total number of casualties injured or killed in the collision. | Integer (`int64`) | 0 missing (0%); Range: 1 - 59 | **EXCLUDE** | **Post-Event Consequence Leakage**: Casualty counts are direct consequences of severity and often revised post-incident following hospital admission. Locked Project Decision. |
| 12 | `date` | Calendar date of collision in DD/MM/YYYY format. | String (`object`) | 0 missing (0%); 2022-01-01 to 2022-12-31 | **FEATURE ENGINEERING** | Raw string excluded; engineered into `collision_month` (1-12) and `day_of_month` to capture seasonal weather patterns and holiday traffic volumes. |
| 13 | `day_of_week` | Day of week: 1 = Sunday, 2 = Monday, ... 7 = Saturday. | Categorical / Int (`int64`) | 0 missing (0%) | **INCLUDE** | **Temporal Risk Factor**: Captures weekend leisure/alcohol-associated travel versus weekday commuter traffic patterns. Known at prediction time. |
| 14 | `time` | Time of collision in 24-hour HH:MM format. | String (`object`) | 0 nulls; string format | **FEATURE ENGINEERING** | Engineered into `collision_hour` (0-23) and `is_night` (indicator). Essential proxy for circadian fatigue, rush hour congestion, and reduced nighttime visibility. |
| 15 | `local_authority_district` | Local administrative district code. | Integer (`int64`) | 0 missing (0%); 100% = -1 | **EXCLUDE** | **Degenerate Feature**: Deprecated in the 2022 DfT open extract in favor of ONS codes; contains constant value -1 for all 106,004 records. Locked Project Decision. |
| 16 | `local_authority_ons_district` | ONS 9-character geographic alpha-code for local authority district. | String (`object`) | 0 missing (0%); ~400 unique codes | **EXCLUDE** | **High Cardinality**: ~400 nominal levels. Risks severe tree overfitting; spatial regional context is adequately represented by `police_force` and `urban_or_rural_area`. |
| 17 | `local_authority_highway` | ONS highway authority administrative code. | String (`object`) | 0 missing (0%); ~200 unique codes | **EXCLUDE** | **High Cardinality / Redundant**: Redundant with regional and road class variables. |
| 18 | `local_authority_highway_current` | Mapped to latest ONS boundaries based on coordinate record. | String (`object`) | 0 missing (0%) | **EXCLUDE** | **Administrative Post-Processing**: Synthetic geographic mapping introduced in 2024 retrospective data. |
| 19 | `first_road_class` | Road classification: 1 = Motorway, 2 = A(M), 3 = A, 4 = B, 5 = C, 6 = Unclassified. | Categorical / Int (`int64`) | 0 missing (0%) | **INCLUDE** | **Key Road Hierarchy**: Fundamental indicator of road design standard, traffic volume, and carriageway separation. Readily known at scene. |
| 20 | `first_road_number` | Identifying road number (e.g., 1 for A1, 0 for unclassified). | Integer (`int64`) | 0 missing (0%); >1,000 distinct values | **EXCLUDE** | **Nominal Memorisation**: Thousands of individual road numbers. Risks memorising specific roads rather than structural roadway properties. |
| 21 | `road_type` | Road layout: 1 = Roundabout, 2 = One-way street, 3 = Dual carriageway, 6 = Single carriageway, 7 = Slip road, 9 = Unknown. | Categorical / Int (`int64`) | 0 nulls; 9 / -1 = Unknown | **INCLUDE** | **Structural Geometry**: Single carriageways carry severe head-on collision risks compared to grade-separated dual carriageways or roundabouts. |
| 22 | `speed_limit` | Posted legal speed limit in miles per hour (20, 30, 40, 50, 60, 70 mph). | Numeric (`int64`) | 0 nulls; -1/99 = missing | **INCLUDE** | **Kinetic Impact Energy**: Physical collision severity is governed by velocity squared (\(E_k = \frac{1}{2}mv^2\)). Primary physical determinant of collision trauma. |
| 23 | `junction_detail_historic` | Junction layout under STATS19 2011 specification (roundabout, T-junction, crossroad, slip road, private drive). | Categorical / Int (`int64`) | 0 nulls; 0 = Not at junction, 99 = Unknown | **INCLUDE (Preferred)** | **Conflict Geometry**: Preserves granular roundabout, mini-roundabout, and slip-road distinctions that are critical conflict points. Preferred over new collapsed version. |
| 24 | `junction_detail` | New 2024 STATS19 specification junction field. | Categorical / Int (`int64`) | 0 nulls; 55,139 coded 0, many -1 | **EXCLUDE** | **Redundant & Lossy**: Collapsed multiple historic categories into generic codes or missing values in 2022 extract. |
| 25 | `junction_control` | Control mechanism at junction: 1 = Authorised person, 2 = Automatic signal, 3 = Stop sign, 4 = Give way/uncontrolled, -1 = Not at junction. | Categorical / Int (`int64`) | 0 nulls; -1 = Not at junction, 9 = Unknown | **INCLUDE** | **Right-of-Way Regulation**: Identifies whether conflict points are actively signalized or rely on driver compliance. Known at scene. |
| 26 | `second_road_class` | Road classification of intersecting minor road at junction. | Categorical / Int (`int64`) | 0 nulls; 0 = Not at junction, -1 = Missing | **INCLUDE** | **Intersection Complexity**: Characterizes speed and volume differentials between intersecting road links. |
| 27 | `second_road_number` | Road number of intersecting minor road. | Integer (`int64`) | 0 nulls | **EXCLUDE** | **Nominal Memorisation**: Same as first road number. |
| 28 | `pedestrian_crossing_human_control_historic` | Physical presence of human crossing controller (school crossing patrol, police). | Categorical / Int (`int64`) | 0 nulls; 0 = None within 50m, 9/-1 = Unknown | **INCLUDE** | **Pedestrian Conflict Mitigation**: Indicates whether vulnerable road users are managed by active marshaling. |
| 29 | `pedestrian_crossing_physical_facilities_historic` | Zebra, pelican, puffin, toucan, traffic signal junction pedestrian phase, footbridge/subway. | Categorical / Int (`int64`) | 0 nulls; 0 = None within 50m, 9/-1 = Unknown | **INCLUDE (Preferred)** | **Vulnerable Road User Infrastructure**: Retains detailed engineering infrastructure distinctions. Known immediately. |
| 30 | `pedestrian_crossing` | New combined 2024 STATS19 crossing field. | Categorical / Int (`int64`) | 0 nulls | **EXCLUDE** | **Redundant**: Aggregates historic fields into a single lossy variable. |
| 31 | `light_conditions` | Ambient light and illumination: 1 = Daylight, 4 = Darkness (lit), 5 = Darkness (unlit), 6 = Darkness (no lighting), 7 = Darkness (unknown). | Categorical / Int (`int64`) | 0 nulls; 1 record = -1 | **INCLUDE** | **Visibility & Reaction Time**: Directly affects perception-reaction distance and emergency braking initiation. Available at scene. |
| 32 | `weather_conditions` | Atmospheric conditions: 1 = Fine, 2 = Rain, 3 = Snow, 4 = Fine + high winds, 5 = Rain + high winds, 6 = Snow + high winds, 7 = Fog/mist, 8/9 = Other/Unknown. | Categorical / Int (`int64`) | 0 nulls; 9 / -1 = Unknown | **INCLUDE** | **Atmospheric Hazard**: Influences roadway grip, spray, and driver sight distance. Available at scene. |
| 33 | `road_surface_conditions` | Surface status: 1 = Dry, 2 = Wet/damp, 3 = Snow, 4 = Frost/ice, 5 = Flood (>3cm), 9/-1 = Unknown. | Categorical / Int (`int64`) | 0 nulls; -1 / 9 = Unknown | **INCLUDE** | **Friction & Braking Distance**: Direct determinant of tire-road coefficient of friction and stopping distance. Available at scene. |
| 34 | `special_conditions_at_site` | Site anomalies: 0 = None, 1 = Signal out, 2 = Signal part defective, 3 = Defective signs/markings, 4 = Roadworks, 5 = Surface defective, 6 = Oil/diesel, 7 = Mud. | Categorical / Int (`int64`) | 0 nulls; 9 / -1 = Unknown | **INCLUDE** | **Site-Specific Engineering Defects**: Captures abnormal road friction or unheralded obstructions present at impact. |
| 35 | `carriageway_hazards_historic` | Obstacles in carriageway: 0 = None, 1 = Dislodged load, 2 = Other object, 3 = Prior collision, 6 = Dog, 7 = Other animal. | Categorical / Int (`int64`) | 0 nulls; 9 / -1 = Unknown | **INCLUDE (Preferred)** | **Sudden Avoidance Hazards**: Identifies sudden collision triggers causing violent evasive maneuvers. |
| 36 | `carriageway_hazards` | New 2024 STATS19 hazard field. | Categorical / Int (`int64`) | 0 nulls | **EXCLUDE** | **Redundant & Inconsistent**: Redundant with historic hazard categorization. |
| 37 | `urban_or_rural_area` | Geographic settlement density: 1 = Urban, 2 = Rural, 3 = Unallocated (22 records). | Categorical / Int (`int64`) | 0 nulls; 22 records = 3 | **INCLUDE** | **Critical Speed/Trauma Proxy**: Rural roads feature substantially higher operating speeds, longer emergency EMS transit times, and narrower margins for error. |
| 38 | `did_police_officer_attend_scene_of_accident` | Attendance flag: 1 = Attended at scene, 2 = No, 3 = Self-completion form. | Categorical / Int (`int64`) | 0 nulls | **EXCLUDE** | **Reporting-Bias Leakage Risk**: Police policy prioritizes physical attendance at severe and fatal collisions, whereas slight collisions are frequently self-reported online. |
| 39 | `trunk_road_flag` | Network jurisdiction: 1 = Trunk road (managed by National Highways), 2 = Non-trunk. | Categorical / Int (`int64`) | 0 nulls; -1 = Missing (7,440) | **INCLUDE** | **High-Capacity Strategic Network**: Identifies primary strategic corridors vs local council roads. |
| 40 | `lsoa_of_accident_location` | ONS Lower Layer Super Output Area code (~34,000 statistical small areas). | String (`object`) | 0 missing (0%); ~30,000 distinct strings | **EXCLUDE** | **Extreme Cardinality**: Induces catastrophic sparsity and memorisation in ML models. |
| 41 | `enhanced_severity_collision` | DfT severity classification enhanced with hospital trauma and clinical linkage data. | Categorical / Int (`int64`) | 0 nulls; -1 = Missing (50,275) | **EXCLUDE** | **Direct Target Leakage**: Retrospective clinical data determining injury severity. Locked Project Decision. |
| 42 | `collision_injury_based` | Binary indicator: 0 = Severity-based reporting, 1 = Injury-based reporting (CRASH/COPA). | Categorical / Int (`int64`) | 0 nulls; 55,729 = 1, 50,275 = 0 | **EXCLUDE** | **Reporting Mechanism Leakage**: Direct relationship to how target severity was collected and adjusted. Locked Project Decision. |
| 43 | `collision_adjusted_severity_serious` | DfT statistical model estimated probability that collision was serious. | Float (`float64`) | 0 nulls; Range: 0.0 - 1.0 | **EXCLUDE** | **Direct Target Leakage**: Retrospective statistical imputation of the target variable. Locked Project Decision. |
| 44 | `collision_adjusted_severity_slight` | DfT statistical model estimated probability that collision was slight. | Float (`float64`) | 0 nulls; Range: 0.0 - 1.0 | **EXCLUDE** | **Direct Target Leakage**: Retrospective statistical imputation of the target variable. Locked Project Decision. |

---

## Approved Final Predictor Allowlist (17 Model Features)

Following the rigorous leakage, availability, and cardinality audit, the following 17 features are approved for model training:

1. `number_of_vehicles` (Numeric)
2. `first_road_class` (Categorical)
3. `road_type` (Categorical)
4. `speed_limit` (Numeric/Ordinal)
5. `junction_detail_historic` (Categorical)
6. `junction_control` (Categorical)
7. `second_road_class` (Categorical)
8. `pedestrian_crossing_human_control_historic` (Categorical)
9. `pedestrian_crossing_physical_facilities_historic` (Categorical)
10. `light_conditions` (Categorical)
11. `weather_conditions` (Categorical)
12. `road_surface_conditions` (Categorical)
13. `special_conditions_at_site` (Categorical)
14. `carriageway_hazards_historic` (Categorical)
15. `urban_or_rural_area` (Categorical)
16. `trunk_road_flag` (Categorical)
17. `police_force` (Categorical)

### Engineered Predictors Derived from Safe Pre-Crash Attributes:
18. `collision_month` (Numeric/Categorical: 1-12, from `date`)
19. `day_of_week` (Categorical: 1-7)
20. `collision_hour` (Numeric: 0-23, from `time`)
21. `is_night` (Binary: 1 if hour in [21, 22, 23, 0, 1, 2, 3, 4, 5], 0 otherwise)
