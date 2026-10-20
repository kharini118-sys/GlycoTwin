# GlycoTwin — Final Submission Checklist

**Deadline:** 20 October 2026, 7:00 PM IST
**Team:** [INSERT TEAM NAME]
**Institution:** [INSERT COLLEGE / INCUBATOR]

---

## ✅ Completed (Ready)

### Source Code & Application
- [x] Working Streamlit application (`streamlit run app/dashboard.py`)
- [x] Landing page with branding and safety information
- [x] Account registration with Argon2id password hashing
- [x] Login with session management
- [x] Research disclaimer acknowledgement
- [x] Participant cohort selection
- [x] Digital Twin initialization from historical data
- [x] Five-minute step replay controls (step/jump/back/reset)
- [x] Real model inference at each replay step
- [x] Twin evolution timeline (actual model outputs, not heuristics)
- [x] Explanation panel (model-associated contributions)
- [x] Scenario simulator with 4 scenario types
- [x] Correct probability difference arithmetic (can increase or decrease)
- [x] PDF session report export (reportlab)
- [x] CSV session report export
- [x] EHR profile display with data provenance
- [x] Model evidence panel with verified metrics
- [x] Ablation study results
- [x] Workspace save/load/delete
- [x] User preferences persistence
- [x] Logout and session clearing

### Machine Learning
- [x] Target definition: ≥30 mg/dL rise / 120 min (no imputed future values)
- [x] Participant-level split: 31/7/7 (zero overlap)
- [x] Calibrated Logistic Regression model artifact
- [x] 24-feature vector (matches training exactly)
- [x] Verified test metrics: AUROC 0.757, AP 0.467, F1 0.482
- [x] Ablation study (4 configurations)
- [x] Model never retrains during dashboard use

### Digital Twin Engine
- [x] `src/twin/state.py` — TwinState dataclass
- [x] `src/twin/updater.py` — EMA baseline, momentum, confidence
- [x] `src/twin/feature_builder.py` — 24-feature builder
- [x] `src/twin/predictor.py` — Model loading and inference
- [x] No future data leakage in feature builder
- [x] No participant overlap between twin history and model training

### Database & Security
- [x] SQLite database (`instance/glycotwin.db`)
- [x] Users table with password hash (never plaintext)
- [x] User preferences table
- [x] Workspaces table with user_id foreign key
- [x] All workspace queries scoped to authenticated user
- [x] `instance/` excluded from Git

### Tests
- [x] 68 passed, 1 intentional skip (`python -m pytest tests/ -q`)
- [x] Auth tests (password hashing, registration, login, isolation)
- [x] Twin state tests (initialization, update, momentum, bounds)
- [x] Scenario tests (cloning, arithmetic, risk increase possible)
- [x] Predictor tests (model loading, probability range)
- [x] Split tests (zero participant overlap)
- [x] UTC timestamp tests (db write/read round-trip, no naive/aware mixing)
- [x] Data loader integration tests (bio.csv shape, schema, dtype, glucose not NaN)
- [x] Intentional skip: `test_skip_message_is_informative` fires only when raw dataset absent

### Documentation
- [x] `docs/INITIAL_AUDIT.md`
- [x] `docs/architecture.md` (with verified metrics)
- [x] `docs/model_card.md`
- [x] `docs/DATA_DICTIONARY.md`
- [x] `docs/DATA_PROVENANCE.md`
- [x] `docs/DATA_LICENSES.md`
- [x] `docs/SAFETY_AND_LIMITATIONS.md`
- [x] `docs/REPRODUCIBILITY.md`
- [x] `docs/ARTIFACT_PROVENANCE.md`
- [x] `video/20_minute_demo_script.md`

### Launch Files
- [x] `run_app.bat` — Windows launcher
- [x] `run_tests.bat` — Test runner
- [x] `requirements.txt` — Complete and pinned
- [x] `.gitignore` — Covers secrets, data, database, venv

---

## ⏳ Requires Participant Action

### Team Information (replace ALL placeholders)
- [ ] README.md Line 12: Team Leader Name
- [ ] README.md Line 13: Team Members
- [ ] README.md Line 14: College / Institute / Incubator
- [ ] README.md Line 15: Contact Email
- [ ] README.md Line 16: Contact Phone *(optional — only include if intended for submission)*
- [ ] README.md Line 18: GitHub Repository URL (once created and pushed)
- [ ] README.md Line 21: Video link (YouTube unlisted or Google Drive)
- [ ] Final Submission Checklist: Team name and institution above

### GitHub Repository
- [ ] Create a public GitHub repository named per challenge format
- [ ] Run `git init` in the project directory
- [ ] Run `git status` to verify no secrets or raw data are staged
- [ ] Run `git add .` (verify `.gitignore` excludes `data/raw/`, `instance/`, `.venv/`)
- [ ] Run `git commit -m "Initial GlycoTwin submission"`
- [ ] Create repository on GitHub.com (public)
- [ ] Run `git remote add origin <URL>`
- [ ] Run `git push -u origin main`
- [ ] Verify README renders correctly on GitHub
- [ ] Copy the repository URL to README.md

### Video Recording
- [ ] Install screen recording software (OBS Studio recommended, free)
- [ ] Start the application: `streamlit run app/dashboard.py`
- [ ] Follow the script in `video/20_minute_demo_script.md`
- [ ] Record a continuous video of at least 20 minutes
- [ ] Upload to YouTube (unlisted) or Google Drive
- [ ] Copy the video link to README.md

### Presentation (Slide Deck)
- [ ] Review `docs/architecture.md` for architecture diagrams
- [ ] Build a slide deck in PowerPoint or Google Slides using the script from `docs/presentation_slides.md`
- [ ] Ensure all metrics in slides match verified values (AUROC 0.757, not 0.92)
- [ ] Export as PDF
- [ ] Add links to README.md

### Final Check Before Submission
- [ ] Verify: `python -m pytest tests/ -q` → all pass
- [ ] Verify: `streamlit run app/dashboard.py` → landing page loads
- [ ] Verify: registration creates account
- [ ] Verify: login works
- [ ] Verify: participant loads and prediction appears
- [ ] Verify: replay controls step through observations
- [ ] Verify: scenario simulator runs
- [ ] Verify: PDF export downloads
- [ ] Verify: no treatment recommendations appear anywhere
- [ ] Verify: raw dataset NOT in git repository
- [ ] Verify: `instance/glycotwin.db` NOT in git repository

---

## ⚠️ Known Issues (Documented)

| Issue | Impact | Status |
|---|---|---|
| sklearn version mismatch (1.9.1 pickled, 1.7.2 installed) | Warning only, model works | Document in README |
| No email-based password recovery | Low security risk for prototype | Documented limitation |
| Small test set (7 participants) | Wide confidence intervals on metrics | Documented in model_card.md |
| NaN → 0 imputation | Not principled uncertainty | Documented in SAFETY_AND_LIMITATIONS.md |

---

## Submission Metadata

- **Challenge:** Happiest Health Digital Twin Challenge 2026
- **Submission Deadline:** 20 October 2026, 7:00 PM IST
- **Team Folder Name:** `[Team Name]_[College Name]`
- **License:** MIT (code) + CC BY-NC-SA 4.0 (dataset — non-commercial, share-alike)
- **Dataset:** PhysioNet CGMacros v1.0.0 (not committed to repo)
