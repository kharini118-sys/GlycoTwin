# GlycoTwin — 20-Minute Demo Video Script

**Event:** Happiest Health Digital Twin Challenge 2026
**Duration:** Minimum 20 minutes
**Format:** Screen recording with narration + slides
**Presenter:** [PARTICIPANT NAME] — to be recorded by the participant

---

## Shot List & Setup

Before recording:
1. Start the application: `streamlit run app/dashboard.py`
2. Open browser to http://localhost:8501
3. Have the landing page visible
4. Open a second browser tab for comparison (login with two users)
5. Ensure screen resolution is 1920×1080 or higher
6. Use a microphone with good audio quality
7. Close Slack, Teams, and other notification popups

---

## SEGMENT 1 — Introduction and Problem Statement (0:00 – 2:00)

**[Slide: Title slide with GlycoTwin wordmark]**

> "Welcome to GlycoTwin — a Personalized Bio-Digital Twin for Two-Hour Glucose Excursion Risk Prediction, built for the Happiest Health Digital Twin Challenge 2026.

> My name is [YOUR NAME], from [YOUR INSTITUTION].

> Over 101 million people in India live with Type 2 Diabetes. Current clinical workflows are reactive — glucose spikes are managed after they occur, not before.

> GlycoTwin transforms this into a proactive, predictive system. It maintains a continuously updated computational representation of a patient — their Digital Twin — and estimates the probability of a significant glucose rise in the next two hours.

> Crucially, this is a research prototype. It is not a diagnostic device and does not provide treatment recommendations."

---

## SEGMENT 2 — Dataset and Privacy (2:00 – 4:00)

**[Slide: Dataset slide]**
**[Screen: Show PhysioNet CGMacros page if internet is available]**

> "We built GlycoTwin on the PhysioNet CGMacros v1.0.0 dataset — an open-source, anonymized, and date-shifted continuous glucose monitoring dataset of 45 participants.

> The dataset provides five-minute CGM readings, heart rate, activity calories, METs, meal events, and static clinical data including age, BMI, HbA1c, and fasting glucose.

> We have not uploaded the raw dataset to our repository. The dataset is licensed under CC BY-NC-SA 4.0 — non-commercial use only, with share-alike obligations. Users must download it from PhysioNet directly after accepting the data use agreement.

> Our model was trained on 31 participants, calibrated on 7, and evaluated on a completely separate held-out set of 7 participants. There is zero participant overlap across splits."

---

## SEGMENT 3 — System Architecture (4:00 – 7:00)

**[Slide: Architecture diagram from docs/architecture.md]**

> "Let me walk through the GlycoTwin architecture.

> We fuse two data streams. Stream One is the static EHR profile — age, BMI, HbA1c, fasting glucose, and insulin. These come from the CGMacros bio.csv file.

> Stream Two is the dynamic wearable and CGM data — five-minute glucose readings, heart rate, activity calories, and METs.

> These two streams feed into the Digital Twin State Engine. The Twin maintains an exponentially updated personal glucose baseline, a glucose momentum estimate, an activity state, a cardiovascular state, and a data confidence score.

> This stateful representation is then used to build a 24-feature vector — the same feature vector that was used during model training.

> The feature vector is passed to a Calibrated Logistic Regression model — with Platt scaling for reliable probability estimates — which outputs the two-hour excursion risk probability.

> Finally, this probability is displayed in the clinician dashboard, updated with every new five-minute observation."

---

## SEGMENT 4 — Target Definition, Model Training, Evaluation (7:00 – 10:00)

**[Slide: ML methodology slide]**
**[Screen: Show models/ablation_results.csv and data/processed/baseline_results.csv]**

> "The prediction target is defined as: the maximum observed glucose in the next 120 minutes is at least 30 milligrams per deciliter above the current glucose level.

> This is a dataset-specific research endpoint. We used only actual observed glucose values for the target — no forward-filled or imputed values.

> We evaluated three model architectures: Logistic Regression, Random Forest, and a small GRU neural network.

> On the held-out test set of seven participants, the Calibrated Logistic Regression achieves an AUROC of 0.757, average precision of 0.467, and an F1 score of 0.482 at our research operating threshold of 20%.

> Our ablation study shows clear value from each component. Static features alone give an AUROC of 0.608. Adding dynamic wearable data improves it to 0.729. Adding the personalized Digital Twin baseline further improves it to 0.742 — validating the core Digital Twin concept.

> The 20% operating threshold is a research choice selected on the validation set. It is not a clinically validated decision boundary."

---

## SEGMENT 5 — Account Creation, Login, Workspace (10:00 – 13:00)

**[Screen: Show the running application at landing page]**

> "Let me now walk through the working application.

> This is the GlycoTwin landing page. It explains the system, shows the architecture, and clearly states that this is a research prototype, not a diagnostic device.

> I'll click 'Create Account' to register."

**[Action: Click Create Account → fill in name, email, password, accept terms → submit]**

> "The registration screen collects a display name, email, institution, and role. Passwords are hashed using Argon2id before storage — the plaintext password is never stored.

> I've filled in my details. I acknowledge the research disclaimer and click Create Account."

**[Action: Login with new credentials]**

> "Now I'll log in. The system verifies my password against the stored hash.

> I'm now authenticated. Notice the portal bar shows my name and role. The session state never contains the password hash.

> Let me save a workspace before selecting a participant."

**[Action: Enter workspace name → Save Workspace]**

> "I can save named research workspaces that persist across sessions. These are scoped to my user account — another user cannot access them."

---

## SEGMENT 6 — Dashboard: Participant Selection and Twin Initialization (13:00 – 17:00)

**[Screen: Sidebar participant selection]**

> "In the sidebar, I can filter participants by HbA1c-based cohort. Note: this is a research grouping, not a clinical diagnosis.

> I'll select CGMacros participant with a HbA1c in the Type 2 diabetes range."

**[Action: Select a participant from the T2D cohort]**

> "The Twin is initialized by replaying all historical observations for this participant. Watch how the metrics update.

> In Tab 1 — Twin Overview — I can see the current glucose, the personal baseline computed from past glucose history, the two-hour risk estimate from the actual saved model, and the sensor confidence score.

> The explanation panel shows why the model is estimating this probability: the glucose deviation from the baseline, the glucose momentum, the activity state, and the data completeness."

**[Screen: Show Tab 4 — Replay Controls]**

> "Tab 4 shows the CGM stream replay. I can step forward one observation at a time, jump twelve observations forward — representing one hour — or reset to the beginning.

> Each step rebuilds the Twin from history and runs inference again. Watch how the risk probability changes as new glucose observations arrive."

**[Action: Click Step Forward 3-4 times, show probability changing]**

> "Tab 2 is the Scenario Simulator."

**[Screen: Tab 2 — Scenario Simulator]**

> "I can select a scenario type — for example, increased physical activity — and set an intensity level. When I click Run Scenario, the system clones the current Twin state, applies a feature-space perturbation, and runs the exact same inference pipeline.

> The result shows the baseline probability, the scenario probability, and the difference in percentage points. Notice that risk can increase or decrease — we never force it in either direction.

> This is clearly labeled as a hypothetical estimate. The assumptions and limitations are displayed below."

**[Action: Run a scenario and show results]**

---

## SEGMENT 7 — Model Evidence, Limitations, and Safety (17:00 – 19:00)

**[Screen: Tab 5 — Model Evidence]**

> "Tab 5 shows the full model evidence panel. All metrics here are loaded from the actual evaluation files — they are never hardcoded.

> Test AUROC: 0.757. Average Precision: 0.467. F1: 0.482. Brier Score: 0.144.

> The ablation chart shows how each feature group contributes to performance.

> I want to highlight the known limitations. The test set has only seven participants — confidence intervals are wide. The 20% threshold is a research choice. Missing sensor values are handled with simple zero imputation, not principled uncertainty. No external validation has been performed.

> GlycoTwin generates no treatment recommendations anywhere in the interface."

**[Screen: EHR Profile tab]**

> "Tab 3 shows the static EHR profile from the dataset. We display the cohort classification with a clear disclaimer that this is a research grouping, not a clinical diagnosis."

---

## SEGMENT 8 — Export and Workspace Persistence (18:30 – 19:30)

**[Screen: Export section in Tab 1]**

> "I can export a PDF research session report. This includes the participant's anonymized dataset ID, twin state snapshots, model estimates, and the research disclaimer. It explicitly labels any scenario outputs as hypothetical.

> I can also export as CSV for further analysis.

> If I log out and log back in, my saved workspace is restored. Let me demonstrate."

**[Action: Logout → Login → Reopen workspace]**

---

## SEGMENT 9 — Conclusion and Future Work (19:30 – 21:00)

**[Slide: Conclusion slide]**

> "GlycoTwin demonstrates a genuine digital twin update loop: each new five-minute observation updates the Twin's computational state and triggers a fresh model inference.

> We validated this approach on a public CGM dataset with a patient-level split, achieving an AUROC of 0.757 on a held-out test set.

> Our ablation study shows that the personalized baseline — the core of the Digital Twin concept — adds measurable predictive value over static and dynamic features alone.

> Future development would include: external validation on independent cohorts, integration with real-time wearable APIs, more sophisticated uncertainty quantification, and clinical partnership for prospective evaluation.

> Thank you. The complete source code, documentation, model card, and data provenance are available in our repository. The dataset used is PhysioNet CGMacros v1.0.0, licensed under CC BY-NC-SA 4.0 — non-commercial research use only."

---

## Recording Checklist

Before publishing the video:
- [ ] All metrics mentioned match the verified values in `data/processed/baseline_results.csv`
- [ ] No fabricated clinical affiliations or endorsements are mentioned
- [ ] The 20% threshold is described as a research choice, not a clinical decision
- [ ] Scenario outputs are introduced as hypothetical, not causal
- [ ] No treatment recommendations are made
- [ ] Team and institution details are accurate
- [ ] Video is at least 20 minutes in duration
- [ ] Audio is clear and narration matches screen actions
- [ ] Upload to YouTube (unlisted) or Google Drive and copy the link to README.md
