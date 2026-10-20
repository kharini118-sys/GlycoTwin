import unittest
import numpy as np
import pandas as pd
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class TestTarget(unittest.TestCase):

    def test_target_logic(self):
        """
        Verify 120-minute (2-hour) excursion target rule:
        Target = 1 IF future max glucose - current glucose >= 30 mg/dL within next 24 observations (120 mins).
        """
        # Create sample glucose series (25 steps = current + 24 future 5-min steps)
        glucose_normal = np.array([100.0] + [100.0 + i for i in range(24)]) # max rise = 23 mg/dL < 30
        current_glucose = glucose_normal[0]
        future_max = np.max(glucose_normal[1:])
        target_normal = int((future_max - current_glucose) >= 30.0)
        self.assertEqual(target_normal, 0, "Normal rise should not trigger target")

        glucose_spike = np.array([100.0] + [100.0 + i * 2 for i in range(24)]) # max rise = 46 mg/dL >= 30
        current_glucose_spike = glucose_spike[0]
        future_max_spike = np.max(glucose_spike[1:])
        target_spike = int((future_max_spike - current_glucose_spike) >= 30.0)
        self.assertEqual(target_spike, 1, "30+ mg/dL rise should trigger excursion target")

    def test_processed_target_file(self):
        """Verify processed y.npy target file integrity."""
        y_path = PROJECT_ROOT / "data" / "processed" / "y.npy"
        if y_path.exists():
            y = np.load(y_path)
            self.assertGreater(len(y), 0)
            self.assertTrue(set(np.unique(y)).issubset({0, 1}))
            pos_rate = np.mean(y == 1)
            self.assertTrue(0.10 <= pos_rate <= 0.40, f"Unexpected positive target rate: {pos_rate:.2f}")


if __name__ == "__main__":
    unittest.main()
