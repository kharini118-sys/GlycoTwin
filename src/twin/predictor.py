from pathlib import Path

import joblib

from .state import TwinState
from .feature_builder import build_prediction_features


PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "glycotwin_logistic_calibrated.pkl"
)

RISK_THRESHOLD = 0.20


class GlycoTwinPredictor:

    def __init__(
        self,
        model_path=MODEL_PATH,
        risk_threshold=RISK_THRESHOLD,
    ):
        self.model_path = Path(model_path)
        self.risk_threshold = risk_threshold

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model not found: {self.model_path}"
            )

        self.model = joblib.load(self.model_path)

    def predict(
        self,
        twin: TwinState,
        profile: dict,
    ):
        features = build_prediction_features(
            twin,
            profile,
        )

        probability = float(
            self.model.predict_proba(features)[0, 1]
        )

        risk = probability >= self.risk_threshold

        twin.risk_probability = probability
        twin.risk_threshold = self.risk_threshold
        twin.excursion_risk = risk

        return {
            "risk_probability": probability,
            "risk_threshold": self.risk_threshold,
            "excursion_risk": risk,
            "data_confidence": twin.data_confidence,
        }