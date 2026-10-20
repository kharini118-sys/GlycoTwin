from pathlib import Path
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
MODELS_DIR = PROJECT_ROOT / "models"

FEATURE_NAMES = [
    "glucose",
    "heart_rate",
    "activity_calories",
    "mets",
]


def main():
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    X = np.load(PROCESSED_DIR / "X_sequence.npy").astype(np.float32)

    train_mask = np.load(PROCESSED_DIR / "train_mask.npy")
    val_mask = np.load(PROCESSED_DIR / "val_mask.npy")
    test_mask = np.load(PROCESSED_DIR / "test_mask.npy")

    print("GLYCOTWIN SEQUENCE PREPROCESSING")
    print("=" * 50)

    print(f"Original shape: {X.shape}")
    print(f"Train samples : {train_mask.sum():,}")
    print(f"Val samples   : {val_mask.sum():,}")
    print(f"Test samples  : {test_mask.sum():,}")

    # ---------------------------------------------------------
    # 1. Calculate statistics ONLY from training data
    # ---------------------------------------------------------

    X_train = X[train_mask]

    medians = np.zeros(X.shape[-1], dtype=np.float32)
    means = np.zeros(X.shape[-1], dtype=np.float32)
    stds = np.ones(X.shape[-1], dtype=np.float32)

    for feature_idx, feature_name in enumerate(FEATURE_NAMES):
        values = X_train[:, :, feature_idx].reshape(-1)
        values = values[np.isfinite(values)]

        medians[feature_idx] = np.median(values)
        means[feature_idx] = np.mean(values)
        stds[feature_idx] = np.std(values)

        # Safety against zero-variance features
        if stds[feature_idx] < 1e-6:
            stds[feature_idx] = 1.0

        print(
            f"{feature_name:18s} "
            f"median={medians[feature_idx]:8.3f} "
            f"mean={means[feature_idx]:8.3f} "
            f"std={stds[feature_idx]:8.3f}"
        )

    # ---------------------------------------------------------
    # 2. Impute missing values
    # ---------------------------------------------------------

    X_processed = X.copy()

    for feature_idx in range(X.shape[-1]):
        missing = ~np.isfinite(X_processed[:, :, feature_idx])

        X_processed[:, :, feature_idx][missing] = medians[feature_idx]

    # ---------------------------------------------------------
    # 3. Standardize using TRAINING statistics only
    # ---------------------------------------------------------

    for feature_idx in range(X.shape[-1]):
        X_processed[:, :, feature_idx] = (
            X_processed[:, :, feature_idx] - means[feature_idx]
        ) / stds[feature_idx]

    # ---------------------------------------------------------
    # 4. Save processed sequences
    # ---------------------------------------------------------

    output_path = PROCESSED_DIR / "X_sequence_processed.npy"
    np.save(output_path, X_processed.astype(np.float32))

    np.save(MODELS_DIR / "sequence_medians.npy", medians)
    np.save(MODELS_DIR / "sequence_means.npy", means)
    np.save(MODELS_DIR / "sequence_stds.npy", stds)

    # ---------------------------------------------------------
    # 5. Verification
    # ---------------------------------------------------------

    train_processed = X_processed[train_mask]

    print("\nVerification")
    print("-" * 50)

    print(
        "Remaining NaNs:",
        int(np.isnan(X_processed).sum())
    )

    print(
        "Remaining inf:",
        int(np.isinf(X_processed).sum())
    )

    print(
        "Processed train mean:",
        float(np.mean(train_processed))
    )

    print(
        "Processed train std:",
        float(np.std(train_processed))
    )

    print("\nSaved:")
    print(f"  {output_path}")
    print(f"  {MODELS_DIR / 'sequence_medians.npy'}")
    print(f"  {MODELS_DIR / 'sequence_means.npy'}")
    print(f"  {MODELS_DIR / 'sequence_stds.npy'}")


if __name__ == "__main__":
    main()