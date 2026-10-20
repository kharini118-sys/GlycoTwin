"""
test_data_loader.py — Tests for CGMacros data loading and cleaning.

Tests that require the raw dataset are skipped when the dataset is not present,
with a clear reason. Tests that validate schema, types, and contracts on the loaded
data are only run when the data is available.
"""

import unittest
import pandas as pd
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ── Check raw dataset availability ───────────────────────────────────────────
_RAW_BIO = PROJECT_ROOT / "data" / "raw" / "cgmacros" / "CGMacros" / "bio.csv"
_DATASET_AVAILABLE = _RAW_BIO.exists()
_SKIP_REASON = (
    "Raw CGMacros dataset not present at data/raw/cgmacros/CGMacros/bio.csv. "
    "Download from https://physionet.org/content/cgmacros/1.0.0/ and place in that directory."
)


@unittest.skipUnless(_DATASET_AVAILABLE, _SKIP_REASON)
class TestDataLoaderWithRawData(unittest.TestCase):
    """Integration tests — only run when the raw CGMacros dataset is present."""

    def test_load_bio_returns_dataframe(self):
        """Verify static patient bio loading returns a non-empty DataFrame."""
        from src.data.load_cgmacros import load_bio
        bio = load_bio()
        self.assertIsInstance(bio, pd.DataFrame)
        self.assertFalse(bio.empty)

    def test_load_bio_participant_count(self):
        """CGMacros v1.0.0 has 45 participants."""
        from src.data.load_cgmacros import load_bio
        bio = load_bio()
        self.assertIn("subject_id", bio.columns)
        self.assertEqual(len(bio), 45,
            f"Expected 45 participants in bio.csv, got {len(bio)}. "
            "If using a different dataset version, update this assertion.")

    def test_clean_cgmacros_schema(self):
        """Verify data cleaning produces the canonical 11-column schema."""
        from src.data.load_cgmacros import load_all_participants
        from src.data.clean_cgmacros import clean_cgmacros

        raw = load_all_participants()
        clean = clean_cgmacros(raw)

        required_columns = [
            "subject_id",
            "timestamp",
            "glucose",
            "heart_rate",
            "activity_calories",
            "mets",
            "age",
            "bmi",
            "hba1c",
            "fasting_glucose",
            "insulin",
        ]
        for col in required_columns:
            self.assertIn(col, clean.columns, f"Missing expected column after cleaning: {col}")

    def test_clean_cgmacros_timestamp_type(self):
        """Timestamps must be parsed as datetime64 after cleaning."""
        from src.data.load_cgmacros import load_all_participants
        from src.data.clean_cgmacros import clean_cgmacros

        raw = load_all_participants()
        clean = clean_cgmacros(raw)
        self.assertTrue(
            pd.api.types.is_datetime64_any_dtype(clean["timestamp"]),
            "timestamp column must be datetime64 dtype after cleaning"
        )

    def test_clean_cgmacros_glucose_not_all_nan(self):
        """Glucose values must not all be NaN after cleaning."""
        from src.data.load_cgmacros import load_all_participants
        from src.data.clean_cgmacros import clean_cgmacros

        raw = load_all_participants()
        clean = clean_cgmacros(raw)
        self.assertFalse(
            clean["glucose"].isna().all(),
            "All glucose values are NaN after cleaning — check the CGM column mapping"
        )

    def test_no_participant_id_in_numeric_features(self):
        """subject_id must not appear as a numeric predictor — only as an identifier."""
        from src.data.load_cgmacros import load_all_participants
        from src.data.clean_cgmacros import clean_cgmacros

        raw = load_all_participants()
        clean = clean_cgmacros(raw)
        # subject_id should be an integer identifier column, not float/continuous
        # (it should NOT be passed directly to a model as a feature)
        self.assertIn("subject_id", clean.columns)
        # The feature builder does not include subject_id — verify it is non-numeric or
        # at minimum that the column exists only as metadata
        numeric_cols = clean.select_dtypes(include=["float64", "float32"]).columns
        self.assertNotIn("subject_id", numeric_cols,
            "subject_id should not be a float feature — it is a participant identifier")


class TestDataLoaderSkipBehavior(unittest.TestCase):
    """Meta-tests that verify the skip mechanism works correctly."""

    def test_dataset_availability_check_runs(self):
        """Confirms the availability flag is computed without error."""
        self.assertIsInstance(_DATASET_AVAILABLE, bool)

    def test_bio_path_constant_is_absolute(self):
        """The bio path must be an absolute path for reliable skip detection."""
        self.assertTrue(_RAW_BIO.is_absolute(),
            "_RAW_BIO path must be absolute to reliably detect dataset presence")

    @unittest.skipIf(_DATASET_AVAILABLE, "Dataset is present — skip guard not needed")
    def test_skip_message_is_informative(self):
        """When dataset is absent, the skip reason should contain the URL."""
        self.assertIn("physionet.org", _SKIP_REASON)
        self.assertIn("cgmacros", _SKIP_REASON)


if __name__ == "__main__":
    unittest.main()
