# GlycoTwin — System Architecture

> **Note:** Previous versions of this file contained incorrect performance figures
> (AUROC 0.92, F1 0.85). All metrics below are verified against
> `data/processed/baseline_results.csv`.

---

## Architecture Overview

GlycoTwin is a three-layer system that fuses static EHR data with dynamic CGM
and wearable observations to maintain a stateful Digital Twin and estimate
2-hour glucose excursion risk.

```
┌─────────────────────────┐    ┌─────────────────────────────┐
│  STATIC EHR INPUT       │    │  DYNAMIC WEARABLE INPUT     │
│  bio.csv (bio.csv)      │    │  CGMacros-0XX.csv           │
│  Age, BMI, HbA1c,       │    │  CGM Glucose, Heart Rate,   │
│  Fasting Glucose,        │    │  Activity Cal, METs         │
│  Fasting Insulin         │    │  5-minute intervals         │
└───────────┬─────────────┘    └────────────────┬────────────┘
            │                                   │
            └──────────────────┬────────────────┘
                               ▼
              ┌────────────────────────────────┐
              │   DATA CLEANING & FEATURES     │
              │   load_cgmacros.py             │
              │   clean_cgmacros.py            │
              │   Resample → 5-min grid        │
              │   Participant split (31/7/7)   │
              └────────────────┬───────────────┘
                               │
               ┌───────────────┴────────────────┐
               ▼                                ▼
  ┌────────────────────────┐    ┌───────────────────────────┐
  │  DIGITAL TWIN STATE    │    │  MODEL TRAINING (offline) │
  │  state.py / updater.py │    │  train_baseline.py        │
  │  Personal baseline EMA │    │  Calibrated Logistic Reg. │
  │  Glucose momentum      │    │  Train set: 31 ptcps      │
  │  Metabolic state       │    │  Val/calib set: 7 ptcps   │
  │  Cardiovascular state  │    │  [Never runs during app]  │
  │  Data confidence       │    └───────────────────────────┘
  └────────────┬───────────┘
               │
               ▼
  ┌────────────────────────────────────────────────┐
  │  24-FEATURE VECTOR  (feature_builder.py)       │
  │  Glucose stats (7) | HR stats (3)              │
  │  Activity stats (4) | METs stats (3)           │
  │  Static clinical (5) | Personal baseline (2)   │
  └────────────────────┬───────────────────────────┘
                       │
          ┌────────────┴───────────────┐
          ▼                            ▼
┌───────────────────────┐   ┌──────────────────────────┐
│  RISK PREDICTION      │   │  SCENARIO SIMULATOR      │
│  predictor.py         │   │  scenario.py             │
│  glycotwin_logistic   │   │  Feature-space           │
│  _calibrated.pkl      │   │  perturbations only      │
│  P(rise ≥30 mg/dL     │   │  Not physiological sim   │
│   in 120 min)         │   │  HYPOTHETICAL outputs    │
│  Threshold: 0.20 (R)  │   └──────────────────────────┘
└───────────┬───────────┘
            │
            ▼
┌───────────────────────────────────────────────────────┐
│  STREAMLIT DASHBOARD  (app/dashboard.py)              │
│  Tab 1: Twin Overview & 2-Hour Prediction             │
│  Tab 2: Scenario Simulator                            │
│  Tab 3: EHR Profile                                   │
│  Tab 4: CGM Replay Controls                           │
│  Tab 5: Model Evidence & Metrics                      │
│  Auth: Argon2id  |  DB: SQLite  |  Export: PDF/CSV   │
└───────────────────────────────────────────────────────┘
```

*(R) = Research operating point — not a clinically validated threshold.*

---

## Verified Test Set Performance

All values from `data/processed/baseline_results.csv` — 7-participant held-out test set.

| Metric | Value |
|---|---|
| Test AUROC | **0.7566** |
| Test Average Precision | **0.4666** |
| Test F1 (@ 20% threshold) | **0.4820** |
| Test Recall | 0.7305 |
| Test Precision | 0.3597 |
| Brier Score | 0.1439 |

**Ablation:** Personal baseline EMA adds +1.3 AUROC points over static + dynamic features alone.

---

## Key Design Decisions

| Decision | Rationale |
|---|---|
| Participant-level split (31/7/7) | Prevents data leakage across rows from the same individual |
| Platt scaling on val set only | Calibration does not touch training or test data |
| Zero imputation for missing sensors | Simplicity for PoC; documented as limitation |
| 20% research threshold | Selected on val-set precision-recall; not clinical |
| No retrain during dashboard use | Dashboard is inference-only; training is a separate offline step |

---

## Further Documentation

| Document | Contents |
|---|---|
| [DATA_DICTIONARY.md](./DATA_DICTIONARY.md) | All 24 features with index, source, and description |
| [DATA_PROVENANCE.md](./DATA_PROVENANCE.md) | Dataset origin, license, participant split |
| [DATA_LICENSES.md](./DATA_LICENSES.md) | Full license text and artifact-level applicability |
| [SAFETY_AND_LIMITATIONS.md](./SAFETY_AND_LIMITATIONS.md) | Complete safety and limitations statement |
| [REPRODUCIBILITY.md](./REPRODUCIBILITY.md) | How to reproduce training and evaluation |
| [model_card.md](./model_card.md) | Model card with verified metrics |
| [GlycoTwin_Architecture.pdf](./GlycoTwin_Architecture.pdf) | Printable architecture diagram |
