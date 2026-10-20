# 🚀 GlycoTwin — CPU-First Deployment & Environment Blueprint

## Overview
GlycoTwin is architected for lightweight, CPU-first, memory-conscious execution on standard hardware (e.g., Intel i7, 16 GB RAM, Windows 11 / Linux / macOS).

---

## 💻 Hardware & Software Requirements
- **CPU**: Dual-core x86_64 CPU or higher (no GPU required).
- **RAM**: Minimum 4 GB RAM (8 GB recommended).
- **OS**: Windows 11, Ubuntu 20.04+, or macOS 12+.
- **Python Runtime**: Python 3.10 or 3.11.

---

## ⚡ Deployment & Startup Principles

### 1. Zero Model Retraining on App Startup
- The Streamlit web application loads pre-trained model artifacts (`models/glycotwin_logistic_calibrated.pkl`) directly.
- The app performs **zero fitting, training, or gradient steps** during user interaction or app launch, guaranteeing sub-second startup times.

### 2. Relative Path & Portable Environment Rules
- All file paths are constructed relative to `PROJECT_ROOT` using Python's `pathlib.Path`.
- No local absolute hard-coded user directory paths exist in the codebase.

### 3. Graceful Fallbacks for Missing Datasets
- If raw dataset files are absent, the application gracefully prompts the user with instructions to download **PhysioNet CGMacros v1.0.0** into `data/raw/cgmacros/CGMacros`.

---

## 🛠️ Step-by-Step Local Deployment Guide

### Step 1: Clone Repository & Set Up Virtual Environment
```bash
git clone https://github.com/TeamGlycoTwin/GlycoTwin.git
cd GlycoTwin

python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run CLI Verification Demo
```bash
python demo.py
```

### Step 4: Run Clinician UI Dashboard
```bash
streamlit run app/dashboard.py
```
The interface will open automatically in your browser at `http://localhost:8501`.
