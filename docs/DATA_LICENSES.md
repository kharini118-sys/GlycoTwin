# GlycoTwin — Data Licenses

---

## Dataset License

**Dataset:** CGMacros: a scientific dataset for personalized nutrition and diet monitoring
**Version:** 1.0.0
**Source:** https://physionet.org/content/cgmacros/1.0.0/
**License:** Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)
**License URL:** https://creativecommons.org/licenses/by-nc-sa/4.0/
**Access type:** Open access after accepting the PhysioNet data use agreement.

> **⚠️ IMPORTANT — Non-Commercial Use Only**
> The CGMacros dataset is licensed under **CC BY-NC-SA 4.0**, which:
> - **Prohibits commercial use** of the dataset or derivatives.
> - **Requires share-alike**: derivative works (including processed arrays and trained model
>   weights derived from this data) must be distributed under the same CC BY-NC-SA 4.0 license.
> - **Requires attribution**: proper credit to the authors is mandatory in any distribution.
>
> GlycoTwin is a non-commercial research prototype. Any commercial use of this project,
> the dataset, the processed arrays, or the trained model artifacts requires independent
> legal review and is likely not permitted without explicit permission from the dataset authors.

---

## Summary of CC BY-NC-SA 4.0 Requirements

You are free to:
- **Share** — copy and redistribute the material in any medium or format
- **Adapt** — remix, transform, and build upon the material

Under the following terms:
- **Attribution (BY)** — You must give appropriate credit, provide a link to the license, and indicate if changes were made.
- **NonCommercial (NC)** — You may not use the material for commercial purposes.
- **ShareAlike (SA)** — If you remix, transform, or build upon the material, you must distribute your contributions under the same CC BY-NC-SA 4.0 license.

---

## Required Dataset Attribution

> Das, A., Kerr, D., Glanz, N., Bevier, W., Santiago, R., Gutierrez-Osuna, R., & Mortazavi, B. (2025).
> CGMacros: a scientific dataset for personalized nutrition and diet monitoring (version 1.0.0).
> PhysioNet. https://doi.org/10.13026/3z8q-x658

BibTeX:
```bibtex
@article{PhysioNet-cgmacros-1.0.0,
  author = {Gutierrez-Osuna, Ricardo and Kerr, David and Mortazavi, Bobak and Das, Anurag},
  title  = {{CGMacros: a scientific dataset for personalized nutrition and diet monitoring}},
  journal = {{PhysioNet}},
  year   = {2025},
  month  = jan,
  note   = {Version 1.0.0},
  doi    = {10.13026/3z8q-x658},
  url    = {https://doi.org/10.13026/3z8q-x658}
}
```

---

## Source Code License

**License:** MIT License
**File:** `LICENSE`

The GlycoTwin **source code** (Python files, Streamlit app, scripts) is licensed under the MIT License.

**Important:** The MIT License applies **only** to original GlycoTwin source code files. It does not
override the CC BY-NC-SA 4.0 license of the underlying dataset or derivative works (processed arrays,
trained model weights) that were produced from that dataset.

---

## License Applicability by Artifact

| Artifact | Type | License | Excluded from repo? | Notes |
|---|---|---|---|---|
| `app/`, `src/`, `tests/`, `scripts/` | Original source code | MIT | No | Original authorship |
| `docs/`, `README.md`, `video/` | Documentation | MIT | No | Original content |
| `data/raw/cgmacros/CGMacros/` | Unmodified upstream data | **CC BY-NC-SA 4.0** | **YES — .gitignore** | Never commit; download from PhysioNet |
| `data/raw/CGMacros_dateshifted365.zip` | Unmodified upstream data | **CC BY-NC-SA 4.0** | **YES — .gitignore** | Source archive; never commit |
| `data/processed/X_sequence.npy` | Derived feature array | **CC BY-NC-SA 4.0** | **YES — .gitignore** | 137,581 × 12 × 4 windowed CGM/HR/METs sequences |
| `data/processed/X_sequence_processed.npy` | Derived feature array | **CC BY-NC-SA 4.0** | **YES — .gitignore** | Normalised version of X_sequence.npy |
| `data/processed/X_static.npy` | Derived feature array | **CC BY-NC-SA 4.0** | **YES — .gitignore** | 137,581 × 6 static EHR features per sample |
| `data/processed/X_static_processed.npy` | Derived feature array | **CC BY-NC-SA 4.0** | **YES — .gitignore** | Normalised version of X_static.npy |
| `data/processed/y.npy` | Derived labels | **CC BY-NC-SA 4.0** | **YES — .gitignore** | 137,581 binary excursion targets |
| `data/processed/subjects.npy` | Derived index | **CC BY-NC-SA 4.0** | **YES — .gitignore** | Participant ID per sample |
| `data/processed/train_mask.npy` | Derived index | **CC BY-NC-SA 4.0** | **YES — .gitignore** | Boolean split mask |
| `data/processed/val_mask.npy` | Derived index | **CC BY-NC-SA 4.0** | **YES — .gitignore** | Boolean split mask |
| `data/processed/test_mask.npy` | Derived index | **CC BY-NC-SA 4.0** | **YES — .gitignore** | Boolean split mask |
| `data/processed/metadata.csv` | Derived metadata | **CC BY-NC-SA 4.0** | **YES — .gitignore** | Subject ID + timestamp per sample; derived from CGMacros |
| `data/processed/participant_splits.csv` | Derived split manifest | **CC BY-NC-SA 4.0** | No (IDs only, no measurements) | Anonymised IDs + split assignment only |
| `data/processed/baseline_results.csv` | Aggregate evaluation metrics | **CC BY-NC-SA 4.0 (derived)** | No | Aggregate AUROC/F1 values; no individual records |
| `models/glycotwin_logistic.pkl` | Trained model | **⚠️ Likely CC BY-NC-SA 4.0** | **YES — .gitignore** | Base logistic regression; trained on CC BY-NC-SA data |
| `models/glycotwin_logistic_calibrated.pkl` | Trained model | **⚠️ Likely CC BY-NC-SA 4.0** | **YES — .gitignore** | Production model (Platt-calibrated); trained on CC BY-NC-SA data |
| `models/glycotwin_random_forest.pkl` | Trained model | **⚠️ Likely CC BY-NC-SA 4.0** | **YES — .gitignore** | 32 MB; Random Forest; trained on CC BY-NC-SA data |
| `models/glycotwin_gru.pt` | Trained model | **⚠️ Likely CC BY-NC-SA 4.0** | **YES — .gitignore** | GRU checkpoint; trained on CC BY-NC-SA data |
| `models/glycotwin_gru_corrected.pt` | Trained model | **⚠️ Likely CC BY-NC-SA 4.0** | **YES — .gitignore** | GRU checkpoint (corrected); trained on CC BY-NC-SA data |
| `models/glycotwin_gru_v2.pt` | Trained model | **⚠️ Likely CC BY-NC-SA 4.0** | **YES — .gitignore** | GRU checkpoint v2; trained on CC BY-NC-SA data |
| `models/sequence_means.npy` | Normalization statistics | **⚠️ Likely CC BY-NC-SA 4.0** | **YES — .gitignore** | Computed from CC BY-NC-SA training data |
| `models/sequence_medians.npy` | Normalization statistics | **⚠️ Likely CC BY-NC-SA 4.0** | **YES — .gitignore** | Computed from CC BY-NC-SA training data |
| `models/sequence_stds.npy` | Normalization statistics | **⚠️ Likely CC BY-NC-SA 4.0** | **YES — .gitignore** | Computed from CC BY-NC-SA training data |
| `models/static_means.npy` | Normalization statistics | **⚠️ Likely CC BY-NC-SA 4.0** | **YES — .gitignore** | Computed from CC BY-NC-SA training data |
| `models/static_medians.npy` | Normalization statistics | **⚠️ Likely CC BY-NC-SA 4.0** | **YES — .gitignore** | Computed from CC BY-NC-SA training data |
| `models/static_stds.npy` | Normalization statistics | **⚠️ Likely CC BY-NC-SA 4.0** | **YES — .gitignore** | Computed from CC BY-NC-SA training data |
| `models/ablation_results.csv` | Aggregate evaluation metrics | **CC BY-NC-SA 4.0 (derived)** | No | Aggregate metrics only; no individual records |
| `models/logistic_threshold_analysis.csv` | Aggregate evaluation metrics | **CC BY-NC-SA 4.0 (derived)** | No | Threshold sweep on held-out test set; aggregate counts |
| `presentation/GlycoTwin_Challenge_Submission.pptx` | Documentation | MIT (original content) | No | Cites dataset under CC BY-NC-SA 4.0 |
| `docs/GlycoTwin_Architecture.pdf` | Documentation | MIT (original content) | No | Architecture diagram; no dataset values |
| `instance/glycotwin.db` | Runtime user database | Private | **YES — .gitignore** | User accounts and workspaces; NEVER commit |

---

## Dependency Licenses

Key dependencies and their licenses:

| Package | License | Notes |
|---|---|---|
| scikit-learn | BSD 3-Clause | Model training and inference |
| pandas | BSD 3-Clause | Data processing |
| numpy | BSD 3-Clause | Numerical computation |
| streamlit | Apache 2.0 | Dashboard framework |
| plotly | MIT | Interactive charts |
| argon2-cffi | MIT | Password hashing |
| reportlab | BSD | PDF generation |
| python-pptx | MIT | PowerPoint generation |
| scipy | BSD 3-Clause | Statistical functions |
| joblib | BSD 3-Clause | Model serialization |
| pytest | MIT | Testing |

All dependency licenses are compatible with non-commercial use of this research prototype.

---

## Important Notices

1. **Raw data must not be committed to the public repository.** The CGMacros dataset must be
   downloaded separately from PhysioNet after accepting the data use agreement.

2. **Processed feature arrays are now excluded by `.gitignore` by default.** The arrays in
   `data/processed/*.npy` and `data/processed/metadata.csv` are derived from CC BY-NC-SA 4.0
   data and are large files (25+ MB each). They are gitignored to prevent accidental public
   redistribution. If you redistribute them, you must comply with CC BY-NC-SA 4.0 share-alike
   and attribution requirements.

3. **This is a non-commercial research prototype.** The CC BY-NC-SA 4.0 license prohibits
   commercial use. Any commercial application would require separate legal review and licensing.

4. **Share-alike obligation.** Derivative works and datasets produced from CGMacros
   (including processed arrays and trained model weights) must also be distributed under CC BY-NC-SA 4.0.

5. **Model artifacts** (`models/*.pkl`, `*.pt`, `*.npy`) are trained on or computed from
   CC BY-NC-SA 4.0 data. The share-alike clause likely extends to these artifacts. They are
   excluded from the repository by default. Verify with a qualified attorney before redistributing.

6. **Aggregate evaluation metrics** (`baseline_results.csv`, `ablation_results.csv`,
   `logistic_threshold_analysis.csv`) contain only summary statistics (AUROC, F1, confusion
   matrix counts). They do not reproduce individual participant records. These are included
   in the repository as they are standard scientific reporting artifacts, but they are still
   considered derived from CC BY-NC-SA 4.0 data.

7. **License verification.** The license shown above was verified directly from the PhysioNet
   dataset page at https://physionet.org/content/cgmacros/1.0.0/ on 2026-10-20.
   Re-verify before any public release, as PhysioNet dataset licenses can be updated.

---

> **⚠️ LEGAL DISCLAIMER:** The licensing analysis above is provided for informational purposes only
> and does not constitute legal advice. The application of CC BY-NC-SA 4.0 to trained machine
> learning models is an unsettled area of law. Consult a qualified attorney before any public
> redistribution of model artifacts or derived data, especially for purposes beyond academic
> research.
