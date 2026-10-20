from pathlib import Path

import pandas as pd


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = PROJECT_ROOT / "data" / "raw" / "cgmacros" / "CGMacros"


def load_bio() -> pd.DataFrame:
    """Load static patient information from bio.csv."""
    bio_path = DATA_ROOT / "bio.csv"

    bio = pd.read_csv(bio_path)

    # Standardize the subject identifier
    bio = bio.rename(columns={"subject": "subject_id"})

    return bio


def load_participant(subject_id: int) -> pd.DataFrame:
    """Load one participant's longitudinal CGM/wearable/meal data."""

    participant_id = f"CGMacros-{subject_id:03d}"
    participant_path = DATA_ROOT / participant_id / f"{participant_id}.csv"

    if not participant_path.exists():
        raise FileNotFoundError(
            f"Participant file not found: {participant_path}"
        )

    df = pd.read_csv(participant_path)

    # Add the subject identifier
    df["subject_id"] = subject_id

    # Parse timestamp
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])

    return df


def load_all_participants() -> pd.DataFrame:
    """
    Load all participant time-series data and attach
    static patient information.
    """

    bio = load_bio()

    participant_frames = []

    for subject_id in bio["subject_id"]:
        df = load_participant(int(subject_id))
        participant_frames.append(df)

    dynamic = pd.concat(
        participant_frames,
        ignore_index=True,
    )

    # Attach static patient information
    combined = dynamic.merge(
        bio,
        on="subject_id",
        how="left",
    )

    return combined


if __name__ == "__main__":
    print("Loading CGMacros...")

    df = load_all_participants()

    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")
    print(f"Participants: {df['subject_id'].nunique()}")

    print("\nDate range:")
    print(df["Timestamp"].min())
    print(df["Timestamp"].max())

    print("\nColumns:")
    for column in df.columns:
        print(f" - {column}")