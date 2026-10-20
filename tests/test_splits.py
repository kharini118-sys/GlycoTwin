import unittest
import numpy as np
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class TestSplits(unittest.TestCase):

    def test_patient_level_splits(self):
        """
        Verify strict patient-level split (31 Train, 7 Val, 7 Test) with ZERO participant overlap.
        """
        processed_dir = PROJECT_ROOT / "data" / "processed"

        subjects_file = processed_dir / "subjects.npy"
        train_mask_file = processed_dir / "train_mask.npy"
        val_mask_file = processed_dir / "val_mask.npy"
        test_mask_file = processed_dir / "test_mask.npy"

        if subjects_file.exists():
            subjects = np.load(subjects_file)
            train_mask = np.load(train_mask_file)
            val_mask = np.load(val_mask_file)
            test_mask = np.load(test_mask_file)

            train_subjects = set(subjects[train_mask])
            val_subjects = set(subjects[val_mask])
            test_subjects = set(subjects[test_mask])

            # Verify zero participant overlap across sets
            self.assertEqual(len(train_subjects.intersection(val_subjects)), 0, "Data Leakage: Train & Val overlap!")
            self.assertEqual(len(train_subjects.intersection(test_subjects)), 0, "Data Leakage: Train & Test overlap!")
            self.assertEqual(len(val_subjects.intersection(test_subjects)), 0, "Data Leakage: Val & Test overlap!")

            # Verify participant split counts (31 Train, 7 Val, 7 Test)
            self.assertEqual(len(train_subjects), 31, f"Expected 31 train subjects, got {len(train_subjects)}")
            self.assertEqual(len(val_subjects), 7, f"Expected 7 val subjects, got {len(val_subjects)}")
            self.assertEqual(len(test_subjects), 7, f"Expected 7 test subjects, got {len(test_subjects)}")


if __name__ == "__main__":
    unittest.main()
