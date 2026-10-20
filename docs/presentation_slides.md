# GlycoTwin — Presentation Slide Outline

> **Note:** This is a corrected slide outline. All performance metrics are sourced from
> `data/processed/baseline_results.csv`. Figures marked AUC 0.92 / F1 0.85 in the
> previous version were incorrect and have been removed.
>
> The generated PPTX file is at `presentation/GlycoTwin_Challenge_Submission.pptx`.

---

## Slide 1: Title & Vision

- **Header:** GlycoTwin: Personalized Bio-Digital Twin for 2-Hour Glucose Excursion Prediction
- **Sub-header:** Research Prototype | Happiest Health Digital Twin Challenge 2026
- **Key message:** Transitioning diabetes care from reactive tracking to proactive 2-hour prediction
- **⚠️ Research Prototype — Not a Medical Device — Not Clinically Validated**

---

## Slide 2: The Healthcare Problem

- 101M+ people in India live with Type 2 Diabetes; 136M+ in pre-diabetic range
- Postprandial glucose excursions: significant glucose rises after meals
- Current care is reactive — spikes are observed after they occur
- Opportunity: CGM and wearable data enable a proactive prediction approach

---

## Slide 3: The GlycoTwin Digital Twin Concept

- **What is a Digital Twin?** A continuously updated computational patient representation
- Fuses two streams: static EHR + dynamic CGM / wearable time-series
- Each new 5-minute observation updates the Twin state and triggers fresh model inference
- Personalized baseline adapts to the individual: `Bₜ = 0.95 × B_{t-1} + 0.05 × Gₜ`
- Ablation study confirms personalization adds measurable predictive value (+1.3 AUROC)

---

## Slide 4: Dataset & Licensing

- **Dataset:** PhysioNet CGMacros v1.0.0
- **License:** CC BY-NC-SA 4.0 — non-commercial use only, share-alike required
- **Attribution:** Gutierrez-Osuna R, Kerr D, Mortazavi B, Das A (2025). DOI: 10.13026/3z8q-x658
- **45 participants:** 15 healthy, 16 pre-diabetes, 14 T2D
- Raw dataset not committed; users download from PhysioNet
- All dates time-shifted for privacy (PHI protection per HIPAA)

---

## Slide 5: System Architecture

- **Two input streams:** Static EHR profile (age, BMI, HbA1c, fasting glucose, insulin) + Dynamic wearable (CGM, HR, activity, METs)
- **Digital Twin State Engine:** Personal baseline, glucose momentum, metabolic state, confidence
- **24-Feature Builder:** Exact same feature definition used in training and inference
- **Calibrated Model:** Logistic Regression + Platt scaling → risk probability
- **Dashboard:** 5-tab Streamlit interface with auth, replay, scenario, export

---

## Slide 6: Verified Model Performance

> All metrics from `data/processed/baseline_results.csv` — 7-participant held-out test set

| Metric | Validation | Test (Held-Out) |
|---|---|---|
| AUROC | 0.7295 | **0.7566** |
| Average Precision | 0.4070 | **0.4666** |
| Recall @ 20% threshold | 0.7597 | **0.7305** |
| Precision @ 20% threshold | 0.3014 | **0.3597** |
| F1 @ 20% threshold | 0.4316 | **0.4820** |
| Brier Score | — | **0.1439** |

- Split: 31 train / 7 val / 7 test — zero participant overlap
- Threshold is a research operating point, NOT a clinically approved threshold

---

## Slide 7: Ablation Study

| Feature Configuration | Test AUROC |
|---|---|
| Static EHR only | 0.608 |
| Dynamic wearable only | 0.646 |
| Static + Dynamic | 0.729 |
| **Static + Dynamic + Personal Baseline ✓ (Production)** | **0.742** |

The Digital Twin personal baseline adds +1.3 AUROC points over static + dynamic features.

---

## Slide 8: Scenario Simulator

- Applies feature-space perturbations to the current Twin state
- 4 scenario types: activity increase/decrease, glucose trend shift, HR elevation
- Risk can **increase or decrease** — never forced in either direction
- Labeled as **hypothetical estimates** — NOT physiological simulations
- NOT dietary or exercise recommendations
- No treatment advice, no medication changes suggested

---

## Slide 9: Safety & Responsible AI

- GlycoTwin is an **experimental research prototype**
- Risk scores are model estimates, **not diagnoses**
- Model is **not clinically validated**
- Output is **not a substitute for professional medical care**
- Must not be used for medication or emergency-care decisions
- 20% threshold is a research choice, not a clinical alert threshold

---

## Slide 10: Conclusion & Future Work

- Demonstrated genuine Digital Twin update loop with measurable personalization benefit
- Open dataset, verified metrics, full source code, 48 passing tests
- **Future work:** External validation, real-time wearable APIs, prospective clinical pilot,
  principled uncertainty quantification, regulatory pathway exploration
