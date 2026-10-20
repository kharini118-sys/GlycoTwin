from pathlib import Path
import sys

# Add the project root to Python's import path.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.twin import (
    TwinState,
    update_twin,
    GlycoTwinPredictor,
)


def main():

    print("GLYCOTWIN LIVE TWIN TEST")
    print("=" * 60)

    profile = {
        "age": 52,
        "bmi": 29.4,
        "hba1c": 7.1,
        "fasting_glucose": 132,
        "insulin": 14.2,
    }

    twin = TwinState(
        patient_id=12
    )

    predictor = GlycoTwinPredictor()

    observations = [
        {
            "timestamp": "2026-01-01 08:00",
            "glucose": 102,
            "heart_rate": 72,
            "activity_calories": 0.8,
            "mets": 1.5,
        },
        {
            "timestamp": "2026-01-01 08:05",
            "glucose": 105,
            "heart_rate": 74,
            "activity_calories": 1.1,
            "mets": 2.0,
        },
        {
            "timestamp": "2026-01-01 08:10",
            "glucose": 111,
            "heart_rate": 78,
            "activity_calories": 2.4,
            "mets": 3.5,
        },
        {
            "timestamp": "2026-01-01 08:15",
            "glucose": 118,
            "heart_rate": 82,
            "activity_calories": 3.1,
            "mets": 4.0,
        },
    ]

    for observation in observations:

        twin = update_twin(
            twin,
            observation,
        )

        result = predictor.predict(
            twin,
            profile,
        )

        print()
        print(observation["timestamp"])

        print(
            f"Glucose: {twin.current_glucose:.1f}"
        )

        print(
            f"Personal baseline: "
            f"{twin.personal_baseline:.1f}"
        )

        print(
            f"Glucose momentum: "
            f"{twin.glucose_momentum:.2f}"
        )

        print(
            f"Activity state: "
            f"{twin.activity_state:.2f}"
        )

        print(
            f"Data confidence: "
            f"{twin.data_confidence:.2f}"
        )

        print(
            f"Risk probability: "
            f"{result['risk_probability']:.3f}"
        )

        print(
            f"Excursion risk: "
            f"{result['excursion_risk']}"
        )

    print()
    print("=" * 60)
    print("FINAL TWIN STATE")
    print("=" * 60)

    print(twin.to_dict())


if __name__ == "__main__":
    main()