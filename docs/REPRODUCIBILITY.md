# GlycoTwin — Reproducibility Guide

This document explains how to reproduce the full GlycoTwin pipeline from raw data to a running application.

---

## Prerequisites

- Python 3.10+ (tested on Python 3.10.11)
- Windows 10/11 or Linux (macOS should work but is untested)
- 16 GB RAM recommended
- CPU only (no GPU required)
- ~700 MB free disk space for the raw dataset

---

## 1. Environment Setup

```bash
# Clone or extract the repository
cd GlycoTwin

# Install all dependencies
pip install -r requirements.txt

# Verify installation
python -c "import streamlit, pandas, sklearn, argon2; print('OK')"
```

---

## 2. Dataset Setup

Download the CGMacros dataset from PhysioNet:

1. Go to: https://physionet.org/content/cgmacros/1.0.0/
2. Accept the data use agreement
3. Download `CGMacros_dateshifted365.zip`
4. Place the zip at: `data/raw/CGMacros_dateshifted365.zip`
5. Extract to: `data/raw/cgmacros/CGMacros/`

Expected directory after extraction:
```
data/raw/cgmacros/CGMacros/
  bio.csv
  gut_health_test.csv
  microbes.csv
  CGMacros-001/
    CGMacros-001.csv
  CGMacros-002/
    CGMacros-002.csv
  ...
  CGMacros-049/
    CGMacros-049.csv
```

Verify the dataset loads:
```bash
python -c "from src.data.load_cgmacros import load_all_participants; df = load_all_participants(); print(f'Loaded {len(df):,} rows, {df.subject_id.nunique()} participants')"
```

---

## 3. Data Processing

> **Note:** Processed feature arrays (`data/processed/*.npy`, `data/processed/metadata.csv`) are
> **excluded from the repository** by `.gitignore` because they are derived from CC BY-NC-SA 4.0
> data. You must regenerate them from the raw dataset, or obtain them from the project authors
> under CC BY-NC-SA 4.0 terms. See `docs/DATA_LICENSES.md` for details.

To reproduce the preprocessing:

```bash
# Build processed dataset
python -m src.data.build_processed_dataset

# Build targets
python -m src.evaluation.build_targets_fast

# Create participant split
python -m src.evaluation.split_data
```

---

## 4. Model Training

> **Note:** Model artifacts (`models/*.pkl`, `models/*.pt`, `models/*.npy`) are **excluded from
> the repository** by `.gitignore` because they are derived from CC BY-NC-SA 4.0 data and their
> redistribution status is under legal review. You must retrain from scratch using the steps
> below. See `docs/DATA_LICENSES.md` and `docs/ARTIFACT_PROVENANCE.md` for details.

To retrain from scratch:

```bash
# Train logistic regression baseline
python -m src.models.train_baseline

# Calibrate with Platt scaling
python -m src.evaluation.calibrate_logistic

# (Optional) Train Random Forest
python -m src.models.train_random_forest

# (Optional) Run ablation study
python -m src.evaluation.run_ablation
```

**Important:** Never retrain while the dashboard is running. The dashboard loads a pre-trained model at startup and never retrains during use.

---

## 5. Model Evaluation

```bash
# Run evaluation on the held-out test set
python -m src.evaluation.calibrate_logistic
```

Metrics are saved to `data/processed/baseline_results.csv`.

---

## 6. Database Initialization

The database is initialized automatically when the app starts. To initialize manually:

```bash
python -c "from src.database.db import init_db; init_db(); print('Database initialized at instance/glycotwin.db')"
```

---

## 7. Run the Application

```bash
streamlit run app/dashboard.py
```

Or use the Windows batch file:
```
run_app.bat
```

Default URL: http://localhost:8501

---

## 8. Run the Test Suite

```bash
python -m pytest tests/ -q
```

Or:
```
run_tests.bat
```

Expected: 54 tests pass, 1 skipped (dataset-absent skip guard in test_data_loader, fires only when raw data absent).

---

## 9. Participant Split Determinism

The participant split is seeded with a fixed random seed in `src/evaluation/split_data.py`. The split is:
- 31 participants: train
- 7 participants: validation
- 7 participants: test

The split manifest is saved at `data/processed/participant_splits.csv` and should not change if re-run with the same seed.

---

## 10. Feature Consistency

The 24-feature vector built at inference time (in `src/twin/feature_builder.py`) must match the feature order used during training (in `src/models/train_baseline.py`).

To verify:
```bash
python -m pytest tests/test_feature_contract.py -v
```

---

## Known Reproducibility Issues

1. **sklearn version:** Model was pickled with sklearn 1.9.1. Loading on 1.7.2 produces a warning but the model functions correctly. For strict reproducibility, use sklearn 1.9.1.
2. **Argon2 parameters:** Password hashes are not reproducible by design (random salt per hash). This is correct security behavior.
3. **Floating-point:** Minor floating-point differences may occur across platforms but should not affect model outcomes.
