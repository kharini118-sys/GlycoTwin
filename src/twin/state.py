from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class PatientProfile:
    """
    Static clinical and demographic profile of a patient (EHR Stream 1).
    """
    patient_id: str
    age: float = 45.0
    sex: str = "M"
    bmi: float = 26.5
    hba1c: float = 6.5
    diabetes_duration_years: float = 3.0
    medication: str = "metformin"
    fasting_glucose: float = 110.0
    insulin: float = 12.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "patient_id": self.patient_id,
            "age": self.age,
            "sex": self.sex,
            "bmi": self.bmi,
            "hba1c": self.hba1c,
            "diabetes_duration_years": self.diabetes_duration_years,
            "medication": self.medication,
            "fasting_glucose": self.fasting_glucose,
            "insulin": self.insulin,
        }


@dataclass
class TwinState:
    """
    Persistent computational state of a GlycoTwin patient.

    This is the Digital Twin state layer.
    It is separate from the prediction model.
    """

    patient_id: int

    current_glucose: Optional[float] = None
    personal_baseline: Optional[float] = None

    metabolic_state: float = 0.0
    activity_state: float = 0.0
    recovery_state: float = 0.0
    cardiovascular_state: float = 0.0
    glucose_momentum: float = 0.0

    data_confidence: float = 0.0

    risk_probability: Optional[float] = None
    risk_threshold: float = 0.20
    excursion_risk: bool = False

    history: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self):
        return {
            "patient_id": self.patient_id,
            "current_glucose": self.current_glucose,
            "personal_baseline": self.personal_baseline,
            "metabolic_state": self.metabolic_state,
            "activity_state": self.activity_state,
            "recovery_state": self.recovery_state,
            "cardiovascular_state": self.cardiovascular_state,
            "glucose_momentum": self.glucose_momentum,
            "data_confidence": self.data_confidence,
            "risk_probability": self.risk_probability,
            "risk_threshold": self.risk_threshold,
            "excursion_risk": self.excursion_risk,
        }