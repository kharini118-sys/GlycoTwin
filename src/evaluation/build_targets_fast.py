from pathlib import Path
from collections import deque

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

THRESHOLD = 30.0
HORIZON = pd.Timedelta(minutes=120)


def build_targets(df):
    """
    Build the GlycoTwin prediction target.

    Positive target:
        glucose rises by >= 30 mg/dL from the current
        observed glucose to any subsequent observed
        glucose measurement within 120 minutes.

    IMPORTANT:
        This function must receive glucose values that
        have NOT been forward-filled.

    Missing glucose measurements are ignored.
    """

    df = df.copy()

    df["timestamp"] = pd.to_datetime(
        df["timestamp"]
    )

    df = (
        df.sort_values(
            ["subject_id", "timestamp"]
        )
        .reset_index(drop=True)
    )

    target = np.full(
        len(df),
        np.nan,
        dtype=np.float32,
    )

    for subject_id, group in df.groupby(
        "subject_id",
        sort=False,
    ):

        idx = group.index.to_numpy()

        timestamps = (
            group["timestamp"]
            .to_numpy()
        )

        glucose = (
            pd.to_numeric(
                group["glucose"],
                errors="coerce",
            )
            .to_numpy(dtype=float)
        )

        # ----------------------------------------------------
        # ONLY ACTUAL OBSERVATIONS
        # ----------------------------------------------------

        valid = ~np.isnan(glucose)

        observed_times = timestamps[valid]

        observed_glucose = glucose[valid]

        if len(observed_glucose) < 2:
            continue

        # ----------------------------------------------------
        # Sliding future window
        # ----------------------------------------------------

        left = np.searchsorted(
            observed_times,
            timestamps,
            side="right",
        )

        right = np.searchsorted(
            observed_times,
            timestamps + HORIZON,
            side="right",
        )

        future_max = np.full(
            len(timestamps),
            np.nan,
            dtype=float,
        )

        dq = deque()

        r = 0

        for i in range(len(timestamps)):

            # Add observations entering
            # the future window.
            while (
                r < len(observed_times)
                and r < right[i]
            ):

                value = observed_glucose[r]

                while (
                    dq
                    and observed_glucose[dq[-1]]
                    <= value
                ):
                    dq.pop()

                dq.append(r)

                r += 1

            # Remove observations that are
            # no longer inside the window.
            while (
                dq
                and dq[0] < left[i]
            ):
                dq.popleft()

            if (
                left[i] < right[i]
                and dq
            ):
                future_max[i] = (
                    observed_glucose[dq[0]]
                )

        # ----------------------------------------------------
        # Create target
        # ----------------------------------------------------

        current_glucose = glucose

        valid_target = (
            ~np.isnan(current_glucose)
            & ~np.isnan(future_max)
        )

        local_target = np.full(
            len(idx),
            np.nan,
            dtype=np.float32,
        )

        local_target[valid_target] = (
            (
                future_max[valid_target]
                - current_glucose[valid_target]
            )
            >= THRESHOLD
        ).astype(np.float32)

        target[idx] = local_target

    return target


if __name__ == "__main__":

    print(
        "GlycoTwin target builder loaded."
    )

    print(
        f"Threshold: +{THRESHOLD:.0f} mg/dL"
    )

    print(
        "Horizon: 120 minutes"
    )

    print(
        "Target source: observed glucose only"
    )