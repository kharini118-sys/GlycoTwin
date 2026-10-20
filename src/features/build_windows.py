from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from src.data.load_cgmacros import load_all_participants
from src.data.clean_cgmacros import clean_cgmacros


SEQUENCE_LENGTH = 12       # 12 x 5-minute samples = 60 minutes
SAMPLE_MINUTES = 5
HORIZON_MINUTES = 120
THRESHOLD = 30.0

DYNAMIC_COLUMNS = [
    "glucose",
    "heart_rate",
    "activity_calories",
    "mets",
]


def build_dataset(df):

    all_sequences = []
    all_static = []
    all_targets = []
    all_subjects = []
    all_timestamps = []

    for subject_id, patient in df.groupby("subject_id"):

        print(f"Processing participant {int(subject_id)}...")

        patient = (
            patient
            .sort_values("timestamp")
            .set_index("timestamp")
        )

        # Resample to exactly 5-minute intervals.
        dynamic = patient[DYNAMIC_COLUMNS].resample("5min").mean()

        # Forward-fill short gaps.
        dynamic = dynamic.ffill(limit=3)

        # Glucose must exist.
        dynamic = dynamic.dropna(subset=["glucose"])

        if len(dynamic) < SEQUENCE_LENGTH + 24:
            continue

        # ---------------------------------------------------------
        # Future maximum glucose over the next 120 minutes
        # ---------------------------------------------------------

        future_max = (
            dynamic["glucose"]
            .shift(-1)
            .rolling(
                window=24,
                min_periods=24
            )
            .max()
            .shift(-23)
        )

        target = (
            future_max - dynamic["glucose"] >= THRESHOLD
        ).astype(float)

        target[future_max.isna()] = np.nan

        # ---------------------------------------------------------
        # Static features
        # ---------------------------------------------------------

        first_row = patient.iloc[0]

        static_values = np.array([
            first_row["age"],
            first_row["bmi"],
            first_row["hba1c"],
            first_row["fasting_glucose"],
            first_row["insulin"],
            patient["glucose"].median(),
        ], dtype=np.float32)

        # ---------------------------------------------------------
        # NumPy sliding windows
        # ---------------------------------------------------------

        values = dynamic.to_numpy(dtype=np.float32)

        windows = np.lib.stride_tricks.sliding_window_view(
            values,
            window_shape=SEQUENCE_LENGTH,
            axis=0,
        )

        # Shape produced by NumPy is:
        # (samples, features, sequence)
        windows = np.transpose(windows, (0, 2, 1))

        # Target begins at the final point of each sequence.
        target_values = target.to_numpy()

        valid_length = min(
            len(windows),
            len(target_values) - SEQUENCE_LENGTH + 1
        )

        windows = windows[:valid_length]

        target_values = target_values[
            SEQUENCE_LENGTH - 1 :
            SEQUENCE_LENGTH - 1 + valid_length
        ]

        valid = ~np.isnan(target_values)

        windows = windows[valid]
        target_values = target_values[valid]

        if len(windows) == 0:
            continue

        static_matrix = np.tile(
            static_values,
            (len(windows), 1)
        )

        timestamps = dynamic.index[
            SEQUENCE_LENGTH - 1 :
            SEQUENCE_LENGTH - 1 + valid_length
        ][valid]

        all_sequences.append(windows)
        all_static.append(static_matrix)
        all_targets.append(target_values.astype(np.int64))
        all_subjects.append(
            np.full(
                len(windows),
                int(subject_id),
                dtype=np.int32,
            )
        )
        all_timestamps.extend(timestamps)

    X_sequence = np.concatenate(all_sequences)
    X_static = np.concatenate(all_static)
    y = np.concatenate(all_targets)
    subjects = np.concatenate(all_subjects)

    timestamps = pd.to_datetime(all_timestamps)

    return X_sequence, X_static, y, subjects, timestamps


if __name__ == "__main__":

    print("Loading CGMacros...")

    raw = load_all_participants()
    clean = clean_cgmacros(raw)

    print("Building optimized 5-minute dataset...")

    X_sequence, X_static, y, subjects, timestamps = build_dataset(clean)

    print("\nDATASET COMPLETE")
    print("=" * 60)

    print("Sequence:", X_sequence.shape)
    print("Static:  ", X_static.shape)
    print("Target:  ", y.shape)

    print("\nTarget distribution:")

    for value in [0, 1]:
        count = int((y == value).sum())
        print(
            f"Class {value}: "
            f"{count:,} "
            f"({count / len(y) * 100:.2f}%)"
        )

    print("\nParticipants:", len(np.unique(subjects)))

    # -------------------------------------------------------------
    # Save processed dataset
    # -------------------------------------------------------------

    output_dir = PROJECT_ROOT / "data" / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)

    np.save(output_dir / "X_sequence.npy", X_sequence)
    np.save(output_dir / "X_static.npy", X_static)
    np.save(output_dir / "y.npy", y)
    np.save(output_dir / "subjects.npy", subjects)

    pd.DataFrame({
        "subject_id": subjects,
        "timestamp": timestamps,
    }).to_csv(
        output_dir / "metadata.csv",
        index=False,
    )

    print("\nSaved to:")
    print(output_dir)

    print("\nFeature construction complete.")