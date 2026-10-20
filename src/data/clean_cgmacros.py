from pathlib import Path
import sys

import pandas as pd


# Allow importing load_cgmacros.py when this file is run directly
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from src.data.load_cgmacros import load_all_participants


def clean_cgmacros(df: pd.DataFrame) -> pd.DataFrame:
    """Convert raw CGMacros data into a clean canonical schema."""

    clean = pd.DataFrame()

    # -------------------------
    # Identifiers and timestamp
    # -------------------------
    clean["subject_id"] = df["subject_id"]
    clean["timestamp"] = pd.to_datetime(df["Timestamp"])

    # -------------------------
    # Glucose
    # -------------------------
    clean["glucose"] = pd.to_numeric(
        df["Libre GL"], errors="coerce"
    )

    clean["dexcom_glucose"] = pd.to_numeric(
        df["Dexcom GL"], errors="coerce"
    )

    # If Libre GL is missing, fallback to Dexcom GL
    clean["glucose"] = clean["glucose"].fillna(clean["dexcom_glucose"])

    # -------------------------
    # Physiological / activity
    # -------------------------
    clean["heart_rate"] = pd.to_numeric(
        df["HR"], errors="coerce"
    )

    clean["activity_calories"] = pd.to_numeric(
        df["Calories (Activity)"], errors="coerce"
    )

    clean["mets"] = pd.to_numeric(
        df["METs"], errors="coerce"
    )

    # -------------------------
    # Meals / nutrition
    # -------------------------
    clean["meal_type"] = df["Meal Type"]

    clean["meal_calories"] = pd.to_numeric(
        df["Calories"], errors="coerce"
    )

    clean["carbs"] = pd.to_numeric(
        df["Carbs"], errors="coerce"
    )

    clean["protein"] = pd.to_numeric(
        df["Protein"], errors="coerce"
    )

    clean["fat"] = pd.to_numeric(
        df["Fat"], errors="coerce"
    )

    clean["fiber"] = pd.to_numeric(
        df["Fiber"], errors="coerce"
    )

    # Handle the dataset's inconsistent trailing whitespace
    amount_column = "Amount Consumed "
    if amount_column in df.columns:
        clean["amount_consumed"] = pd.to_numeric(
            df[amount_column], errors="coerce"
        )
    else:
        clean["amount_consumed"] = pd.to_numeric(
            df.get("Amount Consumed"), errors="coerce"
        )

    # -------------------------
    # Static patient profile
    # -------------------------
    clean["age"] = pd.to_numeric(
        df["Age"], errors="coerce"
    )

    clean["gender"] = df["Gender"]

    clean["bmi"] = pd.to_numeric(
        df["BMI"], errors="coerce"
    )

    clean["hba1c"] = pd.to_numeric(
        df["A1c PDL (Lab)"], errors="coerce"
    )

    clean["fasting_glucose"] = pd.to_numeric(
        df["Fasting GLU - PDL (Lab)"], errors="coerce"
    )

    clean["insulin"] = pd.to_numeric(
        df["Insulin "], errors="coerce"
    )

    clean["triglycerides"] = pd.to_numeric(
        df["Triglycerides"], errors="coerce"
    )

    clean["cholesterol"] = pd.to_numeric(
        df["Cholesterol"], errors="coerce"
    )

    clean["hdl"] = pd.to_numeric(
        df["HDL"], errors="coerce"
    )

    clean["ldl"] = pd.to_numeric(
        df["LDL (Cal)"], errors="coerce"
    )

    # -------------------------
    # Sort chronologically
    # -------------------------
    clean = clean.sort_values(
        ["subject_id", "timestamp"]
    ).reset_index(drop=True)

    return clean


if __name__ == "__main__":
    print("Loading raw CGMacros data...")

    raw = load_all_participants()

    print("Cleaning data...")

    clean = clean_cgmacros(raw)

    print(f"\nRows: {len(clean):,}")
    print(f"Columns: {len(clean.columns)}")
    print(f"Participants: {clean['subject_id'].nunique()}")

    print("\nClean columns:")
    for column in clean.columns:
        print(f" - {column}")

    print("\nFirst 5 rows:")
    print(clean.head().to_string())