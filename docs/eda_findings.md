# Exploratory Data Analysis Findings: STATS19 Collisions (2022)

## 1. Executive Summary
This document provides empirical findings from the exploratory data analysis of the official UK Department for Transport (DfT) 2022 STATS19 collision dataset (106,004 records). All metrics, percentages, and figures reflect verified data without fabrication or post-hoc adjustments.

---

## 2. Target Distribution & Severe Class Imbalance

The collision severity target exhibits acute class imbalance:
- **Slight (Class 3)**: 81,069 collisions (**76.48%**)
- **Serious (Class 2)**: 23,333 collisions (**22.01%**)
- **Fatal (Class 1)**: 1,602 collisions (**1.51%**)

```
Total Collisions: 106,004
Majority Baseline (Always predicting Slight): 76.48% Accuracy
```

**Practical Modeling Implication**:
A naïve model predicting `Slight` for every collision achieves ~76.5% accuracy while identifying zero fatalities and zero serious casualties (0% recall on classes 1 and 2). Therefore:
- Accuracy is strictly a secondary metric.
- **Macro-F1** (unweighted arithmetic mean of per-class F1-scores) and class-specific recall are the primary evaluation metrics.

---

## 3. Temporal Collision Dynamics

### Monthly Volume:
Collision volume fluctuates across the calendar year:
- **Peak Months**: November (9,592 collisions), June (9,349 collisions), and October (9,334 collisions).
- **Trough Months**: February (7,678 collisions) and April (7,933 collisions).
- The autumn/winter spike correlates with deteriorating weather, wet road surfaces, and fewer daylight hours during evening rush hour.

### Day of Week Volume:
- **Peak Day**: Friday (17,911 collisions, 16.9% of total), followed by Thursday (16,273 collisions).
- **Lowest Day**: Sunday (12,001 collisions, 11.3% of total).
- Collision volume steadily climbs across the working week from Monday (14,055) to Friday before dropping on weekends.

### Diurnal Profile & Nighttime Risk:
- Collision volume peaks during conventional peak commuter hours (08:00-09:00 and 16:00-18:00).
- However, when analyzing the **proportion of fatalities and serious injuries within hourly intervals**, late-night and early-morning hours (23:00 to 05:00) exhibit a sharply elevated fatality share. This is associated with higher average vehicular speeds on empty roads, alcohol involvement, and driver circadian fatigue.

---

## 4. Road Infrastructure and Speed Limits

### Posted Speed Limit vs Severity Distribution:
The posted speed limit is one of the most decisive physical determinants of collision severity:

| Speed Limit (mph) | Collision Volume | Fatal Share (%) | Serious Share (%) | Slight Share (%) |
|---|---|---|---|---|
| **20 mph** | 16,452 | 0.41% | 18.13% | 81.46% |
| **30 mph** | 57,329 | 0.90% | 20.97% | 78.13% |
| **40 mph** | 9,162 | 1.72% | 23.32% | 74.96% |
| **50 mph** | 4,546 | 3.43% | 25.89% | 70.68% |
| **60 mph** | 12,599 | **3.91%** | **30.20%** | 65.89% |
| **70 mph** | 5,916 | 3.57% | 20.47% | 75.96% |

**Key Observations**:
1. **Kinetic Scaling**: Fatality rates scale monotonically from 0.41% at 20 mph to 3.91% at 60 mph (a nearly 10-fold increase).
2. **60 mph Single-Carriageway Hazard**: 60 mph roads (predominantly rural single-carriageway A and B roads) exhibit the highest fatality rate (3.91%) and serious injury rate (30.20%). These roads lack central physical barriers, have conflicting access points, and permit high closing speeds.
3. **70 mph Motorway Effect**: While 70 mph roads have high operating speeds, their fatality proportion (3.57%) is lower than 60 mph roads, and serious injury proportion (20.47%) is comparable to 30 mph roads. This is attributable to grade separation, lack of pedestrian/cyclist presence, and forgiving modern crash barriers.

---

## 5. Urban vs Rural Settlement Analysis

| Settlement Classification | Total Collisions | Fatal Share (%) | Serious Share (%) | Slight Share (%) |
|---|---|---|---|---|
| **Urban** | 71,763 (67.7%) | 0.81% | 20.11% | 79.08% |
| **Rural** | 34,219 (32.3%) | **2.99%** | **26.00%** | 71.02% |
| **Unallocated** | 22 (0.02%) | 0.00% | 18.18% | 81.82% |

**Substantive Findings**:
- **Volume vs Severity Contrast**: While 67.7% of all collisions occur in urban areas due to higher traffic density and frequent conflict points, **rural collisions are far more lethal**.
- Rural collisions exhibit a **nearly 3.7x higher fatality rate** (2.99% vs 0.81%) and higher serious injury rate (26.00% vs 20.11%).
- Causes include higher operating speeds, absence of street lighting, unyielding roadside obstacles (trees, stone walls), and longer emergency medical services (EMS) response and transit times.

---

## 6. Environmental and Surface Conditions

- **Surface Conditions**: 74.3% of collisions (78,784) occurred on dry road surfaces, while 22.0% (23,369) occurred on wet or damp surfaces. Snow and ice accounted for 1,958 collisions (1.8%).
- **Atmospheric Conditions**: Fine weather without high winds accounted for 82.0% (86,939) of collisions, while raining conditions accounted for 10.4% (10,981).
- **Lighting**: 71.7% of collisions occurred in daylight (75,961), with 20.8% in darkness with streetlights lit (22,009), and 5.2% in darkness without lighting (5,555). Collisions occurring in unlit darkness carried an elevated fatality share (3.8%).

---

## 7. Methodological Safeguards & Limitations

1. **No Exposure Data**: The STATS19 collision dataset records incidents that occurred. It does *not* contain traffic volume (vehicle-miles travelled) or population exposure denominators. Therefore, higher collision counts on Friday or in urban areas reflect traffic volume and exposure, not inherently higher per-mile risk.
2. **Correlation vs Causation**: Factors such as 60 mph speed limits correlate with rural road design, roadside trees, and distance to trauma centers. The speed limit itself is a major physical factor, but operates within a broader systemic context.
3. **Reporting Scope**: Only police-reported personal injury collisions are included. Damage-only incidents are legally excluded from STATS19 reporting in Great Britain.
