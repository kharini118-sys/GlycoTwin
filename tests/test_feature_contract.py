import unittest
import numpy as np
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.twin.state import TwinState, PatientProfile
from src.twin.updater import update_twin
from src.twin.feature_builder import build_prediction_features


class TestFeatureContract(unittest.TestCase):

    def test_feature_contract_dimensions(self):
        """
        Verify feature matrix construction contract:
        - Must return shape (1, 24) matching model training contract.
        - No NaNs in essential static + dynamic features.
        """
        profile = PatientProfile(
            patient_id="P_TEST",
            age=50.0,
            bmi=28.5,
            hba1c=6.5,
            fasting_glucose=115.0,
            insulin=12.0,
        )

        twin = TwinState(patient_id="P_TEST")

        # Simulate 12 observations
        for i in range(12):
            obs = {
                "timestamp": f"2026-01-01 08:{i*5:02d}",
                "glucose": 110.0 + i * 2,
                "heart_rate": 72.0 + (i % 3),
                "activity_calories": 1.0 + (i * 0.1),
                "mets": 1.5 + (i * 0.1),
            }
            twin = update_twin(twin, obs, profile)

        features = build_prediction_features(twin, profile.to_dict())

        self.assertIsInstance(features, np.ndarray)
        self.assertEqual(features.shape, (1, 24), f"Expected shape (1, 24), got {features.shape}")
        self.assertFalse(np.isnan(features[0, 0]), "Current glucose feature should not be NaN")
        self.assertFalse(np.isnan(features[0, 17]), "Age feature should not be NaN")
        self.assertFalse(np.isnan(features[0, 22]), "Personal baseline feature should not be NaN")


if __name__ == "__main__":
    unittest.main()
