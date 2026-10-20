from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    precision_score,
    recall_score,
    f1_score,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


# ============================================================
# LOAD DATA
# ============================================================

print("GLYCOTWIN ABLATION STUDY")
print("=" * 60)

X_sequence = np.load(PROCESSED_DIR / "X_sequence.npy")
X_static = np.load(PROCESSED_DIR / "X_static.npy")
y = np.load(PROCESSED_DIR / "y.npy")

train_mask = np.load(PROCESSED_DIR / "train_mask.npy")
val_mask = np.load(PROCESSED_DIR / "val_mask.npy")
test_mask = np.load(PROCESSED_DIR / "test_mask.npy")

print("Sequence:", X_sequence.shape)
print("Static:  ", X_static.shape)
print("Target:  ", y.shape)

print()
print("Train:", train_mask.sum())
print("Validation:", val_mask.sum())
print("Test:", test_mask.sum())


# ============================================================
# FEATURE DEFINITIONS
# ============================================================

# Static features in X_static:
#
# 0 age
# 1 bmi
# 2 hba1c
# 3 fasting_glucose
# 4 insulin
# 5 personal_baseline

STATIC_NAMES = [
    "age",
    "bmi",
    "hba1c",
    "fasting_glucose",
    "insulin",
    "personal_baseline",
]


# ============================================================
# DYNAMIC FEATURE ENGINEERING
# ============================================================

def build_dynamic_features(X):
    """
    Convert the 12 x 4 temporal sequence into summary features.

    Dynamic channels:
        0 glucose
        1 heart_rate
        2 activity_calories
        3 mets
    """

    glucose = X[:, :, 0]
    heart_rate = X[:, :, 1]
    activity = X[:, :, 2]
    mets = X[:, :, 3]

    features = np.column_stack([
        # Glucose
        glucose[:, -1],
        np.mean(glucose, axis=1),
        np.std(glucose, axis=1),
        np.min(glucose, axis=1),
        np.max(glucose, axis=1),
        glucose[:, -1] - glucose[:, 0],

        # Heart rate
        heart_rate[:, -1],
        np.mean(heart_rate, axis=1),
        np.std(heart_rate, axis=1),

        # Activity
        activity[:, -1],
        np.mean(activity, axis=1),
        np.sum(activity, axis=1),
        np.max(activity, axis=1),

        # METs
        mets[:, -1],
        np.mean(mets, axis=1),
        np.max(mets, axis=1),
    ])

    return features


dynamic_features = build_dynamic_features(X_sequence)

print()
print("Dynamic feature matrix:", dynamic_features.shape)


# ============================================================
# PERSONALIZED FEATURES
# ============================================================

# Current glucose is dynamic_features[:, 0]
# Personal baseline is X_static[:, 5]

current_glucose = dynamic_features[:, 0]
personal_baseline = X_static[:, 5]

personalized_features = np.column_stack([
    current_glucose - personal_baseline,
])


# ============================================================
# FEATURE GROUPS
# ============================================================

# Static WITHOUT personal baseline
static_only = X_static[:, :5]

# Dynamic only
dynamic_only = dynamic_features

# Static + dynamic, but WITHOUT personalized baseline
static_dynamic = np.column_stack([
    dynamic_features,
    X_static[:, :5],
])

# Full personalized representation
full_features = np.column_stack([
    dynamic_features,
    X_static[:, :5],
    X_static[:, 5],
    personalized_features,
])


experiments = {
    "Static only": static_only,
    "Dynamic only": dynamic_only,
    "Static + Dynamic": static_dynamic,
    "Static + Dynamic + Personalized Baseline": full_features,
}


# ============================================================
# EVALUATION FUNCTION
# ============================================================

def evaluate_model(name, X):
    X_train = X[train_mask]
    X_val = X[val_mask]
    X_test = X[test_mask]

    y_train = y[train_mask]
    y_val = y[val_mask]
    y_test = y[test_mask]

    model = Pipeline([
        (
            "imputer",
            SimpleImputer(strategy="median")
        ),
        (
            "scaler",
            StandardScaler()
        ),
        (
            "classifier",
            LogisticRegression(
                max_iter=1000,
                class_weight="balanced",
                random_state=42,
            )
        ),
    ])

    model.fit(X_train, y_train)

    val_probability = model.predict_proba(X_val)[:, 1]
    test_probability = model.predict_proba(X_test)[:, 1]

    val_prediction = (val_probability >= 0.5).astype(int)
    test_prediction = (test_probability >= 0.5).astype(int)

    result = {
        "Experiment": name,
        "Features": X.shape[1],

        "Val AUROC": roc_auc_score(
            y_val,
            val_probability
        ),

        "Val AP": average_precision_score(
            y_val,
            val_probability
        ),

        "Val F1": f1_score(
            y_val,
            val_prediction,
            zero_division=0
        ),

        "Test AUROC": roc_auc_score(
            y_test,
            test_probability
        ),

        "Test AP": average_precision_score(
            y_test,
            test_probability
        ),

        "Test Precision": precision_score(
            y_test,
            test_prediction,
            zero_division=0
        ),

        "Test Recall": recall_score(
            y_test,
            test_prediction,
            zero_division=0
        ),

        "Test F1": f1_score(
            y_test,
            test_prediction,
            zero_division=0
        ),
    }

    return result


# ============================================================
# RUN ABLATIONS
# ============================================================

results = []

for name, X in experiments.items():

    print()
    print("-" * 60)
    print(name)
    print("Feature count:", X.shape[1])
    print("-" * 60)

    result = evaluate_model(name, X)
    results.append(result)

    print(
        f"Validation AUROC: {result['Val AUROC']:.4f}"
    )

    print(
        f"Validation AP:     {result['Val AP']:.4f}"
    )

    print(
        f"Test AUROC:        {result['Test AUROC']:.4f}"
    )

    print(
        f"Test AP:           {result['Test AP']:.4f}"
    )

    print(
        f"Test Precision:    {result['Test Precision']:.4f}"
    )

    print(
        f"Test Recall:       {result['Test Recall']:.4f}"
    )

    print(
        f"Test F1:            {result['Test F1']:.4f}"
    )


# ============================================================
# RESULTS TABLE
# ============================================================

results_df = pd.DataFrame(results)

print()
print()
print("=" * 80)
print("ABLATION RESULTS")
print("=" * 80)

print(
    results_df.to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}"
    )
)


# ============================================================
# SAVE RESULTS
# ============================================================

output_path = (
    PROCESSED_DIR.parent.parent
    / "models"
    / "ablation_results.csv"
)

results_df.to_csv(output_path, index=False)

print()
print("Results saved to:")
print(output_path)