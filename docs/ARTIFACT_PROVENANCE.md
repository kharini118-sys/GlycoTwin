# GlycoTwin — Artifact Provenance Manifest

**Audit date:** 2026-10-20
**Auditor:** Automated (Antigravity)
**Purpose:** Comprehensive provenance record for licensing and reproducibility review
**Scope:** All non-source-code files in the GlycoTwin project directory

---

## Upstream Dataset

| Field | Value |
|---|---|
| Name | CGMacros: a scientific dataset for personalized nutrition and diet monitoring |
| Version | 1.0.0 |
| Authors | Gutierrez-Osuna R., Kerr D., Mortazavi B., Das A. |
| Published | PhysioNet, 2025 |
| DOI | https://doi.org/10.13026/3z8q-x658 |
| URL | https://physionet.org/content/cgmacros/1.0.0/ |
| License | Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0) |
| Access | Open access after accepting the PhysioNet data use agreement |
| Participants | 45 (IDs 1-49, with gaps; no participants 24, 25, 37, 40) |
| Features used | CGM glucose, heart rate, activity calories, METs, age, BMI, HbA1c, fasting glucose, insulin |
| Features NOT used | gut_health_test.csv, microbes.csv, meal macronutrients, VLDL, cholesterol/HDL |

---

## Category 1: Unmodified Upstream Data -- EXCLUDED from Repository

> **Status: All items in this category are excluded by .gitignore. They must never be committed.**

| Artifact | Path | Size | License | Notes |
|---|---|---|---|---|
| Source archive | data/raw/CGMacros_dateshifted365.zip | ~627 MB | CC BY-NC-SA 4.0 | Downloaded from PhysioNet; contains all participant data |
| Participant CSV files | data/raw/cgmacros/CGMacros/CGMacros-NNN/CGMacros-NNN.csv | varies | CC BY-NC-SA 4.0 | 45 individual participant time-series files |
| Food photo images | data/raw/cgmacros/CGMacros/CGMacros-NNN/photos/*.jpg | varies | CC BY-NC-SA 4.0 | Meal photographs; NOT used in model |
| Static clinical data | data/raw/cgmacros/CGMacros/bio.csv | 5.5 KB | CC BY-NC-SA 4.0 | Age, BMI, HbA1c, fasting glucose, insulin per participant |
| Gut microbiome data | data/raw/cgmacros/CGMacros/microbes.csv | 231 KB | CC BY-NC-SA 4.0 | NOT used in model |
| Gut health test data | data/raw/cgmacros/CGMacros/gut_health_test.csv | 2.7 KB | CC BY-NC-SA 4.0 | NOT used in model |

**Generation:** Downloaded directly from PhysioNet. No modifications made.

---

## Category 2: Derived Feature Arrays -- EXCLUDED from Repository

> **Status: All items in this category are excluded by .gitignore by default.**
> Redistribution requires compliance with CC BY-NC-SA 4.0 (share-alike + attribution).

| Artifact | Path | Size | Shape | License | Generation Script |
|---|---|---|---|---|---|
| Sequence features (raw) | data/processed/X_sequence.npy | 25.2 MB | (137581, 12, 4) float32 | CC BY-NC-SA 4.0 | src/data/build_processed_dataset.py |
| Sequence features (normalised) | data/processed/X_sequence_processed.npy | 25.2 MB | (137581, 12, 4) float32 | CC BY-NC-SA 4.0 | src/models/preprocess_sequences.py |
| Static features (raw) | data/processed/X_static.npy | 3.1 MB | (137581, 6) float32 | CC BY-NC-SA 4.0 | src/data/build_processed_dataset.py |
| Static features (normalised) | data/processed/X_static_processed.npy | 3.1 MB | (137581, 6) float32 | CC BY-NC-SA 4.0 | src/models/preprocess_static.py |
| Binary labels | data/processed/y.npy | 537.6 KB | (137581,) float32 | CC BY-NC-SA 4.0 | src/evaluation/build_targets_fast.py |
| Subject IDs per sample | data/processed/subjects.npy | 537.6 KB | (137581,) int32 | CC BY-NC-SA 4.0 | src/data/build_processed_dataset.py |
| Train split mask | data/processed/train_mask.npy | 134.5 KB | (137581,) bool | CC BY-NC-SA 4.0 | src/evaluation/split_data.py |
| Validation split mask | data/processed/val_mask.npy | 134.5 KB | (137581,) bool | CC BY-NC-SA 4.0 | src/evaluation/split_data.py |
| Test split mask | data/processed/test_mask.npy | 134.5 KB | (137581,) bool | CC BY-NC-SA 4.0 | src/evaluation/split_data.py |
| Sample metadata | data/processed/metadata.csv | 3.6 MB | (137581 rows) | CC BY-NC-SA 4.0 | src/data/build_processed_dataset.py |

**Feature columns:**
- Dynamic (axis 2 of X_sequence): [glucose, heart_rate, activity_calories, mets]
- Static (axis 1 of X_static): [age, bmi, hba1c, fasting_glucose, insulin, personal_baseline]

**PII assessment:** All participant IDs are anonymous integers. Timestamps in metadata.csv are
date-shifted (+-365-720 days) by the dataset publishers. No real names or contact information are
present. However, because these arrays are derived from health records, CC BY-NC-SA 4.0 applies.

---

## Category 3: Trained Model Artifacts -- EXCLUDED from Repository

> **Status: Excluded by .gitignore by default. Legal status requires human confirmation.**
> The application of CC BY-NC-SA 4.0 share-alike to ML model weights is an unsettled legal
> question. Do not redistribute without qualified legal review.

| Artifact | Path | Size | License | Generation Script | Notes |
|---|---|---|---|---|---|
| Logistic regression (base) | models/glycotwin_logistic.pkl | 2.3 KB | CONFIRM | src/models/train_baseline.py | sklearn Pipeline; intermediate artifact |
| Logistic regression (calibrated) | models/glycotwin_logistic_calibrated.pkl | 10.4 KB | CONFIRM | src/evaluation/calibrate_logistic.py | **PRODUCTION MODEL** |
| Random forest | models/glycotwin_random_forest.pkl | 31.9 MB | CONFIRM | src/models/train_random_forest.py | Exploratory only; not used in production |
| GRU checkpoint | models/glycotwin_gru.pt | 24.4 KB | CONFIRM | src/models/train_gru.py | PyTorch; exploratory |
| GRU checkpoint (corrected) | models/glycotwin_gru_corrected.pt | 23.4 KB | CONFIRM | src/models/train_gru.py | PyTorch; exploratory |
| GRU checkpoint v2 | models/glycotwin_gru_v2.pt | 26.1 KB | CONFIRM | src/models/train_gru.py | PyTorch; exploratory |

**Production model training procedure:**
1. 	rain_baseline.py -- Pipeline(SimpleImputer(median), StandardScaler, LogisticRegression(balanced, max_iter=1000)) on train split
2. calibrate_logistic.py -- Same pipeline + CalibratedClassifierCV(method=sigmoid, cv=5) fitted on train+val combined
3. Test split held out; never used for training, calibration, or hyperparameter selection

---

## Category 4: Normalization Statistics -- EXCLUDED from Repository

> **Status: Excluded by .gitignore by default. Computed from training-split participants only.**

| Artifact | Path | Shape | Values (approx.) | Generation Script |
|---|---|---|---|---|
| Dynamic feature means | models/sequence_means.npy | (4,) float32 | [glucose=104.8, HR=77.0, cal=1.86, METs=17.2] | src/models/preprocess_sequences.py |
| Dynamic feature medians | models/sequence_medians.npy | (4,) float32 | [glucose=96.5, HR=77.0, cal=1.29, METs=11.4] | src/models/preprocess_sequences.py |
| Dynamic feature stds | models/sequence_stds.npy | (4,) float32 | [glucose=38.9, HR=14.4, cal=1.33, METs=11.6] | src/models/preprocess_sequences.py |
| Static feature means | models/static_means.npy | (6,) float32 | [age=48.9, bmi=30.8, hba1c=6.0, fglu=117.4, ins=13.4] | src/models/preprocess_static.py |
| Static feature medians | models/static_medians.npy | (6,) float32 | [age=51, bmi=30.0, hba1c=5.8, fglu=104, ins=11.6] | src/models/preprocess_static.py |
| Static feature stds | models/static_stds.npy | (6,) float32 | [age=12.1, bmi=7.0, hba1c=0.77, fglu=27.5, ins=9.2] | src/models/preprocess_static.py |

These statistics are used at runtime inference by the TwinPredictor to normalise observations
before calling the calibrated model. They are computed from training-split participants only.

---

## Category 5: Aggregate Evaluation Results -- Included in Repository

> **Status: Included. Contain only summary statistics; no individual participant records.**
> Considered CC BY-NC-SA 4.0 derived but are standard scientific reporting artifacts.

| Artifact | Path | Size | Content | Generation Script |
|---|---|---|---|---|
| Final test/val metrics | data/processed/baseline_results.csv | 260 B | AUROC, AP, precision, recall, F1 for val and test | src/models/train_baseline.py |
| Ablation results | models/ablation_results.csv | 809 B | 4 feature-group experiments x 8 metrics each | src/evaluation/run_ablation.py |
| Threshold analysis | models/logistic_threshold_analysis.csv | 1.9 KB | Precision/recall/F1 at 17 thresholds (0.10-0.90) | src/evaluation/calibrate_logistic.py |
| Participant split manifest | data/processed/participant_splits.csv | 487 B | Anonymous subject ID + split assignment | src/evaluation/split_data.py |

---

## Category 6: Runtime-Generated Files -- EXCLUDED from Repository

| Artifact | Path | License | Notes |
|---|---|---|---|
| User database | instance/glycotwin.db | Private | SQLite with Argon2-hashed passwords; NEVER commit |
| Presentation slides | presentation/GlycoTwin_Challenge_Submission.pptx | MIT | Generated by scripts/build_presentation.py |
| Architecture PDF | docs/GlycoTwin_Architecture.pdf | MIT | Generated by scripts/build_architecture_pdf.py; included |

---

## Category 7: Synthetic / Demo Data

| Type | Location | Notes |
|---|---|---|
| Demo stream | demo.py lines 33-37 | 4 hard-coded glucose/HR/METs values; clearly labeled fabricated |
| Scenario perturbations | src/simulation/scenario.py | Parameterized perturbations on real Twin state; labeled hypothetical in UI |

No synthetic participant records are used in model training.

---

## Pre-Release Checklist

The following items **require human confirmation** before public release:

| # | Item | Status | Action Required |
|---|---|---|---|
| 1 | Raw CGMacros files not in git | OK - .gitignore excludes data/raw/ | Verify with git check-ignore -v data/raw/ after git init |
| 2 | Processed .npy arrays not in git | OK - .gitignore now excludes all data/processed/*.npy | Verify with git status after git init |
| 3 | Model .pkl/.pt files not in git | OK - .gitignore now excludes all model artifacts | Verify with git status after git init |
| 4 | Legal: redistribute trained model artifacts | REQUIRES HUMAN CONFIRMATION | Consult attorney re: CC BY-NC-SA 4.0 share-alike on ML weights |
| 5 | Legal: redistribute processed feature arrays | REQUIRES HUMAN CONFIRMATION | Same; likely CC BY-NC-SA 4.0 share-alike applies |
| 6 | CC BY-NC-SA attribution in public distribution | TODO if distributing artifacts | Add attribution block to any released archive |
| 7 | instance/glycotwin.db absent from submission | OK - .gitignore excludes instance/ | Do not include in any zip/archive upload |
| 8 | Confirm project is non-commercial as submitted | OK - documented in SAFETY_AND_LIMITATIONS.md | Challenge submission only |
| 9 | Re-verify PhysioNet license before release | REQUIRES HUMAN CONFIRMATION | Check https://physionet.org/content/cgmacros/1.0.0/ before submitting |
| 10 | GRU .pt files not needed for running app | OK - production app uses calibrated LR only | GRU files are exploratory; safely excluded |
