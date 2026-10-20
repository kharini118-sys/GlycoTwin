# 🧬 GlycoTwin
### Personalized Bio-Digital Twin for 2-Hour Glucose Excursion Risk Prediction
**Happiest Health Digital Twin Challenge 2026**

---

## 📌 Submission Metadata & Team Information

| Field | Value |
|---|---|
| **Project Title** | GlycoTwin — Personalized Bio-Digital Twin for 2-Hour Glucose Excursion Risk Prediction |
| **Team Leader** | [INSERT TEAM LEADER NAME] |
| **Team Members** | [INSERT STUDENT 1], [INSERT STUDENT 2], [INSERT STUDENT 3] |
| **Institution** | [INSERT COLLEGE / INSTITUTE / INCUBATOR NAME] |
| **Contact Email** | [INSERT EMAIL ADDRESS] |
| **GitHub Repository** | [INSERT PUBLIC REPOSITORY URL] |
| **Demo Video** | [INSERT YOUTUBE UNLISTED / GOOGLE DRIVE LINK] |
| **License** | [MIT License](./LICENSE) (code) + [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) (dataset) |
| **Submission Deadline** | 20 October 2026, 7:00 PM IST |

> **⚠️ Research Prototype:** GlycoTwin is a proof-of-concept built for a hackathon.
> It is not a medical device, not clinically validated, and does not provide treatment recommendations.

---

## 🎯 Problem Statement & Healthcare Use Case

Over **101 million people in India** live with Type 2 Diabetes, with another **136 million in the pre-diabetic range**. Postprandial glucose variability — glucose spikes in the hours after eating — is a major driver of long-term vascular complications.

Current clinical workflows are **reactive**: clinicians and patients observe glucose excursions after they occur. GlycoTwin explores a **proactive** approach: by continuously fusing static clinical data with dynamic CGM and wearable streams, a stateful Digital Twin estimates the probability of a significant glucose rise in the next 120 minutes.

**This is a research prototype.** It demonstrates the Digital Twin concept on open-source research data. Real-world clinical use would require prospective validation, regulatory approval, and clinical partnership.

---

## 🧬 What Makes GlycoTwin a Digital Twin

A Digital Twin is more than a static dashboard. GlycoTwin implements a genuine update loop:

1. **State Initialization:** The Twin starts with a participant's static EHR profile
2. **Sequential Observation:** Each new 5-minute CGM/wearable observation is processed
3. **State Update:** The Twin updates its personal baseline, glucose momentum, and sensor context
4. **Feature Construction:** A 24-feature vector is built using the same definition as training
5. **Model Inference:** The calibrated model produces a new probability estimate
6. **Dashboard Update:** The UI reflects the new Twin state and risk estimate

The Twin's personal baseline (`Bₜ = 0.95 × B_{t-1} + 0.05 × Gₜ`) adapts over time, creating a participant-specific reference that the population-level model alone cannot provide. The ablation study confirms this personalization adds measurable predictive value.

---

## 🏗️ Architecture

```
Static Clinical Profile (EHR)          Dynamic CGM & Wearable Observations
  Age, BMI, HbA1c, Fasting Glucose        5-min Glucose, HR, Activity, METs
           |                                              |
           └──────────────────┬────────────────────────┘
                              ↓
                   Validation & Preprocessing
                              ↓
               Stateful Digital Twin State Engine
         (Personal Baseline | Momentum | Confidence)
                              ↓
                Training-consistent Feature Builder
                      (24-feature vector)
                              ↓
                  Calibrated ML Predictor
             (Logistic Regression + Platt Scaling)
                              ↓
             2-Hr Glucose Excursion Probability
                              ↓
                 Clinician-Facing Dashboard
        (Replay | Scenario Simulator | Export)
```

See [`docs/architecture.md`](./docs/architecture.md) for the architecture overview and
[`docs/GlycoTwin_Architecture.pdf`](./docs/GlycoTwin_Architecture.pdf) for the printable architecture diagram PDF.

---

## 📊 Dataset

| Property | Value |
|---|---|
| **Name** | PhysioNet CGMacros v1.0.0 |
| **URL** | https://physionet.org/content/cgmacros/1.0.0/ |
| **License** | [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) — Non-commercial use only, share-alike required |
| **Participants** | 45 anonymized individuals |
| **Attribution** | Das A et al. (2025). CGMacros v1.0.0. PhysioNet. https://doi.org/10.13026/3z8q-x658 |

The raw dataset is **not** included in this repository. Download from PhysioNet and place at `data/raw/cgmacros/CGMacros/`.

---

## 🤖 Machine Learning

### Target Definition
> Positive label: the maximum observed glucose in the next 120 minutes is ≥ (current glucose + 30 mg/dL)

No forward-filled or imputed future glucose values are used as ground truth.

### Participant-Level Evaluation (No Data Leakage)

| Split | Participants |
|---|---|
| Train | 31 |
| Validation | 7 (calibration only) |
| Test (held-out) | 7 |

**Zero participant overlap between splits.**

### Verified Performance — Calibrated Logistic Regression

| Metric | Test Set Value |
|---|---|
| **AUROC** | **0.7566** |
| **Average Precision** | **0.4666** |
| **Precision @ 20%** | 0.3597 |
| **Recall @ 20%** | 0.7305 |
| **F1 @ 20%** | **0.4820** |
| **Brier Score** | 0.1439 |

*All metrics from `data/processed/baseline_results.csv` — never fabricated.*

### Ablation Study — Value of Personalization

| Feature Configuration | Test AUROC | Test F1 |
|---|---|---|
| Static EHR only | 0.608 | 0.381 |
| Dynamic wearable only | 0.646 | 0.396 |
| Static + Dynamic | 0.729 | 0.467 |
| **Static + Dynamic + Personal Baseline ✓** | **0.742** | **0.479** |

The personalized baseline (the core Digital Twin feature) adds **+1.3 AUROC points** over static + dynamic features.

### Operating Threshold
The **20% threshold** is a research operating point selected on the validation set. It is NOT a clinically validated decision boundary. At this threshold, the model prioritizes recall (0.730) — flagging most true excursions at the cost of many false positives.

---

## 🚀 Installation & Quickstart

### Prerequisites
- Python 3.10+ (tested on 3.10.11)
- 16 GB RAM
- Windows 10/11 (Linux/Mac should work)

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from src.database.db import init_db; init_db()"

# Launch dashboard
streamlit run app/dashboard.py
```

### Windows (one-click)
```
run_app.bat
```

### Dataset Setup
1. Download CGMacros from https://physionet.org/content/cgmacros/1.0.0/
2. Place at `data/raw/cgmacros/CGMacros/`

### Model Training (optional — artifacts included)
```bash
python -m src.models.train_baseline
python -m src.evaluation.calibrate_logistic
```

---

## 🧪 Application Features

| Feature | Status |
|---|---|
| Landing page with branding | ✅ |
| Account registration (Argon2id) | ✅ |
| Login with session management | ✅ |
| Participant cohort selection | ✅ |
| Digital Twin state initialization | ✅ |
| 5-min step replay controls | ✅ |
| Real model inference at each step | ✅ |
| Twin evolution timeline | ✅ |
| Feature contribution explanation | ✅ |
| Scenario simulator (4 types) | ✅ |
| Correct probability arithmetic | ✅ |
| EHR profile display | ✅ |
| Model evidence panel | ✅ |
| PDF session report export | ✅ |
| CSV data export | ✅ |
| Workspace save/load/delete | ✅ |
| User preferences persistence | ✅ |

---

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -q

# Or use Windows batch file
run_tests.bat
```

**Test coverage:** 48 tests across auth, twin state, scenario simulator, predictor, and data splits.

---

## 📁 Repository Structure

```
GlycoTwin/
├── README.md
├── LICENSE
├── .gitignore
├── requirements.txt
├── run_app.bat
├── run_tests.bat
├── app/
│   ├── dashboard.py          # Main Streamlit application
│   └── auth.py               # Argon2id authentication
├── src/
│   ├── data/                 # CGMacros loaders and cleaners
│   ├── evaluation/           # Target construction, splits, ablation
│   ├── models/               # Training scripts
│   ├── twin/                 # Digital Twin state engine
│   ├── simulation/           # Scenario simulator, PDF/CSV export
│   └── database/             # SQLite persistence layer
├── models/                   # Pre-trained model artifacts
├── data/
│   ├── raw/                  # Raw dataset (NOT in repo)
│   └── processed/            # Preprocessed arrays and metrics
├── docs/
│   ├── architecture.md            # Architecture overview (text)
│   ├── GlycoTwin_Architecture.pdf # Architecture diagram (PDF)
│   ├── model_card.md
│   ├── DATA_DICTIONARY.md
│   ├── DATA_PROVENANCE.md
│   ├── DATA_LICENSES.md
│   ├── SAFETY_AND_LIMITATIONS.md
│   ├── REPRODUCIBILITY.md
│   ├── INITIAL_AUDIT.md
│   └── FINAL_SUBMISSION_CHECKLIST.md
├── video/
│   └── 20_minute_demo_script.md
└── tests/                    # 48 unit and integration tests
```

---

## ⚕️ Safety & Research Disclaimers

- **Research prototype only.** Not a diagnostic device.
- **No treatment recommendations.** GlycoTwin never suggests medication changes.
- **20% threshold is a research operating point**, not a clinically validated boundary.
- **Dataset cohort classification** (HbA1c-based) is a research grouping, not a clinical diagnosis.
- **Scenario outputs** are feature-space perturbations, not causal counterfactuals.
- **External validation** is required before any clinical application.

See [`docs/SAFETY_AND_LIMITATIONS.md`](./docs/SAFETY_AND_LIMITATIONS.md) for the complete safety document.

---

## 📜 License

- **Source code:** [MIT License](./LICENSE)
- **Dataset:** [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) — Non-commercial use only.
  Das A, Kerr D, Glanz N, Bevier W, Santiago R, Gutierrez-Osuna R, Mortazavi B (2025).
  CGMacros v1.0.0. PhysioNet. https://doi.org/10.13026/3z8q-x658
