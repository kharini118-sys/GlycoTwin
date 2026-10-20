"""
GlycoTwin Scenario Simulator
Clones a Twin state, applies a hypothetical feature perturbation,
runs identical inference, and returns the comparison.

Scientific transparency requirements:
  - The scenario is a feature-space perturbation, not a physiological model.
  - Results are NOT causal counterfactuals.
  - Risk can legitimately INCREASE under a scenario.
  - Assumptions are recorded and returned.
  - Results must never be presented as clinical advice.
"""

import copy
from dataclasses import dataclass
from typing import Any, Dict, Optional
import numpy as np

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.twin.state import TwinState
from src.twin.predictor import GlycoTwinPredictor
from src.twin.feature_builder import build_prediction_features


@dataclass
class ScenarioResult:
    baseline_probability: float
    scenario_probability: float
    delta_percentage_points: float   # scenario - baseline, in pp
    scenario_name: str
    modifications: Dict[str, Any]
    assumptions: list
    limitations: list
    is_supported: bool
    model_version: str

    def summary(self) -> str:
        direction = "increased" if self.delta_percentage_points > 0 else "decreased"
        return (
            f"Under '{self.scenario_name}', the model estimates "
            f"probability {direction} by "
            f"{abs(self.delta_percentage_points):.1f} percentage points "
            f"({self.baseline_probability:.1%} → {self.scenario_probability:.1%})."
        )


# ── Available scenario types ──────────────────────────────────────────────────

SCENARIOS = {
    "activity_increase": {
        "label": "Increased Physical Activity",
        "description": (
            "Simulate adding light-to-moderate physical activity by adjusting "
            "activity calories and METs in the Twin's recent history."
        ),
        "is_supported": True,
        "assumptions": [
            "Activity calories in the last window are uniformly increased.",
            "METs are scaled proportionally.",
            "The model's activity features change accordingly.",
        ],
        "limitations": [
            "This is a feature-space perturbation, not a physiological model.",
            "Real glucose response to exercise is highly individual.",
            "This result does not account for delayed effects.",
            "Not a clinical exercise recommendation.",
        ],
    },
    "activity_decrease": {
        "label": "Decreased Physical Activity",
        "description": "Simulate sedentary state by reducing activity features.",
        "is_supported": True,
        "assumptions": [
            "Activity calories set to low baseline values.",
            "METs set close to resting levels.",
        ],
        "limitations": [
            "Feature-space perturbation only.",
            "Not a clinical recommendation.",
        ],
    },
    "glucose_trend_shift": {
        "label": "Altered Glucose Trend",
        "description": (
            "Simulate a shift in the recent glucose trajectory, "
            "without changing the current glucose value."
        ),
        "is_supported": True,
        "assumptions": [
            "Recent glucose window values are uniformly shifted.",
            "Current glucose observation remains unchanged.",
            "Personal baseline is recalculated accordingly.",
        ],
        "limitations": [
            "Does not simulate dietary or pharmacological cause.",
            "Feature-space perturbation only.",
            "Not a treatment recommendation.",
        ],
    },
    "heart_rate_elevated": {
        "label": "Elevated Heart Rate",
        "description": "Simulate sustained elevated heart rate (stress or exertion).",
        "is_supported": True,
        "assumptions": [
            "Heart rate window values set to elevated level.",
            "No other features are changed.",
        ],
        "limitations": [
            "Elevated HR has many causes; this does not distinguish them.",
            "Feature-space perturbation only.",
        ],
    },
}


def run_scenario(
    original_twin: TwinState,
    profile: dict,
    scenario_key: str,
    intensity: float = 0.5,
    predictor: Optional[GlycoTwinPredictor] = None,
) -> ScenarioResult:
    """
    Clone the twin state, apply perturbation, run inference, return comparison.

    Parameters
    ----------
    original_twin : TwinState
        The current (unmodified) twin state.
    profile : dict
        Static clinical profile dict.
    scenario_key : str
        One of the keys in SCENARIOS.
    intensity : float
        0.0 = minimal change, 1.0 = maximal change. Default 0.5.
    predictor : GlycoTwinPredictor, optional
        Reuse an existing predictor to avoid reloading the model.
    """
    if predictor is None:
        predictor = GlycoTwinPredictor()

    scenario_meta = SCENARIOS.get(scenario_key)
    if scenario_meta is None:
        raise ValueError(f"Unknown scenario: {scenario_key!r}")

    # ── Baseline prediction ───────────────────────────────────────────────────
    baseline_features = build_prediction_features(original_twin, profile)

    # Fix NaNs with column medians from training (use 0 as fallback)
    baseline_features_clean = np.nan_to_num(baseline_features, nan=0.0)
    baseline_prob = float(
        predictor.model.predict_proba(baseline_features_clean)[0, 1]
    )

    # ── Clone twin and apply perturbation ─────────────────────────────────────
    scenario_twin = copy.deepcopy(original_twin)
    modifications = {}

    if scenario_key == "activity_increase":
        add_calories = 2.0 + intensity * 5.0   # 2–7 kcal per 5-min window
        add_mets = 1.0 + intensity * 3.0        # 1–4 MET increase
        for entry in scenario_twin.history:
            old_cal = entry.get("activity_calories") or 0.0
            old_mets = entry.get("mets") or 1.0
            entry["activity_calories"] = old_cal + add_calories
            entry["mets"] = min(12.0, old_mets + add_mets)
        modifications = {
            "activity_calories_added": round(add_calories, 2),
            "mets_added": round(add_mets, 2),
        }

    elif scenario_key == "activity_decrease":
        for entry in scenario_twin.history:
            entry["activity_calories"] = 0.2
            entry["mets"] = 1.0
        modifications = {"activity_calories": 0.2, "mets": 1.0}

    elif scenario_key == "glucose_trend_shift":
        shift = (-30.0 + intensity * 60.0)  # -30 to +30 mg/dL shift
        for entry in scenario_twin.history[:-1]:   # don't touch current obs
            g = entry.get("glucose")
            if g is not None:
                entry["glucose"] = max(40.0, g + shift)
        modifications = {"glucose_trend_shift_mgdl": round(shift, 1)}

    elif scenario_key == "heart_rate_elevated":
        target_hr = 70.0 + intensity * 60.0   # 70–130 bpm
        for entry in scenario_twin.history:
            entry["heart_rate"] = round(target_hr, 0)
        modifications = {"heart_rate_bpm": round(target_hr, 0)}

    # ── Scenario prediction ───────────────────────────────────────────────────
    scenario_features = build_prediction_features(scenario_twin, profile)
    scenario_features_clean = np.nan_to_num(scenario_features, nan=0.0)
    scenario_prob = float(
        predictor.model.predict_proba(scenario_features_clean)[0, 1]
    )

    delta_pp = (scenario_prob - baseline_prob) * 100.0

    return ScenarioResult(
        baseline_probability=baseline_prob,
        scenario_probability=scenario_prob,
        delta_percentage_points=round(delta_pp, 2),
        scenario_name=scenario_meta["label"],
        modifications=modifications,
        assumptions=scenario_meta["assumptions"],
        limitations=scenario_meta["limitations"],
        is_supported=scenario_meta["is_supported"],
        model_version="glycotwin_logistic_calibrated",
    )
