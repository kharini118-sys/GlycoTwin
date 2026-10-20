"""
GlycoTwin — Command-Line Demo Script
=====================================
RESEARCH PROTOTYPE — NOT A MEDICAL DEVICE — NOT CLINICALLY VALIDATED

This script demonstrates the Digital Twin update loop using a small
illustrative synthetic observation stream. The risk probabilities shown
are real model outputs but the input glucose/HR values are fabricated
for demonstration purposes only.

Do NOT use any output from this script for clinical decision-making.
"""
from src.twin.state import PatientProfile, TwinState
from src.twin.updater import update_twin
from src.twin.predictor import GlycoTwinPredictor



profile = PatientProfile(
    patient_id="P001",
    age=42,
    sex="M",
    bmi=28.4,
    hba1c=7.1,
    diabetes_duration_years=6,
    medication="metformin",
)

state = TwinState(patient_id=profile.patient_id)
predictor = GlycoTwinPredictor()

stream = [
    {"time": "08:00", "glucose": 112, "heart_rate": 72, "hrv": 55, "activity_calories": 1.2, "mets": 1.8},
    {"time": "08:15", "glucose": 118, "heart_rate": 75, "hrv": 52, "activity_calories": 1.5, "mets": 2.1},
    {"time": "08:30", "glucose": 126, "heart_rate": 78, "hrv": 49, "activity_calories": 2.0, "mets": 2.8},
    {"time": "08:45", "glucose": 138, "heart_rate": 82, "hrv": 44, "activity_calories": 2.5, "mets": 3.2},
]

print("GLYCOTWIN — DIGITAL BIO-TWIN DEMO")
print("=" * 60)

for observation in stream:
    state = update_twin(state, observation, profile)
    pred = predictor.predict(state, profile.to_dict())

    print(f"\nTime: {observation['time']}")
    print(f"  Glucose:           {state.current_glucose:.1f} mg/dL")
    print(f"  Metabolic state:   {state.metabolic_state:.3f}")
    print(f"  Activity state:    {state.activity_state:.3f}")
    print(f"  Cardiovascular:    {state.cardiovascular_state:.3f}")
    print(f"  Glucose momentum:  {state.glucose_momentum:.3f}")
    print(f"  Data confidence:   {state.data_confidence:.3f}")
    print(f"  2-Hr Risk Prob:    {pred['risk_probability']:.1%}")
    print(f"  Excursion Alert:   {'[HIGH RISK]' if pred['excursion_risk'] else '[NORMAL]'}")

print("\n" + "=" * 60)
print("FINAL DIGITAL TWIN STATE SNAPSHOT")
print("=" * 60)
print(state.to_dict())

