from pathlib import Path
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

THRESHOLD = 30.0
HORIZON_MINUTES = 120


def create_targets(df):
    """
    Create a leakage-safe 2-hour glucose excursion target.

    Positive = glucose rises by >=30 mg/dL above the current glucose
    at any valid glucose measurement during the following 120 minutes.

    The target uses timestamps rather than row counts.
    """

    df = df.copy()

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    df = df.sort_values(
        ["subject_id", "timestamp"]
    ).reset_index(drop=True)

    targets = []

    for subject_id, group in df.groupby("subject_id", sort=False):

        group = group.sort_values("timestamp").reset_index()

        timestamps = group["timestamp"].values
        glucose = group["glucose"].to_numpy(dtype=float)

        subject_targets = np.full(len(group), np.nan)

        for i in range(len(group)):

            current_glucose = glucose[i]

            if np.isnan(current_glucose):
                continue

            start_time = timestamps[i]
            end_time = start_time + np.timedelta64(
                HORIZON_MINUTES, "m"
            )

            # Future observations only.
            future_mask = (
                (timestamps > start_time)
                & (timestamps <= end_time)
                & ~np.isnan(glucose)
            )

            future_values = glucose[future_mask]

            if len(future_values) == 0:
                continue

            future_max = np.max(future_values)

            subject_targets[i] = float(
                future_max - current_glucose >= THRESHOLD
            )

        group["target"] = subject_targets

        targets.append(group)

    result = pd.concat(
        targets,
        ignore_index=True
    )

    result = result.sort_values("index").reset_index(drop=True)

    return result["target"].to_numpy()


if __name__ == "__main__":
    print("Leakage-safe target generator ready.")
    print(f"Threshold: +{THRESHOLD:.0f} mg/dL")
    print(f"Horizon: {HORIZON_MINUTES} minutes")