"""
GlycoTwin — Main Streamlit Application
Personalized Bio-Digital Twin for 2-Hour Glucose Excursion Risk Prediction
Happiest Health Digital Twin Challenge 2026

Entry point: streamlit run app/dashboard.py
"""

from pathlib import Path
import sys
import copy
import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# ── Project path ──────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ── Page config MUST be first Streamlit call ──────────────────────────────────
st.set_page_config(
    page_title="GlycoTwin — Digital Bio-Twin Platform",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── GlycoTwin imports ─────────────────────────────────────────────────────────
try:
    from src.data.load_cgmacros import load_all_participants
    from src.data.clean_cgmacros import clean_cgmacros
    from src.twin import TwinState, GlycoTwinPredictor, update_twin
    from src.database.db import init_db, get_workspaces, create_workspace, get_workspace, update_workspace, delete_workspace
    from app.auth import register_user, authenticate_user, get_user_preferences, save_user_preferences
    from src.simulation.scenario import run_scenario, SCENARIOS
    from src.simulation.export import generate_pdf_report, generate_csv_report
    MODULES_OK = True
    MODULE_ERROR = None
except Exception as exc:
    MODULES_OK = False
    MODULE_ERROR = str(exc)

# Initialize DB
if MODULES_OK:
    try:
        init_db()
    except Exception:
        pass

# ── VERIFIED MODEL METRICS (from data/processed/baseline_results.csv) ─────────
VERIFIED_METRICS = {
    "auroc": 0.7566,
    "average_precision": 0.4666,
    "precision": 0.3597,
    "recall": 0.7305,
    "f1": 0.4820,
    "brier_score": 0.1439,
    "val_auroc": 0.7295,
    "val_ap": 0.4070,
}

ABLATION_DATA = [
    {"Feature Configuration": "Static EHR Only", "Test AUROC": 0.608, "Test AP": 0.266, "Test F1": 0.381},
    {"Feature Configuration": "Dynamic Wearable Only", "Test AUROC": 0.646, "Test AP": 0.335, "Test F1": 0.396},
    {"Feature Configuration": "Static + Dynamic", "Test AUROC": 0.729, "Test AP": 0.429, "Test F1": 0.467},
    {"Feature Configuration": "Static + Dynamic + Personal Baseline ✓", "Test AUROC": 0.742, "Test AP": 0.441, "Test F1": 0.479},
]

# ── CSS Styling ───────────────────────────────────────────────────────────────
GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }

.stApp {
    background: linear-gradient(135deg, #0a0f1e 0%, #0d1627 50%, #0a0f1e 100%);
    color: #e2e8f0;
}

/* Landing page */
.gt-landing-hero {
    background: linear-gradient(135deg, rgba(13,30,60,0.95) 0%, rgba(6,20,45,0.98) 100%);
    border: 1px solid rgba(20,184,166,0.3);
    border-radius: 20px;
    padding: 3rem 2.5rem;
    text-align: center;
    margin-bottom: 2rem;
    box-shadow: 0 25px 50px -12px rgba(0,0,0,0.6), 0 0 40px rgba(20,184,166,0.08);
}

.gt-wordmark {
    font-size: 3.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #2dd4bf 0%, #38bdf8 50%, #818cf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -2px;
    line-height: 1.1;
    margin-bottom: 0.5rem;
}

.gt-tagline {
    font-size: 1.15rem;
    color: #94a3b8;
    margin-bottom: 1.5rem;
    font-weight: 400;
}

.gt-challenge-badge {
    display: inline-block;
    background: linear-gradient(90deg, rgba(20,184,166,0.2), rgba(56,189,248,0.2));
    border: 1px solid rgba(20,184,166,0.5);
    border-radius: 50px;
    padding: 0.4rem 1.2rem;
    font-size: 0.85rem;
    color: #2dd4bf;
    font-weight: 600;
    margin-bottom: 2rem;
    letter-spacing: 0.05em;
}

/* Auth cards */
.gt-auth-card {
    background: rgba(15,23,42,0.9);
    border: 1px solid rgba(20,184,166,0.2);
    border-radius: 16px;
    padding: 2.5rem;
    box-shadow: 0 20px 40px -10px rgba(0,0,0,0.5);
    max-width: 480px;
    margin: 0 auto;
}

.gt-auth-title {
    font-size: 1.8rem;
    font-weight: 700;
    color: #f8fafc;
    margin-bottom: 0.3rem;
}

.gt-auth-subtitle {
    color: #64748b;
    font-size: 0.9rem;
    margin-bottom: 2rem;
}

/* Dashboard portal bar */
.gt-portal-bar {
    background: linear-gradient(90deg, rgba(15,23,42,0.95) 0%, rgba(13,17,30,0.98) 100%);
    border: 1px solid rgba(20,184,166,0.25);
    border-radius: 12px;
    padding: 0.8rem 1.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.2rem;
    backdrop-filter: blur(10px);
}

.gt-portal-left { display: flex; align-items: center; gap: 1rem; }
.gt-portal-brand { font-size: 1.1rem; font-weight: 700; color: #2dd4bf; }
.gt-portal-user { font-size: 0.85rem; color: #94a3b8; }
.gt-portal-right { display: flex; align-items: center; gap: 1rem; }

/* Metric cards */
.gt-metric-card {
    background: rgba(15,23,42,0.7);
    border: 1px solid rgba(51,65,85,0.8);
    border-radius: 12px;
    padding: 1.2rem;
    text-align: center;
    transition: border-color 0.2s;
}

.gt-metric-card:hover { border-color: rgba(20,184,166,0.5); }
.gt-metric-value { font-size: 2rem; font-weight: 700; color: #f8fafc; line-height: 1.2; }
.gt-metric-label { font-size: 0.75rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 0.3rem; }
.gt-metric-delta { font-size: 0.85rem; margin-top: 0.2rem; }
.gt-metric-delta.up { color: #f87171; }
.gt-metric-delta.down { color: #34d399; }
.gt-metric-delta.neutral { color: #94a3b8; }

/* Risk gauge */
.gt-risk-elevated {
    background: linear-gradient(135deg, rgba(239,68,68,0.15), rgba(220,38,38,0.1));
    border: 1px solid rgba(239,68,68,0.4);
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
}
.gt-risk-normal {
    background: linear-gradient(135deg, rgba(16,185,129,0.12), rgba(5,150,105,0.08));
    border: 1px solid rgba(16,185,129,0.35);
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
}

/* Twin state panel */
.gt-state-panel {
    background: rgba(15,23,42,0.6);
    border: 1px solid rgba(51,65,85,0.6);
    border-radius: 12px;
    padding: 1.2rem;
}

.gt-state-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.4rem 0;
    border-bottom: 1px solid rgba(51,65,85,0.4);
    font-size: 0.9rem;
}
.gt-state-row:last-child { border-bottom: none; }
.gt-state-key { color: #94a3b8; }
.gt-state-val { color: #e2e8f0; font-weight: 600; }

/* Scenario panel */
.gt-scenario-hypothetical {
    background: repeating-linear-gradient(
        45deg,
        rgba(251,191,36,0.05),
        rgba(251,191,36,0.05) 4px,
        transparent 4px,
        transparent 16px
    );
    border: 2px dashed rgba(251,191,36,0.4);
    border-radius: 12px;
    padding: 1.2rem;
}

/* Badges */
.gt-badge {
    display: inline-block;
    padding: 0.2rem 0.65rem;
    border-radius: 50px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.03em;
}
.gt-badge-replay { background: rgba(16,185,129,0.2); color: #34d399; border: 1px solid #10b981; }
.gt-badge-research { background: rgba(99,102,241,0.2); color: #a5b4fc; border: 1px solid #6366f1; }
.gt-badge-warning { background: rgba(245,158,11,0.2); color: #fbbf24; border: 1px solid #f59e0b; }
.gt-badge-hypo { background: rgba(251,191,36,0.15); color: #fcd34d; border: 1px dashed #f59e0b; }

/* Feature cards on landing */
.gt-feature-card {
    background: rgba(15,23,42,0.7);
    border: 1px solid rgba(51,65,85,0.6);
    border-radius: 12px;
    padding: 1.5rem;
    height: 100%;
    transition: border-color 0.2s, transform 0.2s;
}
.gt-feature-card:hover {
    border-color: rgba(20,184,166,0.4);
    transform: translateY(-2px);
}
.gt-feature-icon { font-size: 2rem; margin-bottom: 0.5rem; }
.gt-feature-title { font-weight: 700; color: #f1f5f9; margin-bottom: 0.4rem; font-size: 1rem; }
.gt-feature-desc { color: #94a3b8; font-size: 0.88rem; line-height: 1.5; }

/* Research disclaimer bar */
.gt-disclaimer-bar {
    background: rgba(239,68,68,0.08);
    border: 1px solid rgba(239,68,68,0.25);
    border-radius: 8px;
    padding: 0.6rem 1rem;
    font-size: 0.8rem;
    color: #fca5a5;
    margin: 0.8rem 0;
}

/* Architecture diagram */
.gt-arch-box {
    background: rgba(15,23,42,0.8);
    border: 1px solid rgba(20,184,166,0.3);
    border-radius: 8px;
    padding: 0.8rem 1rem;
    text-align: center;
    font-size: 0.85rem;
    color: #e2e8f0;
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background: rgba(10,15,30,0.95) !important;
    border-right: 1px solid rgba(20,184,166,0.15) !important;
}

/* Button overrides */
.stButton > button {
    background: linear-gradient(135deg, #0d9488, #0891b2) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.9 !important; }

/* Hide streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""


# ─────────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def find_column(df, candidates):
    if df is None or df.empty:
        return None
    columns = list(df.columns)
    for c in candidates:
        if c in columns:
            return c
    def norm(v):
        return str(v).strip().lower().replace(" ", "_").replace("-", "_").replace("/", "_")
    normalized = {norm(col): col for col in columns}
    for c in candidates:
        k = norm(c)
        if k in normalized:
            return normalized[k]
    return None


def standardize_dataframe(df):
    if df is None:
        raise ValueError("CGMacros loader returned None.")
    if isinstance(df, (list, tuple)):
        frames = [x for x in df if isinstance(x, pd.DataFrame) and not x.empty]
        if not frames:
            raise ValueError("CGMacros loader returned no dataframe.")
        df = pd.concat(frames, ignore_index=True)
    df = df.copy()

    subject_col = find_column(df, ["subject_id", "subject", "participant_id", "patient_id"])
    if subject_col is None:
        raise ValueError(f"No participant column. Available: {list(df.columns)}")
    if subject_col != "subject_id":
        df["subject_id"] = df[subject_col]

    timestamp_col = find_column(df, ["timestamp", "datetime", "date_time", "date", "time", "Timestamp"])
    if timestamp_col is None:
        raise ValueError(f"No timestamp column. Available: {list(df.columns)}")
    if timestamp_col != "timestamp":
        df["timestamp"] = df[timestamp_col]
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    glucose_col = find_column(df, [
        "glucose", "blood_glucose", "sensor_glucose", "cgm_glucose",
        "libre_gl", "libre gl", "Libre GL", "dexcom_gl", "dexcom gl",
        "glucose_value", "dexcom_glucose",
    ])
    if glucose_col is None:
        raise ValueError(f"No glucose column. Available: {list(df.columns)}")
    if glucose_col != "glucose":
        df["glucose"] = df[glucose_col]
    df["glucose"] = pd.to_numeric(df["glucose"], errors="coerce")

    optional_columns = {
        "heart_rate": ["heart_rate", "heartrate", "hr", "heart_rate_bpm", "HR"],
        "activity_calories": ["activity_calories", "activity_calorie", "calories (activity)",
                               "Calories (Activity)", "calories", "active_calories"],
        "mets": ["mets", "met", "metabolic_equivalent", "METs"],
        "hba1c": ["hba1c", "hba1c_percent", "a1c", "A1c PDL (Lab)"],
        "age": ["age", "Age"],
        "bmi": ["bmi", "BMI", "body_mass_index"],
        "fasting_glucose": ["fasting_glucose", "Fasting GLU - PDL (Lab)"],
        "insulin": ["insulin", "Insulin ", "fasting_insulin"],
    }
    for target, candidates in optional_columns.items():
        col = find_column(df, candidates)
        if col is None:
            df[target] = np.nan
        else:
            df[target] = pd.to_numeric(df[col], errors="coerce")

    df = (df.dropna(subset=["subject_id", "timestamp"])
            .sort_values(["subject_id", "timestamp"])
            .reset_index(drop=True))
    return df


@st.cache_data(show_spinner="Loading PhysioNet CGMacros dataset...")
def load_dashboard_data():
    raw_df = load_all_participants()
    try:
        df = clean_cgmacros(raw_df)
    except Exception:
        df = raw_df
    return standardize_dataframe(df)


def get_profile(df_patient):
    defaults = {
        "age": 51.0, "bmi": 30.0, "hba1c": 6.5,
        "fasting_glucose": 110.0, "insulin": 12.0,
    }
    profile = {}
    for feat, default in defaults.items():
        vals = pd.to_numeric(df_patient.get(feat, pd.Series(dtype=float)), errors="coerce").dropna()
        profile[feat] = float(vals.iloc[-1]) if len(vals) > 0 else default

    glucose = pd.to_numeric(df_patient["glucose"], errors="coerce").dropna()
    if len(glucose) >= 5:
        profile["personal_baseline"] = float(glucose.median())
    else:
        profile["personal_baseline"] = 100.0
    return profile


def build_twin_from_history(df_patient, profile):
    """
    Build a TwinState by replaying each historical observation in sequence.
    This is how the Twin update loop is demonstrated.
    """
    patient = df_patient.sort_values("timestamp").reset_index(drop=True)
    twin = TwinState(patient_id=str(patient["subject_id"].iloc[0]))

    for _, row in patient.iterrows():
        obs = {
            "timestamp": str(row["timestamp"]),
            "glucose": row.get("glucose") if pd.notna(row.get("glucose")) else None,
            "heart_rate": row.get("heart_rate") if pd.notna(row.get("heart_rate")) else None,
            "activity_calories": row.get("activity_calories") if pd.notna(row.get("activity_calories")) else None,
            "mets": row.get("mets") if pd.notna(row.get("mets")) else None,
        }
        twin = update_twin(twin, obs)
    return twin


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE INITIALIZATION
# ─────────────────────────────────────────────────────────────────────────────

def _init_session():
    defaults = {
        "authenticated": False,
        "user": None,
        "page": "landing",
        "replay_index": 0,
        "replay_running": False,
        "replay_history": [],
        "active_workspace_id": None,
        "last_predictor": None,
        "last_participant": None,
        "last_twin": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_session()


# ─────────────────────────────────────────────────────────────────────────────
# INJECT GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE ROUTER
# ─────────────────────────────────────────────────────────────────────────────

def goto(page: str):
    st.session_state["page"] = page
    st.rerun()


def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    _init_session()
    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: LANDING
# ─────────────────────────────────────────────────────────────────────────────

def page_landing():
    st.markdown("""
    <div class="gt-landing-hero">
        <div class="gt-wordmark">🧬 GlycoTwin</div>
        <div class="gt-tagline">
            Personalized Bio-Digital Twin for Two-Hour Glucose Excursion Risk Prediction
        </div>
        <div class="gt-challenge-badge">
            🏆 Happiest Health Digital Twin Challenge 2026
        </div>
        <br>
        <div style="color:#64748b; font-size:0.9rem; max-width:600px; margin:0 auto;">
            GlycoTwin is a <strong style="color:#2dd4bf;">research prototype</strong> combining
            static clinical data with dynamic CGM and wearable time-series to maintain a
            continuously updated patient-specific computational representation —
            the Digital Twin — and estimate the probability of a significant
            glucose excursion in the next 120 minutes.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="gt-disclaimer-bar">
        ⚠️ <strong>Research prototype only.</strong> Not a diagnostic device.
        Not clinically validated. Not a treatment recommendation.
        Evaluate results in conjunction with qualified clinical judgment.
    </div>
    """, unsafe_allow_html=True)

    # Feature cards
    c1, c2, c3, c4 = st.columns(4)
    features = [
        ("⚡", "Live Twin Update Loop", "Each new observation updates a stateful patient-specific model. Watch risk probability change in real time."),
        ("🔬", "Multimodal Data Fusion", "Fuses static EHR (age, BMI, HbA1c) with dynamic CGM, heart rate, and activity data."),
        ("🧪", "Scenario Simulator", "Explore model-projected outcomes under hypothetical feature changes. Risk can increase or decrease."),
        ("🛡️", "Transparent Evidence", "Real evaluation metrics, ablation results, and calibration from a patient-level split."),
    ]
    for col, (icon, title, desc) in zip([c1, c2, c3, c4], features):
        with col:
            st.markdown(f"""
            <div class="gt-feature-card">
                <div class="gt-feature-icon">{icon}</div>
                <div class="gt-feature-title">{title}</div>
                <div class="gt-feature-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Architecture overview
    with st.expander("🏗️ System Architecture Overview", expanded=False):
        st.code("""
Static Clinical Profile (EHR)         Dynamic Observations (CGM / Wearable)
  Age, BMI, HbA1c, Fasting Glucose       5-min Glucose, Heart Rate, Activity, METs
          |                                              |
          └──────────────────┬────────────────────────┘
                             ↓
                  ┌─────────────────────┐
                  │  Validation &       │
                  │  Preprocessing      │
                  └──────────┬──────────┘
                             ↓
                  ┌─────────────────────┐
                  │  Stateful Digital   │   ← Personal Baseline (EMA)
                  │  Twin State Engine  │   ← Glucose Momentum
                  └──────────┬──────────┘   ← Data Confidence Score
                             ↓
                  ┌─────────────────────┐
                  │  Training-consistent│
                  │  Feature Builder    │   24-feature vector
                  └──────────┬──────────┘
                             ↓
                  ┌─────────────────────┐
                  │  Calibrated ML      │   Logistic Regression
                  │  Predictor          │   Test AUROC: 0.757
                  └──────────┬──────────┘
                             ↓
                  2-Hr Glucose Excursion Probability
                             ↓
                  ┌─────────────────────────────────┐
                  │  Clinician Dashboard              │
                  │  Replay | Scenario | Export       │
                  └─────────────────────────────────┘
        """, language="text")

    st.markdown("<br>", unsafe_allow_html=True)

    # Data and safety section
    da_col, sa_col = st.columns(2)
    with da_col:
        st.markdown("#### 📦 Dataset & Provenance")
        st.markdown("""
        - **Source:** PhysioNet CGMacros v1.0.0
        - **Participants:** 45 anonymized individuals
        - **Temporal resolution:** ~5-minute CGM intervals
        - **License:** [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) — non-commercial, share-alike
        - Raw data is **not** distributed in this repository
        - All date-shifted to protect privacy
        """)
    with sa_col:
        st.markdown("#### ⚕️ Safety & Limitations")
        st.markdown("""
        - Not for clinical use without validation
        - 20% threshold is a research operating point
        - Dataset-based cohort grouping ≠ clinical diagnosis
        - Model not validated on external populations
        - Scenario results are not causal predictions
        """)

    st.markdown("---")
    b1, b2, b3 = st.columns([1, 1, 1])
    with b1:
        if st.button("🚀 Create Account", use_container_width=True):
            goto("register")
    with b2:
        if st.button("🔑 Login", use_container_width=True):
            goto("login")
    with b3:
        if st.button("👁️ Demo Access", use_container_width=True):
            # Demo login with guest account
            st.session_state["authenticated"] = True
            st.session_state["user"] = {
                "id": 0,
                "display_name": "Demo User",
                "email": "demo@glycotwin.local",
                "role": "researcher",
                "institution": "Demo",
            }
            goto("dashboard")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: REGISTER
# ─────────────────────────────────────────────────────────────────────────────

def page_register():
    if not MODULES_OK:
        st.error(f"Module load error: {MODULE_ERROR}")
        return

    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.markdown("""
        <div class="gt-auth-card">
            <div class="gt-auth-title">Create Account</div>
            <div class="gt-auth-subtitle">Join the GlycoTwin Research Platform</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")

        with st.form("register_form", clear_on_submit=False):
            display_name = st.text_input("Full Name *", placeholder="Your full name")
            email = st.text_input("Email Address *", placeholder="you@institution.edu")
            institution = st.text_input("Institution (optional)", placeholder="University or organization")
            role = st.selectbox(
                "Role *",
                ["Student / Researcher", "Clinician (Demo)"],
                help="For demo and research purposes only. No clinical use.",
            )
            password = st.text_input("Password *", type="password",
                                     help="Min 8 chars, one uppercase, one digit")
            confirm_password = st.text_input("Confirm Password *", type="password")
            terms = st.checkbox(
                "I acknowledge this is a research prototype, not a clinical device, "
                "and I will not use it for medical decisions."
            )

            submitted = st.form_submit_button("Create Account", use_container_width=True)

            if submitted:
                if not terms:
                    st.error("You must acknowledge the research disclaimer to proceed.")
                else:
                    role_map = {"Student / Researcher": "researcher", "Clinician (Demo)": "clinician_demo"}
                    ok, msg, user_id = register_user(
                        display_name=display_name,
                        email=email,
                        password=password,
                        confirm_password=confirm_password,
                        role=role_map.get(role, "researcher"),
                        institution=institution,
                    )
                    if ok:
                        st.success(f"✅ {msg} Please log in.")
                        st.session_state["reg_success"] = True
                    else:
                        st.error(f"❌ {msg}")

        if st.session_state.get("reg_success"):
            if st.button("Proceed to Login"):
                st.session_state.pop("reg_success", None)
                goto("login")

        st.markdown("---")
        if st.button("← Back to Home"):
            goto("landing")
        if st.button("Already have an account? Login"):
            goto("login")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: LOGIN
# ─────────────────────────────────────────────────────────────────────────────

def page_login():
    if not MODULES_OK:
        st.error(f"Module load error: {MODULE_ERROR}")
        return

    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.markdown("""
        <div class="gt-auth-card">
            <div class="gt-auth-title">🧬 GlycoTwin</div>
            <div class="gt-auth-subtitle">Research Platform Login</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")

        with st.form("login_form"):
            email = st.text_input("Email Address", placeholder="you@institution.edu")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True)

            if submitted:
                ok, msg, user = authenticate_user(email, password)
                if ok:
                    st.session_state["authenticated"] = True
                    st.session_state["user"] = user
                    st.success(f"Welcome back, {user['display_name']}!")
                    goto("dashboard")
                else:
                    st.error(f"❌ {msg}")

        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("← Back to Home"):
                goto("landing")
        with c2:
            if st.button("Create Account"):
                goto("register")

        st.markdown("""
        <div style="margin-top:1rem; padding:0.8rem; background:rgba(20,184,166,0.08);
                    border:1px solid rgba(20,184,166,0.2); border-radius:8px; font-size:0.82rem; color:#64748b;">
            💡 <strong>Password recovery:</strong> This local prototype does not send emails.
            If you forget your password, ask an administrator to reset your account in the local database.
            This limitation is documented and expected for a hackathon prototype.
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: MAIN DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────

def page_dashboard():
    if not MODULES_OK:
        st.error(f"Cannot load GlycoTwin modules: {MODULE_ERROR}")
        return

    user = st.session_state["user"]
    uid = user["id"]

    # ── Portal bar ────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="gt-portal-bar">
        <div class="gt-portal-left">
            <span class="gt-portal-brand">🧬 GlycoTwin</span>
            <span class="gt-portal-user">
                {user['display_name']} &nbsp;·&nbsp;
                {user.get('role', 'researcher').replace('_', ' ').title()} &nbsp;·&nbsp;
                {user.get('institution', '') or 'Research Mode'}
            </span>
        </div>
        <div class="gt-portal-right">
            <span class="gt-badge gt-badge-replay">🟢 Historical Replay</span>
            <span class="gt-badge gt-badge-research">Research Prototype</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="gt-disclaimer-bar">
        ⚠️ Research prototype — not a diagnostic device or treatment recommendation.
        All probabilities are model estimates from anonymized research data.
    </div>
    """, unsafe_allow_html=True)

    # ── Load data ─────────────────────────────────────────────────────────────
    try:
        df = load_dashboard_data()
    except Exception as exc:
        st.error(f"Unable to load CGMacros data: {exc}")
        st.info("Ensure the raw dataset is in `data/raw/cgmacros/CGMacros/`.")
        if st.button("Logout"):
            logout()
        return

    # ── Load predictor once ───────────────────────────────────────────────────
    if st.session_state["last_predictor"] is None:
        try:
            st.session_state["last_predictor"] = GlycoTwinPredictor()
        except FileNotFoundError:
            st.error("Model artifact not found. Expected: `models/glycotwin_logistic_calibrated.pkl`")
            st.info("Run `python -m src.evaluation.calibrate_logistic` to train the model.")
            if st.button("Logout"):
                logout()
            return

    predictor = st.session_state["last_predictor"]

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### 🎯 Participant Selection")

        cohort_mode = st.radio(
            "Cohort Filter",
            ["All Participants", "HbA1c ≥ 6.5% (T2D range)", "HbA1c 5.7-6.4% (Pre-DM range)", "HbA1c < 5.7% (Healthy range)"],
            index=0,
            help="Cohort classification uses HbA1c from dataset. This is a research grouping, not a clinical diagnosis.",
        )

        all_ids = sorted(df["subject_id"].dropna().unique().tolist(), key=lambda x: str(x))
        patient_profiles_cache = {}
        t2d_ids, pre_ids, healthy_ids = [], [], []
        for pid in all_ids:
            p_df = df[df["subject_id"] == pid]
            prof = get_profile(p_df)
            patient_profiles_cache[pid] = prof
            hba1c = prof.get("hba1c", 5.5)
            if hba1c >= 6.5:
                t2d_ids.append(pid)
            elif 5.7 <= hba1c < 6.5:
                pre_ids.append(pid)
            else:
                healthy_ids.append(pid)

        if cohort_mode.startswith("HbA1c ≥") and t2d_ids:
            selectable = t2d_ids
        elif cohort_mode.startswith("HbA1c 5.7") and pre_ids:
            selectable = pre_ids
        elif cohort_mode.startswith("HbA1c <") and healthy_ids:
            selectable = healthy_ids
        else:
            selectable = all_ids

        def fmt_pid(pid):
            prof = patient_profiles_cache.get(pid, {})
            hba1c = prof.get("hba1c", 0)
            age = int(prof.get("age", 0))
            return f"CGMacros-{int(pid):03d}  (Age {age} | HbA1c {hba1c:.1f}%)"

        selected_patient = st.selectbox(
            "Participant",
            selectable,
            format_func=fmt_pid,
        )

        # Save preference
        if uid and uid != 0:
            save_user_preferences(uid, last_participant=str(selected_patient), preferred_cohort=cohort_mode)

        st.markdown("---")
        st.markdown("### 💾 Workspaces")

        ws_name = st.text_input("Workspace name", placeholder="My research session")
        if st.button("💾 Save Workspace", use_container_width=True):
            if not ws_name.strip():
                st.warning("Enter a workspace name.")
            elif uid and uid != 0:
                wid = create_workspace(
                    user_id=uid,
                    name=ws_name.strip(),
                    cohort=cohort_mode,
                    participant_id=str(selected_patient),
                    replay_index=st.session_state.get("replay_index", 0),
                )
                st.session_state["active_workspace_id"] = wid
                st.success(f"✅ Saved: '{ws_name.strip()}'")
            else:
                st.info("Login to save workspaces.")

        if uid and uid != 0:
            workspaces = get_workspaces(uid)
            if workspaces:
                st.markdown("**Saved workspaces:**")
                for ws in workspaces[:5]:
                    c1, c2 = st.columns([4, 1])
                    with c1:
                        if st.button(f"📂 {ws['name'][:24]}", key=f"ws_{ws['id']}"):
                            st.session_state["replay_index"] = ws.get("replay_index", 0)
                            st.success(f"Loaded: {ws['name']}")
                    with c2:
                        if st.button("🗑️", key=f"del_{ws['id']}"):
                            delete_workspace(ws["id"], uid)
                            st.rerun()

        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            logout()

    # ── Patient data ──────────────────────────────────────────────────────────
    patient_df = df[df["subject_id"] == selected_patient].sort_values("timestamp").reset_index(drop=True)
    if patient_df.empty:
        st.error("No data for selected participant.")
        return

    profile = patient_profiles_cache[selected_patient]

    # ── Replay state ──────────────────────────────────────────────────────────
    max_idx = len(patient_df) - 1
    replay_idx = st.session_state.get("replay_index", max_idx)
    replay_idx = min(replay_idx, max_idx)
    if replay_idx < 12:
        replay_idx = 12  # need history for features

    # Slice up to replay_idx
    replay_df = patient_df.iloc[:replay_idx + 1]

    # Build twin from replay history
    @st.cache_data(show_spinner=False)
    def get_twin_at_index(_patient_df_hash, idx, _profile):
        sliced = patient_df.iloc[:idx + 1]
        return build_twin_from_history(sliced, _profile)

    try:
        twin = build_twin_from_history(replay_df, profile)
        pred = predictor.predict(twin, profile)
        risk_prob = float(pred["risk_probability"])
        excursion_risk = bool(pred["excursion_risk"])
    except Exception as exc:
        st.error(f"Prediction error: {exc}")
        return

    # ── TABS ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Twin Overview",
        "🧪 Scenario Simulator",
        "🩺 EHR Profile",
        "📡 CGM Replay",
        "🔬 Model Evidence",
    ])

    # =========================================================================
    # TAB 1 — TWIN OVERVIEW & RISK PREDICTION
    # =========================================================================
    with tab1:
        st.markdown("### 🧬 Digital Bio-Twin — Real-Time Telemetry")

        # Metric row
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f"""
            <div class="gt-metric-card">
                <div class="gt-metric-label">Current Glucose</div>
                <div class="gt-metric-value">{twin.current_glucose:.0f}</div>
                <div class="gt-metric-delta neutral">mg/dL</div>
            </div>""", unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
            <div class="gt-metric-card">
                <div class="gt-metric-label">Personal Baseline</div>
                <div class="gt-metric-value">{twin.personal_baseline:.1f}</div>
                <div class="gt-metric-delta neutral">mg/dL (EMA)</div>
            </div>""", unsafe_allow_html=True)
        with m3:
            prob_color = "up" if excursion_risk else "down"
            st.markdown(f"""
            <div class="gt-metric-card">
                <div class="gt-metric-label">2-Hr Excursion Risk</div>
                <div class="gt-metric-value">{risk_prob:.1%}</div>
                <div class="gt-metric-delta {prob_color}">{'⚠️ Elevated' if excursion_risk else '✅ Below threshold'}</div>
            </div>""", unsafe_allow_html=True)
        with m4:
            st.markdown(f"""
            <div class="gt-metric-card">
                <div class="gt-metric-label">Data Confidence</div>
                <div class="gt-metric-value">{twin.data_confidence:.0%}</div>
                <div class="gt-metric-delta neutral">sensor completeness</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Risk status
        if excursion_risk:
            st.markdown(f"""
            <div class="gt-risk-elevated">
                <strong>⚠️ At or above research operating threshold ({risk_prob:.1%})</strong><br>
                <span style="font-size:0.9rem; color:#fca5a5;">
                Model-estimated probability of a ≥30 mg/dL rise within 120 minutes exceeds the 20% research threshold.
                <br><em>Research prototype — not a clinical alert or treatment recommendation.</em>
                </span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="gt-risk-normal">
                <strong>✅ Below research operating threshold ({risk_prob:.1%})</strong><br>
                <span style="font-size:0.9rem; color:#6ee7b7;">
                Model-estimated probability remains below the 20% research operating threshold.
                <br><em>Research prototype — below threshold does not imply clinical safety.</em>
                </span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col_left, col_right = st.columns([3, 2])

        with col_left:
            # Glucose chart
            st.markdown("#### 📈 Glucose History (Last 24 Hours)")
            chart_df = replay_df[["timestamp", "glucose"]].dropna().copy()
            if not chart_df.empty:
                latest = chart_df["timestamp"].max()
                cutoff = latest - pd.Timedelta(hours=24)
                chart_df = chart_df[chart_df["timestamp"] >= cutoff]

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=chart_df["timestamp"],
                    y=chart_df["glucose"],
                    mode="lines+markers",
                    name="CGM Glucose",
                    line=dict(color="#2dd4bf", width=2),
                    marker=dict(size=3),
                ))
                # Baseline line
                fig.add_hline(
                    y=twin.personal_baseline,
                    line_dash="dash",
                    line_color="#818cf8",
                    annotation_text=f"Baseline {twin.personal_baseline:.0f}",
                    annotation_position="bottom right",
                )
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(15,23,42,0.5)",
                    font=dict(color="#94a3b8", size=11),
                    xaxis=dict(gridcolor="rgba(51,65,85,0.5)", title=""),
                    yaxis=dict(gridcolor="rgba(51,65,85,0.5)", title="Glucose (mg/dL)"),
                    height=280,
                    margin=dict(l=0, r=0, t=0, b=0),
                    showlegend=False,
                )
                st.plotly_chart(fig, use_container_width=True)

        with col_right:
            # Twin state panel
            st.markdown("#### 🧬 Twin State")
            dev = (twin.current_glucose or 0) - (twin.personal_baseline or 0)
            st.markdown(f"""
            <div class="gt-state-panel">
                <div class="gt-state-row">
                    <span class="gt-state-key">Participant</span>
                    <span class="gt-state-val">CGMacros-{int(selected_patient):03d}</span>
                </div>
                <div class="gt-state-row">
                    <span class="gt-state-key">Glucose Momentum</span>
                    <span class="gt-state-val">{twin.glucose_momentum:+.1f} mg/dL</span>
                </div>
                <div class="gt-state-row">
                    <span class="gt-state-key">Deviation from Baseline</span>
                    <span class="gt-state-val">{dev:+.1f} mg/dL</span>
                </div>
                <div class="gt-state-row">
                    <span class="gt-state-key">Activity State</span>
                    <span class="gt-state-val">{twin.activity_state:.2f} (norm.)</span>
                </div>
                <div class="gt-state-row">
                    <span class="gt-state-key">Cardiovascular State</span>
                    <span class="gt-state-val">{twin.cardiovascular_state:.2f} (norm.)</span>
                </div>
                <div class="gt-state-row">
                    <span class="gt-state-key">Risk Threshold</span>
                    <span class="gt-state-val">20% (research)</span>
                </div>
                <div class="gt-state-row">
                    <span class="gt-state-key">Observations in Window</span>
                    <span class="gt-state-val">{len(twin.history)}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Evolution timeline using real model inference
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### ⏳ Twin Evolution Timeline (Actual Model Inference)")
        st.caption("Each row shows the Twin's state and model-estimated risk at that point in the historical replay.")

        timeline_samples = patient_df.tail(min(8, len(patient_df))).copy()
        timeline_rows = []
        t_twin = TwinState(patient_id=str(selected_patient))
        for _, row in timeline_samples.iterrows():
            obs = {
                "timestamp": str(row["timestamp"]),
                "glucose": float(row["glucose"]) if pd.notna(row.get("glucose")) else None,
                "heart_rate": float(row["heart_rate"]) if pd.notna(row.get("heart_rate")) else None,
                "activity_calories": float(row["activity_calories"]) if pd.notna(row.get("activity_calories")) else None,
                "mets": float(row["mets"]) if pd.notna(row.get("mets")) else None,
            }
            t_twin = update_twin(t_twin, obs)
            if t_twin.current_glucose is not None:
                try:
                    t_pred = predictor.predict(t_twin, profile)
                    t_prob = t_pred["risk_probability"]
                except Exception:
                    t_prob = None

                t_str = row["timestamp"].strftime("%H:%M") if isinstance(row["timestamp"], pd.Timestamp) else "—"
                baseline_val = t_twin.personal_baseline or 0
                timeline_rows.append({
                    "Time": t_str,
                    "Glucose (mg/dL)": f"{t_twin.current_glucose:.0f}",
                    "Baseline (mg/dL)": f"{baseline_val:.1f}",
                    "Momentum": f"{t_twin.glucose_momentum:+.1f}",
                    "2-Hr Risk": f"{t_prob:.1%}" if t_prob is not None else "—",
                    "Confidence": f"{t_twin.data_confidence:.0%}",
                    "Status": "⚠️ Elevated" if (t_prob or 0) >= 0.20 else "✅ Normal",
                })

        if timeline_rows:
            st.dataframe(pd.DataFrame(timeline_rows), use_container_width=True, hide_index=True)

        # Explanation panel
        st.markdown("#### 🔍 Why is the Twin estimating this probability?")
        st.markdown("""
        <div class="gt-state-panel" style="background:rgba(13,20,40,0.7);">
        """, unsafe_allow_html=True)

        gl = twin.current_glucose or 0
        bl = twin.personal_baseline or 0
        mom = twin.glucose_momentum
        act = twin.activity_state
        conf = twin.data_confidence

        direction = "above" if gl > bl else "below"
        mom_dir = "rising" if mom > 0 else ("falling" if mom < 0 else "stable")

        st.markdown(f"""
        - **Glucose vs Baseline:** Current glucose is **{abs(gl - bl):.1f} mg/dL {direction}** personal baseline
          ({bl:.1f} mg/dL). Glucose above baseline is associated with higher risk in training data.
        - **Glucose Trajectory:** Recent glucose momentum is **{mom_dir}** ({mom:+.1f} mg/dL),
          computed as an exponential moving average of 5-minute changes.
        - **Activity Context:** Normalized activity state is **{act:.2f}**.
          Higher activity is associated with lower risk in training data.
        - **Data Completeness:** Input vector is **{conf:.0%}** complete for this observation.
          Missing sensor values are imputed with zeros for inference.

        *These are model-associated feature contributions, not causal explanations.
        The model uses a 24-feature vector including statistics over the last 12 observations (~60 minutes).*
        """)

        st.markdown("</div>", unsafe_allow_html=True)

        # Export
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("📥 Export Session Report"):
            exp_col1, exp_col2 = st.columns(2)
            with exp_col1:
                if st.button("📄 Download PDF Report"):
                    try:
                        replay_history = [
                            {
                                "timestamp": h["timestamp"],
                                "glucose": h.get("glucose"),
                                "heart_rate": h.get("heart_rate"),
                                "activity_calories": h.get("activity_calories"),
                                "mets": h.get("mets"),
                                "personal_baseline": twin.personal_baseline,
                                "glucose_momentum": twin.glucose_momentum,
                                "data_confidence": twin.data_confidence,
                                "risk_probability": risk_prob,
                                "excursion_risk": excursion_risk,
                            }
                            for h in twin.history
                        ]
                        pdf_bytes = generate_pdf_report(
                            participant_id=f"CGMacros-{int(selected_patient):03d}",
                            cohort=cohort_mode,
                            replay_rows=replay_history,
                            model_version="glycotwin_logistic_calibrated",
                            user_display_name=user["display_name"],
                        )
                        st.download_button(
                            label="⬇️ Save PDF",
                            data=pdf_bytes,
                            file_name=f"glycotwin_report_{selected_patient}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M')}.pdf",
                            mime="application/pdf",
                        )
                    except Exception as exc:
                        st.error(f"PDF generation error: {exc}")
            with exp_col2:
                if st.button("📊 Download CSV"):
                    try:
                        csv_str = generate_csv_report(
                            participant_id=f"CGMacros-{int(selected_patient):03d}",
                            replay_rows=twin.history,
                            model_version="glycotwin_logistic_calibrated",
                        )
                        st.download_button(
                            label="⬇️ Save CSV",
                            data=csv_str,
                            file_name=f"glycotwin_replay_{selected_patient}.csv",
                            mime="text/csv",
                        )
                    except Exception as exc:
                        st.error(f"CSV generation error: {exc}")

    # =========================================================================
    # TAB 2 — SCENARIO SIMULATOR
    # =========================================================================
    with tab2:
        st.markdown("### 🧪 Digital Twin Scenario Simulator")
        st.markdown("""
        <div class="gt-badge gt-badge-hypo">
            ⚠️ HYPOTHETICAL — Feature-space perturbation only. Not a causal model. Not clinical advice.
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        sc_col1, sc_col2 = st.columns([1, 1])
        with sc_col1:
            st.markdown("#### ⚙️ Scenario Configuration")

            scenario_key = st.selectbox(
                "Scenario Type",
                options=list(SCENARIOS.keys()),
                format_func=lambda k: SCENARIOS[k]["label"],
            )

            scenario_meta = SCENARIOS[scenario_key]
            st.caption(scenario_meta["description"])

            intensity = st.slider(
                "Perturbation Intensity",
                min_value=0.0, max_value=1.0, value=0.5, step=0.1,
                help="0 = minimal change, 1 = maximal change within supported range.",
            )

            st.markdown("**Assumptions:**")
            for a in scenario_meta["assumptions"]:
                st.markdown(f"- {a}")

        with sc_col2:
            st.markdown("#### 📊 Projected Outcome Comparison")

            if st.button("▶️ Run Scenario", use_container_width=True):
                try:
                    result = run_scenario(
                        original_twin=twin,
                        profile=profile,
                        scenario_key=scenario_key,
                        intensity=intensity,
                        predictor=predictor,
                    )
                    st.session_state["last_scenario"] = result.__dict__

                    m_c1, m_c2 = st.columns(2)
                    with m_c1:
                        st.metric("Baseline Risk", f"{result.baseline_probability:.1%}")
                    with m_c2:
                        delta_val = result.delta_percentage_points
                        st.metric(
                            "Scenario Risk",
                            f"{result.scenario_probability:.1%}",
                            delta=f"{delta_val:+.1f} pp",
                        )

                    st.markdown(f"""
                    <div class="gt-scenario-hypothetical">
                        <strong>🔬 Hypothetical Result: {result.summary()}</strong><br>
                        <span style="font-size:0.85rem; color:#94a3b8;">
                        Modifications applied: {result.modifications}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)

                    if result.delta_percentage_points < 0:
                        st.success(f"📉 Model projects **lower** risk under this scenario ({abs(result.delta_percentage_points):.1f} pp decrease).")
                    elif result.delta_percentage_points > 0:
                        st.warning(f"📈 Model projects **higher** risk under this scenario (+{result.delta_percentage_points:.1f} pp increase).")
                    else:
                        st.info("Model-projected risk is unchanged under this scenario.")

                except Exception as exc:
                    st.error(f"Scenario error: {exc}")

            elif "last_scenario" in st.session_state:
                result_d = st.session_state["last_scenario"]
                m_c1, m_c2 = st.columns(2)
                with m_c1:
                    st.metric("Baseline Risk", f"{result_d['baseline_probability']:.1%}")
                with m_c2:
                    st.metric("Scenario Risk", f"{result_d['scenario_probability']:.1%}",
                              delta=f"{result_d['delta_percentage_points']:+.1f} pp")
            else:
                st.info("Configure a scenario and click **Run Scenario** to see results.")

        st.markdown("---")
        st.markdown("**⚠️ Scenario Limitations:**")
        for lim in scenario_meta["limitations"]:
            st.markdown(f"- {lim}")
        st.markdown("*Scenario results are research estimates only. Risk can increase or decrease — neither outcome is a clinical recommendation.*")

    # =========================================================================
    # TAB 3 — EHR PROFILE
    # =========================================================================
    with tab3:
        st.markdown("### 🩺 Static EHR Profile & Personal Baseline")
        st.caption("Data from PhysioNet CGMacros v1.0.0 bio.csv — anonymized and date-shifted.")

        ehr_c1, ehr_c2, ehr_c3 = st.columns(3)
        with ehr_c1:
            st.metric("Age", f"{int(profile.get('age', 0))} years")
            st.metric("BMI", f"{profile.get('bmi', 0):.1f} kg/m²")
        with ehr_c2:
            st.metric("HbA1c", f"{profile.get('hba1c', 0):.1f}%",
                      help="Research cohort classification only. Not a clinical diagnosis.")
            st.metric("Fasting Glucose", f"{profile.get('fasting_glucose', 0):.0f} mg/dL")
        with ehr_c3:
            st.metric("Fasting Insulin", f"{profile.get('insulin', 0):.1f} µIU/mL")
            st.metric("Personal Baseline (EMA)", f"{profile.get('personal_baseline', 0):.1f} mg/dL")

        st.markdown("---")
        hba1c_val = profile.get("hba1c", 5.5)
        if hba1c_val >= 6.5:
            cohort_label = "HbA1c ≥ 6.5% range"
            cohort_note = "Dataset-based research grouping. Not a clinical Type 2 Diabetes diagnosis."
        elif hba1c_val >= 5.7:
            cohort_label = "HbA1c 5.7–6.4% range"
            cohort_note = "Dataset-based research grouping. Not a clinical pre-diabetes diagnosis."
        else:
            cohort_label = "HbA1c < 5.7% range"
            cohort_note = "Dataset-based research grouping. Not a clinical normal classification."

        st.info(f"**Research Cohort Classification:** {cohort_label}\n\n{cohort_note}")

        st.markdown("#### Glucose Distribution (All Available History)")
        all_glucose = patient_df["glucose"].dropna()
        if len(all_glucose) > 0:
            fig_hist = px.histogram(
                all_glucose, nbins=30,
                color_discrete_sequence=["#2dd4bf"],
                labels={"value": "Glucose (mg/dL)", "count": "Observations"},
            )
            fig_hist.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(15,23,42,0.5)",
                font=dict(color="#94a3b8"),
                height=250,
                margin=dict(l=0, r=0, t=0, b=0),
            )
            st.plotly_chart(fig_hist, use_container_width=True)

    # =========================================================================
    # TAB 4 — CGM REPLAY
    # =========================================================================
    with tab4:
        st.markdown("### 📡 Historical CGM & Wearable Stream Replay")
        st.markdown("""
        <div class="gt-badge gt-badge-replay">🟢 Historical Replay Active</div>
        <span style="color:#64748b; font-size:0.85rem; margin-left:0.5rem;">
        Open-source CGMacros data replayed sequentially — not a live sensor feed.
        </span>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        rp_col1, rp_col2, rp_col3, rp_col4 = st.columns(4)
        with rp_col1:
            if st.button("▶️ Step Forward", use_container_width=True):
                new_idx = min(replay_idx + 1, max_idx)
                st.session_state["replay_index"] = new_idx
                st.rerun()
        with rp_col2:
            if st.button("⏩ Jump +12", use_container_width=True):
                new_idx = min(replay_idx + 12, max_idx)
                st.session_state["replay_index"] = new_idx
                st.rerun()
        with rp_col3:
            if st.button("⏮️ Back 12", use_container_width=True):
                new_idx = max(replay_idx - 12, 12)
                st.session_state["replay_index"] = new_idx
                st.rerun()
        with rp_col4:
            if st.button("🔄 Reset Replay", use_container_width=True):
                st.session_state["replay_index"] = 12
                st.rerun()

        # Progress
        progress_pct = replay_idx / max(max_idx, 1)
        st.progress(progress_pct, text=f"Replay position: observation {replay_idx}/{max_idx}")

        # Current observation
        current_row = patient_df.iloc[replay_idx]
        rp_m1, rp_m2, rp_m3, rp_m4, rp_m5 = st.columns(5)
        with rp_m1:
            ts = current_row["timestamp"]
            ts_str = ts.strftime("%Y-%m-%d %H:%M") if isinstance(ts, pd.Timestamp) else str(ts)
            st.metric("Timestamp", ts_str[:16])
        with rp_m2:
            gl = current_row.get("glucose", float("nan"))
            st.metric("Glucose", f"{gl:.0f} mg/dL" if pd.notna(gl) else "—")
        with rp_m3:
            hr = current_row.get("heart_rate", float("nan"))
            st.metric("Heart Rate", f"{hr:.0f} bpm" if pd.notna(hr) else "—")
        with rp_m4:
            act = current_row.get("activity_calories", float("nan"))
            st.metric("Activity Cal", f"{act:.1f} kcal" if pd.notna(act) else "—")
        with rp_m5:
            mets = current_row.get("mets", float("nan"))
            st.metric("METs", f"{mets:.1f}" if pd.notna(mets) else "—")

        # Twin state at current replay position
        st.markdown("---")
        rep_c1, rep_c2 = st.columns(2)
        with rep_c1:
            st.markdown("**Twin State at Replay Position:**")
            st.markdown(f"""
            <div class="gt-state-panel">
                <div class="gt-state-row">
                    <span class="gt-state-key">Current Glucose</span>
                    <span class="gt-state-val">{twin.current_glucose:.0f} mg/dL</span>
                </div>
                <div class="gt-state-row">
                    <span class="gt-state-key">Personal Baseline</span>
                    <span class="gt-state-val">{twin.personal_baseline:.1f} mg/dL</span>
                </div>
                <div class="gt-state-row">
                    <span class="gt-state-key">Glucose Momentum</span>
                    <span class="gt-state-val">{twin.glucose_momentum:+.1f} mg/dL</span>
                </div>
                <div class="gt-state-row">
                    <span class="gt-state-key">2-Hr Risk Estimate</span>
                    <span class="gt-state-val">{risk_prob:.1%}</span>
                </div>
                <div class="gt-state-row">
                    <span class="gt-state-key">Data Confidence</span>
                    <span class="gt-state-val">{twin.data_confidence:.0%}</span>
                </div>
            </div>""", unsafe_allow_html=True)

        with rep_c2:
            # Recent history table
            display_cols = ["timestamp", "glucose", "heart_rate", "activity_calories", "mets"]
            avail_cols = [c for c in display_cols if c in replay_df.columns]
            recent_table = replay_df[avail_cols].tail(15).copy()
            if "timestamp" in recent_table.columns:
                recent_table["timestamp"] = recent_table["timestamp"].dt.strftime("%H:%M")
            st.dataframe(recent_table, use_container_width=True, hide_index=True)

    # =========================================================================
    # TAB 5 — MODEL EVIDENCE
    # =========================================================================
    with tab5:
        st.markdown("### 🔬 Model Evidence & Data Provenance")

        st.markdown("#### Calibrated Logistic Regression — Held-Out Test Results")
        st.caption("Participant-level split: 31 train / 7 validation / 7 test. Zero participant overlap.")

        m = VERIFIED_METRICS
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Test AUROC", f"{m['auroc']:.4f}")
            st.metric("Test Avg Precision", f"{m['average_precision']:.4f}")
        with col_b:
            st.metric("Test Precision", f"{m['precision']:.4f}")
            st.metric("Test Recall", f"{m['recall']:.4f}")
        with col_c:
            st.metric("Test F1", f"{m['f1']:.4f}")
            st.metric("Brier Score", f"{m['brier_score']:.4f}")

        st.markdown("---")
        st.markdown("#### Ablation Study — Why Personalization Matters")
        ablation_df = pd.DataFrame(ABLATION_DATA)
        st.dataframe(ablation_df, use_container_width=True, hide_index=True)

        fig_abl = go.Figure(go.Bar(
            x=[d["Feature Configuration"] for d in ABLATION_DATA],
            y=[d["Test AUROC"] for d in ABLATION_DATA],
            marker_color=["#64748b", "#475569", "#0891b2", "#2dd4bf"],
            text=[f"{d['Test AUROC']:.3f}" for d in ABLATION_DATA],
            textposition="outside",
        ))
        fig_abl.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(15,23,42,0.5)",
            font=dict(color="#94a3b8"),
            yaxis=dict(gridcolor="rgba(51,65,85,0.5)", range=[0.5, 0.82], title="AUROC"),
            xaxis=dict(gridcolor="rgba(51,65,85,0.5)"),
            height=300,
            margin=dict(l=0, r=0, t=0, b=0),
        )
        st.plotly_chart(fig_abl, use_container_width=True)

        st.markdown("---")
        st.markdown("#### Model Details")
        st.markdown(f"""
        | Property | Value |
        |---|---|
        | **Model** | Calibrated Logistic Regression (Platt scaling) |
        | **Features** | 24 (7 glucose, 3 heart rate, 4 activity, 3 METs, 5 static, 2 personalization) |
        | **Target** | ≥30 mg/dL rise within 120 minutes from any valid observation |
        | **Operating Threshold** | 20% (research choice, selected on validation data) |
        | **Participant Split** | 31 train / 7 val / 7 test (no participant overlap) |
        | **Dataset** | PhysioNet CGMacros v1.0.0 |
        | **Model Artifact** | `models/glycotwin_logistic_calibrated.pkl` |
        | **Model Version** | glycotwin_logistic_calibrated |
        """)

        st.markdown("---")
        st.markdown("#### ⚠️ Known Limitations")
        st.markdown("""
        1. **Population generalization:** Model trained on CGMacros (45 participants).
           Performance may differ substantially in other populations.
        2. **Threshold is a research choice:** The 20% operating point is not clinically validated.
        3. **Missing data handling:** NaN values imputed with zeros during inference.
           A missing-data warning does not equal calibrated uncertainty.
        4. **No external validation:** Prospective validation on independent data is required
           before any clinical application.
        5. **Temporal coverage:** Historical dataset spans limited study periods per participant.
        6. **Cohort classification:** HbA1c-based grouping in dataset does not replace clinical diagnosis.
        7. **Scenario results:** Feature perturbations are not causal counterfactuals.
        """)

        st.markdown("---")
        st.markdown("#### 📁 Data Provenance")
        st.markdown("""
        - **Dataset:** PhysioNet CGMacros v1.0.0
        - **URL:** https://physionet.org/content/cgmacros/1.0.0/
        - **License:** CC BY-NC-SA 4.0 — non-commercial use only, share-alike
        - **DOI:** https://doi.org/10.13026/3z8q-x658
        - **Participants:** 45 individuals, date-shifted for privacy
        - **Raw data:** Not distributed in repository
        - **Processed data:** Preprocessed arrays in `data/processed/`
        - **Target:** Built from observed glucose (no forward-filled imputed values used as truth)
        """)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN ROUTER
# ─────────────────────────────────────────────────────────────────────────────

if not MODULES_OK:
    st.error(f"❌ GlycoTwin failed to load: {MODULE_ERROR}")
    st.info("Check that all required packages are installed: `pip install -r requirements.txt`")
    st.stop()

page = st.session_state.get("page", "landing")
is_auth = st.session_state.get("authenticated", False)

if page == "landing" or (not is_auth and page not in ["register", "login"]):
    page_landing()
elif page == "register":
    page_register()
elif page == "login":
    page_login()
elif page == "dashboard" and is_auth:
    page_dashboard()
else:
    page_landing()