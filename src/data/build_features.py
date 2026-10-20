from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def add_historical_baseline(df, min_history=12):
    """
    Create a leakage-safe personal glucose baseline.

    For every timestamp, the baseline is calculated using only
    glucose observations that occurred BEFORE that timestamp.

    min_history=12 means the preferred baseline requires at least
    12 previous 5-minute observations (approximately 1 hour).

    During cold-start periods, the available historical observations
    are used instead.

    IMPORTANT:
    No future glucose values are used.
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

    # --------------------------------------------------------
    # Previous glucose only.
    #
    # shift(1) is critical:
    # the current glucose measurement is NOT included.
    # --------------------------------------------------------

    previous_glucose = (
        df.groupby("subject_id")["glucose"]
        .shift(1)
    )

    # --------------------------------------------------------
    # Historical median using only past observations.
    #
    # expanding() operates independently for each participant.
    # --------------------------------------------------------

    historical_median = (
        previous_glucose
        .groupby(df["subject_id"])
        .expanding(
            min_periods=min_history
        )
        .median()
        .reset_index(
            level=0,
            drop=True
        )
    )

    # --------------------------------------------------------
    # Cold-start fallback.
    #
    # If fewer than min_history observations exist, use the
    # median of whatever historical observations are available.
    #
    # Still no future information.
    # --------------------------------------------------------

    historical_fallback = (
        previous_glucose
        .groupby(df["subject_id"])
        .expanding(
            min_periods=1
        )
        .median()
        .reset_index(
            level=0,
            drop=True
        )
    )

    df["personal_baseline"] = (
        historical_median
        .fillna(historical_fallback)
    )

    return df


def add_sequence_features(df):
    """
    Add backward-looking glucose features.

    These features use only the current and previous observations.
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

    grouped = df.groupby(
        "subject_id",
        sort=False
    )

    # --------------------------------------------------------
    # 1-hour glucose mean
    # --------------------------------------------------------

    df["glucose_mean_1h"] = (
        grouped["glucose"]
        .transform(
            lambda x:
            x.rolling(
                12,
                min_periods=1
            ).mean()
        )
    )

    # --------------------------------------------------------
    # 1-hour glucose standard deviation
    # --------------------------------------------------------

    df["glucose_std_1h"] = (
        grouped["glucose"]
        .transform(
            lambda x:
            x.rolling(
                12,
                min_periods=2
            ).std()
        )
    )

    # --------------------------------------------------------
    # 1-hour minimum
    # --------------------------------------------------------

    df["glucose_min_1h"] = (
        grouped["glucose"]
        .transform(
            lambda x:
            x.rolling(
                12,
                min_periods=1
            ).min()
        )
    )

    # --------------------------------------------------------
    # 1-hour maximum
    # --------------------------------------------------------

    df["glucose_max_1h"] = (
        grouped["glucose"]
        .transform(
            lambda x:
            x.rolling(
                12,
                min_periods=1
            ).max()
        )
    )

    # --------------------------------------------------------
    # Change over previous hour
    # --------------------------------------------------------

    df["glucose_change_1h"] = (
        grouped["glucose"]
        .transform(
            lambda x:
            x - x.shift(12)
        )
    )

    # --------------------------------------------------------
    # Current glucose relative to personal baseline
    # --------------------------------------------------------

    df["glucose_vs_baseline"] = (
        df["glucose"]
        - df["personal_baseline"]
    )

    return df


if __name__ == "__main__":

    print(
        "Leakage-safe feature builder ready."
    )