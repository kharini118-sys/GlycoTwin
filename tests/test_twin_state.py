"""
GlycoTwin — Twin Update Loop Tests
Tests initialization, state update, baseline calculation, missing values.
"""
import unittest
import numpy as np
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.twin.state import TwinState
from src.twin.updater import update_twin
from src.twin.feature_builder import build_prediction_features
from src.twin.predictor import GlycoTwinPredictor


class TestTwinState(unittest.TestCase):

    def test_initialization(self):
        twin = TwinState(patient_id="INIT_TEST")
        self.assertIsNone(twin.current_glucose)
        self.assertIsNone(twin.personal_baseline)
        self.assertEqual(twin.glucose_momentum, 0.0)
        self.assertEqual(len(twin.history), 0)

    def test_first_observation_sets_baseline(self):
        twin = TwinState(patient_id="BL_TEST")
        twin = update_twin(twin, {"glucose": 100.0})
        self.assertEqual(twin.current_glucose, 100.0)
        self.assertEqual(twin.personal_baseline, 100.0)

    def test_baseline_ema_update(self):
        twin = TwinState(patient_id="EMA_TEST")
        twin = update_twin(twin, {"glucose": 100.0})
        twin = update_twin(twin, {"glucose": 140.0})
        # 0.95*100 + 0.05*140 = 102.0
        self.assertAlmostEqual(twin.personal_baseline, 102.0, places=1)

    def test_glucose_momentum(self):
        twin = TwinState(patient_id="MOM_TEST")
        twin = update_twin(twin, {"glucose": 100.0})
        twin = update_twin(twin, {"glucose": 115.0})
        # Momentum should reflect upward trend
        self.assertGreater(twin.glucose_momentum, 0.0)

    def test_timestamp_ordering_preserved(self):
        twin = TwinState(patient_id="TS_TEST")
        twin = update_twin(twin, {"timestamp": "2026-01-01 08:00", "glucose": 100.0})
        twin = update_twin(twin, {"timestamp": "2026-01-01 08:05", "glucose": 110.0})
        self.assertEqual(len(twin.history), 2)
        ts1 = twin.history[0]["timestamp"]
        ts2 = twin.history[1]["timestamp"]
        self.assertLess(ts1, ts2)

    def test_missing_sensor_values(self):
        """Twin must handle None sensor values without crashing."""
        twin = TwinState(patient_id="MISS_TEST")
        twin = update_twin(twin, {
            "glucose": 110.0,
            "heart_rate": None,
            "activity_calories": None,
            "mets": None,
        })
        self.assertEqual(twin.current_glucose, 110.0)
        self.assertIsNone(twin.cardiovascular_state or None)

    def test_data_confidence_full(self):
        twin = TwinState(patient_id="CONF_TEST")
        twin = update_twin(twin, {
            "glucose": 100.0,
            "heart_rate": 72.0,
            "activity_calories": 1.0,
            "mets": 1.5,
        })
        self.assertEqual(twin.data_confidence, 1.0)

    def test_data_confidence_partial(self):
        twin = TwinState(patient_id="PCONF_TEST")
        twin = update_twin(twin, {"glucose": 100.0})
        self.assertEqual(twin.data_confidence, 0.25)  # 1 of 4 sensors

    def test_history_bounded(self):
        """History must not grow unboundedly."""
        twin = TwinState(patient_id="HIST_TEST")
        for i in range(150):
            twin = update_twin(twin, {"glucose": 100.0 + i})
        self.assertLessEqual(len(twin.history), 100)


class TestFeatureBuilder(unittest.TestCase):

    def test_feature_vector_shape(self):
        twin = TwinState(patient_id="FEAT_TEST")
        for i in range(15):
            twin = update_twin(twin, {
                "glucose": 100.0 + i,
                "heart_rate": 72.0,
                "activity_calories": 1.0,
                "mets": 1.5,
            })
        profile = {"age": 52, "bmi": 29, "hba1c": 7.0, "fasting_glucose": 120, "insulin": 14}
        features = build_prediction_features(twin, profile)
        self.assertEqual(features.shape[0], 1)
        self.assertEqual(features.shape[1], 24)

    def test_feature_ordering_consistent(self):
        """Same inputs must produce identical feature vectors."""
        twin1 = TwinState(patient_id="FO1")
        twin2 = TwinState(patient_id="FO2")
        obs = {"glucose": 120.0, "heart_rate": 75.0, "activity_calories": 1.5, "mets": 2.0}
        twin1 = update_twin(twin1, obs)
        twin2 = update_twin(twin2, obs)
        profile = {"age": 50, "bmi": 28, "hba1c": 6.8, "fasting_glucose": 110, "insulin": 12}
        f1 = build_prediction_features(twin1, profile)
        f2 = build_prediction_features(twin2, profile)
        np.testing.assert_array_almost_equal(f1, f2)


class TestPredictorProbabilityRange(unittest.TestCase):

    def test_probability_in_range(self):
        predictor = GlycoTwinPredictor()
        twin = TwinState(patient_id="PR_TEST")
        for i in range(15):
            twin = update_twin(twin, {"glucose": 100 + i, "heart_rate": 72, "activity_calories": 1, "mets": 1.5})
        profile = {"age": 52, "bmi": 29, "hba1c": 7.0, "fasting_glucose": 120, "insulin": 14}
        result = predictor.predict(twin, profile)
        self.assertGreaterEqual(result["risk_probability"], 0.0)
        self.assertLessEqual(result["risk_probability"], 1.0)

    def test_model_version_recorded(self):
        predictor = GlycoTwinPredictor()
        self.assertIsNotNone(predictor.model)

    def test_missing_model_raises(self):
        from pathlib import Path
        with self.assertRaises(FileNotFoundError):
            GlycoTwinPredictor(model_path=Path("nonexistent_model.pkl"))


if __name__ == "__main__":
    unittest.main()
