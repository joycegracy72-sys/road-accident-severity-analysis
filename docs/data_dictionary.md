# Data Dictionary: STATS19 Cleaned Datasets (2022)

## 1. Overview
This data dictionary documents the attributes in the processed datasets:
- **`data/processed/collisions_cleaned_model.parquet`** (106,004 records): Full dataset with engineered features, approved model predictors, and target.
- **`data/processed/collisions_cleaned_geo.parquet`** (105,982 records): Subset of records with validated geographic coordinates in Great Britain (EPSG:27700 OSGR and WGS84).

---

## 2. Target Variable

### `collision_severity`
- **Definition**: The recorded severity of the collision, determined by the most severely injured casualty involved.
- **Data Type**: `int64`
- **Values**:
  - `1` = **Fatal**: Collision resulted in at least one death within 30 days of the incident (1,602 records, 1.51%).
  - `2` = **Serious**: Casualty sustained severe injuries (e.g., fractures, severe concussion, internal injuries, detention in hospital) but no fatalities (23,333 records, 22.01%).
  - `3` = **Slight**: Casualty sustained minor injuries (e.g., sprains, cuts, bruises, shock) with no hospital detention exceeding 24 hours (81,069 records, 76.48%).

---

## 3. Model Predictor Features (21 Features)

### A. Numeric & Continuous Features (4)

| Feature Name | Type | Unit / Range | Description & Sentinel Handling |
|---|---|---|---|
| `number_of_vehicles` | Integer (`int64`) | 1 to 16 | Number of vehicles involved in collision. Observed immediately at scene. No missing values. |
| `speed_limit` | Integer (`int64`) | 20, 30, 40, 50, 60, 70 mph | Posted legal speed limit in miles per hour. All 106,004 records contain valid speed limits. |
| `collision_hour` | Integer (`int64`) | 0 to 23 | Hour of day collision occurred, extracted from `time`. Represents diurnal cycle. |
| `collision_month` | Integer (`int64`) | 1 to 12 | Month of year collision occurred, extracted from `date`. Represents seasonal factors. |

### B. Categorical & Indicator Features (17)

| Feature Name | Type | Value Codes / Mappings |
|---|---|---|
| `first_road_class` | Integer (`int64`) | `1`=Motorway, `2`=A(M), `3`=A, `4`=B, `5`=C, `6`=Unclassified |
| `road_type` | Integer (`int64`) | `1`=Roundabout, `2`=One-way street, `3`=Dual carriageway, `6`=Single carriageway, `7`=Slip road, `9`=Unknown, `-1`=Missing |
| `junction_detail_historic` | Integer (`int64`) | `0`=Not at junction, `1`=Roundabout, `2`=Mini-roundabout, `3`=T or staggered, `5`=Slip road, `6`=Crossroads, `7`=Multiple junction, `8`=Private drive, `9`=Other, `99`=Unknown |
| `junction_control` | Integer (`int64`) | `-1`=Not at junction/missing, `1`=Authorised person, `2`=Automatic traffic signal, `3`=Stop sign, `4`=Give way/uncontrolled, `9`=Unknown |
| `second_road_class` | Integer (`int64`) | `0`=Not at junction, `1`=Motorway, `2`=A(M), `3`=A, `4`=B, `5`=C, `6`=Unclassified, `-1`=Missing |
| `pedestrian_crossing_human_control_historic` | Integer (`int64`) | `0`=None within 50m, `1`=School patrol, `2`=Other authorised person, `9`=Unknown, `-1`=Missing |
| `pedestrian_crossing_physical_facilities_historic` | Integer (`int64`) | `0`=No physical facility within 50m, `1`=Zebra, `4`=Pelican/puffin/toucan, `5`=Pedestrian phase at signal, `7`=Footbridge/subway, `8`=Central refuge, `9`=Unknown, `-1`=Missing |
| `light_conditions` | Integer (`int64`) | `1`=Daylight, `4`=Darkness (lights lit), `5`=Darkness (lights unlit), `6`=Darkness (no lighting), `7`=Darkness (lighting unknown), `-1`=Missing |
| `weather_conditions` | Integer (`int64`) | `1`=Fine no high winds, `2`=Raining no high winds, `3`=Snowing no high winds, `4`=Fine + high winds, `5`=Raining + high winds, `6`=Snowing + high winds, `7`=Fog/mist, `8`=Other, `9`=Unknown, `-1`=Missing |
| `road_surface_conditions` | Integer (`int64`) | `1`=Dry, `2`=Wet or damp, `3`=Snow, `4`=Frost or ice, `5`=Flood (>3cm deep), `9`=Unknown, `-1`=Missing |
| `special_conditions_at_site` | Integer (`int64`) | `0`=None, `1`=Auto signal out, `2`=Auto signal part defective, `3`=Defective road sign/marking, `4`=Roadworks, `5`=Road surface defective, `6`=Oil or diesel, `7`=Mud, `9`=Unknown, `-1`=Missing |
| `carriageway_hazards_historic` | Integer (`int64`) | `0`=None, `1`=Vehicle load on road, `2`=Other object, `3`=Previous accident, `6`=Dog on road, `7`=Other animal, `9`=Unknown, `-1`=Missing |
| `urban_or_rural_area` | Integer (`int64`) | `1`=Urban (>10k population), `2`=Rural, `3`=Unallocated (22 records) |
| `trunk_road_flag` | Integer (`int64`) | `1`=Trunk road (National Highways managed), `2`=Non-trunk, `-1`=Missing |
| `police_force` | Integer (`int64`) | Numeric police force code (1 to 98) across Great Britain |
| `day_of_week` | Integer (`int64`) | `1`=Sunday, `2`=Monday, `3`=Tuesday, `4`=Wednesday, `5`=Thursday, `6`=Friday, `7`=Saturday |
| `is_night` | Integer (`int64`) | `1`=Night (hours 21:00-05:59), `0`=Day (hours 06:00-20:59) |

---

## 4. Geographic Coordinate Attributes (Preserved in GIS Dataset)

| Attribute Name | Coordinate Reference System | Bounds | Description |
|---|---|---|---|
| `location_easting_osgr` | British National Grid (EPSG:27700) | 79,266m - 655,345m | Easting coordinate in true metres. Validated within GB grid bounds. |
| `location_northing_osgr` | British National Grid (EPSG:27700) | 10,502m - 1,172,667m | Northing coordinate in true metres. Validated within GB grid bounds. |
| `longitude` | WGS84 Geodetic (EPSG:4326) | -7.353562° to +1.759829° | Longitude in decimal degrees for interactive map display. |
| `latitude` | WGS84 Geodetic (EPSG:4326) | +49.914329° to +60.435892° | Latitude in decimal degrees for interactive map display. |
