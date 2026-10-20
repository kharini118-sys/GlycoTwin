# GlycoTwin — Data Dictionary

**Dataset:** PhysioNet CGMacros v1.0.0
**URL:** https://physionet.org/content/cgmacros/1.0.0/
**Status:** Open-source, anonymized, date-shifted

---

## Static Clinical Features (bio.csv)

| Column | Type | Unit | Description | Missing? |
|---|---|---|---|---|
| `subject` | int | — | Anonymized participant identifier | Never |
| `Age` | float | years | Participant age | Rare |
| `Gender` | str | M/F | Biological sex | Rare |
| `BMI` | float | kg/m² | Body mass index | Rare |
| `A1c PDL (Lab)` | float | % | Glycated hemoglobin HbA1c | Some |
| `Fasting GLU - PDL (Lab)` | float | mg/dL | Fasting blood glucose | Some |
| `Insulin ` | float | µIU/mL | Fasting plasma insulin (note trailing space) | Many |
| `Triglycerides` | float | mg/dL | Fasting triglycerides | Some |
| `Cholesterol` | float | mg/dL | Total cholesterol | Some |
| `HDL` | float | mg/dL | HDL cholesterol | Some |
| `LDL (Cal)` | float | mg/dL | Calculated LDL | Some |

**Note:** `A1c PDL (Lab)` values are used for research cohort classification only. A value ≥6.5% places a participant in the "T2D range" cohort for this research prototype. This is not equivalent to a clinical Type 2 Diabetes diagnosis.

---

## Dynamic Time-Series Features (per-participant CSVs)

| Column | Type | Unit | Cadence | Description |
|---|---|---|---|---|
| `Timestamp` | datetime | — | ~5 min | Observation timestamp (date-shifted) |
| `Libre GL` | float | mg/dL | ~15 min | Abbott Libre CGM glucose reading |
| `Dexcom GL` | float | mg/dL | ~5 min | Dexcom G-series CGM glucose |
| `HR` | float | bpm | ~5 min | Heart rate |
| `Calories (Activity)` | float | kcal | ~5 min | Active calorie expenditure |
| `METs` | float | — | ~5 min | Metabolic equivalent of task |
| `Meal Type` | str | — | Event | Meal type label |
| `Calories` | float | kcal | Event | Meal total calories |
| `Carbs` | float | g | Event | Carbohydrate content |
| `Protein` | float | g | Event | Protein content |
| `Fat` | float | g | Event | Fat content |
| `Fiber` | float | g | Event | Dietary fiber |
| `Amount Consumed ` | float | g/mL | Event | Consumed amount (trailing space) |

**Glucose fallback:** `Libre GL` is used as primary glucose; if missing, `Dexcom GL` is used.

---

## Canonical Model Features (after cleaning)

After `clean_cgmacros.py`, the model uses these 24 features (in fixed order):

| Index | Feature | Source | Description |
|---|---|---|---|
| 0 | `current_glucose` | Dynamic | Most recent CGM reading |
| 1 | `glucose_mean` | Dynamic | Mean over last 12 obs (~60 min) |
| 2 | `glucose_std` | Dynamic | Std over last 12 obs |
| 3 | `glucose_min` | Dynamic | Min over last 12 obs |
| 4 | `glucose_max` | Dynamic | Max over last 12 obs |
| 5 | `glucose_change_from_start` | Dynamic | Current − first of last 12 |
| 6 | `glucose_change_4th_last` | Dynamic | Current − 4th-last reading |
| 7 | `heart_rate_last` | Dynamic | Most recent HR |
| 8 | `heart_rate_mean` | Dynamic | Mean HR over window |
| 9 | `heart_rate_std` | Dynamic | Std HR over window |
| 10 | `activity_last` | Dynamic | Most recent activity calories |
| 11 | `activity_mean` | Dynamic | Mean activity over window |
| 12 | `activity_sum` | Dynamic | Cumulative activity in window |
| 13 | `activity_max` | Dynamic | Peak activity in window |
| 14 | `mets_last` | Dynamic | Most recent METs |
| 15 | `mets_mean` | Dynamic | Mean METs over window |
| 16 | `mets_max` | Dynamic | Peak METs in window |
| 17 | `age` | Static | From bio.csv |
| 18 | `bmi` | Static | From bio.csv |
| 19 | `hba1c` | Static | From bio.csv |
| 20 | `fasting_glucose` | Static | From bio.csv |
| 21 | `insulin` | Static | From bio.csv |
| 22 | `personal_baseline` | Computed | EMA of past glucose observations |
| 23 | `glucose_deviation` | Computed | current_glucose − personal_baseline |

---

## Target Variable

| Name | Type | Definition |
|---|---|---|
| `excursion_label` | binary | 1 if max valid observed glucose in next 120 minutes ≥ (current glucose + 30 mg/dL), else 0 |

**Important:** The target uses only **observed** (non-imputed) future glucose values. Rows with insufficient forward coverage are excluded (labeled unknown, not negative). No forward-filled values are used as ground truth.

---

## Computed Twin State Variables

These are descriptive computational features, not validated physiological equations:

| Variable | Formula | Notes |
|---|---|---|
| `personal_baseline` | EMA: `0.95 × B_{t-1} + 0.05 × G_t` | Slowly adapting mean |
| `glucose_momentum` | EMA: `0.70 × M_{t-1} + 0.30 × (G_t − G_{t-1})` | Recent trend |
| `metabolic_state` | `clamp((G_t − B_t) / 40, −3, 3)` | Normalized deviation |
| `activity_state` | `clamp(calories / 5, 0, 3)` | Normalized activity |
| `cardiovascular_state` | `clamp((HR − 70) / 30, −2, 2)` | Normalized HR |
| `data_confidence` | `#valid_sensors / 4` | Completeness score |

---

## Missing Value Handling

- **Model input:** NaN values are imputed with zeros via `nan_to_num` before inference.
- **This is a convenience imputation, not a calibrated uncertainty estimate.**
- A data confidence score < 1.0 signals incomplete sensor data.
- Missing future glucose excludes that row from the target label (not treated as negative).
