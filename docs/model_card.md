# Model Card: Road Accident Severity Classifier (GB 2022)

## Model Details
- **Model Name**: Balanced Random Forest Severity Classifier
- **Model Version**: 1.0.0
- **Model Type**: Ensemble Decision Trees with Balanced Subsampling (`sklearn.ensemble.RandomForestClassifier`)
- **Primary Objective**: Multi-class classification of collision severity (`Fatal`, `Serious`, `Slight`) given initial pre-crash environmental and infrastructural attributes.
- **Developer**: Joyce Gracy
- **Release Date**: October 2026
- **License**: Open Government Licence v3.0 (Data Source)

---

## Intended Use & Prediction-Time Contract
- **Intended Use**: Educational exploration, academic research, and macroscopic policy scenario analysis of personal-injury road traffic collisions in Great Britain.
- **Prediction Point**: Immediately post-collision, utilizing observational data available at the scene (number of vehicles, speed limit, road geometry, weather, surface conditions, lighting, settlement density).
- **Out-of-Scope & Misuse Risks**:
  - **Not a Occurrence Predictor**: This model does *not* predict whether a collision will happen, only conditional severity given that a collision has occurred.
  - **Not an Operational Dispatch System**: The model must never be used to automate emergency vehicle triage, medical priority dispatch, or liability determination.
  - **No Individual Profiling**: The model does not use or endorse driver demographic profiling.

---

## Factors & Training Data
- **Dataset**: UK Department for Transport (DfT) STATS19 Road Safety Open Data (2022).
- **Total Records**: 106,004 personal-injury collisions.
- **Evaluation Split**: 80% Train (84,803 samples) / 20% Test (21,201 samples), stratified on severity with fixed `random_state=42`.
- **Target Distribution**:
  - Slight (Class 3): 76.48% (81,069 records)
  - Serious (Class 2): 22.01% (23,333 records)
  - Fatal (Class 1): 1.51% (1,602 records)

---

## Leakage Prevention Protocol
Strict exclusion of all:
1. Target variables & retrospective adjustments (`collision_severity`, `enhanced_severity_collision`, `collision_adjusted_severity_serious`, `collision_adjusted_severity_slight`).
2. Post-event consequence fields (`number_of_casualties`, `collision_injury_based`).
3. Reporting attendance biases (`did_police_officer_attend_scene_of_accident`).
4. Nominal identifiers causing memorisation (`collision_index`, `collision_ref_no`, `first_road_number`, `second_road_number`, `lsoa_of_accident_location`, `local_authority_ons_district`).

---

## Evaluation Benchmark & Actual Results

Models were evaluated on the held-out 20% test set (21,201 records):

| Model Candidate | Macro-F1 (Primary) | Accuracy (Secondary) | Balanced Accuracy | Fatal Recall (Class 1) | Serious Recall (Class 2) | Slight Recall (Class 3) |
|---|---|---|---|---|---|---|
| **Majority-Class Dummy Baseline** | **0.2889** | **0.7648** | **0.3333** | 0.00 | 0.00 | **1.00** |
| **Weighted Logistic Regression** | **0.3493** | 0.5017 | **0.5229** | 0.58 | 0.44 | 0.52 |
| **Balanced Random Forest (Selected)** | **0.3691** | **0.5595** | **0.5013** | 0.38 | 0.42 | 0.60 |
| **Histogram Gradient Boosting** | **0.3621** | 0.5281 | 0.5112 | 0.48 | 0.43 | 0.56 |

### Selected Model Justification:
**Balanced Random Forest** achieved the highest Macro-F1 score (**0.3691**), substantially outperforming the majority baseline (**0.2889**). While the naive baseline achieves 76.48% accuracy by systematically failing to detect a single fatal or serious collision, Balanced Random Forest successfully balances sensitivity across all three severity tiers.

---

## Limitations
1. **Single-Year Scope**: Trained strictly on 2022 data; random split evaluates within-year generalisation, not multi-year temporal transfer.
2. **Missing Vehicle Telematics**: Pre-crash impact speeds, deceleration forces, and vehicle occupant ages are unobserved in the collision-level extract.
