# 📋 GlycoTwin — Data Schema Specification

## Dataset Overview
GlycoTwin utilizes the benchmark dataset **PhysioNet CGMacros v1.0.0** (45 participants across healthy, prediabetes, and Type 2 Diabetes cohorts).

---

## 1. Input Features Schema

### A. Static Clinical / Historical Profile (Stream 1)
- `patient_id` *(int / str)*: Unique anonymized participant identifier.
- `age` *(float)*: Chronological age in years.
- `bmi` *(float)*: Body Mass Index ($kg/m^2$).
- `hba1c` *(float)*: Glycated hemoglobin percentage (%).
- `fasting_glucose` *(float)*: Baseline fasting blood glucose ($mg/dL$).
- `insulin` *(float)*: Fasting plasma insulin ($\mu\text{IU/mL}$).
- `personal_baseline` *(float)*: Historical median glucose baseline calculated exclusively from past observations ($mg/dL$).

### B. Dynamic Wearable Sensor Telemetry (Stream 2)
Data is resampled to a standardized **5-minute temporal grid**:
- `timestamp` *(datetime)*: ISO 8601 UTC timestamp.
- `glucose` *(float)*: Continuous Glucose Monitor (CGM) reading ($mg/dL$).
- `heart_rate` *(float)*: Optical PPG heart rate (BPM).
- `activity_calories` *(float)*: Active calorie burn per 5-minute interval (kcal).
- `mets` *(float)*: Metabolic Equivalent of Task.

---

## 2. Sequence Windowing & Temporal Context
- **Historical Context Window**: 12 consecutive observations ($12 \times 5 \text{ mins} = 60 \text{ minutes}$).
- **Sequence Matrix Shape**: $(N_{\text{samples}}, 12, 4)$ representing `[glucose, heart_rate, activity_calories, mets]`.

---

## 3. Research Target Definition

```text
Target (Y) = 1  IF  max(glucose_{t + 5m : t + 120m}) - glucose_{t} >= 30 mg/dL
            = 0  OTHERWISE
```

- **Prediction Horizon**: 120 minutes (2 hours into the future).
- **Research Target Threshold**: $\ge 30 \text{ mg/dL}$ rise above current glucose level within the 120-minute horizon.
- **Scientific Boundary**: This $30 \text{ mg/dL}$ threshold is a **PoC research target definition** engineered for benchmark evaluation. It is NOT a universal clinical definition of hyperglycemia or a treatment threshold.
