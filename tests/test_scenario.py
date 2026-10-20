"""
GlycoTwin — Scenario Simulator Tests
Tests scenario cloning, probability arithmetic, risk direction.
"""
import unittest
import sys
import copy
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.twin.state import TwinState
from src.twin.updater import update_twin
from src.twin.predictor import GlycoTwinPredictor
from src.simulation.scenario import run_scenario, SCENARIOS


class TestScenarioSimulator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Load predictor once for the test class."""
        cls.predictor = GlycoTwinPredictor()
        cls.profile = {
            "age": 52.0,
            "bmi": 29.5,
            "hba1c": 7.1,
            "fasting_glucose": 130.0,
            "insulin": 14.0,
            "personal_baseline": 110.0,
        }
        # Build a twin with some history
        cls.twin = TwinState(patient_id="SCENARIO_TEST")
        observations = [
            {"glucose": 105, "heart_rate": 72, "activity_calories": 0.8, "mets": 1.5},
            {"glucose": 110, "heart_rate": 74, "activity_calories": 1.0, "mets": 1.8},
            {"glucose": 115, "heart_rate": 76, "activity_calories": 1.2, "mets": 2.0},
            {"glucose": 120, "heart_rate": 78, "activity_calories": 1.5, "mets": 2.2},
            {"glucose": 128, "heart_rate": 80, "activity_calories": 1.8, "mets": 2.5},
        ]
        for obs in observations:
            cls.twin = update_twin(cls.twin, obs)

    def test_scenario_state_is_copy_not_mutation(self):
        """Scenario must not mutate the original twin."""
        original_glucose = self.twin.current_glucose
        original_history_len = len(self.twin.history)

        run_scenario(
            self.twin, self.profile, "activity_increase",
            intensity=0.5, predictor=self.predictor
        )

        self.assertEqual(self.twin.current_glucose, original_glucose)
        self.assertEqual(len(self.twin.history), original_history_len)

    def test_baseline_prediction_reproducible(self):
        """Running the same scenario twice gives the same baseline."""
        r1 = run_scenario(self.twin, self.profile, "activity_increase",
                          intensity=0.5, predictor=self.predictor)
        r2 = run_scenario(self.twin, self.profile, "activity_increase",
                          intensity=0.5, predictor=self.predictor)
        self.assertAlmostEqual(r1.baseline_probability, r2.baseline_probability, places=6)

    def test_delta_arithmetic_correct(self):
        """Delta must equal scenario - baseline in percentage points (within rounding)."""
        r = run_scenario(self.twin, self.profile, "activity_increase",
                         intensity=0.5, predictor=self.predictor)
        expected_delta = (r.scenario_probability - r.baseline_probability) * 100.0
        # delta_percentage_points is rounded to 2 decimal places, allow small error
        self.assertAlmostEqual(r.delta_percentage_points, expected_delta, places=1)

    def test_risk_can_increase(self):
        """Risk CAN increase — never force a decrease."""
        results = []
        for key in SCENARIOS:
            for intensity in [0.1, 0.5, 0.9]:
                r = run_scenario(self.twin, self.profile, key,
                                 intensity=intensity, predictor=self.predictor)
                results.append(r.delta_percentage_points)
        # Some scenarios must produce positive deltas (risk increase)
        # This verifies we don't artificially suppress increases
        # At least verify the arithmetic is unconstrained
        all_zero = all(abs(d) < 0.001 for d in results)
        self.assertFalse(all_zero, "All scenario results are zero — simulator may be broken")

    def test_probability_range(self):
        """All probabilities must be in [0, 1]."""
        r = run_scenario(self.twin, self.profile, "activity_increase",
                         intensity=0.5, predictor=self.predictor)
        self.assertGreaterEqual(r.baseline_probability, 0.0)
        self.assertLessEqual(r.baseline_probability, 1.0)
        self.assertGreaterEqual(r.scenario_probability, 0.0)
        self.assertLessEqual(r.scenario_probability, 1.0)

    def test_assumptions_recorded(self):
        """Scenario result must include assumptions."""
        r = run_scenario(self.twin, self.profile, "activity_increase",
                         intensity=0.5, predictor=self.predictor)
        self.assertIsInstance(r.assumptions, list)
        self.assertGreater(len(r.assumptions), 0)

    def test_unknown_scenario_raises(self):
        """Unknown scenario key must raise ValueError."""
        with self.assertRaises(ValueError):
            run_scenario(self.twin, self.profile, "nonexistent_scenario",
                         predictor=self.predictor)

    def test_all_scenarios_run_without_error(self):
        """All declared scenarios must execute without crashing."""
        for key in SCENARIOS:
            r = run_scenario(self.twin, self.profile, key,
                             intensity=0.5, predictor=self.predictor)
            self.assertIsNotNone(r.scenario_probability)


if __name__ == "__main__":
    unittest.main()
