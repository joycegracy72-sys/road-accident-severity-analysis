# Feature Safety and Data Quality Audit

## Project
Road Accident Severity Analysis and Prediction Using Machine Learning

## Dataset
UK Department for Transport STATS19 collision data, 2022.

The dataset covers reported personal-injury road collisions in Great
Britain. It should not be interpreted as a dataset of every road
collision or as data collected in India.

## Prediction Objective
Predict the recorded severity of a collision that has already occurred.

The model does not predict whether a collision will happen.

## Target
- `collision_severity`
- 1 = Fatal
- 2 = Serious
- 3 = Slight

## Preliminary Feature Decisions

### Exclude from predictors
- `collision_index`: unique identifier.
- `collision_severity`: target, not a predictor.
- `number_of_casualties`: excluded initially because it may reveal
  information about the consequences of the collision.
- `collision_injury_based`: excluded because it relates to severity
  reporting.
- `enhanced_severity_collision`: excluded pending definition review.
- `collision_adjusted_severity_serious`: excluded due to potential
  target leakage.
- `collision_adjusted_severity_slight`: excluded due to potential
  target leakage.
- `local_authority_district`: all 106,004 records contain -1, so the
  field has no useful variation in this dataset.
- `junction_detail`: not selected until its conversion rules and
  suitability for 2022 data are understood.

### Potential predictors requiring further review
- `number_of_vehicles`
- `junction_detail_historic`
- `junction_control`
- `weather_conditions`
- `road_surface_conditions`
- `trunk_road_flag`

These are candidates, not yet approved predictors. Their definitions,
missing-value codes, and availability at prediction time must be checked.

## Junction Field Findings

The 2022 dataset contains both `junction_detail_historic` and
`junction_detail`.

The historic field retains categories such as roundabout,
mini-roundabout, and slip road. The newer field uses a different
coding scheme and maps several historic categories to -1 or 0.

The fields must not be treated as interchangeable without reviewing
the applicable conversion rules.

The historic field is the preferred candidate for further investigation.

## Coordinate Quality

Total records: 106,004.

Records missing longitude, latitude, easting, and northing: 22.
All four coordinate fields are missing together in those 22 records.

Records with all four coordinates available: 105,982.

The original dataset will be preserved. Geographic analysis will use
a separate dataset containing records with valid coordinates.

## Severity Distribution

- Fatal (1): 1,602
- Serious (2): 23,333
- Slight (3): 81,069

A baseline that always predicts Slight would achieve approximately
76.5% accuracy. Accuracy alone will therefore be insufficient for
model evaluation.

Planned metrics include macro-F1, per-class precision and recall,
and a confusion matrix.

## Outstanding Checks

1. Verify the applicable field definitions for the 2022 dataset.
2. Investigate why `local_authority_district` is -1 in every record.
3. Review all potential predictors for target leakage.
4. Decide whether `number_of_vehicles` is available at the defined
   prediction time.
5. Verify the meaning of missing and special codes before recoding.
6. Confirm appropriate geographic handling of coordinates.
7. Record final feature decisions before model training.

## Status

Preliminary audit. No model has been trained and no predictive
performance claims have been made.