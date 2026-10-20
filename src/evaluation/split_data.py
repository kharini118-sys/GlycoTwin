from pathlib import Path
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

# Fixed patient-level split.
# No participant can appear in more than one split.
TRAIN_SUBJECTS = [
    1, 2, 3, 6, 8, 10, 11, 12, 14, 15, 16,
    17, 18, 19, 21, 22, 23, 26, 30, 31, 32,
    33, 34, 36, 38, 41, 42, 43, 45, 47, 49
]

VAL_SUBJECTS = [
    5, 7, 13, 20, 28, 39, 48
]

TEST_SUBJECTS = [
    4, 9, 27, 29, 35, 44, 46
]


def main():
    subjects = np.load(PROCESSED_DIR / "subjects.npy")
    y = np.load(PROCESSED_DIR / "y.npy")

    train_subjects = set(TRAIN_SUBJECTS)
    val_subjects = set(VAL_SUBJECTS)
    test_subjects = set(TEST_SUBJECTS)

    # Safety checks
    assert train_subjects.isdisjoint(val_subjects)
    assert train_subjects.isdisjoint(test_subjects)
    assert val_subjects.isdisjoint(test_subjects)

    all_split_subjects = train_subjects | val_subjects | test_subjects
    dataset_subjects = set(np.unique(subjects))

    missing = dataset_subjects - all_split_subjects
    extra = all_split_subjects - dataset_subjects

    if missing:
        raise ValueError(f"Subjects missing from split: {sorted(missing)}")

    if extra:
        raise ValueError(f"Split contains subjects not in dataset: {sorted(extra)}")

    train_mask = np.isin(subjects, TRAIN_SUBJECTS)
    val_mask = np.isin(subjects, VAL_SUBJECTS)
    test_mask = np.isin(subjects, TEST_SUBJECTS)

    # Every sample must belong to exactly one split.
    assert np.all(train_mask.astype(int) +
                  val_mask.astype(int) +
                  test_mask.astype(int) == 1)

    np.save(PROCESSED_DIR / "train_mask.npy", train_mask)
    np.save(PROCESSED_DIR / "val_mask.npy", val_mask)
    np.save(PROCESSED_DIR / "test_mask.npy", test_mask)

    def report(name, mask, split_subjects):
        positives = int(y[mask].sum())
        total = int(mask.sum())
        negatives = total - positives
        prevalence = positives / total if total else 0

        print(f"\n{name}")
        print("-" * 40)
        print(f"Participants : {len(split_subjects)}")
        print(f"Samples      : {total:,}")
        print(f"Positive     : {positives:,}")
        print(f"Negative     : {negatives:,}")
        print(f"Prevalence   : {prevalence:.3f}")
        print(f"Subjects     : {sorted(split_subjects)}")

    print("GLYCOTWIN PATIENT-LEVEL SPLIT")
    print("=" * 50)

    report("TRAIN", train_mask, TRAIN_SUBJECTS)
    report("VALIDATION", val_mask, VAL_SUBJECTS)
    report("TEST", test_mask, TEST_SUBJECTS)

    print("\nSplit verification")
    print("-" * 40)
    print(f"Total samples: {len(subjects):,}")
    print(f"Train + Val + Test: {train_mask.sum() + val_mask.sum() + test_mask.sum():,}")
    print("Participant overlap: NONE")
    print("Split saved successfully.")


if __name__ == "__main__":
    main()