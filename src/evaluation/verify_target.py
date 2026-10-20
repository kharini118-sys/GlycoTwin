from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from src.data.load_cgmacros import load_all_participants
from src.data.clean_cgmacros import clean_cgmacros
from src.evaluation.targets import add_excursion_target


if __name__ == "__main__":
    print("Loading CGMacros...")

    raw = load_all_participants()
    clean = clean_cgmacros(raw)

    print("Building time-based target...")

    data = add_excursion_target(clean)

    valid = data["target_excursion"].dropna()

    print("\nTARGET SUMMARY")
    print("=" * 60)

    print(f"Total rows:       {len(data):,}")
    print(f"Valid targets:    {len(valid):,}")
    print(f"Positive:         {int(valid.sum()):,}")
    print(f"Negative:         {int((valid == 0).sum()):,}")
    print(f"Positive rate:    {valid.mean():.3f}")

    print("\nTARGET BY PARTICIPANT")
    print("=" * 60)

    participant_rates = (
        data.dropna(subset=["target_excursion"])
        .groupby("subject_id")["target_excursion"]
        .agg(["count", "mean"])
    )

    participant_rates.columns = [
        "valid_windows",
        "positive_rate",
    ]

    print(participant_rates.round(3).to_string())

    print("\nTARGET COMPLETE.")