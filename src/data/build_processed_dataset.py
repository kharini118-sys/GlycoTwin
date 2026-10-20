from pathlib import Path
import sys

import numpy as np
import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_RAW = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "cgmacros"
    / "CGMacros"
)

PROCESSED_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
)

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# Make project imports work reliably
sys.path.insert(
    0,
    str(PROJECT_ROOT),
)


from src.data.load_cgmacros import (
    load_all_participants,
)

from src.data.clean_cgmacros import (
    clean_cgmacros,
)

from src.evaluation.build_targets_fast import (
    build_targets,
)


# ============================================================
# CONFIGURATION
# ============================================================

FREQ = "5min"

SEQUENCE_LENGTH = 12

# 12 x 5 minutes = 60 minutes of history


DYNAMIC_FEATURES = [
    "glucose",
    "heart_rate",
    "activity_calories",
    "mets",
]


STATIC_FEATURES = [
    "age",
    "bmi",
    "hba1c",
    "fasting_glucose",
    "insulin",
    "personal_baseline",
]


# ============================================================
# RESAMPLING
# ============================================================

def resample_subject(df):
    """
    Resample one participant to a 5-minute grid.

    IMPORTANT:

    Two glucose concepts are maintained:

    1. target_glucose
       - Actual observed glucose only.
       - NEVER forward-filled.
       - Used exclusively for target construction.

    2. glucose
       - Model-input glucose.
       - May be forward-filled for a short period.
       - Used by the temporal model.

    This separation prevents forward-filled glucose from
    contaminating the prediction target.
    """

    df = df.copy()

    df["timestamp"] = pd.to_datetime(
        df["timestamp"]
    )

    df = (
        df.sort_values("timestamp")
        .set_index("timestamp")
    )

    # --------------------------------------------------------
    # Numeric columns
    # --------------------------------------------------------

    numeric_columns = [
        "glucose",
        "dexcom_glucose",
        "heart_rate",
        "activity_calories",
        "mets",
        "meal_calories",
        "carbs",
        "protein",
        "fat",
        "fiber",
        "amount_consumed",
    ]

    available_columns = [
        column
        for column in numeric_columns
        if column in df.columns
    ]

    # --------------------------------------------------------
    # Resample numeric measurements
    # --------------------------------------------------------

    resampled = (
        df[available_columns]
        .resample(FREQ)
        .mean()
    )

    # --------------------------------------------------------
    # CRITICAL LEAKAGE PROTECTION
    # --------------------------------------------------------

    # Preserve the actual observed glucose BEFORE
    # any forward filling.
    #
    # This column is used only to construct the target.

    resampled["target_glucose"] = (
        resampled["glucose"]
    )

    # Record whether a glucose measurement was actually
    # available at this 5-minute grid point.

    resampled["glucose_observed"] = (
        resampled["target_glucose"].notna()
    )

    # --------------------------------------------------------
    # Model-input imputation
    # --------------------------------------------------------

    # Forward-fill only short gaps.
    #
    # limit=3 means at most 15 minutes:
    #
    # t
    # t+5
    # t+10
    # t+15
    #
    # Longer gaps remain NaN.

    for column in [
        "glucose",
        "heart_rate",
        "activity_calories",
        "mets",
    ]:

        if column in resampled.columns:

            resampled[column] = (
                resampled[column]
                .ffill(limit=3)
            )

    # --------------------------------------------------------
    # Restore participant ID
    # --------------------------------------------------------

    resampled["subject_id"] = (
        df["subject_id"]
        .iloc[0]
    )

    # --------------------------------------------------------
    # Meal information
    # --------------------------------------------------------

    # Meal/nutrition values are event-like.
    # Preserve whether anything occurred during the interval.

    if "meal_type" in df.columns:

        meal_type = (
            df["meal_type"]
            .resample(FREQ)
            .agg(
                lambda x: (
                    x.dropna()
                    .iloc[0]
                    if len(x.dropna()) > 0
                    else np.nan
                )
            )
        )

        resampled["meal_type"] = meal_type

    # --------------------------------------------------------
    # Restore index
    # --------------------------------------------------------

    resampled = (
        resampled
        .reset_index()
    )

    return resampled


# ============================================================
# RESAMPLE ALL PARTICIPANTS
# ============================================================

def resample_all(df):
    """
    Resample every participant independently.

    This prevents one participant's measurements from
    affecting another participant.
    """

    frames = []

    for subject_id, group in df.groupby(
        "subject_id",
        sort=True,
    ):

        print(
            f"Resampling participant {int(subject_id)}..."
        )

        participant = resample_subject(
            group
        )

        frames.append(
            participant
        )

    result = pd.concat(
        frames,
        ignore_index=True,
    )

    result = (
        result
        .sort_values(
            [
                "subject_id",
                "timestamp",
            ]
        )
        .reset_index(drop=True)
    )

    return result


# ============================================================
# STATIC FEATURES
# ============================================================

def add_static_features(
    dynamic,
    original,
):
    """
    Attach participant-level clinical variables.

    These values are static for the participant.
    """

    static_columns = [
        "subject_id",
        "age",
        "gender",
        "bmi",
        "hba1c",
        "fasting_glucose",
        "insulin",
    ]

    available_columns = [
        column
        for column in static_columns
        if column in original.columns
    ]

    static = (
        original[
            available_columns
        ]
        .drop_duplicates(
            "subject_id"
        )
    )

    dynamic = dynamic.merge(
        static,
        on="subject_id",
        how="left",
    )

    return dynamic


# ============================================================
# PERSONAL BASELINE
# ============================================================

def add_historical_baseline(
    df,
    min_history=12,
):
    """
    Calculate a participant-specific historical glucose
    baseline using ONLY previous glucose observations.

    No current or future glucose is included.

    Primary baseline:
        rolling historical median with >=12 previous
        observations.

    Fallback:
        median of whatever previous observations exist.
    """

    df = df.copy()

    df["timestamp"] = pd.to_datetime(
        df["timestamp"]
    )

    df = (
        df.sort_values(
            [
                "subject_id",
                "timestamp",
            ]
        )
        .reset_index(drop=True)
    )

    # Shift first so current glucose is excluded.
    previous_glucose = (
        df.groupby(
            "subject_id"
        )["glucose"]
        .shift(1)
    )

    # Historical median with sufficient history.
    historical_median = (
        previous_glucose
        .groupby(
            df["subject_id"]
        )
        .expanding(
            min_periods=min_history
        )
        .median()
        .reset_index(
            level=0,
            drop=True,
        )
    )

    # Early-history fallback.
    historical_fallback = (
        previous_glucose
        .groupby(
            df["subject_id"]
        )
        .expanding(
            min_periods=1
        )
        .median()
        .reset_index(
            level=0,
            drop=True,
        )
    )

    df["personal_baseline"] = (
        historical_median
        .fillna(
            historical_fallback
        )
    )

    return df


# ============================================================
# TARGET CONSTRUCTION
# ============================================================

def add_targets(df):
    """
    Construct the 2-hour glucose-excursion target.

    IMPORTANT:

    build_targets() receives target_glucose renamed to
    glucose.

    target_glucose contains ONLY actual observed glucose
    measurements and has NOT been forward-filled.

    Therefore the target cannot be created from imputed
    future glucose.
    """

    target_input = df[
        [
            "subject_id",
            "timestamp",
            "target_glucose",
        ]
    ].copy()

    target_input = target_input.rename(
        columns={
            "target_glucose": "glucose"
        }
    )

    targets = build_targets(
        target_input
    )

    df = df.copy()

    df["target"] = targets

    return df


# ============================================================
# SEQUENCE BUILDING
# ============================================================

def build_sequences(df):
    """
    Build:

        X_sequence
            shape = samples x 12 x 4

        X_static
            shape = samples x 6

        y
            binary target

        subjects
            participant ID

        metadata
            useful audit information
    """

    sequence_features = DYNAMIC_FEATURES

    static_features = STATIC_FEATURES

    sequence_list = []
    static_list = []
    target_list = []
    subject_list = []
    timestamp_list = []

    for subject_id, group in df.groupby(
        "subject_id",
        sort=True,
    ):

        group = (
            group
            .sort_values("timestamp")
            .reset_index(drop=True)
        )

        dynamic_values = (
            group[
                sequence_features
            ]
            .to_numpy(
                dtype=np.float32
            )
        )

        static_values = (
            group[
                static_features
            ]
            .to_numpy(
                dtype=np.float32
            )
        )

        targets = (
            group["target"]
            .to_numpy(
                dtype=np.float32
            )
        )

        timestamps = (
            group["timestamp"]
            .to_numpy()
        )

        current_glucose = (
            group["glucose"]
            .to_numpy(
                dtype=np.float32
            )
        )

        # ----------------------------------------------------
        # Sliding windows
        # ----------------------------------------------------

        for end_idx in range(
            SEQUENCE_LENGTH - 1,
            len(group),
        ):

            start_idx = (
                end_idx
                - SEQUENCE_LENGTH
                + 1
            )

            sequence = dynamic_values[
                start_idx:end_idx + 1
            ]

            target = targets[
                end_idx
            ]

            # We need a valid target.
            if np.isnan(target):
                continue

            # Current glucose must exist.
            if np.isnan(
                current_glucose[end_idx]
            ):
                continue

            # Static features should be available.
            static_row = (
                static_values[end_idx]
            )

            if np.any(
                np.isnan(static_row)
            ):
                continue

            sequence_list.append(
                sequence
            )

            static_list.append(
                static_row
            )

            target_list.append(
                target
            )

            subject_list.append(
                subject_id
            )

            timestamp_list.append(
                timestamps[end_idx]
            )

    X_sequence = np.asarray(
        sequence_list,
        dtype=np.float32,
    )

    X_static = np.asarray(
        static_list,
        dtype=np.float32,
    )

    y = np.asarray(
        target_list,
        dtype=np.float32,
    )

    subjects = np.asarray(
        subject_list,
        dtype=np.int32,
    )

    metadata = pd.DataFrame({
        "subject_id": subjects,
        "timestamp": timestamp_list,
        "target": y,
    })

    return (
        X_sequence,
        X_static,
        y,
        subjects,
        metadata,
    )


# ============================================================
# DATASET AUDIT
# ============================================================

def print_audit(
    dynamic,
    X_sequence,
    X_static,
    y,
    subjects,
):
    """
    Print important leakage/data-quality statistics.
    """

    print()
    print("=" * 70)
    print("GLYCOTWIN DATASET AUDIT")
    print("=" * 70)

    print(
        f"Resampled rows: {len(dynamic):,}"
    )

    print(
        f"Participants: "
        f"{dynamic['subject_id'].nunique():,}"
    )

    print()

    # --------------------------------------------------------
    # Observed glucose
    # --------------------------------------------------------

    observed = (
        dynamic["target_glucose"]
        .notna()
        .sum()
    )

    print(
        "Observed glucose rows: "
        f"{observed:,}"
    )

    print(
        "Observed glucose missing: "
        f"{dynamic['target_glucose'].isna().sum():,}"
    )

    print()

    # --------------------------------------------------------
    # Model-input glucose
    # --------------------------------------------------------

    model_glucose_missing = (
        dynamic["glucose"]
        .isna()
        .sum()
    )

    print(
        "Model-input glucose missing: "
        f"{model_glucose_missing:,}"
    )

    # --------------------------------------------------------
    # Target
    # --------------------------------------------------------

    valid_target = (
        dynamic["target"]
        .notna()
    )

    print()

    print(
        "Valid target rows: "
        f"{valid_target.sum():,}"
    )

    if valid_target.sum() > 0:

        positive = (
            dynamic.loc[
                valid_target,
                "target",
            ]
            .sum()
        )

        total = (
            valid_target.sum()
        )

        print(
            f"Positive targets: "
            f"{int(positive):,}"
        )

        print(
            f"Negative targets: "
            f"{int(total - positive):,}"
        )

        print(
            f"Positive prevalence: "
            f"{positive / total:.3f}"
        )

    # --------------------------------------------------------
    # Final tensors
    # --------------------------------------------------------

    print()

    print(
        f"X_sequence shape: "
        f"{X_sequence.shape}"
    )

    print(
        f"X_static shape: "
        f"{X_static.shape}"
    )

    print(
        f"y shape: "
        f"{y.shape}"
    )

    print(
        f"Subjects: "
        f"{len(np.unique(subjects))}"
    )

    print()

    print(
        f"Sequence NaNs: "
        f"{np.isnan(X_sequence).sum():,}"
    )

    print(
        f"Static NaNs: "
        f"{np.isnan(X_static).sum():,}"
    )

    print(
        f"Target NaNs: "
        f"{np.isnan(y).sum():,}"
    )

    print("=" * 70)


# ============================================================
# SAVE DATASET
# ============================================================

def save_dataset(
    X_sequence,
    X_static,
    y,
    subjects,
    metadata,
):
    """
    Save processed arrays.
    """

    np.save(
        PROCESSED_DIR
        / "X_sequence.npy",
        X_sequence,
    )

    np.save(
        PROCESSED_DIR
        / "X_static.npy",
        X_static,
    )

    np.save(
        PROCESSED_DIR
        / "y.npy",
        y,
    )

    np.save(
        PROCESSED_DIR
        / "subjects.npy",
        subjects,
    )

    metadata.to_csv(
        PROCESSED_DIR
        / "metadata.csv",
        index=False,
    )

    print()
    print(
        "Saved processed dataset:"
    )

    print(
        PROCESSED_DIR
    )


# ============================================================
# MAIN PIPELINE
# ============================================================

def main():

    print()
    print("=" * 70)
    print("GLYCOTWIN PROCESSED DATASET BUILDER")
    print("=" * 70)

    # --------------------------------------------------------
    # 1. Load raw CGMacros
    # --------------------------------------------------------

    print()
    print("Loading raw CGMacros data...")

    raw = load_all_participants()

    print(
        f"Raw rows: {len(raw):,}"
    )

    # --------------------------------------------------------
    # 2. Clean
    # --------------------------------------------------------

    print()
    print("Cleaning data...")

    clean = clean_cgmacros(
        raw
    )

    print(
        f"Clean rows: {len(clean):,}"
    )

    # --------------------------------------------------------
    # 3. Resample
    # --------------------------------------------------------

    print()
    print(
        f"Resampling to {FREQ}..."
    )

    dynamic = resample_all(
        clean
    )

    print(
        f"Resampled rows: "
        f"{len(dynamic):,}"
    )

    # --------------------------------------------------------
    # 4. Add static features
    # --------------------------------------------------------

    print()
    print(
        "Adding static clinical features..."
    )

    dynamic = add_static_features(
        dynamic,
        clean,
    )

    # --------------------------------------------------------
    # 5. Personal baseline
    # --------------------------------------------------------

    print()
    print(
        "Calculating past-only personal baseline..."
    )

    dynamic = add_historical_baseline(
        dynamic
    )

    # --------------------------------------------------------
    # 6. Target
    # --------------------------------------------------------

    print()
    print(
        "Building target from observed glucose only..."
    )

    dynamic = add_targets(
        dynamic
    )

    # --------------------------------------------------------
    # 7. Build sequences
    # --------------------------------------------------------

    print()
    print(
        "Building temporal sequences..."
    )

    (
        X_sequence,
        X_static,
        y,
        subjects,
        metadata,
    ) = build_sequences(
        dynamic
    )

    # --------------------------------------------------------
    # 8. Audit
    # --------------------------------------------------------

    print_audit(
        dynamic,
        X_sequence,
        X_static,
        y,
        subjects,
    )

    # --------------------------------------------------------
    # 9. Save
    # --------------------------------------------------------

    save_dataset(
        X_sequence,
        X_static,
        y,
        subjects,
        metadata,
    )

    print()
    print(
        "GLYCOTWIN DATASET BUILD COMPLETE."
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()