from pathlib import Path
import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
MODELS_DIR = PROJECT_ROOT / "models"


# IMPORTANT:
# This order must exactly match build_sequences()
FEATURE_NAMES = [
    "age",
    "bmi",
    "hba1c",
    "fasting_glucose",
    "insulin",
    "personal_baseline",
]


def main():

    MODELS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    X = np.load(
        PROCESSED_DIR / "X_static.npy"
    ).astype(np.float32)

    train_mask = np.load(
        PROCESSED_DIR / "train_mask.npy"
    )

    val_mask = np.load(
        PROCESSED_DIR / "val_mask.npy"
    )

    test_mask = np.load(
        PROCESSED_DIR / "test_mask.npy"
    )

    print(
        "GLYCOTWIN STATIC PREPROCESSING"
    )

    print("=" * 50)

    print(
        f"Original shape: {X.shape}"
    )

    print(
        f"Train samples : "
        f"{train_mask.sum():,}"
    )

    print(
        f"Val samples   : "
        f"{val_mask.sum():,}"
    )

    print(
        f"Test samples  : "
        f"{test_mask.sum():,}"
    )

    # ========================================================
    # TRAINING-ONLY STATISTICS
    # ========================================================

    X_train = X[train_mask]

    medians = np.zeros(
        X.shape[1],
        dtype=np.float32,
    )

    means = np.zeros(
        X.shape[1],
        dtype=np.float32,
    )

    stds = np.ones(
        X.shape[1],
        dtype=np.float32,
    )

    for feature_idx, feature_name in enumerate(
        FEATURE_NAMES
    ):

        values = X_train[
            :,
            feature_idx,
        ]

        values = values[
            np.isfinite(values)
        ]

        if len(values) == 0:

            raise ValueError(
                f"No valid training values "
                f"found for {feature_name}"
            )

        medians[feature_idx] = np.median(
            values
        )

        means[feature_idx] = np.mean(
            values
        )

        stds[feature_idx] = np.std(
            values
        )

        if stds[feature_idx] < 1e-6:

            stds[feature_idx] = 1.0

        print(
            f"{feature_name:20s} "
            f"median={medians[feature_idx]:10.3f} "
            f"mean={means[feature_idx]:10.3f} "
            f"std={stds[feature_idx]:10.3f}"
        )

    # ========================================================
    # IMPUTE MISSING VALUES
    # ========================================================

    X_processed = X.copy()

    for feature_idx in range(
        X.shape[1]
    ):

        missing = ~np.isfinite(
            X_processed[:, feature_idx]
        )

        X_processed[
            missing,
            feature_idx
        ] = medians[feature_idx]

    # ========================================================
    # STANDARDIZE
    #
    # IMPORTANT:
    # Statistics are calculated from TRAINING patients only.
    # ========================================================

    for feature_idx in range(
        X.shape[1]
    ):

        X_processed[
            :,
            feature_idx
        ] = (
            X_processed[
                :,
                feature_idx
            ]
            - means[feature_idx]
        ) / stds[feature_idx]

    # ========================================================
    # SAVE
    # ========================================================

    output_path = (
        PROCESSED_DIR
        / "X_static_processed.npy"
    )

    np.save(
        output_path,
        X_processed.astype(
            np.float32
        ),
    )

    np.save(
        MODELS_DIR
        / "static_medians.npy",
        medians,
    )

    np.save(
        MODELS_DIR
        / "static_means.npy",
        means,
    )

    np.save(
        MODELS_DIR
        / "static_stds.npy",
        stds,
    )

    # ========================================================
    # VERIFICATION
    # ========================================================

    print("\nVerification")
    print("-" * 50)

    print(
        "Remaining NaNs:",
        int(
            np.isnan(
                X_processed
            ).sum()
        ),
    )

    print(
        "Remaining inf:",
        int(
            np.isinf(
                X_processed
            ).sum()
        ),
    )

    print(
        "Processed shape:",
        X_processed.shape,
    )

    print("\nSaved:")

    print(
        f"  {output_path}"
    )

    print(
        f"  {MODELS_DIR / 'static_medians.npy'}"
    )

    print(
        f"  {MODELS_DIR / 'static_means.npy'}"
    )

    print(
        f"  {MODELS_DIR / 'static_stds.npy'}"
    )


if __name__ == "__main__":
    main()