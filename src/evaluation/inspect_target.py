from pathlib import Path
import sys
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from src.data.load_cgmacros import load_all_participants
from src.data.clean_cgmacros import clean_cgmacros


def inspect_future_excursions(df):
    results = []

    for subject_id, patient in df.groupby("subject_id"):
        patient = patient.sort_values("timestamp").copy()

        glucose = patient["glucose"]

        future_max = (
            glucose
            .shift(-1)
            .rolling(window=120, min_periods=120)
            .max()
            .shift(-119)
        )

        patient["future_max_glucose"] = future_max
        patient["max_rise_2h"] = (
            patient["future_max_glucose"] - patient["glucose"]
        )

        results.append(patient)

    return pd.concat(results, ignore_index=True)


if __name__ == "__main__":
    print("Loading CGMacros...")

    raw = load_all_participants()
    clean = clean_cgmacros(raw)

    print("Inspecting maximum future glucose excursions...")

    data = inspect_future_excursions(clean)

    thresholds = [20, 25, 30, 35, 40, 50]

    print("\nOVERALL PREVALENCE")
    print("=" * 60)

    rises = data["max_rise_2h"].dropna()

    for threshold in thresholds:
        prevalence = (rises >= threshold).mean()
        print(
            f"Rise >= {threshold:2d} mg/dL: "
            f"{prevalence:.3f} ({prevalence * 100:.1f}%)"
        )

    print("\nPARTICIPANT-LEVEL PREVALENCE")
    print("=" * 60)

    participant_rows = []

    for subject_id, patient in data.groupby("subject_id"):
        valid = patient["max_rise_2h"].dropna()

        row = {
            "subject_id": subject_id,
            "n_windows": len(valid),
        }

        for threshold in thresholds:
            row[f"positive_{threshold}"] = (
                (valid >= threshold).mean()
                if len(valid) > 0
                else float("nan")
            )

        participant_rows.append(row)

    participant_summary = pd.DataFrame(participant_rows)

    print(
        participant_summary[
            ["subject_id", "n_windows"]
            + [f"positive_{t}" for t in thresholds]
        ]
        .round(3)
        .to_string(index=False)
    )

    print("\nRANGE ACROSS PARTICIPANTS")
    print("=" * 60)

    for threshold in thresholds:
        values = participant_summary[f"positive_{threshold}"]

        print(
            f"{threshold:2d} mg/dL: "
            f"min={values.min():.3f}, "
            f"median={values.median():.3f}, "
            f"max={values.max():.3f}"
        )