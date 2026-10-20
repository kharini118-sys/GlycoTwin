# GlycoTwin — 20-Minute Video Submission Script

**Event:** Happiest Health Digital Twin Challenge 2026
**Duration:** 20–25 minutes
**Format:** Screen recording with narration

> **Note:** This is the corrected demo script. All performance metrics cited here are sourced
> directly from `data/processed/baseline_results.csv`. No metrics have been fabricated.
>
> **Status:** ⏳ Video recording is PENDING. The script below is ready for recording.
> Once recorded, paste the YouTube (unlisted) or Google Drive URL into README.md.

---

## Pre-Recording Setup Checklist

- [ ] Run `streamlit run app/dashboard.py` — confirm the landing page loads
- [ ] Set screen resolution to 1920×1080
- [ ] Open browser to http://localhost:8501
- [ ] Mute all notifications (Slack, Teams, system alerts)
- [ ] Start screen recording software (OBS Studio recommended)
- [ ] Have `docs/architecture.md` open in a browser tab for reference
- [ ] Have `data/processed/baseline_results.csv` open to show real metrics

---

## Video Time Breakdown

| Timestamp | Segment | Key Points |
|---|---|---|
| 00:00–02:00 | Problem Statement & Motivation | 101M Indians with T2D; reactive vs proactive care |
| 02:00–04:30 | Dataset & Licensing | CGMacros CC BY-NC-SA 4.0; 45 participants; data provenance |
| 04:30–07:30 | Architecture Walkthrough | Two-stream fusion; Digital Twin state; feature builder |
| 07:30–10:00 | Training, Evaluation & Ablation | Participant splits; verified metrics from CSV |
| 10:00–13:30 | Dashboard: Landing & Auth | Registration, login, demo access |
| 13:30–16:00 | Dashboard: Twin Overview & Replay | Step controls; real inference; chart |
| 16:00–18:00 | Dashboard: Scenario Simulator | Hypothetical perturbations; risk can increase or decrease |
| 18:00–19:30 | Dashboard: Evidence & Safety | Verified metrics panel; safety disclaimers |
| 19:30–21:00 | Limitations & Future Work | Known gaps; reproducibility; next steps |

---

## Segment 1 — Problem Statement (00:00–02:00)

**[Slide: Title / Problem]**

> "Welcome to GlycoTwin — a Personalized Bio-Digital Twin for two-hour glucose excursion risk
> prediction, submitted to the Happiest Health Digital Twin Challenge 2026.
>
> Over 101 million people in India live with Type 2 Diabetes. A central challenge in management
> is postprandial glucose excursions — significant glucose rises that occur in the hours after
> a meal or during metabolic stress.
>
> Current care is reactive: glucose spikes are managed after they happen.
> GlycoTwin demonstrates a proactive approach: by continuously fusing static clinical data
> with dynamic CGM and wearable observations, we maintain a stateful computational
> representation of a patient — their Digital Twin — and estimate the probability of a
> significant glucose rise in the next 120 minutes.
>
> This is a research prototype. It is not a medical device and does not provide
> treatment recommendations or diagnoses."

---

## Segment 2 — Dataset & Licensing (02:00–04:30)

**[Screen: Show PhysioNet page at https://physionet.org/content/cgmacros/1.0.0/]**

> "We built GlycoTwin using the PhysioNet CGMacros v1.0.0 dataset.
>
> CGMacros is an open research dataset from 45 anonymized participants containing:
> five-minute CGM glucose readings, heart rate, activity, METs, meal events, and
> static clinical data including age, BMI, HbA1c, and fasting glucose.
>
> This dataset is licensed under CC BY-NC-SA 4.0 — it is free to use for non-commercial research,
> with attribution required. The raw dataset is not in our repository — users must download it
> from PhysioNet directly.
>
> The required citation is: Das et al. (2025). CGMacros: a scientific dataset for
> personalized nutrition and diet monitoring. PhysioNet. DOI: 10.13026/3z8q-x658"

**[Screen: Show docs/DATA_PROVENANCE.md]**

> "All participants were anonymized, and dates were time-shifted for privacy protection.
> Our participant split is: 31 for training, 7 for validation and calibration, 7 for the
> held-out test. There is zero participant overlap between splits."

---

## Segment 3 — Architecture (04:30–07:30)

**[Screen: Show docs/architecture.md or architecture diagram]**

> "Let me walk through the system architecture.
>
> We fuse two data streams. Stream One is the static EHR profile: age, BMI, HbA1c,
> fasting glucose, and insulin — from the CGMacros bio.csv file.
>
> Stream Two is the dynamic wearable data: five-minute CGM glucose readings,
> heart rate, activity calories, and METs — from each participant's individual CSV.
>
> These streams feed into the Digital Twin State Engine. The Twin maintains:
> - A personal glucose baseline, updated exponentially: Bₜ = 0.95 × B_{t-1} + 0.05 × Gₜ
> - A glucose momentum estimate: Mₜ = 0.70 × M_{t-1} + 0.30 × (Gₜ − G_{t-1})
> - A data confidence score based on available sensor readings
>
> The state is used to build a 24-feature vector — the same definition used during model
> training — which is passed to the calibrated model for inference."

---

## Segment 4 — Training & Evaluation (07:30–10:00)

**[Screen: Open data/processed/baseline_results.csv in a text editor]**

> "The prediction target is: maximum observed glucose in the next 120 minutes is at least
> 30 mg/dL above the current glucose. Only actually observed future glucose readings
> are used — no imputed values.
>
> We evaluated three model classes: Logistic Regression, Random Forest, and a GRU network.
> The Calibrated Logistic Regression is our production model.
>
> Here are the verified test set results, reading directly from our evaluation file:"

**[Screen: Show the CSV values]**

> "Test AUROC: 0.7566. Average Precision: 0.4666. F1 at our 20% research threshold: 0.4820.
> Recall: 0.7305. Precision: 0.3597. Brier Score: 0.1439.
>
> Our ablation study shows the Digital Twin personal baseline adds +1.3 AUROC points
> over static and dynamic features alone — validating the core Twin concept.
>
> The 20% threshold is a research operating point selected on the validation set.
> It is not a clinically approved threshold."

---

## Segment 5 — Landing Page & Authentication (10:00–13:30)

**[Screen: http://localhost:8501 — landing page]**

> "Here is the running application. The landing page shows GlycoTwin branding, the architecture
> overview, and a prominent disclaimer: this is a research prototype, not a diagnostic device.
>
> I'll click Create Account."

**[Action: Register with a new account]**

> "Registration requires a display name, email, and password. Passwords are hashed with Argon2id
> before storage — the plaintext password is never stored or logged.
>
> I acknowledge the research disclaimer and create my account."

**[Action: Log in, then click Demo Access]**

> "We also support Demo Access for judges — this gives immediate dashboard access using
> the real model and real dataset, without requiring account creation."

---

## Segment 6 — Twin Overview & Replay (13:30–16:00)

**[Screen: Tab 1 — Twin Overview]**

> "In the sidebar I can filter participants by HbA1c cohort. Note: this is a research
> grouping, not a clinical diagnosis. I'll select a participant in the T2D range.
>
> The Twin initializes by replaying all historical observations. The Twin Overview tab
> shows the current glucose from the dataset, the personal baseline computed from past
> history, and the two-hour risk estimate from the actual trained model.
>
> The explanation panel shows which feature groups are most associated with the
> current risk estimate."

**[Screen: Tab 4 — CGM Replay]**

> "Tab 4 shows the replay controls. I can step forward one five-minute observation at a time,
> jump forward twelve observations — representing one hour — or reset to the beginning.
>
> Watch how the risk probability updates with each step as the Twin state evolves."

**[Action: Click Step Forward 3–4 times, show probability changing]**

---

## Segment 7 — Scenario Simulator (16:00–18:00)

**[Screen: Tab 2 — Scenario Simulator]**

> "The Scenario Simulator lets you explore what might happen under different conditions.
>
> I want to be explicit about what this is and what it is not. This is a feature-space
> perturbation: we clone the current Twin state, adjust specific feature values, and
> run the same inference pipeline. It is NOT a physiological or pharmacokinetic model.
>
> Crucially, risk can increase OR decrease under any scenario. We never force a direction.
> The result is clearly labeled as a hypothetical estimate.
>
> I'll run an Activity Increase scenario at 50% intensity."

**[Action: Run scenario, show result]**

> "The result shows baseline probability, scenario probability, and the difference in
> percentage points. Notice the assumptions and limitations are displayed below.
> This output is not a dietary or exercise recommendation."

---

## Segment 8 — Model Evidence & Safety (18:00–19:30)

**[Screen: Tab 5 — Model Evidence]**

> "Tab 5 shows the full model evidence panel. All metrics are loaded from the actual
> evaluation files — nothing is hardcoded.
>
> AUROC 0.757, Average Precision 0.467, F1 0.482, Brier Score 0.144.
>
> The ablation chart shows the contribution of each feature group. Note the known limitations:
> seven-participant test set, wide confidence intervals, simple zero-imputation for missing
> sensors, no external validation."

**[Screen: Show EHR Profile tab]**

> "The EHR Profile tab displays the static clinical values from the dataset with a disclaimer
> that the HbA1c cohort label is a research grouping, not a clinical diagnosis."

---

## Segment 9 — Limitations & Conclusion (19:30–21:00)

**[Slide: Limitations / Future Work]**

> "GlycoTwin demonstrates a genuine digital twin update loop: each new observation refreshes
> the Twin state and triggers fresh model inference. The ablation study confirms that
> personalization adds measurable value.
>
> Key limitations to be transparent about:
> - 45-participant dataset; 7-participant test set means confidence intervals are wide.
> - The 20% operating threshold is not clinically validated.
> - Missing sensor data is handled with simple zero imputation, not principled uncertainty.
> - No prospective or external validation has been performed.
> - sklearn version mismatch (model pickled with 1.9.1, running on 1.7.2) — model works
>   correctly but this should be resolved in production.
>
> Future work would include: external validation on an independent cohort, integration
> with real-time wearable APIs, principled uncertainty quantification, and a prospective
> clinical pilot study.
>
> Thank you. All source code, verified metrics, documentation, and the architecture
> diagram are in our submission repository. The dataset used is CGMacros v1.0.0,
> licensed under CC BY-NC-SA 4.0."

---

## Recording Checklist

Before publishing:
- [ ] All cited metrics match `data/processed/baseline_results.csv` (AUROC 0.7566, F1 0.4820)
- [ ] No mention of fabricated figures (AUC 0.92, F1 0.85, 53.3% demo risk, etc.)
- [ ] License correctly stated as CC BY-NC-SA 4.0, not CC BY 4.0
- [ ] No treatment recommendations made anywhere
- [ ] Scenario outputs introduced as hypothetical, not causal
- [ ] All placeholders in team info replaced with actual names
- [ ] Video is at least 20 minutes
- [ ] Audio is clear; narration matches screen
- [ ] Upload to YouTube (unlisted) or Google Drive
- [ ] Paste the video URL into README.md
