import numpy as np

from .state import TwinState


def _safe_mean(values):
    values = np.asarray(values, dtype=float)
    values = values[~np.isnan(values)]

    if len(values) == 0:
        return np.nan

    return float(np.mean(values))


def _safe_std(values):
    values = np.asarray(values, dtype=float)
    values = values[~np.isnan(values)]

    if len(values) == 0:
        return np.nan

    return float(np.std(values))


def _safe_min(values):
    values = np.asarray(values, dtype=float)
    values = values[~np.isnan(values)]

    if len(values) == 0:
        return np.nan

    return float(np.min(values))


def _safe_max(values):
    values = np.asarray(values, dtype=float)
    values = values[~np.isnan(values)]

    if len(values) == 0:
        return np.nan

    return float(np.max(values))


def build_prediction_features(
    twin: TwinState,
    profile: dict,
):
    """
    Build the 24-feature vector expected by the trained
    GlycoTwin Logistic Regression model.

    Feature order MUST remain identical to train_baseline.py.
    """

    history = twin.history[-12:]

    glucose = [
        item.get("glucose", np.nan)
        for item in history
    ]

    heart_rate = [
        item.get("heart_rate", np.nan)
        for item in history
    ]

    activity = [
        item.get("activity_calories", np.nan)
        for item in history
    ]

    mets = [
        item.get("mets", np.nan)
        for item in history
    ]

    # Need current glucose.
    current_glucose = twin.current_glucose

    if current_glucose is None:
        current_glucose = np.nan

    # 4th-from-last value.
    if len(glucose) >= 4:
        glucose_4th_last = glucose[-4]
    else:
        glucose_4th_last = np.nan

    personal_baseline = twin.personal_baseline

    if personal_baseline is None:
        personal_baseline = np.nan

    features = [
        # ----------------------------------------------------
        # Glucose
        # ----------------------------------------------------
        current_glucose,
        _safe_mean(glucose),
        _safe_std(glucose),
        _safe_min(glucose),
        _safe_max(glucose),

        (
            current_glucose - glucose[0]
            if len(glucose) > 0
            and not np.isnan(glucose[0])
            and not np.isnan(current_glucose)
            else np.nan
        ),

        (
            current_glucose - glucose_4th_last
            if not np.isnan(glucose_4th_last)
            and not np.isnan(current_glucose)
            else np.nan
        ),

        # ----------------------------------------------------
        # Heart rate
        # ----------------------------------------------------
        heart_rate[-1] if len(heart_rate) else np.nan,
        _safe_mean(heart_rate),
        _safe_std(heart_rate),

        # ----------------------------------------------------
        # Activity
        # ----------------------------------------------------
        activity[-1] if len(activity) else np.nan,
        _safe_mean(activity),

        (
            float(np.nansum(activity))
            if len(activity)
            else np.nan
        ),

        _safe_max(activity),

        # ----------------------------------------------------
        # METs
        # ----------------------------------------------------
        mets[-1] if len(mets) else np.nan,
        _safe_mean(mets),
        _safe_max(mets),

        # ----------------------------------------------------
        # Static clinical features
        # ----------------------------------------------------
        profile.get("age", np.nan),
        profile.get("bmi", np.nan),
        profile.get("hba1c", np.nan),
        profile.get("fasting_glucose", np.nan),
        profile.get("insulin", np.nan),

        # Personal baseline
        personal_baseline,

        # Current glucose deviation from personal baseline
        (
            current_glucose - personal_baseline
            if not np.isnan(current_glucose)
            and not np.isnan(personal_baseline)
            else np.nan
        ),
    ]

    return np.asarray(features, dtype=float).reshape(1, -1)