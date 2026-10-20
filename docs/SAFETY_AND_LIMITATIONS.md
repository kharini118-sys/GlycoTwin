# GlycoTwin — Safety and Limitations

> **This document is mandatory reading before using GlycoTwin for any purpose beyond a software demonstration.**

---

## Research Prototype Status

GlycoTwin is a **proof-of-concept research prototype** built for the Happiest Health Digital Twin Challenge 2026.

It is:
- A demonstration of data fusion, stateful digital twin concepts, and machine learning applied to CGM data
- Evaluated on a small, open-source research dataset
- Intended for educational and research purposes only

It is NOT:
- A medical device
- A diagnostic tool
- Clinically validated
- Approved by any regulatory body (FDA, CE, CDSCO, or equivalent)
- A substitute for clinical judgment

---

## Dataset Limitations

| Limitation | Detail |
|---|---|
| Small sample size | 45 participants total; 7 in the held-out test set |
| Single study | All data from one research cohort (CGMacros) |
| No external validation | Performance on other populations is unknown |
| Date-shifted timestamps | Actual clinical dates are not available |
| Missing sensors | Heart rate, activity, and METs have high missingness rates |
| Population | Study participants are not a representative clinical population |
| Geography | Dataset origin and population demographics not fully documented |

---

## Model Limitations

| Limitation | Detail |
|---|---|
| AUROC 0.757 | This is the test set performance; real-world performance could be lower |
| High recall, low precision | At 20% threshold: recall 0.730, precision 0.360 — many false positives |
| Threshold is arbitrary | 20% was selected on validation data as a research operating point |
| No prospective validation | Model has not been tested on prospective real-world glucose data |
| NaN imputation | Missing sensor values imputed with zeros, not with principled imputation |
| Calibration | Platt scaling calibrated on 7-participant validation set |
| sklearn version | Model pickled with sklearn 1.9.1; minor version mismatch warnings may appear |
| No temporal CV | Evaluation uses participant-level split, not temporal cross-validation |

---

## Target Definition Limitations

The target is:

> Maximum observed glucose in the next 120 minutes ≥ current glucose + 30 mg/dL

- This is a dataset-specific research endpoint, not a universal clinical excursion definition
- It does not correspond to any specific clinical glycemic guideline
- Rows with insufficient future glucose coverage are excluded, not labeled negative
- The cutoff of 30 mg/dL was chosen as a representative threshold for this prototype

---

## Cohort Classification Limitations

HbA1c-based cohort grouping in the application:

- **≥6.5%** is labeled "T2D range" — this is a research grouping, NOT a Type 2 Diabetes diagnosis
- **5.7–6.4%** is labeled "Pre-DM range" — this is a research grouping, NOT a pre-diabetes diagnosis
- Clinical diagnosis requires physical examination, symptom assessment, and multiple confirmatory tests
- Never use this application's cohort labels to infer a patient's clinical status

---

## Operating Threshold Limitations

The 20% risk threshold:

- Was selected by examining the validation set precision-recall curve
- Is NOT a clinically validated decision boundary
- Does NOT mean that a probability below 20% indicates clinical safety
- Does NOT mean that a probability above 20% indicates clinical danger
- May produce many false positive classifications in practice

---

## Scenario Simulator Limitations

The scenario simulator:

- Applies feature-space perturbations to the model input vector
- Does **not** model physiology, pharmacokinetics, or dietary absorption
- Is **not** a causal counterfactual model
- Risk can **increase** or **decrease** under any scenario
- Results are **not** dietary or exercise recommendations
- A simulated decrease in risk under a scenario is not an endorsement of that behavior
- A simulated increase in risk is not a contraindication

---

## Authentication Limitations

The local authentication system:

- Uses Argon2id password hashing (secure for prototype use)
- Is stored in a local SQLite file (`instance/glycotwin.db`)
- Is NOT suitable for production multi-user deployment
- Does NOT provide network security, HTTPS, or rate limiting
- Does NOT implement production session signing or multi-device identity
- Password recovery is not available without database administrator access

**For production deployment:** Replace with a hardened identity provider, implement HTTPS, add rate limiting, and use a production database.

---

## Safety Prohibitions

The following actions are **prohibited** when using this application:

1. Using any output to change insulin dosing, medication, or clinical management
2. Presenting model outputs to a patient as a medical assessment
3. Using this application in lieu of a clinical consultation
4. Inferring that a low probability estimate means a patient is safe
5. Inferring that a high probability estimate requires clinical intervention
6. Presenting scenario outputs as causal clinical predictions
7. Using this application on identifiable patient data

---

## Required Future Work Before Clinical Use

Any clinical application of this approach would require:

1. Prospective validation on an independent patient population
2. Regulatory review and approval (CDSCO in India; FDA in USA; CE in EU)
3. Clinical validation study with appropriate endpoints
4. Hardened data security and patient privacy infrastructure
5. Integration with certified medical device data streams
6. Peer-reviewed publication of methodology and results
7. Informed consent framework
8. Adverse event monitoring and post-market surveillance

---

*This document must be included in any distribution of GlycoTwin or derived works.*
