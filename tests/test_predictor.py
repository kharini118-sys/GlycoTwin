import unittest
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.twin.state import TwinState, PatientProfile
from src.twin.updater import update_twin
from src.twin.predictor import GlycoTwinPredictor


class TestPredictor(unittest.TestCase):

    def test_glycotwin_predictor_execution(self):
        """
        Verify trained model artifact loading and prediction execution.
        - Model artifact exists.
        - Risk probability returned in range [0.0, 1.0].
        - Excursion risk boolean returned correctly based on threshold 0.20.
        """
        predictor = GlycoTwinPredictor()
        self.assertIsNotNone(predictor.model)

        profile = PatientProfile(
            patient_id="P_PRED_TEST",
            age=55.0,
            bmi=31.2,
            hba1c=7.2,
            fasting_glucose=140.0,
            insulin=15.0,
        )

        twin = TwinState(patient_id="P_PRED_TEST")

        observations = [
            {"glucose": 120.0, "heart_rate": 75, "activity_calories": 1.0, "mets": 1.5},
            {"glucose": 135.0, "heart_rate": 80, "activity_calories": 1.5, "mets": 2.0},
            {"glucose": 155.0, "heart_rate": 88, "activity_calories": 2.5, "mets": 3.0},
        ]

        for obs in observations:
            twin = update_twin(twin, obs, profile)

        result = predictor.predict(twin, profile.to_dict())

        self.assertIn("risk_probability", result)
        self.assertIn("excursion_risk", result)
        self.assertTrue(0.0 <= result["risk_probability"] <= 1.0)
        self.assertIsInstance(result["excursion_risk"], bool)
        self.assertEqual(result["risk_threshold"], 0.20)


if __name__ == "__main__":
    unittest.main()
