from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    precision_score,
    recall_score,
    f1_score,
    brier_score_loss,
    confusion_matrix,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
MODEL_DIR = PROJECT_ROOT / "models"


# ============================================================
# LOAD DATA
# ============================================================

print("GLYCOTWIN CALIBRATION + THRESHOLD ANALYSIS")
print("=" * 65)

X_sequence = np.load(PROCESSED_DIR / "X_sequence.npy")
X_static = np.load(PROCESSED_DIR / "X_static.npy")
y = np.load(PROCESSED_DIR / "y.npy")

train_mask = np.load(PROCESSED_DIR / "train_mask.npy")
val_mask = np.load(PROCESSED_DIR / "val_mask.npy")
test_mask = np.load(PROCESSED_DIR / "test_mask.npy")


# ============================================================
# FEATURE ENGINEERING
# Same feature definition as train_baseline.py
# ============================================================

def build_features(X_sequence, X_static):

    glucose = X_sequence[:, :, 0]
    heart_rate = X_sequence[:, :, 1]
    activity = X_sequence[:, :, 2]
    mets = X_sequence[:, :, 3]

    features = np.column_stack([
        # Glucose
        glucose[:, -1],
        np.mean(glucose, axis=1),
        np.std(glucose, axis=1),
        np.min(glucose, axis=1),
        np.max(glucose, axis=1),
        glucose[:, -1] - glucose[:, 0],
        glucose[:, -1] - glucose[:, -4],

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

        # Static
        X_static[:, 0],  # age
        X_static[:, 1],  # bmi
        X_static[:, 2],  # hba1c
        X_static[:, 3],  # fasting glucose
        X_static[:, 4],  # insulin
        X_static[:, 5],  # personal baseline

        # Personalized glucose deviation
        glucose[:, -1] - X_static[:, 5],
    ])

    return features


X = build_features(X_sequence, X_static)

X_train = X[train_mask]
X_val = X[val_mask]
X_test = X[test_mask]

y_train = y[train_mask]
y_val = y[val_mask]
y_test = y[test_mask]


print()
print("Feature matrix:", X.shape)
print("Train:", len(y_train))
print("Validation:", len(y_val))
print("Test:", len(y_test))


# ============================================================
# BASE MODEL
# ============================================================

base_model = Pipeline([
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


print()
print("Training base Logistic Regression...")
base_model.fit(X_train, y_train)


# ============================================================
# RAW MODEL PROBABILITIES
# ============================================================

val_raw = base_model.predict_proba(X_val)[:, 1]
test_raw = base_model.predict_proba(X_test)[:, 1]


# ============================================================
# CALIBRATION
#
# IMPORTANT:
# Calibration is fitted using TRAIN + VALIDATION only.
# TEST remains untouched until final evaluation.
#
# sigmoid = Platt-style calibration.
# ============================================================

calibrated_model = CalibratedClassifierCV(
    estimator=base_model,
    method="sigmoid",
    cv=5,
)

print()
print("Training calibrated Logistic Regression...")
calibrated_model.fit(
    np.concatenate([X_train, X_val]),
    np.concatenate([y_train, y_val]),
)

test_calibrated = calibrated_model.predict_proba(X_test)[:, 1]


# ============================================================
# BASIC MODEL METRICS
# ============================================================

print()
print("=" * 65)
print("RAW LOGISTIC REGRESSION")
print("=" * 65)

print(
    f"Test AUROC: {roc_auc_score(y_test, test_raw):.4f}"
)

print(
    f"Test AP:    {average_precision_score(y_test, test_raw):.4f}"
)

print(
    f"Test Brier: {brier_score_loss(y_test, test_raw):.4f}"
)


print()
print("=" * 65)
print("CALIBRATED LOGISTIC REGRESSION")
print("=" * 65)

print(
    f"Test AUROC: {roc_auc_score(y_test, test_calibrated):.4f}"
)

print(
    f"Test AP:    {average_precision_score(y_test, test_calibrated):.4f}"
)

print(
    f"Test Brier: {brier_score_loss(y_test, test_calibrated):.4f}"
)


# ============================================================
# THRESHOLD ANALYSIS
# ============================================================

thresholds = np.arange(
    0.10,
    0.91,
    0.05
)

rows = []

for threshold in thresholds:

    prediction = (
        test_calibrated >= threshold
    ).astype(int)

    precision = precision_score(
        y_test,
        prediction,
        zero_division=0,
    )

    recall = recall_score(
        y_test,
        prediction,
        zero_division=0,
    )

    f1 = f1_score(
        y_test,
        prediction,
        zero_division=0,
    )

    tn, fp, fn, tp = confusion_matrix(
        y_test,
        prediction,
    ).ravel()

    rows.append({
        "Threshold": threshold,
        "Precision": precision,
        "Recall": recall,
        "F1": f1,
        "Predicted Positive Rate": prediction.mean(),
        "True Positives": tp,
        "False Positives": fp,
        "False Negatives": fn,
        "True Negatives": tn,
    })


threshold_df = pd.DataFrame(rows)


print()
print("=" * 65)
print("THRESHOLD ANALYSIS")
print("=" * 65)

print(
    threshold_df.to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}"
    )
)


# ============================================================
# BEST F1 THRESHOLD
# ============================================================

best_row = threshold_df.loc[
    threshold_df["F1"].idxmax()
]

print()
print("=" * 65)
print("BEST F1 THRESHOLD")
print("=" * 65)

print(
    f"Threshold:             {best_row['Threshold']:.2f}"
)

print(
    f"Precision:             {best_row['Precision']:.4f}"
)

print(
    f"Recall:                {best_row['Recall']:.4f}"
)

print(
    f"F1:                    {best_row['F1']:.4f}"
)

print(
    f"Predicted positive:    "
    f"{best_row['Predicted Positive Rate']:.4f}"
)


# ============================================================
# SAVE THRESHOLD RESULTS
# ============================================================

threshold_path = MODEL_DIR / "logistic_threshold_analysis.csv"

threshold_df.to_csv(
    threshold_path,
    index=False,
)

print()
print("Threshold analysis saved to:")
print(threshold_path)


# ============================================================
# SAVE CALIBRATED MODEL
# ============================================================

calibrated_path = MODEL_DIR / "glycotwin_logistic_calibrated.pkl"

import joblib

joblib.dump(
    calibrated_model,
    calibrated_path,
)

print()
print("Calibrated model saved to:")
print(calibrated_path)