# Project Limitations & Boundary Conditions

## 1. Exposure Data Absence
- **Denominator Blindness**: The STATS19 dataset contains records of collisions that *did occur*. It does not record traffic exposure (vehicle miles travelled, pedestrian footfall, or entering junction counts).
- **Analytical Precaution**: High collision counts in urban areas or on Fridays reflect exposure volume, not necessarily higher per-mile hazard.

## 2. Single-Year Snapshot (2022)
- The dataset is strictly confined to calendar year 2022.
- A random stratified train/test split evaluates interpolation within 2022; it does **not** constitute empirical validation across future years or under shifting macroeconomic/regulatory regimes.

## 3. Police Reporting Threshold
- Damage-only collisions are excluded from STATS19 reporting in Great Britain.
- Minor collisions with very slight injuries may suffer from under-reporting compared to fatal incidents where police attendance is legally mandatory.

## 4. Model Interpretation Caveat
- The trained classifiers predict **conditional severity** given an accident has occurred. They do not predict crash probability.
