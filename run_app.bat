@echo off
echo ============================================================
echo  GlycoTwin -- Personalized Bio-Digital Twin Platform
echo  Happiest Health Digital Twin Challenge 2026
echo ============================================================
echo.

:: Check Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Install Python 3.10+ and try again.
    pause
    exit /b 1
)

:: Check streamlit is installed
python -c "import streamlit" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing dependencies...
    python -m pip install -r requirements.txt
)

:: Initialize database
python -c "from src.database.db import init_db; init_db(); print('Database initialized.')"

:: Check model artifact
if not exist "models\glycotwin_logistic_calibrated.pkl" (
    echo WARNING: Model artifact not found.
    echo Expected: models\glycotwin_logistic_calibrated.pkl
    echo Run: python -m src.evaluation.calibrate_logistic
    echo.
)

:: Check dataset
if not exist "data\raw\cgmacros\CGMacros\bio.csv" (
    echo WARNING: Dataset not found.
    echo Expected: data\raw\cgmacros\CGMacros\bio.csv
    echo Download from: https://physionet.org/content/cgmacros/1.0.0/
    echo.
)

echo Starting GlycoTwin Dashboard...
echo Navigate to the URL shown below.
echo Press Ctrl+C to stop.
echo.

streamlit run app/dashboard.py --server.headless false --browser.gatherUsageStats false

pause
