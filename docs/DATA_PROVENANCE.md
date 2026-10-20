# GlycoTwin — Data Provenance

---

## Primary Dataset

**Name:** CGMacros: a scientific dataset for personalized nutrition and diet monitoring
**Version:** 1.0.0
**URL:** https://physionet.org/content/cgmacros/1.0.0/
**License:** Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)
**Published:** PhysioNet (2025)
**DOI:** https://doi.org/10.13026/3z8q-x658

### Required Attribution

> Gutierrez-Osuna, R., Kerr, D., Mortazavi, B., & Das, A. (2025). CGMacros: a scientific
> dataset for personalized nutrition and diet monitoring (version 1.0.0). PhysioNet.
> https://doi.org/10.13026/3z8q-x658

BibTeX:
```bibtex
@article{PhysioNet-cgmacros-1.0.0,
  author  = {Gutierrez-Osuna, Ricardo and Kerr, David and Mortazavi, Bobak and Das, Anurag},
  title   = {{CGMacros: a scientific dataset for personalized nutrition and diet monitoring}},
  journal = {{PhysioNet}},
  year    = {2025},
  month   = jan,
  note    = {Version 1.0.0},
  doi     = {10.13026/3z8q-x658},
  url     = {https://doi.org/10.13026/3z8q-x658}
}
```

### Description

CGMacros provides multimodal data from 45 participants: continuous glucose monitoring (CGM),
heart rate, activity (METs, calories), meal events with macronutrient content, and static EHR
data (age, BMI, HbA1c, fasting glucose, insulin). Data spans approximately 10 consecutive days
per participant in a free-living setting.

Participant breakdown: 15 healthy (HbA1c < 5.7%), 16 pre-diabetes (5.7–6.4%), 14 T2D (> 6.4%).

### Privacy

- All participant identifiers are anonymized (numeric IDs only).
- Dates are time-shifted by +/− N days (365 < N < 720) to protect privacy (PHI under HIPAA).
- No real names, locations, or contact information are present.
- GlycoTwin does **not** distribute the raw dataset.

---

## What GlycoTwin Stores

| Data Type | Storage Location | License | Excluded from repo? |
|---|---|---|---|
| Raw CGMacros CSVs | `data/raw/cgmacros/CGMacros/` | CC BY-NC-SA 4.0 | **YES — .gitignore** |
| Source archive | `data/raw/CGMacros_dateshifted365.zip` | CC BY-NC-SA 4.0 | **YES — .gitignore** |
| Preprocessed feature arrays | `data/processed/X_*.npy`, `y.npy`, `subjects.npy`, masks | CC BY-NC-SA 4.0 (derived) | **YES — .gitignore** |
| Sample metadata | `data/processed/metadata.csv` | CC BY-NC-SA 4.0 (derived) | **YES — .gitignore** |
| Participant split manifest | `data/processed/participant_splits.csv` | CC BY-NC-SA 4.0 (derived) | No (IDs only) |
| Aggregate evaluation metrics | `data/processed/baseline_results.csv` | CC BY-NC-SA 4.0 (derived) | No (aggregate only) |
| Trained model (production) | `models/glycotwin_logistic_calibrated.pkl` | ⚠️ Likely CC BY-NC-SA 4.0 | **YES — .gitignore** |
| Trained model (base) | `models/glycotwin_logistic.pkl` | ⚠️ Likely CC BY-NC-SA 4.0 | **YES — .gitignore** |
| Trained model (RF) | `models/glycotwin_random_forest.pkl` | ⚠️ Likely CC BY-NC-SA 4.0 | **YES — .gitignore** |
| Trained model (GRU variants) | `models/glycotwin_gru*.pt` | ⚠️ Likely CC BY-NC-SA 4.0 | **YES — .gitignore** |
| Normalization statistics | `models/sequence_*.npy`, `models/static_*.npy` | ⚠️ Likely CC BY-NC-SA 4.0 | **YES — .gitignore** |
| Ablation results | `models/ablation_results.csv` | CC BY-NC-SA 4.0 (derived) | No (aggregate only) |
| Threshold analysis | `models/logistic_threshold_analysis.csv` | CC BY-NC-SA 4.0 (derived) | No (aggregate only) |
| GlycoTwin source code | `app/`, `src/`, `tests/`, `scripts/` | MIT | No |
| User account database | `instance/glycotwin.db` | Private (user data) | **YES — .gitignore** |

> **Note on model artifacts:** Trained models and normalisation statistics are derived from or
> computed using CC BY-NC-SA 4.0 data. The share-alike clause likely extends to these artifacts.
> They are gitignored by default. Consult a qualified attorney before any redistribution.


---

## Data Flow

```
PhysioNet CGMacros v1.0.0 (CC BY-NC-SA 4.0)
        |
        ↓  [downloaded by user — not committed to repo]
data/raw/cgmacros/CGMacros/
        |
        ↓  src/data/load_cgmacros.py
        |  src/data/clean_cgmacros.py
        ↓
Canonical DataFrame (in memory, no PII)
        |
        ↓  src/data/build_processed_dataset.py
        |  src/evaluation/build_targets_fast.py
        |  src/evaluation/split_data.py
        ↓
data/processed/ (preprocessed arrays, no PII, CC BY-NC-SA 4.0 derived)
        |
        ↓  src/models/train_baseline.py
        |  src/evaluation/calibrate_logistic.py
        ↓
models/glycotwin_logistic_calibrated.pkl (CC BY-NC-SA 4.0 derived)
        |
        ↓  src/twin/ (runtime inference — read-only, no training)
        ↓
Streamlit Dashboard (app/dashboard.py)
```

---

## Participant Split Manifest

The 45 participants are divided into three non-overlapping sets at the participant level.
No participant appears in more than one split.

| Split | Count | Participant IDs |
|---|---|---|
| Train | 31 | 18,14,47,16,10,17,42,34,30,1,33,32,6,12,36,2,45,22,3,38,26,41,11,23,19,49,21,8,15,31,43 |
| Validation | 7 | 28,20,39,13,7,48,5 |
| Test (held-out) | 7 | 4,27,44,35,46,9,29 |

**Split procedure:** Participant-level stratified random split (seeded). Calibration (Platt
scaling) was fitted on validation split labels only. The test split was used only for final
evaluation and was never used to select thresholds, features, or hyperparameters.

---

## What Was Not Used

| Data | Reason |
|---|---|
| `gut_health_test.csv` | Viome gut health scores — not in 24-feature model |
| `microbes.csv` | Microbiome bacteria presence — not in 24-feature model |
| Meal macronutrient fields | Loaded during cleaning but not in current feature set |
| VLDL, Cholesterol/HDL ratio | Present in bio.csv but not in current feature set |
| Sleep data | Not reliably present in dataset |

---

## Synthetic / Demo Data

No synthetic patient data is used in production inference. The scenario simulator applies
feature-space perturbations to real observed Twin states and is clearly labeled as hypothetical.

Demo Access mode uses the real model and the real CGMacros dataset observations.
No probabilities are hardcoded or injected into demo mode.

---

## How to Obtain the Dataset

1. Visit https://physionet.org/content/cgmacros/1.0.0/
2. Create a PhysioNet account if you do not have one
3. Review and accept the data use agreement
4. Download `CGMacros_dateshifted365.zip` (or individual files)
5. Extract to `data/raw/cgmacros/CGMacros/` within the project directory
6. Verify: `python -c "from src.data.load_cgmacros import load_bio; print(load_bio().shape)"`

Expected output: `(45, 24)` or similar (45 participants, multiple columns).
