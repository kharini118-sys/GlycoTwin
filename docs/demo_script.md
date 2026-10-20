# GlycoTwin — Live Demo Script (Corrected)

> **Corrected version.** Previous version contained fabricated performance figures (AUC 0.92,
> F1 0.85) and hardcoded demo values (53.3% risk, 12.4% post-intervention risk). These have
> been removed. All metrics now reference `data/processed/baseline_results.csv`.

---

## 20-Minute Demo Outline

| Time | Topic | Key Points |
|---|---|---|
| 00:00–01:30 | Healthcare Problem | 101M with T2D in India; reactive vs proactive care |
| 01:30–03:00 | Digital Twin Concept | Stateful update loop; two-stream fusion |
| 03:00–05:00 | Dataset & Licensing | CGMacros CC BY-NC-SA 4.0; 45 participants; provenance |
| 05:00–07:00 | Architecture | State engine; 24-feature builder; calibrated model |
| 07:00–10:00 | Training & Evaluation | Participant splits; verified metrics from CSV |
| 10:00–12:00 | Dashboard: Landing & Auth | Registration; Argon2id hashing; demo access |
| 12:00–15:00 | Dashboard: Twin Overview | Real model inference; step replay; Plotly charts |
| 15:00–17:00 | Dashboard: Scenario Simulator | Hypothetical perturbations; risk may increase or decrease |
| 17:00–18:30 | Dashboard: Model Evidence | Verified AUROC 0.757; ablation chart; limitations |
| 18:30–19:30 | Safety & Limitations | Non-diagnostic; no treatment recommendations |
| 19:30–20:00 | Conclusion | Reproducibility; future work; dataset attribution |

---

## Live Demo Walkthrough

### Step 1: Patient Profile Initialization

> "I select participant `CGMacros-001` from the sidebar. The Digital Twin initializes
> by replaying all historical observations for this participant."

**Show:** Static clinical profile values (age, BMI, HbA1c, fasting glucose) — read from the
actual `bio.csv` file for this participant. Do **not** state specific fabricated values;
let the actual loaded values speak.

---

### Step 2: Dynamic Wearable Stream Replay

> "In the CGM Replay tab, I can step through the observation sequence one 5-minute interval
> at a time. Watch how the Twin State updates — the personal baseline adapts, the glucose
> momentum changes, and the model re-runs inference."

**Show:** Step through 3–5 observations using the Step Forward button. The probability
shown is the actual model output for those feature values.

---

### Step 3: Risk Prediction Display

> "The risk probability shown here is the output of the Calibrated Logistic Regression model
> — the same model that achieved AUROC 0.757 and F1 0.482 on the 7-participant held-out test.
>
> Our research operating threshold is 20%. This is a research choice, not a clinically
> validated decision boundary."

**Important:** Do NOT describe the risk display as a "clinical alert." Do NOT state specific
probability values in the narration — let the actual displayed value speak.

---

### Step 4: Scenario Simulator

> "The Scenario Simulator allows exploration of hypothetical scenarios. I select 'Activity
> Increase' and run it. Notice that the result shows the baseline probability and the
> scenario probability — the difference can be positive or negative.
>
> This is a feature-space perturbation, not a physiological simulation. It is not a
> recommendation to exercise. The assumptions and limitations are shown below the result."

**Show:** Run one scenario. Note that the result and delta are actual model outputs.

---

### Step 5: Model Evidence Panel

> "Here are the verified performance metrics, loaded directly from the evaluation file
> in our repository. AUROC 0.757. Average Precision 0.467. F1 0.482. Brier Score 0.144.
>
> The ablation study shows that the Digital Twin personal baseline adds +1.3 AUROC
> points over static and dynamic features alone."

**Show:** Model Evidence tab. Open `data/processed/baseline_results.csv` side-by-side to
demonstrate that the displayed numbers are not hardcoded — they match the CSV.

---

## Safety Statement to Read On Camera

> "GlycoTwin is an experimental research prototype built for a hackathon.
> It has not been clinically validated and is not a medical device.
> The risk score is a statistical model estimate, not a diagnosis.
> It must not be used to make decisions about medication, insulin dosing,
> or any form of clinical care. The 20% risk threshold is a research operating point,
> not a clinically approved intervention threshold."
