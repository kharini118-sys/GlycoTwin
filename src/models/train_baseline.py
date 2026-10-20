from pathlib import Path

import numpy as np

from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
MODEL_DIR = PROJECT_ROOT / "models"

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# LOAD DATA
# ============================================================

X_sequence = np.load(
    PROCESSED_DIR / "X_sequence.npy"
).astype(np.float32)

X_static = np.load(
    PROCESSED_DIR / "X_static.npy"
).astype(np.float32)

y = np.load(
    PROCESSED_DIR / "y.npy"
).astype(np.int32)

train_mask = np.load(
    PROCESSED_DIR / "train_mask.npy"
)

val_mask = np.load(
    PROCESSED_DIR / "val_mask.npy"
)

test_mask = np.load(
    PROCESSED_DIR / "test_mask.npy"
)


# ============================================================
# FEATURE CONSTRUCTION
# ============================================================

def make_features(
    X_sequence,
    X_static,
):
    """
    Convert the 12 x 4 temporal sequence into
    interpretable summary statistics.

    Dynamic feature order:

        0 = glucose
        1 = heart_rate
        2 = activity_calories
        3 = mets

    Static feature order:

        0 = age
        1 = bmi
        2 = hba1c
        3 = fasting_glucose
        4 = insulin
        5 = personal_baseline
    """

    glucose = X_sequence[:, :, 0]

    heart_rate = X_sequence[:, :, 1]

    activity = X_sequence[:, :, 2]

    mets = X_sequence[:, :, 3]

    features = np.column_stack([
        # ----------------------------------------------------
        # Glucose state
        # ----------------------------------------------------

        glucose[:, -1],

        glucose.mean(axis=1),

        glucose.std(axis=1),

        glucose.min(axis=1),

        glucose.max(axis=1),

        glucose[:, -1]
        - glucose[:, 0],

        glucose[:, -1]
        - glucose[:, -4],

        # ----------------------------------------------------
        # Heart rate
        # ----------------------------------------------------

        heart_rate[:, -1],

        heart_rate.mean(axis=1),

        heart_rate.std(axis=1),

        # ----------------------------------------------------
        # Activity
        # ----------------------------------------------------

        activity[:, -1],

        activity.mean(axis=1),

        activity.sum(axis=1),

        activity.max(axis=1),

        # ----------------------------------------------------
        # METs
        # ----------------------------------------------------

        mets[:, -1],

        mets.mean(axis=1),

        mets.max(axis=1),

        # ----------------------------------------------------
        # Static patient state
        # ----------------------------------------------------

        X_static[:, 0],  # age
        X_static[:, 1],  # bmi
        X_static[:, 2],  # hba1c
        X_static[:, 3],  # fasting glucose
        X_static[:, 4],  # insulin

        # Personal baseline
        X_static[:, 5],

        # Current glucose relative to personal baseline
        glucose[:, -1]
        - X_static[:, 5],
    ])

    return features.astype(
        np.float32
    )


X = make_features(
    X_sequence,
    X_static,
)


print("GLYCOTWIN LOGISTIC REGRESSION")
print("=" * 60)

print(
    f"Feature matrix: {X.shape}"
)

print(
    f"Train: {train_mask.sum():,}"
)

print(
    f"Validation: {val_mask.sum():,}"
)

print(
    f"Test: {test_mask.sum():,}"
)


# ============================================================
# SPLITS
# ============================================================

X_train = X[train_mask]
X_val = X[val_mask]
X_test = X[test_mask]

y_train = y[train_mask]
y_val = y[val_mask]
y_test = y[test_mask]


# ============================================================
# MODEL
# ============================================================

model = Pipeline([
    (
        "imputer",
        SimpleImputer(
            strategy="median"
        ),
    ),

    (
        "scaler",
        StandardScaler(),
    ),

    (
        "classifier",
        LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=42,
        ),
    ),
])


# ============================================================
# TRAIN
# ============================================================

print("\nTraining...")

model.fit(
    X_train,
    y_train,
)


# ============================================================
# EVALUATION
# ============================================================

def evaluate(
    name,
    model,
    X,
    y,
):

    probability = model.predict_proba(
        X
    )[:, 1]

    prediction = (
        probability >= 0.5
    ).astype(int)

    auroc = roc_auc_score(
        y,
        probability,
    )

    ap = average_precision_score(
        y,
        probability,
    )

    precision = precision_score(
        y,
        prediction,
        zero_division=0,
    )

    recall = recall_score(
        y,
        prediction,
        zero_division=0,
    )

    f1 = f1_score(
        y,
        prediction,
        zero_division=0,
    )

    cm = confusion_matrix(
        y,
        prediction,
    )

    print(f"\n{name}")
    print("-" * 60)

    print(
        f"AUROC:     {auroc:.4f}"
    )

    print(
        f"AP:        {ap:.4f}"
    )

    print(
        f"Precision: {precision:.4f}"
    )

    print(
        f"Recall:    {recall:.4f}"
    )

    print(
        f"F1:        {f1:.4f}"
    )

    print(
        "Confusion matrix:"
    )

    print(cm)

    return {
        "auroc": auroc,
        "ap": ap,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


# ------------------------------------------------------------
# Validation
# ------------------------------------------------------------

val_metrics = evaluate(
    "VALIDATION",
    model,
    X_val,
    y_val,
)


# ------------------------------------------------------------
# Test
# ------------------------------------------------------------

test_metrics = evaluate(
    "FINAL TEST",
    model,
    X_test,
    y_test,
)


# ============================================================
# SAVE MODEL
# ============================================================

import joblib

model_path = (
    MODEL_DIR
    / "glycotwin_logistic.pkl"
)

joblib.dump(
    model,
    model_path,
)

print(
    f"\nModel saved to:"
)

print(
    model_path
)