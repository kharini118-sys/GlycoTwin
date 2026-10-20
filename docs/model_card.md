# GlycoTwin — Model Card

**Model:** Calibrated Logistic Regression with Platt scaling
**Version:** glycotwin_logistic_calibrated.pkl
**Task:** Binary classification — will glucose rise ≥ 30 mg/dL within 120 minutes?
**Dataset:** PhysioNet CGMacros v1.0.0 (CC BY-NC-SA 4.0)

---

## Verified Test Set Metrics

All values from `data/processed/baseline_results.csv` — 7-participant held-out test set.
No values are hardcoded or fabricated.

| Metric | Value |
|---|---|
| Test AUROC | **0.7566** |
| Test Average Precision | **0.4666** |
| Test F1 (@ 0.20 threshold) | **0.4820** |
| Test Recall (@ 0.20 threshold) | **0.7305** |
| Test Precision (@ 0.20 threshold) | **0.3597** |
| Brier Score | **0.1439** |

---

## Intended Use

- Educational demonstration of Digital Twin concepts applied to CGM data
- Research prototype for the Happiest Health Digital Twin Challenge 2026
- **Not** for clinical decision-making, diagnosis, or treatment

## Out-of-scope Use

- Insulin dosing decisions
- Emergency clinical management
- Any use on identifiable real patient data
- Any commercial use (dataset is CC BY-NC-SA 4.0)

---

## Model Details

| Property | Value |
|---|---|
| Model family | Logistic Regression (sklearn Pipeline) |
| Calibration | Platt scaling on 7-participant validation set |
| Input | 24-feature vector (see [DATA_DICTIONARY.md](./DATA_DICTIONARY.md)) |
| Output | Probability in [0, 1]; threshold 0.20 is a research operating point |
| Training participants | 31 (patient-level split) |
| Validation participants | 7 (calibration only) |
| Test participants | 7 (held-out, never used during development) |

---

## Known Limitations

| Limitation | Detail |
|---|---|
| Small test set | 7 participants → wide confidence intervals |
| No external validation | Unknown performance on other populations |
| sklearn version mismatch | Pickled with 1.9.1, running on 1.7.2; works but warns |
| Zero imputation | Missing sensors filled with 0, not principled imputation |
| No temporal cross-validation | Participant-level split only |
| Threshold not clinical | 20% selected on validation data, not clinically validated |

---

## Training Data Statement

Training data was drawn from the PhysioNet CGMacros v1.0.0 dataset, licensed under
CC BY-NC-SA 4.0. The raw dataset is not distributed in this repository. Trained model
artifacts are derived from this CC BY-NC-SA 4.0 data; the share-alike clause may apply.

See [DATA_LICENSES.md](./DATA_LICENSES.md) for full license details.
See [DATA_PROVENANCE.md](./DATA_PROVENANCE.md) for participant split and data flow.
