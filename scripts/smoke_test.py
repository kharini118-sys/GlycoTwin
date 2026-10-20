"""GlycoTwin Smoke Test — runs all critical modules end-to-end."""
import sys, tempfile, shutil
from pathlib import Path
# scripts/ is one level below project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

errors = []

def check(label, fn):
    try:
        fn()
        print(f"  OK  {label}")
    except Exception as exc:
        print(f"  FAIL {label}: {exc}")
        errors.append(label)

# 1 Database init
def t_db():
    from src.database.db import init_db
    init_db()
check("Database init", t_db)

# 2 Auth round-trip
def t_auth():
    import src.database.db as db_module
    tmpdir = tempfile.mkdtemp()
    db_module.DB_PATH = Path(tmpdir) / "test.db"
    db_module.init_db()
    from app.auth import register_user, authenticate_user
    ok, msg, uid = register_user("Test", "t@test.local", "ValidPass1", "ValidPass1")
    assert ok, f"Registration failed: {msg}"
    ok2, msg2, user = authenticate_user("t@test.local", "ValidPass1")
    assert ok2, f"Login failed: {msg2}"
    assert user is not None
    assert "password" not in user, "Password in user dict!"
    assert "password_hash" not in user, "Hash in user dict!"
    shutil.rmtree(tmpdir, ignore_errors=True)
check("Auth round-trip (register + login)", t_auth)

# 3 Workspace isolation
def t_ws():
    import src.database.db as db_module
    tmpdir = tempfile.mkdtemp()
    db_module.DB_PATH = Path(tmpdir) / "test.db"
    db_module.init_db()
    from src.database.db import create_user, create_workspace, get_workspace
    from app.auth import hash_password
    uid1 = create_user("U1", "u1@test.local", hash_password("ValidPass1"))
    uid2 = create_user("U2", "u2@test.local", hash_password("ValidPass1"))
    wid = create_workspace(uid1, "WS1", participant_id="5")
    assert get_workspace(wid, uid2) is None, "Isolation breach!"
    assert get_workspace(wid, uid1) is not None
    shutil.rmtree(tmpdir, ignore_errors=True)
check("Workspace isolation", t_ws)

# 4 Predictor end-to-end
def t_predictor():
    from src.twin.predictor import GlycoTwinPredictor
    from src.twin.state import TwinState
    from src.twin.updater import update_twin
    p = GlycoTwinPredictor()
    t = TwinState(patient_id="SMOKE")
    for i in range(15):
        t = update_twin(t, {"glucose": 110+i, "heart_rate": 72.0,
                             "activity_calories": 1.0, "mets": 1.5})
    profile = {"age":52,"bmi":29,"hba1c":7.0,"fasting_glucose":120,"insulin":14}
    res = p.predict(t, profile)
    prob = res["risk_probability"]
    assert 0.0 <= prob <= 1.0, f"Probability out of range: {prob}"
    print(f"      prob={prob:.3f} excursion={res['excursion_risk']}")
check("Predictor inference", t_predictor)

# 5 Scenario simulator
def t_scenario():
    from src.twin.predictor import GlycoTwinPredictor
    from src.twin.state import TwinState
    from src.twin.updater import update_twin
    from src.simulation.scenario import run_scenario
    p = GlycoTwinPredictor()
    t = TwinState(patient_id="SMOKE2")
    for i in range(15):
        t = update_twin(t, {"glucose": 110+i, "heart_rate": 72.0,
                             "activity_calories": 1.0, "mets": 1.5})
    profile = {"age":52,"bmi":29,"hba1c":7.0,"fasting_glucose":120,"insulin":14}
    r = run_scenario(t, profile, "activity_increase", intensity=0.5, predictor=p)
    assert 0.0 <= r.baseline_probability <= 1.0
    assert 0.0 <= r.scenario_probability <= 1.0
    print(f"      baseline={r.baseline_probability:.3f} scenario={r.scenario_probability:.3f} delta={r.delta_percentage_points:+.1f}pp")
check("Scenario simulator", t_scenario)

# 6 PDF export
def t_pdf():
    from src.simulation.export import generate_pdf_report
    pdf = generate_pdf_report("SMOKE-001", "Test", [], user_display_name="Test User")
    assert len(pdf) > 1000, f"PDF too small: {len(pdf)} bytes"
    assert pdf[:4] == b"%PDF", "Not a valid PDF"
    print(f"      {len(pdf):,} bytes")
check("PDF export", t_pdf)

# 7 CSV export
def t_csv():
    from src.simulation.export import generate_csv_report
    rows = [{"timestamp": "2026-01-01 08:00", "glucose": 110.0, "risk_probability": 0.15}]
    csv_str = generate_csv_report("SMOKE-001", rows)
    assert "GlycoTwin" in csv_str
    assert "RESEARCH PROTOTYPE" in csv_str
check("CSV export", t_csv)

# 8 Data loader
def t_data():
    from src.data.load_cgmacros import load_all_participants
    df = load_all_participants()
    assert df is not None
    n = len(df) if hasattr(df, "__len__") else "?"
    print(f"      loaded {n} rows")
check("Data loader (CGMacros)", t_data)

# Summary
print()
print("=" * 50)
if errors:
    print(f"FAILURES: {len(errors)}")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print(f"ALL SMOKE TESTS PASSED (8/8)")
