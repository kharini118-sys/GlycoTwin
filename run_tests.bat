@echo off
echo ============================================================
echo  GlycoTwin -- Test Suite Runner
echo ============================================================
echo.

python -m pytest tests/ -v --tb=short 2>&1

echo.
echo ============================================================
pause
