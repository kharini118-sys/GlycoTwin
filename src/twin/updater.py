from datetime import datetime, timezone
from typing import Dict, Any

from .state import TwinState, PatientProfile


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def update_twin(
    twin: TwinState,
    observation: Dict[str, Any],
    profile: Any = None,
) -> TwinState:
    """
    Update the persistent Digital Twin state from a new observation.

    This state update is intentionally interpretable and lightweight.
    It is NOT a medical equation and is not presented as a physiological
    model. The learned prediction model remains responsible for risk
    estimation.
    """

    glucose = observation.get("glucose")
    heart_rate = observation.get("heart_rate")
    activity = observation.get("activity_calories")
    mets = observation.get("mets")

    timestamp = observation.get("timestamp")

    if glucose is not None:
        glucose = float(glucose)

        previous_glucose = twin.current_glucose

        twin.current_glucose = glucose

        if twin.personal_baseline is None:
            twin.personal_baseline = glucose
        else:
            # Slowly adapting baseline.
            # This prevents a single measurement from dominating it.
            twin.personal_baseline = (
                0.95 * twin.personal_baseline
                + 0.05 * glucose
            )

        if previous_glucose is not None:
            delta = glucose - previous_glucose

            twin.glucose_momentum = (
                0.70 * twin.glucose_momentum
                + 0.30 * delta
            )

        if twin.personal_baseline:
            deviation = (
                glucose - twin.personal_baseline
            )

            twin.metabolic_state = _clamp(
                deviation / 40.0,
                -3.0,
                3.0,
            )

    if activity is not None:
        activity = float(activity)

        twin.activity_state = _clamp(
            activity / 5.0,
            0.0,
            3.0,
        )

    if mets is not None:
        mets = float(mets)

        twin.activity_state = _clamp(
            0.5 * twin.activity_state
            + 0.5 * (mets / 10.0),
            0.0,
            3.0,
        )

    if heart_rate is not None:
        heart_rate = float(heart_rate)

        # Interpretable normalized cardiovascular state.
        twin.cardiovascular_state = _clamp(
            (heart_rate - 70.0) / 30.0,
            -2.0,
            2.0,
        )

    # --------------------------------------------------------
    # Data confidence
    # --------------------------------------------------------

    available = 0
    total = 4

    for value in [
        glucose,
        heart_rate,
        activity,
        mets,
    ]:
        if value is not None:
            available += 1

    twin.data_confidence = available / total

    # --------------------------------------------------------
    # Recovery state
    #
    # CGMacros does not provide a reliable sleep signal in the
    # cleaned modeling dataset, so recovery is kept neutral.
    # --------------------------------------------------------

    twin.recovery_state = 0.0

    # --------------------------------------------------------
    # Store observation history
    # --------------------------------------------------------

    twin.history.append({
        "timestamp": (
            str(timestamp)
            if timestamp is not None
            else datetime.now(timezone.utc).isoformat()
        ),
        "glucose": glucose,
        "heart_rate": heart_rate,
        "activity_calories": activity,
        "mets": mets,
    })

    # Keep recent state bounded.
    if len(twin.history) > 100:
        twin.history = twin.history[-100:]

    return twin